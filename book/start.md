# Start with the original notebooks

Open the [original course index in JupyterLite](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=legacy/index.ipynb), or begin [NB00: Setup and configuration](legacy/nb00-setup.md) in this Book. The index leads through nine core chapters, two topic extensions and five historical variants: **16 legacy notebooks** in total.

## Read and inspect the original course

1. Open the index and choose NB00, then follow NB01, NB01B, NB02, NB02B and NB03–NB06.
2. Read the archive notice first. It gives the original cell count, reading limits and companion links, and links to the manifest's notebook-specific data, package, API and download requirements.
3. Read Markdown, figures and editable source code without executing it. A notebook may offer a kernel chooser; **No Kernel** is sufficient for reading. The Book displays historical code without running it.
4. Download any edits you want to keep. Browser-local storage can be cleared and is not a backup.

The original code is not verified executable end-to-end in Pyodide. Its installers, native geospatial/netCDF packages, authenticated CDS/Healthsites services and large datasets may require a full Python/Jupyter environment. The archive does not include credentials or the original climate/facility datasets. Scientific statements, placeholders and unfinished exercises are preserved rather than corrected.

The [complete index](legacy.md) also links the provenance image/JSON, original quiz resources and map HTML. The HTML is an **OpenStreetMap basemap only, with no heat overlay**. Remote illustrations, linked sites, CDN scripts and map tiles may need internet access or be unavailable. Two attachment references in the older NB01 Introduction variant were already missing from the source; its three supplied attachments remain intact.

## Use an optional runnable companion

Each original chapter links relevant exercises from the secondary collection of **14 modern runnable lessons**. To try one:

1. Open the [companion orientation](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/00_start_here.ipynb).
2. Select **Python (Pyodide)** and wait for Idle. First use downloads the runtime and requires connectivity.
3. In a companion notebook, select **Run → Run All Cells**, then change an assumption and inspect the result.
4. Keep `healthlab.py`, `data/` and `notebooks/` together and download work you want to keep.

The companion labs bundle compact inputs and need no API key. Their Book pages include executed outputs. These instructions apply to the companions; original notebooks retain their separate runtime limits.

## Troubleshooting and access

- **Old edits after an update:** download work before clearing browser data or using a fresh browser profile. Lab preserves your existing files.
- **Slow companion kernel:** allow the initial runtime download and check institutional filtering. Use the Book while waiting.
- **No 3D:** the explorer retains its 2D map, controls and exact tables. Use `?view=scene&webgl=off` to inspect the fallback.
- **A figure is missing:** check the archive notice and manifest; external images need network access. Original local assets are bundled.
- **Direct Lab entry:** open `START_HERE.ipynb` in the root file browser to reach the original course index.

The modern explorer offers keyboard controls and tables alongside maps. Historical material retains its original accessibility limitations, including uneven image descriptions. Use the Book and original source together when an old figure or activity needs interpretation.
