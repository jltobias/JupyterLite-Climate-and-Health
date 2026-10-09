"""Exercise packaged sources and catalog failure/pagination behavior in a browser.

The live network check is opt-in; deterministic tests intercept remote catalog
responses, never claim those responses are actual observations.
"""
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import tempfile
from playwright.sync_api import sync_playwright
from browser_smoke import ROOT, PREFIX, Handler


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
    registry=json.loads((ROOT/'web/stac/sources.json').read_text(encoding='utf-8'))
    assert len({s['id'] for s in registry['sources']})==len(registry['sources'])
    meta=json.loads((ROOT/'content/data/coralwatch_random_survey_20.metadata.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/'content/data'/meta['csv_file']).read_bytes()).hexdigest()==meta['csv_sha256']
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}{PREFIX}'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            options={}
            if args.live:
                # DEA's public load balancer rejects HeadlessChrome with HTTP 403.
                # Test the deployed user's standard Chrome request profile explicitly.
                probe=browser.new_page();agent=probe.evaluate('navigator.userAgent');probe.close()
                options['user_agent']=agent.replace('HeadlessChrome','Chrome')
                print('Live-provider compatibility check uses a standard Chrome User-Agent; DEA rejects HeadlessChrome.')
            page=browser.new_page(viewport={'width':1440,'height':1000},**options)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/stac/')
            page.wait_for_function("document.querySelector('#results').children.length===6")
            assert page.locator('.source-card').count()==len(registry['sources'])
            page.click('#facilities')
            assert page.locator('.leaflet-interactive').count()>=30
            page.locator('#results button').first.click()
            assert 'Asset references' in page.locator('#detail').inner_text()
            page.click('[data-snapshot=dea_beira]');page.wait_for_function("document.querySelector('#results').children.length===4")
            assert '2022-12-31' in page.locator('#results').inner_text()
            assert page.locator('#results').inner_text().count('Not supplied')==4
            page.click('[data-snapshot=allen_mombasa]');page.wait_for_function("document.querySelector('#results').children.length===8")
            assert 'Seagrass' in page.locator('#results').inner_text()
            page.fill('#source-search','malaria');assert page.locator('.source-card').count()==1
            page.fill('#source-search','');page.select_option('#theme','Water');assert page.locator('.source-card').count()>2
            page.select_option('#theme','all')
            # Last successful dataset and provenance survive an explicit network failure.
            page.route('https://stac.dataspace.copernicus.eu/**',lambda r:r.fulfill(status=503,body='Unavailable'))
            page.click('#search');page.wait_for_function("document.querySelector('#status').textContent.includes('503')")
            with page.expect_download() as download:page.click('#export')
            with tempfile.TemporaryDirectory() as tmp:
                target=Path(tmp)/'export.json';download.value.save_as(target);export=json.loads(target.read_text(encoding='utf-8'))
                assert len(export['features'])==8 and export['provenance']['mode']=='Packaged snapshot'
                assert 'Allen' in export['provenance']['provider']
            page.unroute('https://stac.dataspace.copernicus.eu/**')
            item={'type':'Feature','id':'test-only-scene','collection':'sentinel-2-l2a','geometry':{'type':'Polygon','coordinates':[[[72.8,19],[72.9,19],[72.9,19.1],[72.8,19.1],[72.8,19]]]},'properties':{'datetime':'2024-04-01T00:00:00Z','eo:cloud_cover':0}}
            def response(route):
                second='page=2' in route.request.url
                features=[item,{**item,'id':'second-test-scene'}] if second else [item]
                links=[] if second else [{'rel':'next','href':'https://stac.dataspace.copernicus.eu/v1/search?page=2'}]
                route.fulfill(json={'type':'FeatureCollection','features':features,'links':links})
            page.route('https://stac.dataspace.copernicus.eu/**',response)
            page.click('#search');page.wait_for_function("document.querySelector('#results').children.length===1")
            assert '0.0%' in page.locator('#results').inner_text()
            page.fill('#bbox','0,0,1,1')  # Unsubmitted edits must not alter export query.
            page.click('#next');page.wait_for_function("document.querySelector('#results').children.length===2")
            with page.expect_download() as download:page.click('#export')
            with tempfile.TemporaryDirectory() as tmp:
                target=Path(tmp)/'export.json';download.value.save_as(target);export=json.loads(target.read_text(encoding='utf-8'))
                assert export['provenance']['query']['bbox']!=[0,0,1,1]
                assert len(export['features'])==2 and len(export['provenance']['requests'])==2
            page.unroute('https://stac.dataspace.copernicus.eu/**')
            # A geometrically invalid response must not overwrite successful data.
            invalid={**item,'id':'invalid-response','geometry':{'type':'Polygon','coordinates':[[['bad',19]]]}}
            page.route('https://stac.dataspace.copernicus.eu/**',lambda r:r.fulfill(json={'type':'FeatureCollection','features':[invalid]}))
            page.click('#search');page.wait_for_function("document.querySelector('#status').textContent.includes('invalid identifier or WGS84 geometry')")
            assert page.locator('#results tr').count()==2
            with page.expect_download() as download:page.click('#export')
            with tempfile.TemporaryDirectory() as tmp:
                target=Path(tmp)/'export.json';download.value.save_as(target);export=json.loads(target.read_text(encoding='utf-8'))
                assert {f['id'] for f in export['features']}=={'test-only-scene','second-test-scene'}
                assert len(export['provenance']['requests'])==2
            page.unroute('https://stac.dataspace.copernicus.eu/**')
            page.route('https://explorer.digitalearth.africa/**',lambda r:r.fulfill(json={'type':'FeatureCollection','features':[{**item,'collection':'gm_s2_annual'}]}))
            page.select_option('#provider','dea');page.select_option('#collection','gm_s2_annual');page.click('#search')
            page.wait_for_function("document.querySelector('#interpretation').textContent.includes('geomedian')")
            page.locator('#results button').first.click()
            assert 'GeoMAD_specs' in page.locator('#detail a').first.get_attribute('href')
            page.unroute('https://explorer.digitalearth.africa/**')
            page.select_option('#provider','copernicus')
            if args.live:
                page.select_option('#context','mumbai');page.click('#search')
                page.wait_for_function("!document.querySelector('#search').disabled",timeout=30000)
                assert 'live catalog' in page.locator('#status').inner_text(),page.locator('#status').inner_text()
                assert page.locator('#results tr').count()>0
                page.select_option('#provider','dea');page.click('#search')
                page.wait_for_function("!document.querySelector('#search').disabled",timeout=30000)
                assert 'live catalog' in page.locator('#status').inner_text(),page.locator('#status').inner_text()
                assert page.locator('#results tr').count()>0
                print('PASS actual Copernicus and DEA browser fetch/CORS queries')
            page.click('[data-snapshot=copernicus_mumbai]');page.wait_for_function("document.querySelector('#results').children.length===6")
            page.evaluate('scrollTo(0,0)')
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Mobile horizontal overflow'
            page.screenshot(path=str(ROOT/'test-results/evidence-mobile.png'),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path=str(ROOT/'test-results/evidence-atlas.png'))
            assert not errors,errors
            browser.close()
        print('PASS source library, metadata inspection, actual snapshots, failure preservation, pagination, provenance export and mobile layout')
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
