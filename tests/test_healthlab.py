from pathlib import Path
import hashlib
import contextlib
import io
import json
import math
import sys
import unittest
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content'))
sys.path.insert(0,str(ROOT/'scripts'))
import healthlab as h
from prepare_data import annual_temperature_rows


class NumericalBehavior(unittest.TestCase):
    def test_daily_indices_and_runs(self):
        result=h.heat_indices([36,37,30,36],[26,27,20,25])
        self.assertEqual(result,dict(TXx=37,TNn=20,TXn=30,TNx=27,days_above=3,longest_run=2))
        self.assertEqual(h.longest_run([35,36,36],35),2)
        self.assertEqual(h.season_key('2024-12-31'),(2025,'DJF'))
        self.assertEqual(h.season_key('2025-01-01'),(2025,'DJF'))

    def test_units_weights_and_quantiles(self):
        self.assertAlmostEqual(h.kelvin_to_celsius(273.15),0)
        self.assertAlmostEqual(h.area_mean([0,30],[0,60]),10)
        self.assertAlmostEqual(h.quantile([0,10,20],.1),2)
        self.assertEqual(h.annual_hot_days([1]*12, 2025),12)
        with self.assertRaises(ValueError):h.annual_hot_days([1]*11+[None], 2025)
        for value in [float('nan'),float('inf'),-1]:
            with self.assertRaises(ValueError):h.kelvin_to_celsius(value)

    def test_calendar_month_counts(self):
        self.assertEqual(h.annual_hot_days([31,29,31,30,31,30,31,31,30,31,30,31], 2024),366)
        self.assertEqual(h.annual_hot_days([31,28,31,30,31,30,31,31,30,31,30,31], 2025),365)
        for year, month, count in [(2025,2,29),(1900,2,29),(2024,2,30),(2025,4,31),(2025,1,1.5)]:
            counts=[0]*12;counts[month-1]=count
            with self.subTest(year=year,month=month,count=count),self.assertRaises(ValueError):
                h.annual_hot_days(counts,year)
        self.assertEqual(h.annual_hot_days([0,29]+[0]*10, 2000),29)
        for year in [2024.5,True,0]:
            with self.assertRaises(ValueError):h.annual_hot_days([0]*12,year)

    def test_dhw_qualification_and_window(self):
        self.assertEqual(h.degree_heating_weeks([.99]*84),0)
        self.assertEqual(h.degree_heating_weeks([1]*84),12)
        self.assertEqual(h.degree_heating_weeks([2]*84),24)
        with self.assertRaises(ValueError):h.degree_heating_weeks([1]*83)

    def test_water_mass_balance(self):
        self.assertEqual(h.water_balance(300,100,30,20),dict(demand_l=600,remaining_l=0,deficit_l=200))
        self.assertEqual(h.water_balance(700,100,30,20)['remaining_l'],200)

    def test_scenario_thresholds_and_benefits(self):
        for c in h.cases():
            baseline=h.scenario(c,2,1)
            improved=h.scenario(c,2,1,'combined')
            self.assertLessEqual(0,baseline['capacity'])
            self.assertLessEqual(baseline['capacity'],c['daily_visits'])
            self.assertGreaterEqual(improved['capacity'],baseline['capacity'])
            self.assertEqual(baseline['capacity']+baseline['unmet_visits'],c['daily_visits'])
            if c['coastal']:
                self.assertTrue(h.scenario(c,water_m=c['road_m']-.001)['access_open'])
                self.assertFalse(h.scenario(c,water_m=c['road_m'])['access_open'])
                for package, inputs in h.ADAPTATIONS.items():
                    road=math.floor((c['road_m']+inputs['road_raise_m'])*1000+.5)/1000
                    with self.subTest(case=c['id'],package=package):
                        self.assertTrue(h.scenario(c,water_m=road-.001,adaptation=package)['access_open'])
                        at_threshold=h.scenario(c,water_m=road,adaptation=package)
                        self.assertFalse(at_threshold['access_open'])
                        self.assertEqual(at_threshold['road_m'],road)
                        self.assertFalse(h.scenario(c,water_m=road-1e-12,adaptation=package)['access_open'])
            else:self.assertTrue(h.scenario(c,water_m=3)['access_open'])
        for bad in [math.nan,math.inf,-1,6]:
            with self.assertRaises(ValueError):h.scenario(h.cases()[0],heat_delta=bad)
        with self.assertRaises(ValueError):h.scenario(h.cases()[0],adaptation='unknown')


