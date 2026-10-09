"""Import the explicitly supplied 2024 checkpoints without executing their code.

Run with --source PATH to import, or add --check to reproduce and compare the
committed archive. Without --source, validate the portable manifest and files.
The source tree is read-only. Credentials and large scientific data are never
copied. No network calls, installers, or notebook execution occur here.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import json
import re
import shutil
import tempfile

import nbformat

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'content/legacy'
LIVE = 'https://jltobias.github.io/JupyterLite-Climate-and-Health'
LAB = LIVE + '/lite/lab/index.html?path='
NOTEBOOKS = (
    'NB00-Setup-and-Configuration-checkpoint.ipynb',
    'NB01-Background-Foundation-for-Global-Heat-Stress-checkpoint.ipynb',
    'NB01-Introduction-and-Background-checkpoint.ipynb',
    'NB01B-Introduction-Climate-Data-Store-API-and-Climate-Data-Source-ipynb-checkpoint',
    'NB02-Introduction-to-Climate-Data-Store-API-and-Climate-Data-Management-checkpoint.ipynb',
    'NB02B-Data-Collection-and-Analysis-checkpoint.ipynb',
    'NB03-Impact-Assessment-checkpoint.ipynb',
    'NB04-Adaptation-and-Mitigation-Strategies-checkpoint.ipynb',
    'NB05-Modeling-Simulation-and-Decision-Making-checkpoint.ipynb',
    'NB06-Conclusion-and-Reflection-checkpoint.ipynb',
    'NBXX-Air-Polllution-Impacts-HIV-and-TB-checkpoint.ipynb',
    'NBXX-Wildfires-Cyclones-Natural-Disasters-Impacts-to-HIV-and-TB-checkpoint.ipynb',
    'Old-NB01-Global-Heat-Stress-Introduction-and-Data-Management-Updated-checkpoint.ipynb',
    'Old_NB01B-Hello-World-Map-checkpoint.ipynb',
    'Old_NB02-Introduction-to-Climate-Data-Store-API-and-Climate-Data-Management-checkpoint.ipynb',
    'VERYOLD_NB01-Introduction-Background-Data-Management-Copy1-checkpoint.ipynb',
)
SUPPORT = ('provenance-checkpoint.json', 'provenance-checkpoint.png',
           'temperature_above_35_map-checkpoint.html')
SUCCESSORS = (
    ('00_start_here', '13_evidence_atlas'),
    ('01_global_temperature', '03_daily_heat', '04_urban_cooling'),
    ('01_global_temperature', '02_climate_data_literacy'),
    ('02_climate_data_literacy', '03_daily_heat', '13_evidence_atlas'),
    ('02_climate_data_literacy', '03_daily_heat', '13_evidence_atlas'),
    ('02_climate_data_literacy', '03_daily_heat'),
    ('05_coastal_access', '06_service_continuity', '07_mobility'),
    ('04_urban_cooling', '08_coral_bleaching', '09_food_water', '11_adaptation'),
    ('10_compound_hazards', '11_adaptation', '12_capstone'),
    ('12_capstone',),
    ('10_compound_hazards',),
    ('10_compound_hazards', '06_service_continuity'),
    ('01_global_temperature', '02_climate_data_literacy', '03_daily_heat'),
    ('03_daily_heat', '13_evidence_atlas'),
    ('02_climate_data_literacy', '03_daily_heat', '13_evidence_atlas'),
    ('01_global_temperature', '03_daily_heat'),
)
CORE = (0, 1, 3, 4, 5, 6, 7, 8, 9)
EXTENSIONS = (10, 11)
VARIANTS = (2, 12, 13, 14, 15)
BOOK_SLUGS = ('nb00-setup', 'nb01-foundations', 'nb01-introduction-variant',
              'nb01b-data-sources', 'nb02-data-management', 'nb02b-data-analysis',
              'nb03-impact', 'nb04-adaptation', 'nb05-modeling', 'nb06-reflection',
              'nbxx-air-pollution', 'nbxx-disasters', 'old-nb01', 'old-nb01b',
              'old-nb02', 'veryold-nb01')
TITLES = ('NB00 · Setup and configuration', 'NB01 · Background and foundations',
          'NB01 · Introduction and background (historical variant)',
          'NB01B · Climate Data Store API and climate data sources',
          'NB02 · Climate Data Store API and data management',
          'NB02B · Data collection and analysis', 'NB03 · Impact assessment',
          'NB04 · Adaptation and mitigation', 'NB05 · Modeling and decision-making',
          'NB06 · Conclusion and reflection', 'NBXX · Air pollution, HIV and TB',
          'NBXX · Wildfires, cyclones and natural disasters',
          'Old NB01 · Introduction and data management', 'Old NB01B · Hello world map',
          'Old NB02 · Climate data management', 'Very old NB01 · Introduction and background')
RIGHTS = ('Legacy notebooks, their text/code, attachments, third-party figures and '
          'supporting resources are excluded from this repository\'s blanket MIT, '
          'CC BY 4.0 and CC0 grants for original material. Existing notices, '
          'citations and rights remain. The source LICENSE.txt is preserved as '
          'ODbL-1.0; it does not establish a license for individual figures, text '
          'or code. Figure reuse rights have not been independently established.')
RUNTIME = ('Historical reading and editable source archive; not verified executable '
           'end-to-end in JupyterLite/Pyodide. Original scientific statements and '
           'incomplete exercises are preserved, not corrected or endorsed. Saved '
           'code outputs and execution counts are cleared; original attachments '
           'remain. Some cells require a full Python/Jupyter environment, native '
           'geospatial/netCDF libraries, ipywidgets, external downloads or '
           'authenticated CDS/Healthsites APIs. Large climate/facility datasets '
           'and .cdsapirc are not included. Old installers/downloads are not run '
           'by the import, build or archive checks.')
IMAGE = re.compile(r'!\[[^\]]*\]\((?P<markdown>[^\n)]+)\)|'
                   r'<img\b[^>]*?\bsrc=["\'](?P<html>[^"\']+)["\']', re.I)
URL = re.compile(r'https?://[^\s<>"\')\]]+')
FILE_LITERAL = re.compile(r'["\']([^"\'\n]+\.(?:json|csv|nc|png|html|zip|shp|tif|grib|geojson|xlsx))["\']', re.I)
ASSIGNMENT = re.compile(
    r'(?im)(?:["\']?\b(?:api[-_]?key|access[-_]?token|token|secret|password|key)["\']?'
    r'[ \t]*[:=][ \t]*)')
QUOTED_VALUE = re.compile(r'''(?P<quote>["'])(?P<value>(?:\\.|(?!(?P=quote))[^\\\r\n])*)(?P=quote)''')
BARE_VALUE = re.compile(r'''(?P<value>\[REDACTED-CREDENTIAL\]|[^\s"'`,;)}\]]+)(?=[ \t]*(?:$|[,;)}\]]|\#))''')
CREDENTIAL_NAME = re.compile(r'(?:api[-_]?key|access[-_]?token|token|secret|password|key)', re.I)
TOKEN = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|'
                   r'AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{24,})\b|'
                   r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?'
                   r'-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', re.S)


def digest(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def source_text(cell):
    value = cell['source']
    return ''.join(value) if isinstance(value, list) else value


def target_name(name):
    return name if name.endswith('.ipynb') else name + '.ipynb'


def title(name):
    names = [target_name(item) for item in NOTEBOOKS]
    return TITLES[names.index(target_name(name))]


def placeholder(value):
    # Whole-value examples only: real tokens can contain words such as "example".
    return value == '' or bool(re.fullmatch(
        r'(?:\.{3}|\[REDACTED-CREDENTIAL\]|<YOUR[-_ ](?:API[-_ ]KEY|TOKEN|PASSWORD|SECRET)>|'
        r'(?:YOUR|INSERT|REPLACE)[-_ ](?:(?:PERSONAL|ACCESS|API)[-_ ])?'
        r'(?:KEY|TOKEN|SECRET|PASSWORD)(?:[-_ ]HERE)?|'
        r'EXAMPLE[-_](?:API[-_]KEY|TOKEN|PASSWORD|SECRET)|PLACEHOLDER)', value, re.I))


def credential_spans(text):
    """Return locations only: never log or store credential values in a manifest."""
    spans = [(m.start(), m.end()) for m in TOKEN.finditer(text)]
    for match in ASSIGNMENT.finditer(text):
        remainder = text[match.end():].split('\n', 1)[0].rstrip('\r')
        literal = QUOTED_VALUE.match(remainder)
        quoted = literal is not None
        literal = literal or BARE_VALUE.match(remainder)
        if literal is None:
            continue  # Expressions and explanatory prose are not literal assignments.
        value = literal.group('value')
        if not quoted and value.startswith(('http://', 'https://')):
            continue  # Original prose links to the page where a key can be obtained.
        if not placeholder(value):
            start, end = literal.span('value')
            spans.append((match.end() + start, match.end() + end))
    # Merge overlapping recognizers so replacements remain deterministic.
    merged = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def redact(text):
    edits = [{'kind': 'credential_redaction', 'start': start, 'end': end,
              'replacement': '[REDACTED-CREDENTIAL]'} for start, end in credential_spans(text)]
    for edit in reversed(edits):
        text = text[:edit['start']] + edit['replacement'] + text[edit['end']:]
    return text, edits


def assert_no_credentials(value, label):
    # Error messages include locations/paths only, never matched values.
    if isinstance(value, str) and credential_spans(value):
        raise ValueError(f'Credential-like content remains in {label}')
    if isinstance(value, dict):
        for key, child in value.items():
            if CREDENTIAL_NAME.fullmatch(key) and isinstance(child, str) and not placeholder(child):
                raise ValueError(f'Credential-like content remains in {label}')
            if key == 'source' and isinstance(child, list) and all(isinstance(line, str) for line in child):
                assert_no_credentials(''.join(child), label)
            assert_no_credentials(child, label)
    elif isinstance(value, list):
        for child in value:
            assert_no_credentials(child, label)


def valid_notebook(data, label):
    try:
        nbformat.validate(data)
    except Exception:
        # nbformat's default exception includes notebook content, possibly secrets.
        raise ValueError(f'Malformed source notebook: {label}') from None


def safe_source(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path.name == '.cdsapirc':
        raise ValueError('Source path must remain within the collection; credentials are excluded')
    return path


def image_references(text):
    for match in IMAGE.finditer(text):
        key = 'markdown' if match.group('markdown') is not None else 'html'
        raw = match.group(key)
        # These sources use unquoted image destinations, with no Markdown titles.
        yield raw, match.start(key), match.end(key)


def repair_images(text, source, notebook, cell_index, assets):
    edits, missing, remote = [], [], []
    for raw, start, end in image_references(text):
        if raw.startswith(('attachment:', 'data:')):
            continue
        if urlsplit(raw).scheme or raw.startswith('//'):
            remote.append(raw)
            continue
        normalized = unquote(raw).replace('\\', '/').lstrip('./')
        candidates = [normalized, 'images/' + Path(normalized).name]
        found = next((item for item in candidates if safe_source(source, item).is_file()), None)
        if found is None:
            missing.append(raw)
            continue
        target = 'images/' + Path(found).name
        asset = assets.setdefault(target, {'source_path': found, 'kind': 'image', 'references': []})
        if asset['source_path'] != found:
            raise ValueError(f'Ambiguous image filename: {target}')
        asset['references'].append({'notebook': notebook, 'cell_index': cell_index,
                                    'original_reference': raw})
        if raw != target:
            edits.append({'kind': 'markdown_image_path', 'start': start, 'end': end,
                          'original': raw, 'replacement': target})
    for edit in reversed(edits):
        text = text[:edit['start']] + edit['replacement'] + text[edit['end']:]
    return text, edits, missing, remote


def runtime_requirements(cells, source, notebook, assets):
    imports, files, downloads, installers, apis = set(), {}, [], [], []
    for index, cell in enumerate(cells):
        text = source_text(cell)
        if cell['cell_type'] != 'code':
            continue
        imports.update(re.findall(r'(?m)^\s*(?:from|import)\s+([A-Za-z_]\w*)', text))
        if re.search(r'(?i)cdsapi|healthsites|coreapi', text):
            apis.append(index)
        if re.search(r'(?i)\.retrieve\(|urlretrieve|requests\.get|!\s*(?:wget|curl)|\.download\(', text):
            downloads.append(index)
        if re.search(r'(?i)(?:!|%|\$)\s*(?:pip|conda)|pip install|subprocess', text):
            installers.append(index)
        for value in FILE_LITERAL.findall(text):
            normalized = value.replace('\\', '/')
            if urlsplit(normalized).scheme or normalized.startswith(('Plot saved', '.')):
                continue
            if '*' in normalized or '{' in normalized:
                status = 'pattern or generated output; not bundled'
            elif Path(normalized).suffix.lower() == '.json':
                candidates = (normalized, 'resources/' + Path(normalized).name)
                found = next((s for s in candidates if safe_source(source, s).is_file()), None)
                if found:
                    target = 'resources/' + Path(found).name
                    asset = assets.setdefault(target, {'source_path': found, 'kind': 'resource', 'references': []})
                    asset['references'].append({'notebook': notebook, 'cell_index': index,
                                                'original_reference': value})
                    status = 'bundled for inspection at ' + target + '; original code path retained'
                else:
                    status = 'missing from supplied source'
            else:
                path = safe_source(source, normalized)
                status = ('present in source; scientific data/generated output not imported'
                          if path.is_file() else 'missing from supplied source or generated by original code')
            entry = files.setdefault(value, {'reference': value, 'status': status, 'cell_indices': []})
            entry['cell_indices'].append(index)
    return {'imports': sorted(imports), 'local_dependencies': list(files.values()),
            'download_cell_indices': downloads, 'installer_cell_indices': installers,
            'authenticated_api_cell_indices': apis,
            'limits': RUNTIME,
            'resource_path_note': 'Original code paths, including Windows backslashes and bare quiz filenames, remain unchanged. Inspect bundled JSON through the index; path portability is not asserted.'}


def notice(entry):
    successors = ', '.join(f'[{name.replace("_", " ")}]({LAB}notebooks/{name}.ipynb)'
                           for name in entry['modern_successors'])
    return (f'# Archived 2024 notebook — historical source\n\n'
            f'**{entry["original_cell_count"]} original cells** follow. Historical statements and unfinished '
            'activities are preserved. Saved outputs are cleared; original code and supplied attachments remain.\n\n'
            '**Read and edit here; the original workflow is not verified executable end-to-end in Pyodide.** '
            'Old code may need authenticated APIs, external downloads, native packages and a full Python environment. '
            'Large climate/facility data and credentials are omitted. '
            '[Source, exact transformations, imports and missing dependencies](manifest.json).\n\n'
            f'**Optional runnable companions:** {successors}. '
            'The **16 legacy notebooks** lead the course; **14 modern runnable lessons** provide companion practice.\n\n'
            + (f'**Missing from the original:** {len(entry["missing_reading_images"])} image references have no supplied image; see the manifest.\n\n'
               if entry['missing_reading_images'] else '')
            + '**Rights:** legacy text/code, figures and resources retain existing rights and are excluded from '
            'blanket licenses for new original material. [Source ODbL](LICENSE.txt) does not establish individual '
            'content rights. [Course index and full notices](index.ipynb).\n')


def retained_cell(cell):
    """Digest everything except documented transient execution fields."""
    result = deepcopy(cell)
    result.pop('outputs', None)
    result.pop('execution_count', None)
    result['metadata'] = {k: v for k, v in result.get('metadata', {}).items()
                          if k not in ('widgets', 'execution')}
    return result


def import_notebook(source, name, successors, assets):
    relative = '.ipynb_checkpoints/' + name
    raw = safe_source(source, relative).read_bytes()
    try:
        original = json.loads(raw)
    except (ValueError, UnicodeError):
        raise ValueError(f'Malformed source notebook: {name}') from None
    valid_notebook(original, name)
    data = deepcopy(original)
    entry = {'source_path': relative, 'target_path': target_name(name),
             'source_sha256': digest(raw), 'source_bytes': len(raw),
             'original_cell_count': len(data['cells']),
             'modern_successors': list(successors), 'cells': [], 'transformations': [],
             'missing_reading_images': [], 'external_reading_images': []}
    entry['runtime'] = runtime_requirements(original['cells'], source, name, assets)
    if not name.endswith('.ipynb'):
        entry['transformations'].append({'kind': 'append_ipynb_extension'})
    for key in ('widgets',):
        if key in data['metadata']:
            del data['metadata'][key]
            entry['transformations'].append({'kind': 'remove_notebook_metadata', 'key': key})
    for index, cell in enumerate(data['cells']):
        old = original['cells'][index]
        text, redactions = redact(source_text(cell))
        edits = list(redactions)
        if cell['cell_type'] == 'markdown':
            text, repairs, missing, remote = repair_images(text, source, name, index, assets)
            edits += repairs
            entry['missing_reading_images'] += missing
            entry['external_reading_images'] += remote
            for reference, _, _ in image_references(text):
                if reference.startswith('attachment:') and reference[11:] not in cell.get('attachments', {}):
                    entry['missing_reading_images'].append(reference)
        if edits:
            # Redaction coordinates refer to original text; image coordinates to
            # text after redaction. This order is recorded and replayable.
            cell['source'] = text.splitlines(keepends=True) if isinstance(cell['source'], list) else text
            entry['transformations'].append({'kind': 'source_edits', 'cell_index': index,
                                            'stages': ['credential_redaction', 'markdown_image_path'], 'edits': edits})
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
            entry['transformations'].append({'kind': 'clear_execution', 'cell_index': index,
                                            'original_output_count': len(old.get('outputs', [])),
                                            'had_execution_count': old.get('execution_count') is not None})
        for key in ('widgets', 'execution'):
            if key in cell['metadata']:
                del cell['metadata'][key]
                entry['transformations'].append({'kind': 'remove_cell_metadata', 'cell_index': index, 'key': key})
        entry['cells'].append({'index': index, 'cell_type': cell['cell_type'],
                               'original_source_sha256': digest(source_text(old)),
                               'archived_source_sha256': digest(source_text(cell)),
                               'original_retained_sha256': digest(canonical(retained_cell(old))),
                               'archived_retained_sha256': digest(canonical(retained_cell(cell))),
                               'attachments_sha256': digest(canonical(old.get('attachments', {}))),
                               'attachment_names': list(old.get('attachments', {}))})
    data['cells'].insert(0, {'cell_type': 'markdown', 'id': 'legacy-archive-notice',
                             'metadata': {}, 'source': notice(entry).splitlines(keepends=True)})
    entry['transformations'].append({'kind': 'prepend_archive_notice', 'cell_index': 0})
    valid_notebook(data, name)
    assert_no_credentials(data, name)
    return data, entry


def catalog(manifest, location='archive'):
    external = location == 'book'
    base = LIVE + '/lite/files/legacy/' if external else ''
    index = LAB + 'legacy/index.ipynb' if external else 'index.ipynb'
    lines = ['# Original 2024 legacy notebook collection', '',
             '**16 legacy notebooks · 14 separate modern runnable lessons**', '',
             f'[Open the archive index in JupyterLite]({index}) · '
             f'[Optional runnable companion labs]({LAB}notebooks/00_start_here.ipynb)', '',
             RUNTIME, '', RIGHTS, '',
             'Local illustrations and cell attachments are retained for reading, with original citations. '
             'Remote images and linked sites still need internet access and may be unavailable. '
             'Quiz/flashcard JSON is available below; original Windows code paths are preserved.', '']
    for label, indices in [('Original course: nine core chapters', CORE),
                           ('Topic extensions', EXTENSIONS), ('Historical variants', VARIANTS)]:
        lines += ['## ' + label, '', '| Original notebook | Original cells | Open in Lab | Runnable companions |',
                  '|---|---:|---|---|']
        for i in indices:
            item = manifest['notebooks'][i]
            target = item['target_path']
            successors = ', '.join(f'[{s.replace("_", " ")}]({LAB}notebooks/{s}.ipynb)' for s in item['modern_successors'])
            launch = LAB + 'legacy/' + target if external else target
            name = f'[{title(target)}](legacy/{BOOK_SLUGS[i]}.md)' if external else title(target)
            lines.append(f'| {name} | {item["original_cell_count"]} | [Open]({launch}) | {successors} |')
        lines += ['']
    lines += ['', '## Supplied support files', '',
              f'- [Provenance JSON]({base}provenance-checkpoint.json): original provenance record, copied verbatim.',
              f'- [Provenance diagram]({base}provenance-checkpoint.png): original image, copied verbatim.',
              f'- [Original map HTML]({base}temperature_above_35_map-checkpoint.html): **OSM basemap only; no heat overlay**. '
              'Download/open as HTML; its external Leaflet/CDN and tile services need internet access.',
              f'- [Manifest]({base}manifest.json): source/target SHA-256, exact transformations, cell and attachment hashes, '
              'asset provenance, original dependencies and runtime limits.',
              f'- [Preserved source LICENSE.txt]({base}LICENSE.txt): ODbL-1.0; individual content rights remain separate.',
              f'- [Original environment.yml]({base}environment.yml): historical full-environment package list, not a tested install recipe.',
              '', '## Reading resources', '']
    for item in manifest['assets']:
        if item['kind'] == 'resource':
            lines.append(f'- [{item["target_path"]}]({base}{item["target_path"]})')
    lines += ['', '## Preservation and verification', '',
              'The source folder is unchanged. Notebook code/text and attachments are preserved except for recorded '
              'credential redactions (if any) and relative Markdown image-path repairs. All saved code outputs, '
              'execution counts and transient widget/execution metadata are removed. The manifest uses zero-based '
              'original cell indices; add one for the prepended notice. The manifest lists each notebook’s imports, API/download '
              'requirements and missing or omitted local dependencies. Data references include generated output names; '
              'their presence does not establish an input is required.', '',
              'Only the companion labs in `content/notebooks/*.ipynb` are executed by the build. Original Book '
              'chapters are non-executed reading copies. Legacy checks validate preservation and browser opening '
              'without running historical code. The [Book reading-copy manifest]('
              + LIVE + '/legacy-reading-manifest.json) records presentation-only changes to the Book, including '
              'remote-image links, literal DOI text, attachment extraction and heading levels.', '']
    return '\n'.join(lines)


def build_archive(source, destination):
    """Build in a separate destination only; failure cannot mutate the source."""
    source, destination = source.resolve(), destination.resolve()
    if destination == source or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError('Import destination must be separate from the source collection')
    expected = [source / '.ipynb_checkpoints' / name for name in (*NOTEBOOKS, *SUPPORT)]
    expected += [source / 'LICENSE.txt', source / 'environment.yml']
    for path in expected:
        if not path.is_file():
            raise FileNotFoundError(f'Missing explicit source: {path.name}')
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 1, 'source_collection': '2024-Climate-Heat-Stress',
                'notebook_count': 16, 'modern_lesson_count': 14, 'rights': RIGHTS,
                'runtime_limits': RUNTIME, 'notebooks': [], 'assets': []}
    assets, originals = {}, {}
    for name, successors in zip(NOTEBOOKS, SUCCESSORS, strict=True):
        data, entry = import_notebook(source, name, successors, assets)
        path = destination / entry['target_path']
        write_json(path, data)
        entry.update(target_sha256=digest(path.read_bytes()), target_bytes=path.stat().st_size)
        manifest['notebooks'].append(entry)
        originals[name] = json.loads((source / entry['source_path']).read_bytes())
    for name in SUPPORT:
        assets[name] = {'source_path': '.ipynb_checkpoints/' + name, 'kind': 'support', 'references': []}
    for name in ('LICENSE.txt', 'environment.yml'):
        assets[name] = {'source_path': name, 'kind': 'source_notice' if name == 'LICENSE.txt' else 'environment', 'references': []}
    for target, asset in sorted(assets.items()):
        raw = safe_source(source, asset['source_path']).read_bytes()
        if Path(target).suffix in ('.json', '.html', '.txt', '.yml'):
            assert_no_credentials(raw.decode('utf-8'), target)
        path = destination / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        contexts = []
        for ref in asset['references']:
            cells = originals[ref['notebook']]['cells']
            indices = [i for i in range(max(0, ref['cell_index'] - 2), min(len(cells), ref['cell_index'] + 3))
                       if cells[i]['cell_type'] == 'markdown']
            urls = sorted({url for i in indices for url in URL.findall(source_text(cells[i]))})
            contexts.append({'notebook': ref['notebook'], 'original_markdown_cell_indices': indices,
                             'unverified_nearby_context_urls': urls})
        manifest['assets'].append(dict(asset, target_path=target, source_sha256=digest(raw),
                                       target_sha256=digest(raw), bytes=len(raw),
                                       attribution={'status': 'Original notices/citations retained; no new reuse license asserted.',
                                                    'image_source': 'Unresolved; nearby context URLs do not establish the image source or license.'
                                                    if asset['kind'] == 'image' else 'Not an image attribution claim.',
                                                    'original_context': contexts}))
    assert_no_credentials(manifest, 'manifest')
    write_json(destination / 'manifest.json', manifest)
    markdown = catalog(manifest)
    (destination / 'README.md').write_bytes(markdown.encode('utf-8'))
    # Split the index into small Markdown cells for reliable JupyterLab rendering.
    index_cells = []
    for i, section in enumerate(re.split(r'(?m)(?=^## )', markdown)):
        index_cells.append({'cell_type': 'markdown', 'id': f'archive-index-{i}',
                            'metadata': {}, 'source': section.splitlines(keepends=True)})
    write_json(destination / 'index.ipynb', {'cells': index_cells, 'metadata': {}, 'nbformat': 4, 'nbformat_minor': 5})
    validate_archive(destination)
    return manifest


def validate_archive(directory=ARCHIVE):
    manifest = json.loads((directory / 'manifest.json').read_bytes())
    entries = manifest['notebooks']
    if [item['source_path'] for item in entries] != ['.ipynb_checkpoints/' + n for n in NOTEBOOKS]:
        raise AssertionError('The archive must contain exactly the 16 explicit notebooks in order')
    assert manifest['notebook_count'] == 16 and manifest['modern_lesson_count'] == 14
    expected_files = {'manifest.json', 'README.md', 'index.ipynb'}
    expected_files.update(item['target_path'] for item in entries + manifest['assets'])
    actual_files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert actual_files == expected_files, 'Archive contains missing or unlisted files'
    # Validate every published textual artifact, including generated navigation
    # and support files whose hashes alone cannot establish credential safety.
    for relative in sorted(expected_files):
        path = safe_source(directory, relative)
        if path.suffix.lower() in ('.ipynb', '.json', '.md', '.html', '.txt', '.yml', '.yaml'):
            try:
                text = path.read_text(encoding='utf-8')
                value = json.loads(text) if path.suffix in ('.ipynb', '.json') else text
            except (ValueError, UnicodeError):
                raise ValueError(f'Invalid textual archive artifact: {relative}') from None
            assert_no_credentials(value, relative)
    for entry in entries:
        path = directory / entry['target_path']
        assert digest(path.read_bytes()) == entry['target_sha256'], f'Notebook digest mismatch: {path.name}'
        data = json.loads(path.read_bytes())
        valid_notebook(data, path.name)
        assert len(data['cells']) == entry['original_cell_count'] + 1
        assert source_text(data['cells'][0]) == notice(entry)
        assert 'widgets' not in data['metadata']
        for cell, record in zip(data['cells'][1:], entry['cells'], strict=True):
            assert digest(source_text(cell)) == record['archived_source_sha256']
            assert digest(canonical(retained_cell(cell))) == record['archived_retained_sha256']
            assert digest(canonical(cell.get('attachments', {}))) == record['attachments_sha256']
            assert not {'widgets', 'execution'} & cell['metadata'].keys()
            if cell['cell_type'] == 'code':
                assert cell['outputs'] == [] and cell['execution_count'] is None
            if cell['cell_type'] == 'markdown':
                for reference, _, _ in image_references(source_text(cell)):
                    if reference.startswith('attachment:'):
                        assert reference[11:] in cell.get('attachments', {}) or reference in entry['missing_reading_images']
                    elif not urlsplit(reference).scheme and not reference.startswith('//'):
                        assert (directory / reference).is_file() or reference in entry['missing_reading_images']
    for asset in manifest['assets']:
        assert digest((directory / asset['target_path']).read_bytes()) == asset['target_sha256'] == asset['source_sha256']
    assert not list(directory.rglob('.cdsapirc'))
    valid_notebook(json.loads((directory / 'index.ipynb').read_bytes()), 'index.ipynb')
    return manifest


def synchronize_archive(stage, destination, source, repository_root=ROOT):
    """Replace the published inventory only after validating and bounding every path."""
    validate_archive(stage)
    stage, destination, source = stage.resolve(), destination.resolve(), source.resolve()
    repository_root = repository_root.resolve()
    intended = repository_root / 'content' / 'legacy'
    if (destination != intended or not destination.is_relative_to(repository_root)
            or destination.is_relative_to(source) or source.is_relative_to(destination)
            or destination == stage or destination.is_relative_to(stage) or stage.is_relative_to(destination)):
        raise ValueError('Archive synchronization must stay in the intended repository archive and outside the source')

    def checked(path):
        resolved = path.resolve()
        if (path.is_symlink() or not resolved.is_relative_to(destination)
                or resolved.is_relative_to(source)):
            raise ValueError('Unsafe archive synchronization path')
        return path

    staged = {p.relative_to(stage) for p in stage.rglob('*') if p.is_file()}
    existing = list(destination.rglob('*')) if destination.exists() else []
    # Complete the safety audit before deleting or copying anything.
    for path in [*existing, *(destination / relative for relative in staged)]:
        checked(path)
    for path in existing:
        if path.is_file() and path.relative_to(destination) not in staged:
            checked(path).unlink()
    for path in sorted((p for p in existing if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(path.iterdir()):
            checked(path).rmdir()
    destination.mkdir(parents=True, exist_ok=True)
    for relative in sorted(staged):
        target = checked(destination / relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage / relative, target)
    validate_archive(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Explicit path to the untouched 2024 source collection')
    parser.add_argument('--check', action='store_true', help='Reproduce from source and compare; write nothing to the archive')
    args = parser.parse_args()
    if not args.source:
        if args.check:
            parser.error('--check requires --source')
        validate_archive()
        print('PASS legacy manifest: 16 notebooks, source-cell/attachment hashes, assets and runtime notices')
        return
    with tempfile.TemporaryDirectory(prefix='legacy-import-') as temporary:
        stage = Path(temporary) / 'legacy'
        manifest = build_archive(args.source, stage)
        book = catalog(manifest, 'book').encode('utf-8')
        if args.check:
            staged = {p.relative_to(stage) for p in stage.rglob('*') if p.is_file()}
            packaged = {p.relative_to(ARCHIVE) for p in ARCHIVE.rglob('*') if p.is_file()}
            assert staged == packaged, 'Archive file inventory differs from reproducible import'
            for relative in staged:
                assert (stage / relative).read_bytes() == (ARCHIVE / relative).read_bytes(), f'Import differs: {relative}'
            assert (ROOT / 'book/legacy.md').read_bytes() == book
        else:
            synchronize_archive(stage, ARCHIVE, args.source)
            (ROOT / 'book/legacy.md').write_bytes(book)
    print('PASS reproducible legacy import' + (' (check only)' if args.check else '') +
          ': 16 notebooks, all original cells and attachments, referenced reading assets; no legacy code executed')


if __name__ == '__main__':
    main()
