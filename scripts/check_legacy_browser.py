"""Open original notebooks and Book chapters under the Pages prefix; execute no code."""
from http.server import ThreadingHTTPServer
from collections import Counter
from pathlib import Path
from threading import Thread
import base64
import json
import re

from playwright.sync_api import TimeoutError as PlaywrightTimeout, expect, sync_playwright

from check_runtime import Handler, PREFIX, ROOT
from import_legacy import ARCHIVE, BOOK_SLUGS, NOTEBOOKS, SUPPORT, digest, image_references, source_text, target_name


def open_notebook(page, base, name):
    page.goto(base + '/lite/lab/index.html?path=legacy/' + name,
              wait_until='domcontentloaded', timeout=60000)
    # The browser title truncates long filenames once multiple tabs are open.
    # The active document tab retains its complete path in the tooltip.
    expect(page.locator('.lm-TabBar-tab.lm-mod-current[title*="Path: legacy/' + name + '"]')).to_be_visible(timeout=90000)
    panel = page.locator('.jp-NotebookPanel:visible')
    expect(panel).to_have_count(1)
    expect(panel.locator('.jp-MarkdownCell').first).to_contain_text(
        'Original 2024 legacy notebook collection' if name == 'index.ipynb'
        else 'Archived 2024 notebook', timeout=60000)
    # Reading requires no kernel. The chooser can appear after Markdown starts
    # rendering, and must be dismissed before inspecting/clicking the document.
    chooser = page.get_by_role('dialog').get_by_role('button', name='No Kernel', exact=True)
    try:
        chooser.wait_for(state='visible', timeout=2000)
        chooser.click()
    except PlaywrightTimeout:
        pass
    return panel


def verify_nb06_summary(page, timeout=10000):
    # Independent original prose expectations: hashes in a generated manifest
    # cannot prove that the renderer actually included the source summary.
    article = page.locator('article').first
    for phrase in (
        'Climate change includes global temperature increases, global heat stress, sea-level-rise',
        'The Copernicus Climate Data Store is a repository of climate data and metadata',
        'Healthsites.io is a repository of global health facility data',
        'Representative Concentration Pathways are standardized scenarios used in climate modeling',
        'Modeling and Simulation of future climate scenarios can be a useful tool for global health',
    ):
        expect(article).to_contain_text(phrase, timeout=timeout)


def verify_book(page, base, manifest):
    """Check all routes and every bundled figure occurrence against canonical sources."""
    figures_seen = set()
    for entry, slug in zip(manifest['notebooks'], BOOK_SLUGS, strict=True):
        response = page.goto(base + '/book/legacy/' + slug + '/', wait_until='networkidle')
        assert response.ok, slug
        expect(page.locator('article').first).to_contain_text('historical reading copy')
        notebook = json.loads((ARCHIVE / entry['target_path']).read_bytes())
        expected = []
        for cell in notebook['cells'][1:]:
            if cell['cell_type'] != 'markdown':
                continue
            for reference, _, _ in image_references(source_text(cell)):
                if reference.startswith('images/'):
                    expected.append(digest((ARCHIVE / reference).read_bytes()))
                elif reference.startswith('attachment:'):
                    attachment = cell.get('attachments', {}).get(reference[11:])
                    if attachment:
                        mime = next(m for m in attachment if m.startswith('image/'))
                        expected.append(digest(base64.b64decode(''.join(attachment[mime]))))
        images = page.locator('article img')
        assert images.count() == len(expected), f'Bundled figure count differs in {slug}'
        actual = []
        for index in range(images.count()):
            figure = images.nth(index)
            figure.scroll_into_view_if_needed()
            expect(figure).to_be_visible()
            page.wait_for_function('(image) => image.complete && image.naturalWidth > 0', arg=figure.element_handle())
            image_response = page.request.get(figure.evaluate('(image) => image.currentSrc'))
            assert image_response.ok, f'Figure request failed in {slug}'
            actual.append(digest(image_response.body()))
        assert Counter(actual) == Counter(expected), f'Bundled figure bytes differ in {slug}'
        figures_seen.update(actual)
        if slug == 'nb06-reflection':
            verify_nb06_summary(page)
    print(f'PASS legacy Book: 16 reading routes, {len(figures_seen)} unique supplied figures/attachments and substantive NB06 summary', flush=True)


