# Attribution and provenance

**Original curriculum and implementation:** James L. Tobias and contributors, *Climate & Health*, 2026. Source repository: https://github.com/jltobias/JupyterLite-Climate-and-Health . The 2024 Climate Heat Stress notebook collection supplied the educational sequence and many learning questions. Code/prose here are independently rewritten; [migration](book/migration.md) maps every source notebook and its methodological corrections.

**Related projects examined:** James L. Tobias and contributors' [JupyterLite Sea-Level-Rise](https://github.com/jltobias/JupyterLite-Sea-Level-Rise) supplied the Book/Lite/dashboard architecture pattern, explicit observed-versus-fictional distinction and service/equity framing. Its README, source audit and helper were inspected; no original poster, actual facilities or flood outputs copied. [DRC Mobility](https://github.com/jltobias/JupyterLite-DRC-Population-Mobility-Border-Mapping) informed portable map stories and movement definitions. [HIVDB Maps](https://github.com/jltobias/JupyterLite-HIVDB-Drug-Resistance-Maps) informed dated snapshot and browser-storage documentation. Those ideas are credited without importing their data or code. STAC gateway reuse is documented with its own source registry.

**Observed temperature:** GISTEMP Team (2026), NASA Goddard Institute for Space Studies, [GISTEMP v4](https://data.giss.nasa.gov/gistemp/), accessed 2026-10-09. Lenssen et al. (2024), *A GISTEMPv4 observational uncertainty ensemble*, https://doi.org/10.1029/2023JD040179 . Global annual J-D °C anomalies relative to 1951–1980, not local temperature observations. Raw snapshot, hash and transform retained.

**Cartography:** Made with Natural Earth, v5.1.2, 1:110m land, public domain. Original source: https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_110m_land.geojson . Not suitable for local coastal risk.

**Actual mapped facilities:** © OpenStreetMap contributors; extracted by Healthsites.io. Archived, non-exhaustive city samples from the user's original World-node source. ODbL-1.0; exact hash, selection and unknown source-date disclosure in `content/data/healthsites_provenance.json`. No claim of current service availability or actual PEPFAR support. The actual layer is never assigned fictional scenario impacts.

**Conceptual illustration:** Built-in OpenAI image generation, original commissioned scene; prompt and generation provenance in `assets/splash-provenance.md`. Fictional people and places. Not a photograph, observed climate event or agency endorsement.

**Methods and contextual references:** [Book reference desk](book/references.md) links WHO, IPCC, NOAA CRW, UNHCR, IDMC, IUCN, CDC India and environmental data providers. NOAA DHW definitions are acknowledged; the teaching SST/HotSpot series is original synthetic data. No linked publisher figure is redistributed.

**Visualization software:** Plotly.js 3.1.0, Copyright Plotly, Inc., MIT. Full license in `licenses/plotly-MIT.txt`; bundled unchanged from https://cdn.plot.ly/plotly-3.1.0.min.js . Runtime software retains upstream notices.

**Evidence Atlas software:** Leaflet 1.9.4, BSD-2-Clause, Vladimir Agafonkin and CloudMade; full notice in `web/stac/vendor/LICENSE-Leaflet.txt`. The original STAC adapter takes architectural inspiration from [JupyterLite-STAC-Browser](https://github.com/jltobias/JupyterLite-STAC-Browser) without copying its code.

**Copernicus metadata:** Copernicus Sentinel-2 data, ESA / European Commission, accessed through Copernicus Data Space Ecosystem on 2026-10-09. Exact scene IDs, query and raw-response digest are packaged. Contains Copernicus Sentinel data (2024); Sentinel legal notice applies. No raster assets are copied.

**Digital Earth Africa metadata:** Water Observations from Space annual summary, 2022; Digital Earth Africa, CC BY 4.0. Item identifiers, query and source links are packaged; cite the [WOfS product specifications](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html). No imagery is copied.

**Reef habitats:** Allen Coral Atlas (2022), *Imagery, maps and monitoring of the world's tropical coral reefs*, doi:10.5281/zenodo.3833242. Allen Coral Atlas Partnership / Arizona State University. CC BY 4.0. Changes: bounded extract of eight WFS polygons near Mombasa, retrieved 2026-10-09. This is not a Planet imagery mosaic or bleaching observation.

**Citizen science:** CoralWatch (2026), Random Survey dataset, public survey `bd39e449-038f-4d45-ab6d-b56922a6f532`, Abu Sawatyr, Egypt, accessed 2026-10-09. CC BY 4.0. Changes: reduced to 20 coral records, numeric chart scores extracted, personal fields/photos/precise coordinates omitted. Source attribution and verification limitations are preserved in `content/data/coralwatch_random_survey_20.metadata.json`.

**Reading and discovery sources:** Every user-suggested provider has a dated card in the [evidence library](book/evidence-library.md), generated from `web/stac/sources.json`. Atlas figures, proprietary layers and external dashboard datasets are linked rather than included unless explicitly listed above.
