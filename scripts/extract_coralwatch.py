"""Fetch and minimize one public CC BY 4.0 CoralWatch Random Survey.

Python standard library only. No authentication. Raw HTML is processed in memory
and never saved; personal fields, photographs, species assertions, and coordinates
are deliberately excluded. Execute this file to regenerate artifacts beside it.
Outputs go to content/data. The public BioCollect page's embedded JSON is not a stable versioned API.
"""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import csv
import hashlib
import io
import json
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / 'content' / 'data'
RECORD_ID = 'bd39e449-038f-4d45-ab6d-b56922a6f532'
PROJECT_ID = '9c55416c-f56a-4917-a65e-da1d64a851f7'
SURVEY_DEFINITION_ID = '6355f9da-ac48-4e23-bb09-e4fdaf3e446f'
SOURCE_URL = f'https://biocollect.ala.org.au/coralwatch/bioActivity/index/{RECORD_ID}'
EXPECTED_LICENSE = 'https://creativecommons.org/licenses/by/4.0/'


def embedded_json(html, name):
    match = re.search(r'var\s+' + re.escape(name) + r'\s*=\s*JSON\.parse\((.*?)\);', html, re.S)
    if not match:
        raise ValueError(f'No embedded {name} JSON; source format changed.')
    literal = match.group(1).strip()
    if not (literal.startswith("'") and literal.endswith("'")):
        raise ValueError('Unexpected JavaScript string encoding; review extractor.')
    # BioCollect encodes JSON as a single-quoted string of Unicode escapes.
    decoded = json.loads('"' + literal[1:-1].replace('"', '\\"') + '"')
    return json.loads(decoded)


def numeric_colour(code):
    match = re.fullmatch(r'[BCDE]([1-6])', str(code))
    if not match:
        raise ValueError('Unexpected chart code; no value will be invented.')
    return int(match.group(1))


request = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'ClimateHealthEducationalExtractor/1.0'})
with urllib.request.urlopen(request, timeout=90) as response:
    raw = response.read()
accessed_at = datetime.now(timezone.utc).isoformat()
html = raw.decode('utf-8')
activity = embedded_json(html, 'activity')
survey = embedded_json(html, 'pActivity')
assert activity['activityId'] == RECORD_ID
assert activity['projectId'] == PROJECT_ID
assert activity['projectActivityId'] == SURVEY_DEFINITION_ID
assert survey['name'] == 'CoralWatch Random Survey'
assert survey['dataSharingLicense'] == EXPECTED_LICENSE, 'License changed: review before redistributing.'
outputs = [o['data'] for o in activity['outputs'] if isinstance(o.get('data'), dict) and 'coralObservations' in o['data']]
assert len(outputs) == 1
source = outputs[0]

# Retain country and reef name only, never point geometry or personal details.
reef_name = None
for site in survey.get('sites', []):
    if isinstance(site, dict) and (site.get('siteId') == source.get('location') or site.get('id') == source.get('location')):
        reef_name = site.get('name')
        break
assert reef_name == 'Abu Sawatyr, Red Sea, Egypt', 'Review geographic context if source changed.'

rows = []
for observation in source['coralObservations']:
    light = numeric_colour(observation['colourCodeLightest'])
    dark = numeric_colour(observation['colourCodeDarkest'])
    average = Decimal(str(observation['colourCodeAverage']))
    assert light <= dark
    assert average == (Decimal(light) + Decimal(dark)) / 2
    rows.append({
        'survey_record_id': RECORD_ID,
        'sample_id': str(observation['sampleId']),
        'event_datetime_source': source['eventDate'],
        'country': source['countryOfSurvey'],
        'reef_context': reef_name,
        'coral_form': observation['typeOfCoral'],
        'lightest_colour_score': light,
        'darkest_colour_score': dark,
        'average_colour_score': str(average),
        'location_accuracy_value_source': source.get('locationAccuracy'),
    })
assert len(rows) == 20, 'Expected source snapshot changed: review before replacing data.'
assert len({r['sample_id'] for r in rows}) == len(rows)

buffer = io.StringIO(newline='')
writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
writer.writeheader()
writer.writerows(rows)
csv_bytes = buffer.getvalue().encode('utf-8')
csv_name = 'coralwatch_random_survey_20.csv'
(ROOT / csv_name).write_bytes(csv_bytes)

