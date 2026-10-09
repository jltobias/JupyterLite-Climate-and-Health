"""Regression smoke tests against the actual assembled repository-prefix site."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
import argparse
import csv
import io
import json
import os
import sys
import tempfile
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PREFIX='/JupyterLite-Climate-and-Health'


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        from urllib.parse import urlsplit
        route=unquote(urlsplit(path).path)
        if route.startswith(PREFIX+'/'):route=route[len(PREFIX):]
        target=(ROOT/'_site'/route.lstrip('/')).resolve()
        if not target.is_relative_to((ROOT/'_site').resolve()):return str(ROOT/'_site'/'404.html')
        return str(target)
    def log_message(self,*args):pass


def explorer_regressions(page, base):
    """Check reviewed numerical, state, availability, focus and async-render failures."""
    model_checks=page.evaluate("""async()=>{
      const {scenario}=await import('./model.js');
      const c=(await(await fetch('../data/cases.json')).json()).find(c=>c.id==='mumbai');
      const a=await(await fetch('../data/adaptations.json')).json();
      const thresholds=['engineering','combined'].map(key=>({
        below:scenario(c,1.5,1.699,key,a),equal:scenario(c,1.5,1.7,key,a),
        roundoff:scenario(c,1.5,1.7000000000000002,key,a)}));
      const inherited=['toString','constructor','__proto__'].map(key=>{
        try{scenario(c,1.5,.6,key,a);return false;}catch(e){return e.message==='Unknown adaptation';}});
      return {thresholds,inherited};
    }""")
    assert all(model_checks['inherited'])
    for check in model_checks['thresholds']:
        assert check['below']['access_open']
        for key in ['equal','roundoff']:
            assert not check[key]['access_open'] and check[key]['road_m']==1.7
    for key in ['toString','constructor','__proto__']:
        page.goto(base+'/explore/?adaptation='+key,wait_until='networkidle')
        assert page.input_value('#adaptation')=='baseline'
        assert page.locator('#data-table tbody tr').count()==7

    # Assert fixed expected values through controls, metrics, table, map and export.
    page.locator('#heat').fill('4');page.locator('#heat').dispatch_event('input')
    page.select_option('#layer','heat')
    assert page.locator('#metrics .value').nth(0).inner_text()=='39.7\u00b0C'
    assert page.locator('#metrics .value').nth(2).inner_text()=='59 / 140'
    assert page.locator('#data-table tr.selected td').nth(2).inner_text()=='39.7'
    assert page.locator('#data-table tr.selected td').nth(4).inner_text()=='59'
    assert page.locator('#data-table tr.selected td').nth(5).inner_text()=='81'
    assert '39.7' in page.locator('#map [data-case=mumbai]').get_attribute('aria-label')
    with page.expect_download() as event:page.click('#csv')
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'heat.csv';event.value.save_as(path)
        with path.open(encoding='utf-8') as stream:row=next(csv.DictReader(stream))
        assert float(row['heat_delta_c'])==4 and float(row['indoor_c'])==39.7
        assert int(row['capacity'])==59 and int(row['unmet_visits'])==81

    page.click('[data-view=tour]');page.click('#next');page.click('#next')
    assert 'step=2' in page.url and page.input_value('#case')=='lusaka'
    title=page.locator('#tour-title').inner_text()
    page.reload(wait_until='networkidle')
    assert page.locator('#tour-step').inner_text()=='STOP 3 OF 5'
    assert page.locator('#tour-title').inner_text()==title and page.input_value('#case')=='lusaka'
    page.click('#reset')
    assert page.locator('#tour-step').inner_text()=='STOP 1 OF 5'
    assert page.locator('#tour-title').inner_text()=='Begin with the evidence'
    assert page.input_value('#case')=='mumbai' and 'step=0' in page.url
    for step in ['-1','5','1.5','NaN']:
        page.goto(base+'/explore/?view=tour&step='+step,wait_until='networkidle')
        assert page.locator('#tour-step').inner_text()=='STOP 1 OF 5'
    page.click('[data-view=map]')
    for case,key in [('beira','Enter'),('mumbai','Space')]:
        marker=page.locator(f'#map [data-case={case}]');marker.focus();marker.press(key)
        assert page.input_value('#case')==case
        assert page.evaluate('document.activeElement.dataset.case')==case

    page.route('**/data/healthsites_facilities.geojson',lambda route:route.fulfill(status=503,body='Unavailable'))
    page.goto(base+'/explore/?layer=healthsites',wait_until='networkidle')
    assert 'Facility data unavailable' in page.locator('#data-table').inner_text()
    assert 'Synthetic results' not in page.locator('#data-table').inner_text()
    assert page.locator('#csv').is_disabled() and page.locator('#story-export').is_disabled()
    page.select_option('#layer','capacity')
    assert page.locator('#csv').is_enabled() and page.locator('#story-export').is_enabled()
    page.unroute('**/data/healthsites_facilities.geojson')
    page.goto(base+'/explore/',wait_until='networkidle')

    # Control settlement order: an older rejected plot must not hide a newer scene.
    page.evaluate("""()=>{window.savedReact=Plotly.react;window.pendingPlots=[];
      Plotly.react=()=>new Promise((resolve,reject)=>pendingPlots.push({resolve,reject}));}""")
    try:
        page.click('[data-view=map3d]');page.click('[data-view=scene]')
        assert page.evaluate('pendingPlots.length')==2
        page.evaluate("async()=>{pendingPlots[1].resolve();await Promise.resolve();}")
        status=page.locator('#view-status').inner_text()
        page.evaluate("async()=>{pendingPlots[0].reject(Error('delayed older failure'));await Promise.resolve();}")
        assert page.locator('#plot').is_visible() and not page.locator('#map').is_visible()
        assert page.locator('#view-status').inner_text()==status and 'orbit' in status
        assert 'conceptual coastal clinic' in page.locator('#visual-title').inner_text()
        # A later map update invalidates an outstanding successful 3D completion too.
        page.click('[data-view=map3d]');page.click('[data-view=map]')
        page.locator('#heat').fill('4');page.locator('#heat').dispatch_event('input')
        status=page.locator('#view-status').inner_text()
        page.evaluate("async()=>{pendingPlots[2].resolve();await Promise.resolve();}")
        assert page.locator('#map').is_visible() and not page.locator('#plot').is_visible()
        assert page.locator('#view-status').inner_text()==status
        assert page.locator('#data-table tr.selected td').nth(4).inner_text()=='59'
    finally:page.evaluate('()=>{Plotly.react=window.savedReact;}')
    page.goto(base+'/explore/',wait_until='networkidle')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--explorer-only',action='store_true',help='Skip unchanged homepage and Book checks')
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}{PREFIX}'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            if not args.explorer_only:
                page.goto(base+'/',wait_until='networkidle')
                assert page.title().startswith('Climate & Health')
                assert page.locator('h1').inner_text().startswith('A changing climate.')
            page.goto(base+'/explore/',wait_until='networkidle')
            page.wait_for_function("document.querySelector('#data-table tbody tr')!==null")
            assert page.locator('#data-table tbody tr').count()==7
            explorer_regressions(page,base)
            # Verify JS uses the same numerical contract as all Python fixture combinations.
            checks=json.loads((ROOT/'content/data/scenario-checks.json').read_text())
            actual=page.evaluate("""async checks=>{const {scenario}=await import('./model.js');const cases=await(await fetch('../data/cases.json')).json();const a=await(await fetch('../data/adaptations.json')).json();return checks.map(c=>scenario(cases.find(x=>x.id===c.case_id),c.heat_delta_c,c.water_m,c.adaptation,a));}""",checks)
            for expected,got in zip(checks,actual):
                for key in expected:
                    if isinstance(expected[key],float):assert abs(expected[key]-got[key])<1e-8,(key,expected,got)
                    else:assert expected[key]==got[key],(key,expected,got)
            page.select_option('#case','beira')
            page.locator('#water').fill('0.8');page.locator('#water').dispatch_event('input')
            assert 'Closed' in page.locator('#metrics').inner_text()
            page.select_option('#adaptation','engineering')
            assert 'Open' in page.locator('#metrics').inner_text()
            with page.expect_download() as event:page.click('#csv')
            export=event.value
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'scenario.csv';export.save_as(path)
                row=list(csv.DictReader(path.open(encoding='utf-8')))[0]
                assert row['case_id']=='beira' and row['adaptation']=='engineering' and row['data_type']=='synthetic'
            with page.expect_download() as event:page.click('#story-export')
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'story.jGIS';event.value.save_as(path)
                story=json.loads(path.read_text())
                assert story['schemaVersion']=='0.6.0' and json.loads(story['metadata']['exportedScenario'])['case_id']=='beira'
            page.click('[data-view=map3d]');page.wait_for_function("document.querySelector('#plot').data?.some(x=>x.type==='mesh3d')",timeout=30000)
            before=page.evaluate("JSON.stringify(document.querySelector('#plot')._fullLayout.scene.camera)")
            bounds=page.locator('#plot').bounding_box();page.mouse.move(bounds['x']+bounds['width']*.6,bounds['y']+200);page.mouse.down();page.mouse.move(bounds['x']+bounds['width']*.6+90,bounds['y']+245,steps=8);page.mouse.up();page.wait_for_timeout(250)
            after=page.evaluate("JSON.stringify(document.querySelector('#plot')._fullLayout.scene.camera)")
            assert before!=after,'3D orbit did not change camera'
            page.click('[data-view=scene]');page.wait_for_function("document.querySelector('#plot').data?.some(x=>x.name?.includes('clinic'))")
            page.click('[data-view=adapt]');assert page.locator('.compare-row').count()==5
            page.click('[data-view=tour]');assert 'STOP 1 OF 5' in page.locator('#tour-step').inner_text();page.click('#next');assert 'Beira' in page.locator('#case option:checked').inner_text()
            page.select_option('#layer','healthsites');assert page.locator('#data-table tbody tr').count()==11
            assert 'No link' in page.locator('#metrics').inner_text()
            page.select_option('#case','mumbai');assert page.locator('#data-table tbody tr').count()==24
            assert page.locator('#heat').is_disabled()
            with page.expect_download() as event:page.click('#csv')
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'actual.csv';event.value.save_as(path)
                rows=list(csv.DictReader(path.open(encoding='utf-8')))
                assert len(rows)==24 and rows[0]['data_type']=='archived_osm' and 'capacity' not in rows[0]
            with page.expect_download() as event:page.click('#story-export')
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'actual.jGIS';event.value.save_as(path)
                story=json.loads(path.read_text())
                assert 'exportedScenario' not in story['metadata'] and 'healthsites_facilities' in story['sources']['sites-data']['parameters']['path']
            page.check('[name=quiz][value=arithmetic]');page.check('[name=quiz][value=dependency]');page.click('#quiz-check');assert page.locator('#quiz-feedback').inner_text().startswith('Correct.')
            page.goto(base+'/explore/?view=scene&webgl=off',wait_until='networkidle');assert '3D rendering is unavailable' in page.locator('#view-status').inner_text();assert page.locator('#map').is_visible();assert page.locator('#data-table tbody tr').count()==7
            page.set_viewport_size({'width':390,'height':844})
            if not args.explorer_only:
                page.goto(base+'/',wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
            page.goto(base+'/explore/',wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
            # The generated Book must load under the same prefix as the application.
            if not args.explorer_only:
                page.goto(base+'/book/',wait_until='networkidle');assert 'Climate' in page.title()
            assert not errors,errors
            browser.close()
            print('PASS browser: scenario parity and adapted thresholds; heat metrics/table/export; tour URL/reset; inherited keys; missing facilities; keyboard focus; stale 3D promises; explorer controls, 3D, exports and fallback'+('' if args.explorer_only else '; homepage and Book prefix'))
    finally:server.shutdown();server.server_close()


if __name__=='__main__':main()
