# Make your own geographic story

Open [the JupyterGIS story in the browser Lab](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=projects/climate-health.jGIS). The project uses JupyterGIS 0.16.7 schema 0.6.0 and local GeoJSON paths. It includes five guided segments and bundled Natural Earth land, so its starting map does not require external tiles.

1. Open `projects/climate-health.jGIS` from the Lab file browser. Wait for the document's layers to load.
2. Expand the story panel and choose the **Climate and health: continuity of care** guided story. Start the presentation/story view and move through its segments.
3. Edit a segment's title and Markdown narrative. Use a place, a learning question, a cited observation, clearly labeled assumptions and a limitation. Keep scenario values distinct from observed layers.
4. Adjust the map extent or create a new segment with the documented JupyterGIS story tools. Preserve layer/source references.
5. Download the `.jGIS` file and any changed GeoJSON together. Relative paths such as `../data/study-sites.geojson` require the original `projects/` and sibling `data/` folder structure.

The explorer's **Download story project** preserves the supported project schema and records your selected synthetic scenario in `metadata.exportedScenario`. Open it in the same `projects/` folder in Lab, then edit the narrative. It does not upload a project or publish your story. In synthetic mode the CSV download records the selected case, assumptions, units, results and limitations. In archived Healthsites mode it instead exports only the selected actual facility features and their ODbL/source metadata; fictional controls and views are disabled. The matching [Healthsites JupyterGIS project](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=projects/healthsites-context.jGIS) keeps those actual map features separate from synthetic impacts.

For an alternative runtime, use the documented [Notebook.link repository launcher](https://notebook.link/github/jltobias/JupyterLite-Climate-and-Health/) and open `content/projects/climate-health.jGIS`. The repository includes `.nblink/environment.yml` with xeus-python and JupyterGIS. Environment solving and the external hosted launch are separate from the locally tested Pages Lab; do not assume collaborative editing or an authored hosted project has been validated.

JupyterGIS Lite has browser/CORS and memory limitations. It does not provide real-time collaboration, QGIS import/export or server raster tiling. Its preview STAC support is not a substitute for this site's separate metadata gateway. Use small, licensed local geographic files and explicit provenance.

References: [JupyterGIS story maps](https://jupytergis.readthedocs.io/en/latest/user_guide/how-tos/story-maps.html), [Notebook.link repository preparation](https://notebook.link/docs/user-guide/enable-your-github-repository/), [JupyterLite documentation](https://jupyterlite.readthedocs.io/).
