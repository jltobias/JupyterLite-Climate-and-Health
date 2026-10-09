# Start in your browser

Open the [learning hub](https://jltobias.github.io/JupyterLite-Climate-and-Health/), choose **Read the book**, **Open Python lab**, or **Explore**. No login or API key is needed for the core lessons. A current desktop browser is most comfortable for coding; reading, tables and scenario controls also work on small screens.

## Run your first notebook

1. Open the [start notebook in JupyterLite](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/00_start_here.ipynb).
2. Wait for the Python (Pyodide) kernel to become idle. First use downloads the runtime and may take a minute or more. Choose **Python (Pyodide)** if a kernel chooser appears.
3. Select **Run → Run All Cells**. Read each output, edit a small assumption, and rerun the affected cells.
4. Download work you want to keep from the File menu or file browser. Browser storage can be cleared by the browser, private mode or an explicit reset; it is not a backup.

The small data files and helper module are bundled with the notebooks. Core analysis uses Python's standard library plus Jupyter display utilities. No credentialed API request or multi-gigabyte NetCDF download runs inside a lesson. Initial runtime downloads still require connectivity; this is not a fully offline Python distribution.

## If something does not load

- **Kernel stays busy:** give the first download time, check connectivity and allow the runtime CDN through institutional filtering. Restart the kernel and run all cells again. The Book's saved outputs remain readable.
- **Module or data missing:** keep `healthlab.py`, `data/` and `notebooks/` together. Open notebooks through the bundled Lab rather than uploading an isolated notebook.
- **3D unavailable:** the explorer switches to the 2D map and retains the table and exact scenario output. Its basemap uses bundled Natural Earth geometry, so no tile provider is needed. The query `?view=scene&webgl=off` exercises this fallback.
- **Old edits appear after an update:** JupyterLite intentionally preserves browser-local work. Download your edits before using Help → Clear Browser Data or a new browser profile to load the published version.
- **A map feature seems wrong:** check the source, date, units, footprint and known limitations before interpreting it. Archived Healthsites features do not establish current service operation or program support.

## Accessibility

Use labeled selects and sliders with a keyboard. The 2D map's markers support Enter/Space and the context select provides the same choice. Tables carry the exact values independently of color and 3D. The story has explicit Previous/Next controls and no auto-advance; animations respect reduced-motion preferences in the surrounding interface. For a screen-reader or low-power device, use the reading edition and tables; the 3D scene itself is a visual supplement.
