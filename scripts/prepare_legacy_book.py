"""Render reading copies of all legacy cells; never execute historical code.

Canonical notebooks stay in content/legacy. Book-specific changes and source
cell hashes are recorded in reading-manifest.json in the generated subtree.
"""
from pathlib import Path
import base64
import html
import json
import re
import shutil

from import_legacy import (ARCHIVE, BOOK_SLUGS, LAB, LIVE, ROOT, catalog, digest,
                           source_text, title, validate_archive, write_json)

# Descriptions come from the supplied figures and their preserved surrounding
# explanations. They describe historical illustrations, not verified findings.
FIGURE_DESCRIPTIONS = {
    'rowboat.png': 'Cartoon of people sharing a leaking boat, illustrating the shared consequences of ignoring a problem at the other end.',
    'ostrich.png': 'Illustration of an ostrich with its head in the sand, used in the original lesson as a metaphor for ignoring warming.',
    'Mora-et-al-2017.png': 'Four world maps compare historical conditions with RCP 2.6, 4.5 and 8.5 using the paper’s temperature-and-humidity heat threshold; the original caption explains uncertainty.',
    'BN459_Fig1.jpg': 'Historical ranking of ten global risks, with climate action failure and extreme weather at the top and colors grouping risk categories.',
    'Global-Environmental-Change.jpg': 'Conceptual feedback diagram linking environmental change with migration, infectious disease, infrastructure, food security, HIV/AIDS and household resources.',
    '1-s2.0-S2667278221001036-gr1.jpg': 'Conceptual model of pathways from climate hazards and social determinants of health to HIV-related outcomes, discussed in the surrounding original text.',
    'Frontline-AIDS-Climate-HIV-Framework.png': 'Framework connecting climate hazards, migration, food insecurity, economic stress and health-system disruption with HIV prevention, treatment, health and rights.',
    'Bressler-Moore-Rennert-Antoff-2021.png': 'Two world maps compare projected end-of-century temperature-related mortality under RCP 4.5 and RCP 8.5; gray marks countries without sufficient data.',
    'Bressler-Moore-Rennert-Antoff-2021-2.png': 'Two world maps compare projected temperature-related mortality with income-based adaptation under RCP 4.5 and RCP 8.5; gray marks insufficient data.',
    'Mora-et-al-2022.png': 'Historical infographic with a ring chart separating infectious diseases described as aggravated or not aggravated by climatic hazards in the cited review.',
    'AIDS2024eposterTHPEF698.png': 'AIDS 2024 conference poster on potential sea-level-rise and storm-surge impacts to coastal cities and health facilities, with maps, methods and references.',
    'powerbi-report.png': 'Screenshot of the original Power BI report comparing health-facility flood-risk maps by decade and RCP scenario, as described in the adjacent notebook text.',
    'trees.png': 'Urban-tree infographic illustrating shade, evapotranspiration, rain interception, carbon storage and air-pollutant uptake around buildings.',
    'SpongeCities.png': 'Sponge-city illustration of green roofs, wetlands, trees and permeable surfaces used to capture, slow and filter stormwater.',
    '1-s2.0-S0308597X23001537-ga1_lrg.jpg': 'Nature, technology and society diagram used in the original discussion of uncertainty, ambiguity and adaptive coping strategies for coastal planning.',
    'Trillion-Trees.png': 'Tree-shaped infographic linking forest protection, restoration and ending deforestation with community action, global commitments and suitable planting locations.',
    'How-soils-sustains-ecosystems.png': 'Soil cross-section surrounded by explanations of plant growth, carbon storage, habitat, nutrient cycling, water filtration and water storage.',
    'Coastal-Blue-Carbon.png': 'Coastal cross-section showing carbon uptake, release and storage across kelp, seagrass, mangroves, salt marsh and underlying sediments.',
    'Particulate-Size-Comparison.png': 'Size comparison of PM10 and PM2.5 particles with a human hair; the diagram labels their diameter ranges in micrometers.',
    '6dc804d3-5f44-415c-a5ee-d6b0c96da43d.png': 'Screenshot of a National Geographic greenhouse-effect article, including arrows for incoming sunlight and heat exchange between the surface and atmosphere.',
    'caff1161-00cb-45eb-94f1-a5b0116b7e6d.png': 'Cartoon of passengers in a leaking boat; a speech bubble dismisses the hole because it is at the other end.',
    '51a447b9-ea8f-4884-8b27-06650c224e1a.png': 'Illustration of an ostrich standing on sand with its head in a hole, used as a metaphor for ignoring a shared problem.',
}


