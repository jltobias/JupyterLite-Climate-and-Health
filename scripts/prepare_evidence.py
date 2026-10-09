"""Render the source registry into the Book and author the portable evidence lesson.

No network access. Run after editing web/stac/sources.json. Notebook execution is
performed separately by check_notebooks.py; do not regenerate after execution.
"""
from pathlib import Path
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    registry = json.loads((ROOT / 'web/stac/sources.json').read_text(encoding='utf-8'))
    (ROOT / 'content/data/source-registry.json').write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    page = '''# Evidence library and atlas reading room

Use the [interactive Evidence Atlas](https://jltobias.github.io/JupyterLite-Climate-and-Health/stac/) to search satellite metadata, inspect actual habitat polygons and filter this library by theme. [Run the evidence notebook](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/13_evidence_atlas.ipynb) to audit the packaged records without downloading large rasters.

## Choose a health question first

For public-health students and practitioners, the useful starting point is a service, population or exposure question. Use the seven teaching contexts, including India, to investigate care continuity. Their inclusion does not establish that every mapped clinic receives PEPFAR support. See [CDC's India HIV/TB partnership description](https://www.cdc.gov/global-hiv-tb/php/where-we-work/india.html).

| Question | Suggested evidence trail | What to test |
|---|---|---|
| How might extreme heat affect care? | NASA → local weather → archived facility context → WHO/WMO and EAACI | Global anomaly versus local exposure; staffing, power and indoor conditions |
| Which coastal access assumptions matter? | Copernicus → DEA → Climate Central → local elevation and route evidence | Datum, timing, drainage, uncertainty and alternate access |
| What do reef indicators actually measure? | Allen habitat → NOAA thermal stress → CoralWatch field observations | Location and time alignment; habitat, stress and observed colour are distinct |
| What affects food and water security? | FEWS NET → Aqueduct → Global Fishing Watch → local service evidence | Forecast versus assessment, basin versus tap, fishing effort versus nutrition |
| How do risks and resources differ? | Gapminder → MAP → IOM → local disaggregated data | Denominators, missingness, unequal within-country exposure and capacity |
| Which response deserves testing? | Sponge-city activity → UNEP → forest/nature evidence → EAACI | Maintenance, land rights, pollen, drainage, biodiversity and unequal benefits |

## Story studio

Build a five-stop story: **place → observed evidence → uncertainty → possible response → decision needing local input**. Keep a source card beside each map. The bundled JupyterGIS projects demonstrate guided stories; the browser explorer exports a selected scenario or an actual facility project. Notebook.link is an optional launch path, not a dependency or a promise that every upstream integration is available there.

Try a clinic-to-coast tour around Beira; a Mumbai heat and shaded-walking-route proposal; a Mombasa habitat-versus-thermal-stress comparison; or a mobility story that preserves definitions of people and movement events. For an allergy-focused extension, compare shade benefits with pollen and maintenance considerations, using EAACI as a reading source rather than a local risk predictor. For a disparity story, inspect population denominators and within-country differences before interpreting country averages.

## Catalog and reuse boundaries

Checked 9 October 2026. **Bundled** means a named, reproducible local extract exists. **Gateway/reference** means the source is linked for exploration; its underlying datasets are not automatically copied, licensed by this repository, or executed in the core lesson. A provider's terms can differ by product. The table of sources is generated from the same registry as the web atlas.

'''
    for s in registry['sources']:
        page += f"## {s['title']}\n\n**{s['kind']}** · {', '.join(s['themes'])}\n\n{s['description']}\n\n"
        page += f"- **Access:** {s['access']}\n- **Rights:** {s['license']}\n- **Interpretation:** {s['caveat']}\n- **Citation:** {s['citation']}\n\n"
        page += ' · '.join(f'[{name}]({url})' for name, url in s['links'].items()) + '\n\n'
    (ROOT / 'book/evidence-library.md').write_text(page.rstrip() + '\n', encoding='utf-8')
    md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    nb = nbf.v4.new_notebook(cells=[
        md('''# 13 · From a source to a defensible map story

[Run this lesson in Python Lab](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/13_evidence_atlas.ipynb) · [Open the Evidence Atlas](https://jltobias.github.io/JupyterLite-Climate-and-Health/stac/)

**Audience:** public-health students and practitioners. **Time:** 45–60 minutes.

Audit actual packaged satellite metadata, mapped reef habitats, archived facility locations and citizen-science observations. Learn to preserve the denominator, acquisition period, geographic support and license. Nothing in this lesson estimates a patient's disease risk.

The small local files work in JupyterLite. No account, secret key or global raster download is required.'''),
        code('''from pathlib import Path
import json, csv, hashlib
from collections import Counter
from statistics import mean
from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path('../data') if Path('../data').is_dir() else Path('data')
def read_json(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))

snapshots = {name: read_json('stac_' + name + '.json')
             for name in ['copernicus_mumbai', 'dea_beira', 'allen_mombasa']}
audit = [{'sample': name, 'records': len(doc['feature_collection']['features']),
          'class': doc['provenance']['data_class'],
          'retrieved': doc['provenance']['retrieved_on'],
          'rights': doc['provenance']['license']}
         for name, doc in snapshots.items()]
display(pd.DataFrame(audit))'''),
        md('''## Read the time and the footprint

The date when this repository retrieved metadata is distinct from the satellite acquisition date and processing time. A DEA annual item covers an interval. A STAC geometry is a scene footprint, not a flood boundary. Missing cloud cover stays missing.'''),
        code('''rows = []
for name in ['copernicus_mumbai', 'dea_beira']:
    for item in snapshots[name]['feature_collection']['features']:
        p = item['properties']
        rows.append({'sample': name, 'id': item['id'],
                     'start': p.get('start_datetime', p.get('datetime')),
                     'end': p.get('end_datetime', p.get('datetime')),
                     'cloud_percent': p.get('eo:cloud_cover'),
                     'assets': len(item.get('assets', {}))})
display(pd.DataFrame(rows))
print('Cloud values absent:', sum(r['cloud_percent'] is None for r in rows))
print('No imagery pixels have been downloaded or analyzed.')'''),
        md('''## Map a real habitat extract in two dimensions

Allen Coral Atlas provides mapped benthic habitat. The eight polygons below came from one bounded WFS request near Mombasa. They are the first returned features, not a representative sample. Areas and classes are provider attributes; this exercise does not recompute area in longitude/latitude degrees.'''),
        code('''habitats = snapshots['allen_mombasa']['feature_collection']['features']
fig, ax = plt.subplots(figsize=(7, 5))
for feature in habitats:
    geometry = feature['geometry']
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    for polygon in polygons:
        ring = polygon[0]  # Outer ring only: this display is not an area calculation.
        ax.plot([xy[0] for xy in ring], [xy[1] for xy in ring], linewidth=1)
ax.set(xlabel='Longitude (degrees)', ylabel='Latitude (degrees)',
       title='Allen Coral Atlas: eight actual habitat polygons near Mombasa')
ax.set_aspect('equal'); ax.ticklabel_format(useOffset=False)
plt.show()
display(pd.DataFrame([f['properties'] for f in habitats]))
print('Allen Coral Atlas Partnership / Arizona State University; CC BY 4.0; doi:10.5281/zenodo.3833242')'''),
        md('''## Compare field observations without conflating indicators

The CoralWatch sample is from **Egypt**, not the Mombasa polygons above. It demonstrates a different type of evidence and must not be joined as if the locations or dates matched. Each lightest/darkest pair describes one sampled coral. Colour scores are not percent bleaching, reef-wide cover or NOAA Degree Heating Weeks.'''),
        code('''coral_meta = read_json('coralwatch_random_survey_20.metadata.json')
coral_path = DATA / coral_meta['csv_file']
assert hashlib.sha256(coral_path.read_bytes()).hexdigest() == coral_meta['csv_sha256']
corals = pd.read_csv(coral_path)
assert ((corals.lightest_colour_score + corals.darkest_colour_score) / 2 == corals.average_colour_score).all()
print(coral_meta['reef_context'])
print('Published eventDate:', coral_meta['event_datetime_source'])
print('Submitted corals:', len(corals))
print('Descriptive mean of chart scores:', round(mean(corals.average_colour_score), 3))
print(coral_meta['citation'])
display(corals.groupby('coral_form').average_colour_score.agg(['count', 'mean']))'''),
        md('''## Check facility coverage and source rights

The archived Healthsites extract includes India and six African teaching contexts. Counts reflect the selection procedure, not country totals or a measure of health-system capacity. No facility is assigned a synthetic hazard score or presumed PEPFAR service status.'''),
        code('''facilities = read_json('healthsites_facilities.geojson')['features']
assert len({f['properties']['osm_id'] for f in facilities}) == len(facilities)
display(pd.DataFrame(sorted(Counter(f['properties']['context_city'] for f in facilities).items()),
                     columns=['Selected context', 'Archived point features']))
registry = read_json('source-registry.json')
theme = 'Disease'  # Try Water, Reefs, Equity, Adaptation or Earth observation.
display(pd.DataFrame([{'source': s['title'], 'access': s['access'], 'rights': s['license']}
                      for s in registry['sources'] if theme in s['themes']]))'''),
        md('''## Your exercise

1. Change `theme` to a topic relevant to your practice. Choose one source and write the health question it can help contextualize.
2. Use the Evidence Atlas to load one packaged example, inspect an item and export its metadata. Then try a bounded live query. Record whether it succeeded; a failed request does not mean no observations exist.
3. Write a five-stop tour: place, observed evidence, uncertainty, possible response and decision needing local input. Create a source card with product, version, dates, geographic support, units, denominator, missingness and license.
4. Explain why these Egyptian field observations cannot validate a Kenyan habitat polygon, and what a suitable matched field study would require.
5. For a malaria extension, use the MAP gateway to identify one named country summary. Record species, metric, denominator, release, year and uncertainty. Do not call modeled incidence a surveillance count or an effect caused by climate.

## Interpretation

The satellite samples contain scene metadata, not raster measurements. Allen polygons are habitat classifications. CoralWatch contains submitted field colour observations from one survey. Healthsites provides archived map features. Each can support a different question; proximity or shared geography alone cannot establish a causal pathway to health outcomes.

For a disparity story, compare sources that retain population denominators and missingness. Country means hide within-country variation. Separate exposure, susceptibility, service access and adaptive capacity before discussing priorities.

## Source and limitation

Packaged provenance accompanies each source. [Copernicus](https://documentation.dataspace.copernicus.eu/APIs/STAC.html) uses the Sentinel legal notice; [DEA WOfS](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html) and the [Allen mapped habitat product](https://allencoralatlas.org/resources/) use CC BY 4.0. The specific [CoralWatch survey](https://biocollect.ala.org.au/coralwatch/bioActivity/index/bd39e449-038f-4d45-ab6d-b56922a6f532) states CC BY 4.0; other survey types differ. Healthsites/OSM is ODbL 1.0. No provider endorsement is implied.

See the [Book evidence library](https://jltobias.github.io/JupyterLite-Climate-and-Health/book/evidence-library/) for MAP, WHO/WMO, EAACI, IOM, FEWS NET, Aqueduct, forests, fisheries and other linked providers. Linking a gateway does not mean its dataset is packaged or its figures may be copied.''')
    ])
    nb.metadata = {'kernelspec': {'display_name': 'Python (Pyodide)', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}}
    nbf.write(nb, ROOT / 'content/notebooks/13_evidence_atlas.ipynb')
    print(f"Rendered {len(registry['sources'])} source cards and lesson 13")


if __name__ == '__main__':
    main()
