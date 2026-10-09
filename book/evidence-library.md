# Evidence library and atlas reading room

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

## The GDELT Project

**News-derived metadata gateway** · Conflict context, Disease, Storytelling, Climate literacy

Machine-extracted events, mentions, themes, locations and tone support media-literacy exercises around climate and health reporting.

- **Access:** Public bulk metadata, BigQuery and documented DOC/GEO APIs. Search availability can be intermittent; no live media result is required by core lessons.
- **Rights:** GDELT's own terms permit dataset reuse and redistribution with citation and a project link. These rights do not license publishers' articles, images or video.
- **Interpretation:** News mentions are not verified event counts, disease incidence or causation. Geocoding, language, outlet coverage and duplicated reporting introduce bias; sparse coverage does not mean low need.
- **Citation:** The GDELT Project, named Event/Mentions/GKG or API product, extraction query, time window, release and access date; link original reports when checking claims.

[User-suggested project](https://gdeltproject.org/) · [Data and documentation](https://gdeltproject.org/data.html) · [Terms](https://gdeltproject.org/about.html#termsofuse) · [GEO API](https://blog.gdeltproject.org/gdelt-geo-2-0-api-debuts/)

## PovertyMaps.net / Meta Relative Wealth Index

**Modeled relative-wealth gateway** · Equity, Livelihoods, Care access

Berkeley/Meta microestimates describe relative living standards within countries at approximately 2.4 km resolution, with uncertainty.

- **Access:** Country CSVs via HDX. The user-suggested PovertyMaps.net beta viewer currently redirects to an HTTP IP address; use the HTTPS HDX gateway for source data.
- **Rights:** Upstream HDX metadata specifies CC BY-NC 4.0. Preserve authors, license, changes and uncertainty; do not infer rights from a differently licensed derivative catalog.
- **Interpretation:** Relative wealth is not a dollar poverty threshold or household/clinic status, and raw scores are not directly comparable across countries. Paper coverage and downloadable release coverage differ; metadata update dates are not observation years.
- **Citation:** Chi, G., Fang, H., Chatterjee, S., and Blumenstock, J.E. (2022). Microestimates of wealth for all low- and middle-income countries. PNAS 119(3), e2113658119. doi:10.1073/pnas.2113658119; cite selected HDX release.

[HTTPS data gateway](https://data.humdata.org/dataset/relative-wealth-index) · [User-suggested viewer (redirects to HTTP)](https://www.povertymaps.net/) · [Primary metadata and license](https://data.humdata.org/api/3/action/package_show?id=relative-wealth-index) · [Research](https://doi.org/10.1073/pnas.2113658119)

## Gapminder: climate gaps and disparities

**Interactive indicator and household-context gateway** · Equity, Climate literacy

Explore country indicators in Gapminder Tools and household examples in Dollar Street. Compare emissions, income and population with aligned years and denominators.

- **Access:** Public tools and indicator downloads; trace each indicator to its original source.
- **Rights:** Covered Gapminder free materials and Dollar Street images: CC BY 4.0 with supplied credits. Underlying indicator and software licenses vary; do not infer blanket rights.
- **Interpretation:** Interpolated or extrapolated series are not all direct observations. Country means hide inequality; Dollar Street households are examples, not prevalence estimates. PPP-adjusted household consumption differs from salary or GDP.
- **Citation:** Gapminder, selected tool/indicator, original provider, release and access date. Adapted material credit: Based on free material from GAPMINDER.ORG, CC-BY LICENSE.

[Provider](https://www.gapminder.org/) · [Tools](https://www.gapminder.org/tools/) · [Data](https://www.gapminder.org/data/) · [Dollar Street](https://www.gapminder.org/dollar-street) · [Material terms](https://www.gapminder.org/free-material/) · [Gap filling](https://www.gapminder.org/sources/data-crunching-principles/)

## Global Nature Watch / Global Forest Watch

**Forest and ecosystem monitoring gateway** · Ecosystems, Adaptation, Earth observation

WRI renamed Global Forest Watch to Global Nature Watch in September 2026; existing forest maps and dashboards continue within broader ecosystem monitoring.

- **Access:** Public maps, layer metadata and downloads. Some analysis endpoints require API keys or OAuth; large rasters need an appropriate workflow.
- **Rights:** Named UMD tree-cover-loss and integrated-alert layers: CC BY 4.0. Other layer and platform rights vary. Tree-cover credit: Source: Hansen/UMD/Google/USGS/NASA.
- **Interpretation:** Tree-cover loss can reflect harvest, fire or natural disturbance, not necessarily deforestation. Alerts are investigation leads, not unbiased regional trend/area estimates. Tree gain can include plantations.
- **Citation:** Hansen et al. (2013), doi:10.1126/science.1244693; tree-cover loss v1.13 through 2025, accessed 2026-10-09. Integrated alerts: UMD/GLAD and WUR, accessed through Global Nature Watch; retain exact version.

[User-suggested platform](https://globalnaturewatch.org/) · [Rename announcement](https://www.wri.org/news/release-global-forest-watch-becomes-global-nature-watch-expanding-cover-more-land-ecosystems) · [Tree-cover metadata](https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss) · [Alert metadata](https://data-api.globalforestwatch.org/dataset/gfw_integrated_alerts)

## Global Nature Watch Horizon

**AI-assisted discovery preview** · Ecosystems, Climate literacy

A separate interface for exploring GNW and Land & Carbon Lab evidence through natural-language questions.

- **Access:** External preview; no public integration API verified. Follow its source references back to the underlying data.
- **Rights:** Underlying dataset terms remain separate from interface and generated-summary rights. No platform output or imagery republished here.
- **Interpretation:** AI summaries can be incomplete or incorrect; verify figures, dates, place definitions and citations. A generated answer is not a validated local environmental assessment.
- **Citation:** Global Nature Watch Horizon / WRI, underlying named dataset and exact cited release; record access date and any generated interpretation separately.

[Horizon](https://horizon.globalnaturewatch.org/) · [Underlying platform](https://globalnaturewatch.org/)

## An atlas of human suffering — public communication

**Historical advocacy commentary** · Equity, Climate literacy

A Campaign against Climate Change response to the 2022 IPCC impacts assessment, useful for tracing public claims back to assessed evidence.

- **Access:** Public article; linked reading only.
- **Rights:** No open reuse license verified. Do not copy the article's separately credited photograph.
- **Interpretation:** This is a secondary advocacy article, not an official IPCC atlas, dataset or independent scientific assessment.
- **Citation:** Claire (2022-03-01). An atlas of human suffering: the latest IPCC report. Campaign against Climate Change.

[User-suggested article](https://www.campaigncc.org/ipcc_atlas_of_human_suffering) · [Primary IPCC assessment](https://www.ipcc.ch/report/ar6/wg2/)

## IPCC AR6: Impacts, Adaptation and Vulnerability

**Primary scientific assessment** · Climate literacy, Adaptation, Disease, Equity

The 2022 Working Group II assessment provides the scientific context for climate impacts, adaptation options and vulnerability.

- **Access:** Public report and chapter downloads; use official citations and chapter-specific confidence statements.
- **Rights:** IPCC/Cambridge publication rights and figure credits apply; this project links the report and writes its own synthesis.
- **Interpretation:** Preserve scenario, period, geography and assessed confidence. Global findings do not independently validate a local clinic model or attribute an individual disaster.
- **Citation:** IPCC (2022). Climate Change 2022: Impacts, Adaptation and Vulnerability. Cambridge University Press. doi:10.1017/9781009325844.

[Report](https://www.ipcc.ch/report/ar6/wg2/) · [Official citation](https://www.ipcc.ch/report/ar6/wg2/about/how-to-cite-this-report/)

## JRC World Atlas of Desertification

**Historical atlas and convergence-of-evidence gateway** · Land degradation, Food, Water, Livelihoods

Third-edition WAD3 maps overlapping land, water and socioeconomic concerns as starting points for local investigation.

- **Access:** Public atlas, data catalog, convergence explorer and country reports; some legacy interactive endpoints can be intermittent.
- **Rights:** © European Union 2018; WAD3-JRC material reusable with source acknowledgement and preserved meaning. Third-party material retains separate rights. Named convergence dataset separately states CC BY 4.0.
- **Interpretation:** Convergence of issues is not measured land degradation, a current drought forecast or a health-risk score. Indicators span different historical periods and need local validation.
- **Citation:** Cherlet, M., Hutchinson, C., Reynolds, J., Hill, J., Sommer, S., and von Maltitz, G. (eds.) (2018). World Atlas of Desertification, 3rd ed. Publications Office of the European Union. doi:10.2760/06292.

[User-suggested atlas](https://wad.jrc.ec.europa.eu/) · [Data catalog](https://wad.jrc.ec.europa.eu/geoportal) · [Convergence explorer](https://wad.jrc.ec.europa.eu/convergenceofevidence) · [Rights](https://wad.jrc.ec.europa.eu/about_atlas) · [Publication](https://publications.jrc.ec.europa.eu/repository/handle/JRC111155)

## University of Washington Global Refugee Atlas

**Historical humanistic-GIS reference** · Mobility, Equity, Storytelling

Origin–host connections, journey narratives, camp imagery and contextual indicators demonstrate multiple ways to communicate refugee experiences.

- **Access:** Public atlas and source inventory; obtain analysis data from the original providers.
- **Rights:** No project-wide reuse license verified. Open-source dependencies do not license all photographs, narratives, geometry or underlying data. Link only.
- **Interpretation:** Its page titled Flow explains end-2018 refugee population stocks. Connections are not observed routes or annual movements and do not establish climate causation.
- **Citation:** Zhao, B., Van Den Hoek, J., Alix-Garcia, J., Svevo, G., Baldrica-Franklin, G., and Katz, G. (2019). Global Refugee Atlas. University of Washington Humanistic GIS project.

[User-suggested atlas](https://hgis.uw.edu/refugee/) · [Origins and hosts](https://hgis.uw.edu/refugee/origin.html) · [Journeys](https://hgis.uw.edu/refugee/journey_menu.html) · [Sources](https://hgis.uw.edu/refugee/sources.html)

## UNHCR forcibly displaced and stateless population maps

**Official population-statistics gateway** · Mobility, Equity, Care access

Compare populations by origin, asylum and defined status; pair maps with official stock-versus-flow guidance.

- **Access:** Public annex and data portal. Preserve the selected reference date; the inspected annex describes end-2025 data. Automated access can be rate limited.
- **Rights:** Refugee Data Portal datasets: CC BY 4.0 unless otherwise indicated; website design, software and logos excluded. Preserve original providers and disclose changes.
- **Interpretation:** Refugees, asylum-seekers, IDPs, returnees and stateless people have distinct definitions and can overlap. Stocks are not annual arrivals. These data alone cannot identify climate-attributable displacement.
- **Citation:** UNHCR, Maps of forcibly displaced and stateless people, selected population group and reference date; underlying Refugee Data Portal release, accessed 2026-10-09.

[User-suggested maps](https://www.unhcr.org/refugee-statistics/insights/annexes/forcibly-displaced-maps.html) · [Common mistakes](https://www.unhcr.org/refugee-statistics/insights/explainers/common-mistakes-forcibly-displaced-data.html) · [Flow data](https://www.unhcr.org/refugee-statistics/insights/explainers/forcibly-displaced-flow-data.html) · [Terms](https://refugeedata.unhcr.org/en/terms-and-conditions-of-use/)

## Atlas of Informality

**Public neighborhood-case map and methods** · Urban health, Equity, Care access, Storytelling

Selected informal-neighborhood boundaries at two historical dates support discussion of settlement change, heat, flooding and service access.

- **Access:** Public ArcGIS map and mapping protocol; no geometry or photographs copied into this repository.
- **Rights:** Dataset license unspecified in inspected ArcGIS metadata. The linked 2020 article is CC BY 4.0; this does not establish rights for separate map geometry or images.
- **Interpretation:** Curated cases are not a complete settlement inventory. Boundary growth does not independently measure population, displacement, exposure or health-service access.
- **Citation:** Samper, J., Shelby, J.A., and Behary, D. (2020). The Paradox of Informal Settlements Revealed in an ATLAS of Informality. Sustainability 12(22), 9510. doi:10.3390/su12229510.

[User-suggested atlas](https://www.atlasofinformality.com/) · [Protocol](https://www.atlasofinformality.com/protocol) · [Map](https://ucboulder.maps.arcgis.com/apps/mapviewer/index.html?webmap=004efe9b9a2646b3b66625092771cf1e) · [Article](https://doi.org/10.3390/su12229510)

## Atlas of Vulnerability: Developing Countries and the Pandemic

**Regional indicator-dashboard reference** · Equity, Care access, Climate literacy

Jubilee USA Network and LATINDADD compare economic, social, health and environmental conditions across 26 Latin American and Caribbean countries; database updated September 2024.

- **Access:** Public indicator comparisons and exports; versions and indicator years differ.
- **Rights:** No explicit open reuse license verified. Download availability does not grant redistribution permission; check original indicator terms.
- **Interpretation:** This is a regional indicator dashboard, not a global climate score. Latest-available values can refer to different years; align units, dates, denominators and missingness before comparison.
- **Citation:** Jubilee USA Network and LATINDADD. Atlas of Vulnerability: Developing Countries and the Pandemic. Database updated September 2024; accessed 2026-10-09.

[User-suggested atlas](https://vulnerabilityatlas.org/) · [Instructions](https://vulnerabilityatlas.org/using-the-map?lang=en)

## Surgo Africa COVID-19 Community Vulnerability Index

**Historical pandemic-planning index** · Disease, Equity, Care access

The 2021 release compares seven vulnerability themes across 756 admin-1 regions in 48 countries.

- **Access:** Public dashboard and archived Zenodo dataset; cross-country scores cover 36 countries because source differences restrict comparability.
- **Rights:** Archived dataset: CC BY-NC 4.0; dashboard content separately reserves rights. No index data copied here.
- **Interpretation:** Relative rankings depend on comparison scope; they are not infection probabilities, current burden or individual risk. Facility-per-capita indicators do not identify PEPFAR-supported facilities.
- **Citation:** Mishra, A., et al. (2021). Africa COVID-19 Community Vulnerability Index (CCVI). Zenodo, published 28 April 2021. doi:10.5281/zenodo.4725492.

[User-suggested dashboard](https://precisionforcovid.org/africa) · [Dataset](https://doi.org/10.5281/zenodo.4725492) · [Methods](https://covid-static-assets.s3.amazonaws.com/Africa+CCVI+methodology.pdf)

## World Bank Global Subnational Poverty Atlas

**Subnational socioeconomic-data gateway** · Equity, Livelihoods, Care access

GSAP supplies survey-based poverty estimates aligned to common years, principally at admin-1 scale. Current catalog identifies the AM26 / September 2026 vintage.

- **Access:** Public map, downloadable tables and polygons. The linked map selects a 2023 estimate, not a 2023 PPP base.
- **Rights:** CC BY 4.0 plus World Bank published additional terms; preserve release, original sources and transformations. No household-microdata access is implied.
- **Interpretation:** The $3.00 threshold is per person per day in 2021 PPP international dollars, not nominal USD. Area poverty rates do not identify individual poverty, clinic vulnerability or climate-caused displacement.
- **Citation:** World Bank (2026). Global Subnational Poverty Atlas, AM26/September 2026 vintage; $3.00/day, 2021 PPP; reference year 2023. Accessed 2026-10-09.

[User-suggested map](https://pipmaps.worldbank.org/en/data/datatopics/poverty-portal/poverty-geospatial?dataset=PovertyRate3.00-gsap&zoomLevel=3&lat=19.53676432208408&lng=15.02343750000001&year=2023) · [Data catalog](https://datacatalog.worldbank.org/search/dataset/0042041/global-subnational-poverty-atlas-gsap) · [Terms](https://datacatalog.worldbank.org/public-licenses?fragment=cc)

## GEM Global Economic Vulnerability Map

**Hazard-specific comparison index** · Equity, Climate literacy

Version 2020.1 combines country-level economic exposure and resilience indicators in an earthquake-oriented framework covering 136 countries.

- **Access:** Public product description and OpenQuake viewer; linked comparison only.
- **Rights:** CC BY-NC-SA 4.0. This license remains separate from the repository's original materials.
- **Interpretation:** An earthquake economic-vulnerability index is not a climate-risk forecast or facility assessment. The source page's PDF/citation text refers inconsistently to the social-vulnerability product; use the economic title, version and DOI.
- **Citation:** Burton, C., and Toquica, M. (2020). Global Economic Vulnerability Map, version 2020.1. doi:10.13117/GEM-ECONOMIC-VULNERABILITY-MAP.

[User-suggested product](https://www.globalquakemodel.org/gem-maps/global-economic-vulnerability-map) · [Viewer](https://maps.openquake.org/map/sv-global-economic-vulnerability/) · [Economic-map DOI](https://doi.org/10.13117/GEM-ECONOMIC-VULNERABILITY-MAP)

## NASA GISTEMP v4

**Bundled observations** · Heat, Climate literacy

Global annual land–ocean temperature anomalies, with raw source snapshot and provenance.

- **Access:** Packaged CSV; public NASA tables.
- **Rights:** NASA scientific data; cite GISTEMP Team and the dataset methods paper.
- **Interpretation:** Anomaly relative to 1951–1980; global average is not a clinic temperature or personal heat exposure.
- **Citation:** GISTEMP Team (2026), GISS Surface Temperature Analysis v4; Lenssen et al. (2024), doi:10.1029/2023JD040179. Accessed 2026-10-09.

[Data](https://data.giss.nasa.gov/gistemp/) · [Methods](https://doi.org/10.1029/2023JD040179)

## Healthsites.io / OpenStreetMap

**Bundled archived facility locations** · Care access, Facilities

155 unique OSM point features selected from the original repository's Healthsites archive across seven teaching contexts, including Mumbai.

- **Access:** Local GeoJSON and provenance; Healthsites services for fresh data.
- **Rights:** Open Database License 1.0. © OpenStreetMap contributors, via Healthsites.io. Derivative database obligations apply.
- **Interpretation:** Original extraction date unknown. Selected point features are incomplete; location does not establish current operation, service availability or PEPFAR funding.
- **Citation:** Healthsites.io / OpenStreetMap contributors. Selected archived World-node features from 2024-Climate-Heat-Stress; processed 2026-10-09. Original OSM node IDs retained.

[Provider](https://healthsites.io/) · [Attribution](https://www.openstreetmap.org/copyright) · [License](https://opendatacommons.org/licenses/odbl/1-0/)

## Copernicus Data Space STAC

**Live metadata + packaged scenes** · Earth observation, Coasts, Heat

Search bounded Sentinel-2 L2A scene footprints and asset metadata; Mumbai example included.

- **Access:** Public metadata search; asset downloads can have separate authentication requirements.
- **Rights:** Copernicus Sentinel Data Legal Notice; collection declares license identifier 'other'. Preserve acquisition and source credit.
- **Interpretation:** Reflectance is not air temperature. A footprint does not show hazard extent; cloud fraction for a whole scene does not describe a specific clinic pixel.
- **Citation:** Copernicus Sentinel-2 data, ESA / European Commission, accessed via Copernicus Data Space Ecosystem; exact scene identifiers and access date in export.

[User-suggested browser](https://browser.stac.dataspace.copernicus.eu/) · [API documentation](https://documentation.dataspace.copernicus.eu/APIs/STAC.html) · [Legal notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice)

## Digital Earth Africa

**Live metadata + packaged annual-water items** · Earth observation, Water, Adaptation

WOfS annual water observations and Sentinel-2 GeoMAD metadata; Beira WOfS example included.

- **Access:** Public STAC metadata and cloud-hosted assets; advanced raster analysis can use the DEA Sandbox.
- **Rights:** Named WOfS and GeoMAD products: CC BY 4.0, with product acknowledgements including modified Copernicus data for GeoMAD.
- **Interpretation:** Wet/clear observation frequency is not flood probability, depth or water quality. Preserve valid-observation counts, clouds, acquisition period and CRS.
- **Citation:** Digital Earth Africa Water Observations from Space annual summary, 2022, accessed 2026-10-09; exact item identifiers in snapshot. Cite the selected product specifications.

[Catalog](https://explorer.digitalearth.africa/) · [WOfS specifications](https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html) · [GeoMAD specifications](https://docs.digitalearthafrica.org/en/latest/data_specs/GeoMAD_specs.html)

## Allen Coral Atlas

**Bundled bounded habitat extract** · Reefs, Earth observation, Coasts

Eight actual benthic habitat polygons near Mombasa, served from the provider's public WFS. They complement the synthetic thermal-stress lesson.

- **Access:** Public WFS/WMS; some downloads require registration. No global Atlas dataset or Planet mosaic is republished here.
- **Rights:** Mapped habitat products: CC BY 4.0; separate Planet imagery terms include CC BY-NC-SA 4.0. Consult provider conditions for global redistribution.
- **Interpretation:** Habitat classification is not observed bleaching, current ecological condition or fish production. This first-page extract is not representative coverage.
- **Citation:** Allen Coral Atlas (2022), Imagery, maps and monitoring of the world's tropical coral reefs. doi:10.5281/zenodo.3833242. Allen Coral Atlas Partnership / Arizona State University. Bounded extract accessed 2026-10-09.

[Atlas](https://allencoralatlas.org/) · [Resources and rights](https://allencoralatlas.org/resources/) · [Citation](https://doi.org/10.5281/zenodo.3833242)

## NOAA Coral Reef Watch

**Methods and operational-data gateway** · Reefs, Heat

Satellite sea-surface temperature and thermal-stress products; methodology informs the course's synthetic 84-day Degree Heating Week exercise.

- **Access:** Public product and methodology pages; no operational NOAA reef observations are bundled in the DHW exercise.
- **Rights:** NOAA public-domain data, with NOAA Coral Reef Watch attribution and product-specific citation.
- **Interpretation:** Thermal stress indicates exposure, not directly observed bleaching. Do not substitute CoralWatch chart scores for satellite DHW.
- **Citation:** NOAA Coral Reef Watch: cite exact product, version, dates and recommended publication from its citation guidance.

[Methods](https://coralreefwatch.noaa.gov/product/5km/methodology.php) · [Citation guidance](https://coralreefwatch.noaa.gov/satellite/docs/recommendations_crw_citation.php)

## CoralWatch citizen science

**Bundled real field observations** · Reefs, Citizen science

Twenty coral colour observations from one public Random Survey at Abu Sawatyr, Red Sea, Egypt. Personal fields and precise coordinates omitted.

- **Access:** Packaged CSV plus public BioCollect survey; published eventDate retained verbatim.
- **Rights:** This Random Survey explicitly states CC BY 4.0. Other survey types can use CC BY-NC 2.5: never generalize this license to the entire portal.
- **Interpretation:** Scores are a descriptive chart index, not percent bleaching, coral cover or a representative reef estimate. Schema checks do not independently verify field observations.
- **Citation:** CoralWatch (2026), Random Survey bd39e449-038f-4d45-ab6d-b56922a6f532, Abu Sawatyr, Egypt. 20-observation reduced extract, accessed 2026-10-09. Changes documented in packaged metadata.

[Provider](https://coralwatch.org/) · [Survey](https://biocollect.ala.org.au/coralwatch/bioActivity/index/bd39e449-038f-4d45-ab6d-b56922a6f532) · [Methods](https://coralwatch.org/faqs/)

## Climate Central coastal tools

**External tool / licensed-data gateway** · Coasts, Sea level, Care access

Coastal Risk Finder, CoastalDEM, coastal flood layers and portfolio screening support advanced coastal questions.

- **Access:** Use public tools; data packages and commercial products require the applicable negotiated access or license.
- **Rights:** Product-specific Climate Central terms. No CoastalDEM raster, proprietary flood layer or restricted portfolio dataset is bundled.
- **Interpretation:** Elevation threshold maps require datum, connectivity, uncertainty, defenses and time-horizon checks before inferring inundation or facility disruption.
- **Citation:** Climate Central: cite selected tool or product, model version, scenario, horizon and access date.

[Provider](https://www.climatecentral.org/) · [Coastal Risk Finder](https://coastal.climatecentral.org/) · [CoastalDEM](https://www.climatecentral.org/climate-services/coastaldem) · [Terms](https://www.climatecentral.org/what-we-do/legal)

## AlphaEarth.ai — carbon-market platform

**External commercial platform** · Adaptation, Climate literacy

The user-suggested alphaearth.ai domain is a carbon-market intelligence platform operated by Crelocks LLC.

- **Access:** Subscription and platform-specific access.
- **Rights:** Provider terms; no redistribution permission inferred and no platform dataset copied.
- **Interpretation:** This domain is distinct from Google / Google DeepMind's AlphaEarth Foundations satellite embeddings.
- **Citation:** AlphaEarth.ai, Crelocks LLC. Platform and terms accessed 2026-10-09.

[User-suggested platform](https://alphaearth.ai/) · [Terms](https://alphaearth.ai/terms)

## Google AlphaEarth Foundations

**Advanced open-data gateway** · Earth observation, Adaptation

Annual 10 m satellite embeddings with 64 dimensions for environmental pattern analysis, available through Earth Engine and a public cloud bucket.

- **Access:** Earth Engine account or documented public GCS access; large tiles need a suitable processing environment.
- **Rights:** CC BY 4.0. Required credit: The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.
- **Interpretation:** Embedding dimensions are not temperature, disease, carbon or habitat measurements. Validate any downstream classifier; preserve exact tile and year availability.
- **Citation:** Google and Google DeepMind, Satellite Embedding V1 Annual; Brown et al. (2025), doi:10.48550/arXiv.2507.22291. Cite the exact release and tiles used.

[Dataset](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL) · [Public cloud guide](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme)

## Global Fishing Watch

**External map / authenticated API** · Food, Reefs, Livelihoods

Explore apparent fishing effort and maritime activity as livelihood and ecosystem context.

- **Access:** Public map; API requires a personal bearer token. No API token is embedded in the site.
- **Rights:** Public API terms include CC BY-NC 4.0 plus dataset-specific conditions. Required attribution: Powered by Global Fishing Watch.
- **Interpretation:** Modeled apparent fishing hours are not catch, illegal activity or dietary intake. AIS coverage favors larger vessels and misses much artisanal activity.
- **Citation:** Global Fishing Watch, exact dataset/version and period; cite API terms and methods. Powered by Global Fishing Watch.

[Map](https://globalfishingwatch.org/map/) · [Datasets](https://globalfishingwatch.org/datasets-and-code/) · [API terms](https://api-doc.globalfishingwatch.org/our-apis/documentation/docs/license-rate-limits)

## FEWS NET food-security outlooks

**External assessment-data gateway** · Food, Livelihoods, Care access

Acute food insecurity maps and outlooks provide regional livelihood and nutrition context.

- **Access:** Public map and geographic-data downloads; retain issue date, target period and assessed versus projected status.
- **Rights:** Dataset-specific FEWS NET use and attribution policy; do not assume a blanket Creative Commons license.
- **Interpretation:** An ordinal area phase is not every household's outcome and must not be averaged into a disease-risk score. IPC-compatible analyses are not necessarily IPC consensus products.
- **Citation:** FEWS NET, country, product, issue date, assessment/projection period, URL and access date; include credited partner sources.

[Provider](https://fews.net/) · [Acute food insecurity data](https://fews.net/data/acute-food-insecurity) · [Attribution policy](https://help.fews.net/fdp/data-and-information-use-and-attribution-policy)

## WRI Aqueduct Water Risk Atlas 4.0

**External open-data gateway** · Water, Adaptation

Baseline and future water-risk indicators for comparing explicitly defined basin-level conditions.

- **Access:** Public map, data downloads and indicator dictionary.
- **Rights:** CC BY 4.0 for the named Aqueduct 4.0 data; credit WRI and original providers.
- **Interpretation:** Baseline water stress measures demand relative to renewable supply, not tap-water safety or clinic water availability. Raw indicators, normalized scores and future scenarios are distinct.
- **Citation:** Kuzma et al. (2023), Aqueduct 4.0: Updated decision-relevant global water risk indicators. WRI, doi:10.46830/writn.23.00061.

[Atlas](https://www.wri.org/aqueduct) · [Data](https://www.wri.org/data/aqueduct-global-maps-40-data) · [Dictionary](https://github.com/wri/Aqueduct40/blob/master/data_dictionary_water-risk-atlas.md) · [Methods](https://doi.org/10.46830/writn.23.00061)

## IOM environmental migration resources

**Reference and data-discovery gateways** · Mobility, Equity, Care access

Migration Data Portal, IOM environmental migration resources and DTM climate-and-mobility material support careful interpretation of movement and immobility.

- **Access:** External portals; some pages can restrict automated access. Select an explicitly documented underlying dataset before analysis.
- **Rights:** Dataset- and publication-specific IOM/provider terms. Linked references only here.
- **Interpretation:** Stocks, flows, displacement events and unique people differ. Migration is multicausal; movement does not automatically confer refugee status. Avoid identifiable routes or vulnerable-person locations.
- **Citation:** IOM / Migration Data Portal / DTM, exact named product, location, reporting period, release and access date.

[Environmental migration theme](https://www.migrationdataportal.org/themes/environmental-migration) · [IOM resources](https://environmentalmigration.iom.int/data-and-resources) · [DTM climate and mobility](https://dtm.iom.int/climate-and-mobility)

## Climate Conflict Vulnerability Index

**External composite-index gateway** · Conflict context, Climate literacy

A quarterly 0.5-degree composite index for investigating interacting contextual vulnerabilities.

- **Access:** Public maps and release-specific scores; raw indicator availability and historical release corrections vary.
- **Rights:** Data: CC BY-NC 4.0. Software: GPL 3.0. These are separate rights; no index data bundled here.
- **Interpretation:** An expert-weighted index is not a calibrated probability of violence or evidence that climate causes conflict. Check input dates, missingness, scale and release corrections; never rank patients or communities with it.
- **Citation:** Climate Conflict Vulnerability Index, University of the Bundeswehr Munich / PIK / German Federal Foreign Office; cite exact quarterly release and methodology.

[User-suggested site](https://climate-conflict.org/www) · [Project](https://climate-conflict.org/www/project) · [Methodology](https://climate-conflict.org/www/index/methodology)

## Climate change and mass atrocities: a research frontier

**Historical research commentary** · Conflict context, Equity

A discussion prompt about pathways, institutions, prevention and uncertainty, paired with current scientific evidence.

- **Access:** Public museum article; no dataset or figures copied.
- **Rights:** USHMM terms; linked reference and original summary only.
- **Interpretation:** A 2017 research commentary is not a current risk forecast, causal model or operational targeting layer.
- **Citation:** Blatt, Charlotte (2017-08-16). Climate Change and Mass Atrocities: A New Research Frontier. United States Holocaust Memorial Museum.

[Article](https://www.ushmm.org/genocide-prevention/blog/climate-change-and-mass-atrocities-a-new-research-frontier) · [Terms](https://www.ushmm.org/copyright-and-legal-information/terms-of-use)

## Sponge cities and green infrastructure

**Design concept and reading pathway** · Adaptation, Water, Urban health

Connect permeable surfaces, storage, vegetation and drainage to the adaptation lesson's auditable rainfall-volume calculation.

- **Access:** Background encyclopedia and primary environmental guidance; no copied maps or text.
- **Rights:** Wikipedia text has its own share-alike terms; primary guidance retains provider rights. Original course exercise is separately licensed.
- **Interpretation:** Storage capacity alone cannot predict flood prevention. Consider infiltration, saturation, maintenance, drainage, mosquitoes, accessibility and tradeoffs in pollen exposure.
- **Citation:** Cite the exact design guidance and local hydrologic evidence used. Wikipedia is a background orientation, not a substitute for engineering validation.

[User-suggested background](https://en.wikipedia.org/wiki/Sponge_city) · [US EPA green infrastructure](https://www.epa.gov/green-infrastructure)

## Nature-based solutions for climate change mitigation

**Scientific policy report** · Adaptation, Ecosystems, Equity

Conservation, restoration and ecosystem management as climate mitigation, with safeguards and limits.

- **Access:** Public UNEP report; linked reading and original course synthesis.
- **Rights:** Report-specific UNEP/IUCN rights and third-party credits. Figures are not republished here.
- **Interpretation:** Mitigation potential is not a guaranteed local health benefit or a substitute for emissions reductions. Test biodiversity, tenure, livelihoods, maintenance and distributional impacts.
- **Citation:** UNEP and IUCN (2021). Nature-based solutions for climate change mitigation. Published 4 November 2021.

[Report](https://www.unep.org/resources/report/nature-based-solutions-climate-change-mitigation)

## WHO / WMO Atlas of Health and Climate

**Foundational historical atlas** · Disease, Heat, Climate literacy

Joint meteorological and public-health cases spanning infections, emergencies, environmental conditions and preparedness.

- **Access:** WHO, TDR and WMO landing pages point to the same 2012 work. Linked reference, no copied figures.
- **Rights:** Current WHO page states CC BY-NC-SA 3.0 IGO, while original PDF says © WHO/WMO 2012 all rights reserved and credits third-party figures. Treat illustrations individually.
- **Interpretation:** Historical synthesis: update epidemiology and current climate evidence separately. WHO and WMO landing-page dates differ; the publication year is 2012.
- **Citation:** WHO and WMO (2012). Atlas of Health and Climate. 64 pp. ISBN 9789241564526; WMO-No.1098.

[WHO publication](https://www.who.int/publications/i/item/9789241564526) · [User-suggested TDR page](https://tdr.who.int/home/our-work/global-engagement/9789241564526) · [WMO publication](https://wmo.int/publication-series/atlas-of-health-and-climate)

## Malaria Atlas Project

**Modeled-estimate data gateway** · Disease, Equity, Care access

Explore malaria incidence, prevalence, interventions and uncertainty, using small country/admin summaries before global raster analysis.

- **Access:** Public platform and documented HTTP access guide; select an explicit release, species, indicator and denominator.
- **Rights:** MAP maps explicitly CC BY 3.0; original survey/provider rights remain separate. Cite the exact data layer and associated publication.
- **Interpretation:** Modeled estimates are not surveillance case counts or climate-attributable cases. Validate zero-versus-missing conventions and whether a metric has genuine uncertainty bounds.
- **Citation:** Malaria Atlas Project, exact dataset/layer and publication, species, release, year, URL and access date. Do not cite only the portal for an analysis.

[Provider](https://malariaatlas.org/) · [Data platform](https://data.malariaatlas.org/) · [HTTP access guide](https://data.malariaatlas.org/llms.txt) · [Open-access policy](https://malariaatlas.org/open-access-policy/)

## EAACI Global Atlas of Planetary Health

**Clinical-science reference** · Disease, Urban health, Adaptation

Climate, air pollution, allergy, asthma, pollen, healthcare sustainability and nature-based solutions broaden the clinical pathways in the course.

- **Access:** Public 2025 atlas PDF; v1.2 appears in the supplied filename, not an independently verified edition statement.
- **Rights:** No blanket open license verified; figure-specific permissions differ. Linked reference and original synthesis, no figures copied.
- **Interpretation:** A clinical-science atlas is not a geospatial dataset or local asthma predictor. Urban planting can have seasonal pollen tradeoffs; assess locally appropriate species and exposure.
- **Citation:** Akdis, C., Agache, I., Nadeau, K.C., and Pali-Schöll, I. (eds.) (2025). Global Atlas of Planetary Health. European Academy of Allergy and Clinical Immunology.

[Publication](https://eaaci.org/books/global-atlas-of-planetary-health/) · [User-suggested PDF](https://eaaci.org/wp-content/uploads/2025/09/Planetary-Health-Atlas-v1.2.pdf)

## ClimaHealth / Wellcome Climate Change Impact Map

**External historical interactive reference** · Disease, Heat, Equity

Wellcome's country explorer combines historical climate, disaster impacts and climate-sensitive disease literature; ClimaHealth provides the discovery entry.

- **Access:** Public interactive dashboard. No underlying CRU or EM-DAT data copied into this repository.
- **Rights:** Wellcome website default CC BY 4.0 does not override upstream rights. CRU data: ODbL / Database Contents License. EM-DAT: registration and restrictive product-specific terms.
- **Interpretation:** Historical interface series extend through 2021 and use a 1991–2020 anomaly baseline; literature panel covers 2013–2020. Missing disaster records do not establish no event or no harm.
- **Citation:** Wellcome (2022-07-05). Tracking the health effects of climate change around the world; Climate and Health Dashboard v15. Discovered via ClimaHealth; accessed 2026-10-09.

[User-suggested resource](https://climahealth.info/resource-library/climate-change-impact-map/) · [Primary article](https://wellcome.org/insights/articles/tracking-health-effects-climate-change-around-world) · [Interactive map](https://climate-and-health-dashboard.s3.eu-west-1.amazonaws.com/v15/index.html) · [EM-DAT terms](https://doc.emdat.be/docs/legal/terms-of-use/) · [CRU terms](https://crudata.uea.ac.uk/cru/data/hrg/)
