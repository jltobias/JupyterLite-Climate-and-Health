"""Exercise the built JupyterLite kernel and JupyterGIS story in Chromium.

Run after scripts/build.py, using the development virtual environment.
Requires Playwright Chromium and network access for the initial Pyodide runtime.
Edits exist only in a disposable browser context; repository notebooks are not
modified. Screenshots are written to the ignored test-results/ directory.
"""
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import unquote, urlsplit
from uuid import uuid4
import json
import re

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
PREFIX = "/JupyterLite-Climate-and-Health"


class Handler(SimpleHTTPRequestHandler):
    """Serve the assembled products with their GitHub Pages repository prefix."""

    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if route.startswith(PREFIX + "/"):
            route = route[len(PREFIX):]
        target = (SITE / route.lstrip("/")).resolve()
        if not target.is_relative_to(SITE.resolve()):
            return str(SITE / "404.html")
        return str(target)

    def log_message(self, *_args):
        pass


def verify_kernel(page, base):
    page.goto(base + "/lite/lab/index.html?path=notebooks/00_start_here.ipynb",
              wait_until="domcontentloaded", timeout=60000)
    editor = page.locator(".jp-CodeCell .cm-content").first
    editor.wait_for(timeout=90000)
    marker = "PYODIDE_RUNTIME_" + uuid4().hex
    # A new nonce prevents pre-rendered notebook outputs from passing this test.
    code = f'''import sys, pathlib, json, csv
root = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
            if (p / "healthlab.py").exists())
sys.path.insert(0, str(root))
import healthlab as h
assert sys.platform == "emscripten", sys.platform
cases = h.cases()
assert len(cases) == 7
assert {{c["country"] for c in cases}} >= {{"India", "Mozambique", "Kenya"}}
case = cases[0]
result = h.scenario(case)
assert result["capacity"] + result["unmet_visits"] == case["daily_visits"]
observations = list(csv.DictReader((h.DATA / "global-temperature.csv").open()))
assert len(observations) > 100
facilities = json.loads((h.DATA / "healthsites_facilities.geojson").read_text())
assert facilities["type"] == "FeatureCollection" and len(facilities["features"]) > 0
print({marker!r}, sys.platform, case["city"], len(observations), len(facilities["features"]))
'''
    editor.fill(code)
    editor.press("Shift+Enter")
    output = page.locator(".jp-OutputArea-output").filter(has_text=marker)
    output.wait_for(timeout=240000)
    result = output.inner_text().strip()
    assert "emscripten Mumbai" in result, result
    print("PASS Pyodide: fresh cell execution, local module/CSV/GeoJSON, scenario invariants", flush=True)
    return result