schema = {
    'survey_record_id': 'Public BioCollect activity UUID; this identifies a survey, not a person.',
    'sample_id': 'Published within-survey coral sample label; not an observer or global coral identity.',
    'event_datetime_source': 'Published eventDate preserved verbatim. No local-date or local-time-zone inference.',
    'country': 'Published countryOfSurvey, unmodified.',
    'reef_context': 'Published site name at reef/country scale. All coordinates and site geometry omitted.',
    'coral_form': 'Published typeOfCoral morphology category, not verified species identity.',
    'lightest_colour_score': 'Integer 1-6 extracted from published chart code by removing its hue letter.',
    'darkest_colour_score': 'Integer 1-6 extracted from published chart code by removing its hue letter.',
    'average_colour_score': 'Published per-coral colourCodeAverage preserved, and validated as arithmetic mean of the two numeric chart scores.',
    'location_accuracy_value_source': 'Published locationAccuracy value 50; unit not independently verified. Do not assume metres or measurement accuracy.'
}
metadata = {
    'title': 'CoralWatch Random Survey: 20 coral observations from Abu Sawatyr, Egypt',
    'data_kind': 'Actual public citizen-science observations; not synthetic and not satellite-derived thermal stress.',
    'source_record_url': SOURCE_URL,
    'project_url': f'https://biocollect.ala.org.au/coralwatch/project/index/{PROJECT_ID}',
    'project_id': PROJECT_ID,
    'survey_record_id': RECORD_ID,
    'survey_definition_id': SURVEY_DEFINITION_ID,
    'survey_name': survey['name'],
    'event_datetime_source': source['eventDate'],
    'event_time_source': source.get('eventTime'),
    'date_interpretation': 'eventDate and eventTime are source fields. Their local-time-zone relationship is not verified. No conversion or correction was made.',
    'country': source['countryOfSurvey'],
    'reef_context': reef_name,
    'location_accuracy_value_source': source.get('locationAccuracy'),
    'location_accuracy_unit': None,
    'location_accuracy_note': 'Raw published value retained. Unit unverified; source page form includes a default of 50, so this value does not establish a measured positional error.',
    'spatial_accuracy_description_source': survey.get('spatialAccuracy'),
    'method_name_source': survey.get('methodName'),
    'verification_status_source': activity.get('verificationStatus'),
    'license': 'CC BY 4.0',
    'license_url': EXPECTED_LICENSE,
    'license_evidence_url': SOURCE_URL,
    'license_evidence_json_path': 'JavaScript var pActivity -> dataSharingLicense',
    'license_evidence_value': survey['dataSharingLicense'],
    'legal_custodian_organisation_source': survey.get('legalCustodianOrganisation'),
    'source_attribution_verbatim': survey.get('attribution'),
    'citation': f'CoralWatch (2026). CoralWatch Random Survey dataset, survey {RECORD_ID}, Abu Sawatyr, Egypt; 20-observation reduced extract. {SOURCE_URL} (accessed {accessed_at[:10]}). CC BY 4.0. Changes: numeric scores extracted from chart codes; personal fields, exact coordinates, and photographs omitted.',
    'accessed_at_utc': accessed_at,
    'access_date_utc': accessed_at[:10],
    'source_html_sha256': hashlib.sha256(raw).hexdigest(),
    'source_html_retained': False,
    'csv_file': csv_name,
    'csv_sha256': hashlib.sha256(csv_bytes).hexdigest(),
    'record_count': len(rows),
    'extraction_recipe': 'Run python extract_coralwatch.py. Fetch one public survey HTML; decode embedded activity and pActivity JSON; verify exact survey type and CC BY 4.0; select only named fields; strip hue letters from numeric scores; preserve and validate each published average; write sanitized CSV and this metadata.',
    'extractor_file': 'extract_coralwatch.py',
    'extractor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'methods_reference': 'https://coralwatch.org/faqs/',
    'scientific_semantics': [
        'Lightest and darkest are two readings from the same coral colony; their mean is one per-coral descriptive chart index, not two independent coral samples.',
        'Hue letters help observers match colour; this extract retains only the numeric brightness/saturation chart score, as supported by the CoralWatch method.',
        'All 20 published average scores equal (lightest numeric score + darkest numeric score) / 2 exactly.',
        'The 1-6 chart index is not percent bleaching, percent coral cover, chlorophyll concentration, disease risk, or a NOAA Degree Heating Week value.',
        'An average across these 20 per-coral values describes this submitted survey only; it does not estimate all corals in Egypt or the reef, a time trend, climate attribution, or clinical outcomes.',
        'Source verification status is preserved as not applicable; schema and arithmetic checks do not independently verify field observations.'
    ],
    'privacy_and_precision': 'No observer names, observer IDs, contacts, species photos, exact coordinates, centroids, or geometry are retained. Public record link remains available for provenance.',
    'schema': schema,
}
(ROOT / 'coralwatch_random_survey_20.metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'artifact_directory': str(ROOT), 'row_count': len(rows), 'csv_sha256': metadata['csv_sha256'], 'access_date_utc': accessed_at[:10], 'all_published_averages_validated': True}, indent=2))