def main():
    manifest = json.loads((ARCHIVE / 'manifest.json').read_bytes())
    artifacts = ROOT / 'test-results'; artifacts.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}{PREFIX}'
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1500, 'height': 1050})
            try:
                page.goto(base + '/', wait_until='networkidle')
                expect(page.locator('a.nav-button')).to_have_attribute('href', 'lite/lab/index.html?path=legacy/index.ipynb')
                expect(page.locator('#course article')).to_have_count(9)
                expect(page.get_by_text('16 legacy notebooks', exact=True)).to_be_visible()
                page.screenshot(path=str(artifacts / 'legacy-home.png'), full_page=True)
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.set_viewport_size({'width': 1500, 'height': 1050})

                verify_book(page, base, manifest)
                page.goto(base + '/book/legacy/nb00-setup/', wait_until='networkidle')
                expect(page.locator('article').first).to_contain_text('cdsapi')
                page.screenshot(path=str(artifacts / 'legacy-book.png'), full_page=True)

                # Byte identity through the built HTTP routes, including all 16 notebooks.
                for entry in manifest['notebooks'] + manifest['assets']:
                    response = page.request.get(base + '/lite/files/legacy/' + entry['target_path'])
                    assert response.ok, entry['target_path']
                    assert digest(response.body()) == entry['target_sha256'], entry['target_path']
                response = page.request.get(base + '/legacy-reading-manifest.json')
                assert response.ok and len(response.json()['chapters']) == 16

                panel = open_notebook(page, base, 'index.ipynb')
                expect(panel.locator('a[href*="' + target_name(NOTEBOOKS[0]) + '"]').first).to_be_visible(timeout=30000)
                # Lab defers rendering Markdown cells outside the viewport.
                links = set()
                for _ in range(10):
                    links.update(panel.locator('a').evaluate_all('(nodes) => nodes.map(a => a.getAttribute("href"))'))
                    panel.hover(); page.mouse.wheel(0, 700); page.wait_for_timeout(150)
                for name in NOTEBOOKS:
                    assert any(target_name(name) in href for href in links), name
                for name in SUPPORT:
                    assert any(name in href for href in links), name
                expect(panel).to_contain_text('no heat overlay')
                # Follow an actual index link, rather than checking its URL alone.
                panel.hover(); page.mouse.wheel(0, -10000)
                expect(panel.get_by_role('heading', name='Original 2024 legacy notebook collection', exact=True)).to_be_visible()
                expect(panel.locator('a[href*="' + target_name(NOTEBOOKS[0]) + '"]').first).to_be_visible()
                page.screenshot(path=str(artifacts / 'legacy-index.png'))
                panel.locator('a[href*="' + target_name(NOTEBOOKS[0]) + '"]').first.click()
                expect(page.locator('.lm-TabBar-tab.lm-mod-current[title*="Path: legacy/' + target_name(NOTEBOOKS[0]) + '"]')).to_be_visible(timeout=60000)
                expect(page.locator('.jp-NotebookPanel:visible').get_by_role('heading', name='OBJECTIVES', exact=True)).to_be_visible()

                for entry in manifest['notebooks']:
                    # Disposable contexts keep old auto-selected kernels/workers
                    # and browser-local files from accumulating across the 16 opens.
                    page.close()
                    page = browser.new_page(viewport={'width': 1500, 'height': 1050})
                    panel = open_notebook(page, base, entry['target_path'])
                    expect(panel.locator('.jp-MarkdownCell').first).to_contain_text(
                        str(entry['original_cell_count']) + ' original cells')
                    assert panel.locator('.jp-OutputArea-output').count() == 0
                    print('PASS legacy Lab open: ' + entry['target_path'], flush=True)

                # Source text renders in a representative small, Markdown-only notebook.
                small = target_name(NOTEBOOKS[11])
                panel = open_notebook(page, base, small)
                expect(panel).to_contain_text('Wildfires')
                page.screenshot(path=str(artifacts / 'legacy-small.png'), full_page=True)

                # Verify a repaired relative image path in the actual Lab renderer.
                panel = open_notebook(page, base, target_name(NOTEBOOKS[1]))
                # JupyterLite resolves local Markdown images to data URLs, so
                # the original relative path is no longer present in the DOM.
                local_image = panel.locator('.jp-MarkdownCell').filter(
                    has_text='We are all in the same boat').locator('img').first
                for _ in range(12):
                    if local_image.count():
                        break
                    panel.hover(); page.mouse.wheel(0, 700); page.wait_for_timeout(200)
                local_image.scroll_into_view_if_needed(timeout=30000)
                expect(local_image).to_be_visible()
                page.wait_for_function('(image) => image.complete && image.naturalWidth > 0', arg=local_image.element_handle())
                rendered_source = local_image.get_attribute('src')
                assert rendered_source.startswith('data:image/png;base64,')
                assert digest(base64.b64decode(rendered_source.split(',', 1)[1])) == digest(
                    (ARCHIVE / 'images/rowboat.png').read_bytes())
                assert panel.locator('.jp-OutputArea-output').count() == 0

                # Bring the first supplied embedded attachment into the viewport.
                panel = open_notebook(page, base, target_name(NOTEBOOKS[2]))
                embedded = panel.locator('img[src^="data:"]').first
                for _ in range(12):
                    if embedded.count():
                        break
                    panel.hover(); page.mouse.wheel(0, 700); page.wait_for_timeout(200)
                embedded.scroll_into_view_if_needed(timeout=30000)
                expect(embedded).to_be_visible()
                assert embedded.evaluate('(image) => image.complete && image.naturalWidth > 0')
                page.screenshot(path=str(artifacts / 'legacy-attachment.png'))
                assert panel.locator('.jp-OutputArea-output').count() == 0
                print('PASS legacy browser: all 16 Book/Lab routes; every bundled Book figure/attachment; NB06 prose; index navigation; byte-identical assets/support; repaired local Lab image and embedded attachment; no historical code executed')
            except Exception:
                page.screenshot(path=str(artifacts / 'legacy-failure.png'))
                # Avoid dumping notebook source or arbitrary browser contents to logs.
                raise
            finally:
                browser.close()
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()