def verify_story(page, base, artifacts):
    page.goto(base + "/lite/lab/index.html?path=projects/climate-health.jGIS",
              wait_until="domcontentloaded", timeout=60000)
    editor_button = page.get_by_role(
        "button", name="Open the story editor for the current JupyterGIS document.", exact=True)
    editor_button.wait_for(timeout=90000)
    expect(page.get_by_text("Natural Earth land (public domain)", exact=True)).to_be_visible()
    # Visible canvas pixels verify actual local geographic rendering, not a
    # successfully parsed project with an empty map.
    page.wait_for_function("""() => [...document.querySelectorAll('canvas')].filter(canvas => {
        try {
            const context = canvas.getContext('2d');
            if (!context || !canvas.width || !canvas.height) return false;
            return context.getImageData(0, 0, canvas.width, canvas.height).data
                .some((value, index) => index % 4 === 3 && value > 0);
        } catch (_) { return false; }
    }).length >= 2""", timeout=30000)
    editor_button.click()
    expect(page.get_by_text("5 segments", exact=True)).to_be_visible()
    page.get_by_role("button", name="Preview story", exact=True).click()
    expect(page.get_by_role("heading", name="Mumbai, India", exact=True)).to_be_visible()
    page.wait_for_timeout(1400)  # The authored camera transition lasts one second.
    map_view = page.locator(".ol-viewport").first
    mumbai_image = map_view.screenshot()
    page.screenshot(path=str(artifacts / "runtime-story-mumbai.png"))

    page.get_by_role("button", name="Next slide", exact=True).click()
    expect(page.get_by_role("heading", name="Beira, Mozambique", exact=True)).to_be_visible()
    page.wait_for_timeout(1400)
    beira_image = map_view.screenshot()
    assert sha256(mumbai_image).digest() != sha256(beira_image).digest(), "Story map did not change."
    page.screenshot(path=str(artifacts / "runtime-story-beira.png"))

    for heading in ("Mombasa, Kenya", "Lusaka, Zambia", "Lagos, Nigeria"):
        page.get_by_role("button", name="Next slide", exact=True).click()
        expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
    page.get_by_role("button", name="Previous slide", exact=True).click()
    expect(page.get_by_role("heading", name="Lusaka, Zambia", exact=True)).to_be_visible()
    page.get_by_role("button", name="Back to editor", exact=True).click()
    expect(page.get_by_text("5 segments", exact=True)).to_be_visible()
    print("PASS JupyterGIS: rendered local layers, five story slides, map transition, backward navigation and editor", flush=True)


def verify_evidence_lesson(page, base):
    """Run every actual evidence-lesson code cell in the browser's Python runtime."""
    page.goto(base + '/lite/lab/index.html?path=notebooks/13_evidence_atlas.ipynb',
              wait_until='domcontentloaded', timeout=60000)
    # The workspace restores its previous notebook before opening the URL's
    # requested document. An arbitrary first editor can belong to that restored
    # tab, whose outputs become hidden as soon as the requested notebook opens.
    expect(page).to_have_title(re.compile(r'^13_evidence'), timeout=90000)
    notebook_panel=page.locator('.jp-NotebookPanel:visible')
    expect(notebook_panel).to_have_count(1)
    editor=notebook_panel.locator('.jp-CodeCell .cm-content').first
    editor.wait_for(timeout=90000)
    expect(editor).to_contain_text('import pandas as pd')
    notebook=json.loads((ROOT/'content/notebooks/13_evidence_atlas.ipynb').read_text(encoding='utf-8'))
    marker='EVIDENCE_LESSON_'+uuid4().hex
    code='\n\n'.join(''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code')
    code+='\nassert len(corals) == 20 and abs(mean(corals.average_colour_score)-2.875)<1e-12\n'
    code+='\nimport sys\nassert sys.platform == "emscripten"\n'
    code+=f'print({marker!r}, sys.platform, len(corals), mean(corals.average_colour_score))\n'
    editor.fill(code);editor.press('Control+Enter')
    # Run without selecting the next cell, and scope the output to lesson 13.
    output=notebook_panel.locator('.jp-OutputArea-output').filter(has_text=marker)
    output.wait_for(state='attached',timeout=180000)
    assert output.count()>0
    assert 'emscripten 20 2.875' in output.inner_text()
    print('PASS evidence notebook: every code cell executed in Pyodide, including pandas, matplotlib, habitat map, CoralWatch and source registry',flush=True)


def main():
    assert (SITE / "lite/lab/index.html").is_file(), "Build the site before running this check."
    artifacts = ROOT / "test-results"
    artifacts.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}{PREFIX}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
            page = browser.new_page(viewport={"width": 1500, "height": 1050})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            try:
                execution = verify_kernel(page, base)
                verify_evidence_lesson(page, base)
                verify_story(page, base, artifacts)
                assert not errors, errors
                print(json.dumps({"status": "passed", "browser": browser.version,
                                  "kernel_output": execution, "story_segments": 5}))
            except Exception:
                page.screenshot(path=str(artifacts / "runtime-failure.png"))
                print(page.locator("body").inner_text()[-5000:], flush=True)
                raise
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