def describe_images(text, transforms):
    def description(target, old):
        name = Path(target).name
        if target.startswith('attachments/'):
            name = name.split('-', 1)[1]  # Remove the extracted attachment digest.
        if name not in FIGURE_DESCRIPTIONS:
            raise ValueError(f'No reviewed Book image description: {name}')
        value = FIGURE_DESCRIPTIONS[name]
        transforms.append({'image_description': {'target': target, 'original_alt': old,
                                                  'description': value,
                                                  'basis': 'Supplied image and preserved nearby explanation; not independent scientific or rights verification.'}})
        return value

    def markdown(match):
        target = match.group('target')
        return '![' + description(target, match.group('alt')) + '](' + target + ')'

    def image_tag(match):
        tag = match.group()
        target = re.search(r'\bsrc=["\']([^"\']+)["\']', tag).group(1)
        alt = re.search(r'\balt=(["\'])(.*?)\1', tag)
        value = html.escape(description(target, alt.group(2) if alt else None), quote=True)
        if alt:
            return tag[:alt.start()] + f'alt="{value}"' + tag[alt.end():]
        return re.sub(r'\s*/?>$', f' alt="{value}">', tag)

    text = re.sub(r'!\[(?P<alt>[^\]]*)\]\((?P<target>(?:images|attachments)/[^)]+)\)', markdown, text)
    return re.sub(r'<img\b[^>]*?\bsrc=["\'](?:images|attachments)/[^"\']+["\'][^>]*>', image_tag, text)