class ContentContracts(unittest.TestCase):
    def test_annual_temperature_column_and_incomplete_year(self):
        raw=(ROOT/'tests/fixtures/nasa-annual-column.csv').read_text()
        self.assertEqual(annual_temperature_rows(raw),[(2023,.44,'observed'),(2024,1.01,'observed')])

    def test_generated_core_launch_links_and_capstone_assumptions(self):
        import make_notebooks
        for slug,*_ in make_notebooks.LESSONS:
            nb=json.loads((ROOT/'content/notebooks'/f'{slug}.ipynb').read_text(encoding='utf-8'))
            intro=''.join(nb['cells'][0]['source'])
            self.assertIn(f'path=notebooks/{slug}.ipynb',intro)
            self.assertIn('archived Healthsites / OpenStreetMap points',intro)
            self.assertNotIn('all local facilities',intro)
        capstone=next(lesson for lesson in make_notebooks.LESSONS if lesson[0]=='12_capstone')
        scope={'h':h,'cases':h.cases(),'json':json}
        with contextlib.redirect_stdout(io.StringIO()):exec(capstone[3][0],scope)
        brief=scope['brief'];inputs=brief['assumptions'];case=inputs['case_inputs']
        self.assertEqual(inputs['selected_package'],h.ADAPTATIONS[inputs['adaptation']])
        self.assertEqual(brief['before'],h.scenario(case,inputs['heat_delta_c'],inputs['water_m'],'baseline'))
        self.assertEqual(brief['after'],h.scenario(case,inputs['heat_delta_c'],inputs['water_m'],inputs['adaptation']))

    def test_observations_are_global_and_hashed(self):
        metadata=json.loads((h.DATA/'provenance.json').read_text())
        self.assertIn('global',metadata['observed']['title'])
        self.assertIn('1951-1980',metadata['observed']['units'])
        self.assertEqual(metadata['observed']['sha256'],hashlib.sha256((h.DATA/'nasa-gistemp-raw.csv').read_bytes()).hexdigest())
        rows=h.read_csv('global-temperature.csv')
        self.assertGreater(len(rows),100)
        self.assertTrue(all(r['data_type']=='observed' and math.isfinite(float(r['anomaly_c'])) for r in rows))

    def test_lesson_content_and_labels(self):
        paths=list((ROOT/'content/notebooks').glob('*.ipynb'))
        self.assertGreaterEqual(len(paths),12)
        for path in paths:
            nb=json.loads(path.read_text(encoding='utf-8'))
            text='\n'.join(''.join(c['source']) for c in nb['cells'])
            self.assertIn('## Your exercise',text,path.name)
            self.assertIn('## Interpretation',text,path.name)
            self.assertIn('## Source and limitation',text,path.name)
            self.assertGreaterEqual(sum(c['cell_type']=='code' for c in nb['cells']),3)
        self.assertIn('India',{c['country'] for c in h.cases()})

    def test_jgis_paths_and_story(self):
        schema_dir=ROOT/'tests/schemas/jupytergis-0.16.7'
        for path in (ROOT/'content/projects').glob('*.jGIS'):
            p=json.loads(path.read_text())
            jsonschema.validate(p,json.loads((schema_dir/'jgis.json').read_text()))
            self.assertEqual(p['schemaVersion'],'0.6.0')
            self.assertGreaterEqual(len(p['stories']['climate-health']['storySegments']),5)
            for source in p['sources'].values():
                jsonschema.validate(source['parameters'],json.loads((schema_dir/'sources/geoJsonSource.json').read_text()))
                if 'path' in source['parameters']:self.assertTrue((path.parent/source['parameters']['path']).exists())
            for layer in p['layers'].values():
                name='storySegmentLayer' if layer['type']=='StorySegmentLayer' else 'vectorLayer'
                jsonschema.validate(layer['parameters'],json.loads((schema_dir/'layers'/f'{name}.json').read_text()))


if __name__=='__main__':unittest.main()
