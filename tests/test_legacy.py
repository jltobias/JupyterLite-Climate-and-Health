"""Preservation and navigation tests; never execute an original notebook cell."""
from copy import deepcopy
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import import_legacy as legacy
from prepare_legacy_book import prepare


def source_fixture(root, with_image=False):
    """Small synthetic source collection; never write to the user's originals."""
    checkpoints = root / '.ipynb_checkpoints'; checkpoints.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(legacy.NOTEBOOKS):
        source = '# Historical fixture\n'
        if i == 0 and with_image:
            source += '![image](images/obsolete.png)\n'
        legacy.write_json(checkpoints / name, {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {},
            'cells': [{'cell_type': 'markdown', 'id': 'fixture', 'metadata': {}, 'source': source}]})
    (root / 'images').mkdir(exist_ok=True)
    (root / 'images/obsolete.png').write_bytes(b'synthetic-image-fixture')
    for name, raw in [('provenance-checkpoint.json', b'{}'), ('provenance-checkpoint.png', b'fixture'),
                      ('temperature_above_35_map-checkpoint.html', b'<html>OSM basemap</html>')]:
        (checkpoints / name).write_bytes(raw)
    (root / 'LICENSE.txt').write_text('Synthetic license fixture', encoding='utf-8')
    (root / 'environment.yml').write_text('name: historical-fixture', encoding='utf-8')
    (root / '.cdsapirc').write_text('Excluded synthetic configuration', encoding='utf-8')


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): legacy.digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}


class LegacyPreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = legacy.validate_archive()

    def test_exact_inventory_and_size(self):
        paths = {p.name for p in legacy.ARCHIVE.glob('*.ipynb')}
        self.assertEqual(paths, {'index.ipynb', *(legacy.target_name(n) for n in legacy.NOTEBOOKS)})
        self.assertEqual(len(self.manifest['notebooks']), 16)
        self.assertLess(sum(p.stat().st_size for p in legacy.ARCHIVE.glob('*.ipynb')), 12_000_000)
        self.assertEqual(len(list((ROOT / 'content/notebooks').glob('*.ipynb'))), 14)
        for entry in self.manifest['notebooks']:
            for name in entry['modern_successors']:
                self.assertTrue((ROOT / 'content/notebooks' / (name + '.ipynb')).is_file(), name)
        self.assertEqual({name for entry in self.manifest['notebooks'] for name in entry['modern_successors']},
                         {p.stem for p in (ROOT / 'content/notebooks').glob('*.ipynb')})
        self.assertIn('08_coral_bleaching', self.manifest['notebooks'][7]['modern_successors'])

    def test_reconstruct_original_cells_from_documented_repairs(self):
        """Detect altered prose/code using pre-import cell hashes, even without originals in CI."""
        for entry in self.manifest['notebooks']:
            data = json.loads((legacy.ARCHIVE / entry['target_path']).read_bytes())
            transformed = {t['cell_index']: t for t in entry['transformations'] if t['kind'] == 'source_edits'}
            for cell, record in zip(data['cells'][1:], entry['cells'], strict=True):
                original = deepcopy(cell)
                text = legacy.source_text(cell)
                edits = transformed.get(record['index'], {}).get('edits', [])
                if any(e['kind'] == 'credential_redaction' for e in edits):
                    # Secret content cannot be reconstructed or exposed in a portable manifest.
                    continue
                offset, positioned = 0, []
                for edit in edits:
                    positioned.append((edit, edit['start'] + offset))
                    offset += len(edit['replacement']) - (edit['end'] - edit['start'])
                for edit, begin in reversed(positioned):
                    self.assertEqual(text[begin:begin + len(edit['replacement'])], edit['replacement'])
                    text = text[:begin] + edit['original'] + text[begin + len(edit['replacement']):]
                original['source'] = text.splitlines(keepends=True) if isinstance(cell['source'], list) else text
                self.assertEqual(legacy.digest(text), record['original_source_sha256'], entry['target_path'])
                self.assertEqual(legacy.digest(legacy.canonical(legacy.retained_cell(original))),
                                 record['original_retained_sha256'], entry['target_path'])
                if cell['cell_type'] == 'code':
                    self.assertFalse(edits, 'Code must remain verbatim apart from credentials')

    def test_source_files_when_available(self):
        source = ROOT.parent / '2024-Climate-Heat-Stress'
        if not source.is_dir():
            self.skipTest('Local source not supplied; CI verifies the portable source hashes')
        for entry in self.manifest['notebooks'] + self.manifest['assets']:
            self.assertEqual(legacy.digest((source / entry['source_path']).read_bytes()), entry['source_sha256'])

    def test_support_assets_attribution_and_known_missing_dependencies(self):
        assets = {a['target_path']: a for a in self.manifest['assets']}
        for name in legacy.SUPPORT:
            self.assertEqual(assets[name]['source_path'], '.ipynb_checkpoints/' + name)
            self.assertEqual(assets[name]['source_sha256'], assets[name]['target_sha256'])
        self.assertGreater(sum(a['kind'] == 'image' for a in assets.values()), 15)
        self.assertEqual(sum(a['kind'] == 'resource' for a in assets.values()), 12)
        for asset in assets.values():
            self.assertTrue(asset['attribution']['status'])
            if asset['kind'] in ('image', 'resource'):
                self.assertTrue(asset['references'])
                self.assertTrue(asset['attribution']['original_context'])
                for context in asset['attribution']['original_context']:
                    self.assertIn('unverified_nearby_context_urls', context)
                    self.assertNotIn('nearby_citation_urls', context)
            if asset['kind'] == 'image':
                self.assertIn('Unresolved', asset['attribution']['image_source'])
        variant = self.manifest['notebooks'][2]
        self.assertEqual(sum(len(c['attachment_names']) for c in variant['cells']), 3)
        self.assertEqual(len(variant['missing_reading_images']), 2)
        html = (legacy.ARCHIVE / 'temperature_above_35_map-checkpoint.html').read_text(encoding='utf-8')
        self.assertIn('openstreetmap', html.lower())
        self.assertNotIn('heatLayer', html)
        self.assertNotIn('geo_json', html)

    def test_credential_redaction_preserves_examples_and_never_logs_values(self):
        sample = 'key: YOUR-PERSONAL-TOKEN\napi-key="YOUR-API-KEY-HERE"\napi_key="12345678-abcd-abcd-abcd-123456789012"'
        result, edits = legacy.redact(sample)
        self.assertIn('YOUR-PERSONAL-TOKEN', result)
        self.assertIn('YOUR-API-KEY-HERE', result)
        self.assertIn('[REDACTED-CREDENTIAL]', result)
        self.assertEqual(len(edits), 1)
        self.assertNotIn('12345678', json.dumps(edits))
        with self.assertRaisesRegex(ValueError, 'Credential-like content remains in fixture'):
            legacy.assert_no_credentials(sample, 'fixture')

    def test_literal_credentials_have_no_length_digit_or_substring_exemptions(self):
        # Synthetic values only. Failure labels contain case names, never values.
        cases = {
            'all_letters': 'api_key="alphabeticalcredential"',
            'short_password': "password='abc'",
            'contains_example': 'token="prefixexampleSuffix"',
            'contains_your': 'access_token="prefixyourSuffix"',
            'bracketed_nonplaceholder': 'secret="<actualvalue>"',
            'unquoted_yaml': 'api_key: alphabeticalcredential',
            'unquoted_assignment': 'token=lettersOnly',
            'punctuation': 'password="a!b$c"',
        }
        for label, sample in cases.items():
            with self.subTest(case=label):
                result, edits = legacy.redact(sample)
                self.assertEqual(len(edits), 1, label)
                self.assertIn('[REDACTED-CREDENTIAL]', result, label)
                self.assertEqual(set(edits[0]), {'kind', 'start', 'end', 'replacement'})
                legacy.assert_no_credentials(result, label)
                with self.assertRaisesRegex(ValueError, 'Credential-like content remains in ' + label):
                    legacy.assert_no_credentials(sample, label)
        for value in ('YOUR-API-KEY-HERE', 'YOUR-PERSONAL-TOKEN', '<YOUR_API_KEY>', '...', ''):
            text = 'key="' + value + '"'
            self.assertEqual(legacy.redact(text), (text, []))
        with self.assertRaisesRegex(ValueError, 'Credential-like content remains in nested JSON'):
            legacy.assert_no_credentials({'credentials': {'token': 'syntheticexamplevalue'}}, 'nested JSON')

    def test_all_textual_artifacts_are_scanned_with_safe_error_labels(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / 'source'; source_fixture(source)
            archive = root / 'archive'; legacy.build_archive(source, archive)
            paths = ('manifest.json', 'index.ipynb', 'README.md', 'provenance-checkpoint.json',
                     'temperature_above_35_map-checkpoint.html', 'LICENSE.txt', 'environment.yml')
            for relative in paths:
                path = archive / relative; original = path.read_bytes()
                with self.subTest(artifact=relative):
                    if path.suffix in ('.json', '.ipynb'):
                        data = json.loads(original)
                        data['test_credentials'] = {'password': 'syntheticShort'}
                        legacy.write_json(path, data)
                    else:
                        path.write_bytes(original + b'\npassword="syntheticShort"\n')
                    with self.assertRaises(ValueError) as caught:
                        legacy.validate_archive(archive)
                    self.assertEqual(str(caught.exception), 'Credential-like content remains in ' + relative)
                    path.write_bytes(original)

    def test_reimport_removes_obsolete_files_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / 'source'; repo = root / 'repository'
            destination = repo / 'content/legacy'
            source_fixture(source, with_image=True)
            before = tree_hashes(source)
            first = root / 'stage-first'; legacy.build_archive(source, first)
            legacy.synchronize_archive(first, destination, source, repo)
            self.assertEqual(tree_hashes(source), before)
            self.assertTrue((destination / 'images/obsolete.png').is_file())
            # Deliberate fixture-only source revision: the second import has fewer assets.
            source_fixture(source, with_image=False)
            before = tree_hashes(source)
            second = root / 'stage-second'; legacy.build_archive(source, second)
            legacy.synchronize_archive(second, destination, source, repo)
            self.assertEqual(tree_hashes(source), before)
            self.assertFalse((destination / 'images/obsolete.png').exists())
            self.assertFalse((destination / '.cdsapirc').exists())
            self.assertEqual(tree_hashes(destination), tree_hashes(second))
            outside = root / 'outside'; outside.mkdir(); (outside / 'keep.txt').write_text('keep')
            with self.assertRaises(ValueError):
                legacy.synchronize_archive(second, outside, source, repo)
            with self.assertRaises(ValueError):
                legacy.synchronize_archive(second, source, source, repo)
            self.assertEqual((outside / 'keep.txt').read_text(), 'keep')
            self.assertEqual(tree_hashes(source), before)

    def test_missing_and_malformed_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source'; source.mkdir()
            with self.assertRaisesRegex(FileNotFoundError, 'Missing explicit source'):
                legacy.build_archive(source, root / 'out')
            checkpoints = source / '.ipynb_checkpoints'; checkpoints.mkdir()
            path = checkpoints / legacy.NOTEBOOKS[0]
            path.write_text('{"nbformat":4,"cells":"secret-content"}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Malformed source notebook') as error:
                legacy.import_notebook(source, path.name, (), {})
            self.assertNotIn('secret-content', str(error.exception))
            with self.assertRaises(ValueError):
                legacy.safe_source(source, '../outside.png')
            with self.assertRaises(ValueError):
                legacy.safe_source(source, '.cdsapirc')

    def test_indexes_and_primary_order(self):
        index = json.loads((legacy.ARCHIVE / 'index.ipynb').read_bytes())
        text = '\n'.join(legacy.source_text(c) for c in index['cells'])
        self.assertTrue(all(c['cell_type'] == 'markdown' for c in index['cells']))
        self.assertEqual(text.count('](' + legacy.target_name(legacy.NOTEBOOKS[3]) + ')'), 1)
        for name in legacy.NOTEBOOKS:
            self.assertIn('](' + legacy.target_name(name) + ')', text)
        positions = [text.index(legacy.title(legacy.NOTEBOOKS[i])) for i in (*legacy.CORE, *legacy.EXTENSIONS, *legacy.VARIANTS)]
        self.assertEqual(positions, sorted(positions))
        for name in legacy.SUPPORT:
            self.assertIn('](' + name + ')', text)
        self.assertIn('no heat overlay', text)
        for path in ('README.md', 'book/index.md', 'book/start.md', 'book/myst.yml', 'web/index.html', 'web/stac/index.html'):
            self.assertIn('?path=legacy/index.ipynb', (ROOT / path).read_text(encoding='utf-8'), path)
        toc = (ROOT / 'book/myst.yml').read_text(encoding='utf-8')
        self.assertLess(toc.index('legacy/nb00-setup.md'), toc.index('notebooks/*.ipynb'))
        self.assertNotIn('license: CC-BY-4.0', toc)
        self.assertTrue((ROOT / 'content/START_HERE.ipynb').is_file())
        self.assertIn('| NB01B Climate Data Store API and Climate Data Sources |',
                      (ROOT / 'book/migration.md').read_text(encoding='utf-8'))
        self.assertIn("manifest's notebook-specific", (ROOT / 'book/start.md').read_text(encoding='utf-8'))

    def assert_markdown_reaches_reading_copy(self, notebook, record, text):
        blocks = {int(index): block.rstrip('\n') for index, block in re.findall(
            r'<!-- Original cell (-?\d+); archive notice is -1\. -->\n(.*?)(?=\n<!-- Original cell |\Z)', text, re.S)}
        for index, cell in enumerate(notebook['cells'][1:]):
            if cell['cell_type'] != 'markdown':
                continue
            source = legacy.source_text(cell)
            actual = blocks[index]
            if not record['cells'][index + 1]['transformations']:
                self.assertEqual(actual.strip(), source.strip(), f'Original Markdown cell {index} was altered or omitted')
            else:
                # Presentation edits can change headings, images and DOI markup.
                # Other prose must reach the actual cell block independently of hashes.
                for line in source.splitlines():
                    if line.strip() and not re.search(r'!\[|<img|attachment:|doi\.org', line):
                        self.assertIn(re.sub(r'^#{1,6}\s+', '', line), actual,
                                      f'Original prose missing from cell {index}')

    def test_book_reading_copies_preserve_every_cell_without_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            records = prepare(destination)
            self.assertEqual(len(records), 16)
            for entry, record in zip(self.manifest['notebooks'], records, strict=True):
                self.assertEqual(len(record['cells']), entry['original_cell_count'] + 1)
                source = json.loads((legacy.ARCHIVE / entry['target_path']).read_bytes())
                text = (destination / record['reading_copy']).read_bytes().decode('utf-8')
                self.assertNotIn('```{code-cell}', text)
                self.assertIn('code is not executed', text)
                for cell, saved in zip(source['cells'], record['cells'], strict=True):
                    self.assertEqual(legacy.digest(legacy.source_text(cell)), saved['archived_source_sha256'])
                    if cell['cell_type'] == 'code':
                        self.assertIn(legacy.source_text(cell), text)
                self.assert_markdown_reaches_reading_copy(source, record, text)
                if record['reading_copy'] == 'nb06-reflection.md':
                    summary = legacy.source_text(source['cells'][3])
                    self.assertEqual(len(summary), 1022)
                    self.assertIn(summary, text)
                    # Reproduce the reviewer's empty-summary mutation; the new
                    # assertion must fail even if all recorded hashes still match.
                    with self.assertRaises(AssertionError):
                        self.assert_markdown_reaches_reading_copy(source, record, text.replace(summary, '', 1))
            self.assertEqual(len(list((destination / 'attachments').glob('*'))), 3)
            # Independent expected presentation results, not renderer-computed hashes.
            foundations = (destination / 'nb01-foundations.md').read_text(encoding='utf-8')
            self.assertIn('![Cartoon of people sharing a leaking boat, illustrating the shared consequences of ignoring a problem at the other end.](images/rowboat.png)', foundations)
            self.assertIn('[External illustration: image](https://docs.xarray.dev/en/stable/_images/dataset-diagram.png)', foundations)
            impact = (destination / 'nb03-impact.md').read_text(encoding='utf-8')
            self.assertIn('alt="AIDS 2024 conference poster on potential sea-level-rise and storm-surge impacts to coastal cities and health facilities, with maps, methods and references."', impact)
            self.assertIn('`https://doi.org/10.1029/2020EF001885`', impact)
            variant = (destination / 'nb01-introduction-variant.md').read_text(encoding='utf-8')
            self.assertIn('![Screenshot of a National Geographic greenhouse-effect article, including arrows for incoming sunlight and heat exchange between the surface and atmosphere.]', variant)
            self.assertIn('**Missing original image:**', variant)
            for record in records:
                for cell in record['cells']:
                    for change in cell['transformations']:
                        if isinstance(change, dict) and 'image_description' in change:
                            self.assertTrue(change['image_description']['basis'])


if __name__ == '__main__':
    unittest.main()