def prepare(destination=None):
    destination = destination or ROOT / 'book/legacy'
    destination.mkdir(parents=True, exist_ok=True)
    manifest = validate_archive()
    for asset in manifest['assets']:
        if asset['kind'] == 'image':
            target = destination / asset['target_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ARCHIVE / asset['target_path'], target)
    records = []
    for entry, slug in zip(manifest['notebooks'], BOOK_SLUGS, strict=True):
        notebook = json.loads((ARCHIVE / entry['target_path']).read_bytes())
        lines = [f'# {title(entry["target_path"])}', '',
                 '**Original 2024 chapter · historical reading copy · code is not executed**', '',
                 'Local figures are shown below. Remote illustrations remain links; DOI strings are shown '
                 'verbatim as text to avoid adding live citation lookups to the historical reading edition. '
                 'Original links and formatting remain in the Lab notebook.', '',
                 f'[Open the complete original notebook in Lab]({LAB}legacy/{entry["target_path"]}) '
                 '· [Course index](../legacy.md)', '']
        cells = []
        heading_depth = 1
        for index, cell in enumerate(notebook['cells']):
            text = source_text(cell)
            transforms = []
            if index == 0:
                # The archive notice is authored, not part of the original source.
                text = text.replace('# Archived 2024 notebook — historical source', '## Archive notice')
                for target in ('index.ipynb', 'manifest.json', 'LICENSE.txt'):
                    url = LAB + 'legacy/index.ipynb' if target.endswith('.ipynb') else LIVE + '/lite/files/legacy/' + target
                    text = text.replace('](' + target + ')', '](' + url + ')')
                transforms.append('Adapt added archive notice links for the Book')
            elif cell['cell_type'] == 'code':
                fence = '`' * max(3, max((len(m.group()) + 1 for m in re.finditer(r'`+', text)), default=3))
                text = f'{fence}python\n{text}\n{fence}'
                transforms.append('Wrap original code in a non-executing Python fence')
            elif cell['cell_type'] == 'raw':
                text = '````text\n' + text + '\n````'
                transforms.append('Wrap raw cell as literal text')
            if cell['cell_type'] == 'markdown':
                for name, attachment in cell.get('attachments', {}).items():
                    mime = next((m for m in attachment if m.startswith('image/')), None)
                    if mime is None:
                        raise ValueError('Unsupported reading attachment MIME type')
                    raw = base64.b64decode(''.join(attachment[mime]))
                    attachment_target = 'attachments/' + digest(raw)[:16] + '-' + name
                    path = destination / attachment_target
                    path.parent.mkdir(exist_ok=True)
                    path.write_bytes(raw)
                    text = text.replace('attachment:' + name, attachment_target)
                    transforms.append({'attachment_extracted': name, 'target': attachment_target, 'sha256': digest(raw)})
                for missing in entry['missing_reading_images']:
                    if missing in text:
                        text = re.sub(r'!\[([^\]]*)\]\(' + re.escape(missing) + r'\)',
                                      r'**Missing original image:** \1 (`' + missing + '`)', text)
                        transforms.append({'missing_image_placeholder': missing})
                def remote_image(match):
                    url = match.group('url')
                    replacement = '[External illustration: ' + (match.groupdict().get('alt') or 'original source') + '](' + url + ')'
                    transforms.append({'remote_image_to_link': url})
                    return replacement
                text = re.sub(r'!\[(?P<alt>[^\]]*)\]\((?P<url>https?://[^)]+)\)', remote_image, text)
                text = re.sub(r'<img\b[^>]*?src=["\'](?P<url>https?://[^"\']+)["\'][^>]*>', remote_image, text)
                text = describe_images(text, transforms)
                # MyST automatically fetches citations for DOI links; the archive
                # preserves their original text without inventing citation data.
                doi = r'https?://(?:dx\.)?doi\.org/[^\s<>"\]]+'
                def doi_link(match):
                    label, url = match.group(1), match.group(2)
                    transforms.append({'doi_link_to_literal': url})
                    return label + ' (`' + url + '`)'
                text = re.sub(r'\[([^\]]*)\]\((' + doi + r')\)', doi_link, text)
                def literal_doi(match):
                    url = match.group(0)
                    transforms.append({'doi_to_literal': url})
                    return '`' + url + '`'
                text = re.sub(r'(?<![`(])' + doi, literal_doi, text)
                normalized = []
                for line in text.splitlines(keepends=True):
                    match = re.match(r'^(#{1,6})[ \t]+', line)
                    if match:
                        depth = min(max(2, len(match.group(1))), heading_depth + 1)
                        heading_depth = depth
                        if depth != len(match.group(1)):
                            transforms.append({'heading_depth': [len(match.group(1)), depth], 'text': line.rstrip()})
                            line = '#' * depth + line[len(match.group(1)):]
                    normalized.append(line)
                text = ''.join(normalized)
            lines += [f'<!-- Original cell {index - 1}; archive notice is -1. -->', text, '']
            cells.append({'original_cell_index': index - 1, 'archived_source_sha256': digest(source_text(cell)),
                          'reading_source_sha256': digest(text), 'transformations': transforms})
        rendered = '\n'.join(lines).encode('utf-8')
        (destination / (slug + '.md')).write_bytes(rendered)
        records.append({'notebook': entry['target_path'], 'reading_copy': slug + '.md',
                        'sha256': digest(rendered), 'cells': cells})
    write_json(destination / 'reading-manifest.json', {'execution': 'never', 'chapters': records})
    return records


if __name__ == '__main__':
    prepare()
    print('Prepared 16 original Book reading chapters without executing legacy code')
