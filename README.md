# Climate & Health

The **original 2024 Climate Heat Stress notebooks** organize this course for public-health students and practitioners: nine core chapters from setup and climate foundations through impact, adaptation, modeling and reflection, plus two topic extensions. All 16 supplied historical notebooks are preserved; 14 newer runnable notebooks serve as optional companion labs.

[![Climate & Health conceptual illustration](assets/climate-health-splash.png)](https://jltobias.github.io/JupyterLite-Climate-and-Health/)

*Original AI-generated conceptual artwork: fictional places and people, not observations. [Prompt and provenance](assets/splash-provenance.md).*

| Open the live experience | What you can do |
|---|---|
| [Learning hub](https://jltobias.github.io/JupyterLite-Climate-and-Health/) | Choose a reading, coding or exploration path |
| [Jupyter Book](https://jltobias.github.io/JupyterLite-Climate-and-Health/book/) | Read original chapters, preserved text/code and local figures; companion labs include executed results |
| [Original course in Lab](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/index.ipynb) | Browse nine core chapters, two extensions and five historical variants |
| [Runnable companion labs](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/00_start_here.ipynb) | Optional: edit and run 14 compact modern exercises |
| [Maps and adaptation explorer](https://jltobias.github.io/JupyterLite-Climate-and-Health/explore/) | Switch 2D/rotatable extruded 3D maps, actual Healthsites context, fictional scenarios and exports |
| [3D coastal clinic](https://jltobias.github.io/JupyterLite-Climate-and-Health/explore/?view=scene&case=beira) | Move the conceptual water plane and compare road/floor thresholds |
| [Guided story tour](https://jltobias.github.io/JupyterLite-Climate-and-Health/explore/?view=tour) | Follow evidence → access → service dependencies → adaptation → uncertainty |
| [JupyterGIS story project](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=projects/climate-health.jGIS) | Open local geographic layers and author a guided story |
| [Satellite metadata gateway](https://jltobias.github.io/JupyterLite-Climate-and-Health/stac/) | Discover Copernicus and other environmental data, sources and limitations |
| [Notebook.link launcher](https://notebook.link/github/jltobias/JupyterLite-Climate-and-Health/) | Alternative repository runtime; open `content/projects/climate-health.jGIS` |

Reading the original course needs no login. Historical notebooks retain their original text/code and embedded figures, with an archive notice and outputs cleared. They are **not verified executable end-to-end in Pyodide**: original downloads, API credentials, native packages and large data may require a full environment. Original science and incomplete activities are preserved, not corrected. The local source folder remains unchanged.

The optional companion labs need no API key and run in Python (Pyodide). Download browser-local edits to keep them. The explorer's 3D view needs WebGL; its 2D map and tables remain usable without it.

## Original course sequence

- [NB00 · Setup and configuration](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB00-Setup-and-Configuration-checkpoint.ipynb)
- [NB01 · Background and foundations](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB01-Background-Foundation-for-Global-Heat-Stress-checkpoint.ipynb)
- [NB01B · Climate Data Store API and climate data sources](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB01B-Introduction-Climate-Data-Store-API-and-Climate-Data-Source-ipynb-checkpoint.ipynb)
- [NB02 · Climate Data Store API and data management](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB02-Introduction-to-Climate-Data-Store-API-and-Climate-Data-Management-checkpoint.ipynb)
- [NB02B · Data collection and analysis](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB02B-Data-Collection-and-Analysis-checkpoint.ipynb)
- [NB03 · Impact assessment](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB03-Impact-Assessment-checkpoint.ipynb)
- [NB04 · Adaptation and mitigation](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB04-Adaptation-and-Mitigation-Strategies-checkpoint.ipynb)
- [NB05 · Modeling and decision-making](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB05-Modeling-Simulation-and-Decision-Making-checkpoint.ipynb)
- [NB06 · Conclusion and reflection](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/NB06-Conclusion-and-Reflection-checkpoint.ipynb)

Two NBXX extensions cover air pollution and wildfires/cyclones/disasters. Five older variants remain in the [complete 16-notebook index](book/legacy.md), alongside the provenance diagram/JSON, **OSM-only map (no heat overlay)**, quiz resources, cell-level manifest and source notices. Each chapter links to relevant companion exercises.

## Optional runnable companion labs

| Lesson | Core analysis |
|---|---|
| 00 Start here | Provenance, actual mapped-feature sample versus fictional clinics, and a first service calculation |
| 01 Global temperature | Real NASA GISTEMP anomalies, baseline and period comparisons |
| 02 Climate data literacy | Kelvin conversion, latitude-area weighting, ensemble quantiles and missingness |
| 03 Daily heat | Correct extremes, counts, persistence and season-year grouping |
| 04 Urban cooling | Surface albedo arithmetic and explicit cooling assumptions |
| 05 Coastal access | Shared vertical datum, access/floor thresholds and elevation sensitivity |
| 06 Service continuity | HIV/TB service dependencies, water/power bottlenecks and supply cover |
| 07 Mobility | Movement events versus people; host-community demand |
| 08 Coral thermal stress | Exactly 84 days of qualifying HotSpots and DHW; stress versus bleaching |
| 09 Food and water | Storage mass balance, deficits and household budget sensitivity |
| 10 Compound hazards | Service dependencies under heat, outages, storms and security interruption |
| 11 Adaptation | Nature-based and engineering packages, budget constraints, equity and sponge-city runoff arithmetic |
| 12 Capstone | A reproducible briefing, local export, story and formative self-assessment |
| 13 Evidence atlas | Inspect real environmental metadata, provider provenance and evidence limits |

All 14 companion labs include runnable analysis, interpretation, exercise, source and limitation. [Teaching guide](book/teaching-guide.md) · [Migration from original notebooks](book/migration.md) · [Data and methods](book/data-and-methods.md) · [Evidence library](book/evidence-library.md) · [Story authoring](book/story-authoring.md).

## Evidence and scope

NASA GISTEMP is a **real global observed annual anomaly series**, not a local heat exposure dataset. Natural Earth supplies coarse public-domain geography. Archived Healthsites/OpenStreetMap features are a separate incomplete, dated-unknown map inventory; presence does not establish current operation, HIV/TB services or PEPFAR support.

The Evidence Atlas includes bounded Copernicus and Digital Earth Africa metadata snapshots, eight Allen Coral Atlas habitat polygons, and a reproducible 20-record CoralWatch survey extract. Its **37-source library** covers every suggested provider and atlas, including Malaria Atlas Project, FEWS NET, Aqueduct, forests, migration, planetary health, poverty and disparities. Each card states its citation, rights, access and limits. External gateways remain distinct from bundled data; no provider API key is embedded.

Clinic attributes, daily local temperature, capacities, costs and movements are **original synthetic teaching data**. The explorer is not a flood forecast, causal disease model, validated digital twin, legal-status determination or country risk ranking. India, Mozambique, South Africa, Kenya, Zambia, Uganda and Nigeria are teaching contexts, not a complete program roster. The companion labs do not contain a PEPFAR facility portfolio, patient records, old API keys or multi-GB inputs. The separate legacy collection preserves supplied historical figures and source code under their existing rights; those items are excluded from this repository's original-content license grants.

The source `2024-Climate-Heat-Stress` files remain unchanged. Related public projects, explicitly including [JupyterLite Sea-Level-Rise](https://github.com/jltobias/JupyterLite-Sea-Level-Rise), informed the combined Book/Lite/dashboard, source-audit and continuity-story patterns. [Attribution](ATTRIBUTIONS.md) records the adaptations and providers.

## Build and verify

Use Python 3.13. Direct build packages are pinned; Node is supplied by `nodejs-wheel`. Activate your environment so its executables are on PATH.

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python -m unittest discover -s tests
node --test tests/test_stac.mjs
python scripts/build.py
python scripts/browser_smoke.py
python scripts/check_legacy_browser.py
python scripts/check_evidence.py
python scripts/check_runtime.py
```

The build regenerates deterministic fixtures, executes the 14 companion notebooks in fresh kernels, prepares non-executed reading copies of the 16 original notebooks, builds **Jupyter Book 2** with strict checks, builds **JupyterLite + Pyodide + JupyterGIS + Specta**, assembles `_site/`, and validates authored local links. It reuses the observed snapshot; `python scripts/prepare_data.py --refresh` explicitly refreshes NASA and the pinned geography. `scripts/make_notebooks.py` regenerates authored lessons before re-execution. Actual Healthsites and STAC archives have separate acquisition/provenance scripts.

After editing `web/stac/sources.json`, run `python scripts/prepare_evidence.py` to regenerate the Book library, portable registry and evidence lesson, then rebuild to execute it. `scripts/check_evidence.py --live` additionally checks current provider browser access; external availability is not required for the packaged lessons. `scripts/check_runtime.py` proves fresh Pyodide execution and navigates the actual JupyterGIS story.

For a root local preview, run `python scripts/build.py --base-url ""`, then `python -m http.server 8000 --directory _site`. The default build embeds `/JupyterLite-Climate-and-Health/book` in Book assets, matching Pages. The browser smoke script serves that prefix correctly without changing the build.

GitHub Actions runs numerical checks, notebook execution, strict builds, route checks and browser interactions before deployment on `main`. Configure Pages source to **GitHub Actions**. Failed checks prevent artifact deployment. No credentials are needed for the static site; external data services may have their own terms or authentication for optional downloads.

## Repository layout

`content/legacy/` holds the primary original course and manifest; `content/START_HERE.ipynb` makes it visible at Lab root. `content/notebooks/` contains optional runnable companions. `content/` also contains, portable helpers, small data and `.jGIS` projects. `book/` holds MyST pages and configuration. `web/` holds the hub, explorer and catalog gateway. `scripts/` prepares, builds and verifies; `tests/` covers calculations and provenance. `_site/`, build caches and local environments are ignored.

Original software: [MIT](LICENSE). Original educational prose: CC BY 4.0. Original synthetic data: CC0. External data and software retain their terms. See [license scope](LICENSES.md), [full references](book/references.md), and [CITATION.cff](CITATION.cff). No agency endorsement or accredited certification is implied.

To reproduce the legacy import from the untouched source, run `python scripts/import_legacy.py --source "C:/Users/duf2/2024-Climate-Heat-Stress" --check`. Omit `--check` to regenerate the archive. `python scripts/import_legacy.py` validates the packaged manifest without needing the source folder. `scripts/prepare_legacy_book.py` creates non-executed Book reading copies and a separate transformation manifest; it never runs old code.
