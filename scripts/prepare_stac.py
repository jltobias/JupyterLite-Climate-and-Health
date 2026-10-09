"""Fetch bounded, public metadata examples. No imagery or credentials are downloaded."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'content/data'
DATE = datetime.now(timezone.utc).date().isoformat()
QUERIES = [
    ('copernicus_mumbai', 'https://stac.dataspace.copernicus.eu/v1/search',
     {'collections':'sentinel-2-l2a','bbox':'72.63,18.88,73.13,19.28','datetime':'2024-04-01T00:00:00Z/2024-04-30T23:59:59Z','limit':6},
     'Copernicus Data Space Ecosystem / ESA / European Commission',
     'Copernicus Sentinel data legal notice; collection license identifier: other',
     'https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice'),
    ('dea_beira', 'https://explorer.digitalearth.africa/stac/search',
     {'collections':'wofs_ls_summary_annual','bbox':'34.59,-20.03,35.09,-19.63','datetime':'2022-01-01T00:00:00Z/2022-12-31T23:59:59Z','limit':6},
     'Digital Earth Africa', 'CC-BY-4.0', 'https://docs.digitalearthafrica.org/en/latest/data_specs/Landsat_WOfS_specs.html'),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retrieved-on', default=DATE, help='Record actual acquisition date (YYYY-MM-DD)')
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    for name, endpoint, parameters, provider, license_name, license_url in QUERIES:
        url = endpoint + '?' + urlencode(parameters)
        request = Request(url, headers={'Accept':'application/geo+json, application/json','User-Agent':'ClimateHealthEducation/1.0'})
        with urlopen(request, timeout=35) as response:
            raw = response.read()
        document = json.loads(raw)
        if document.get('type') != 'FeatureCollection' or not isinstance(document.get('features'), list):
            raise ValueError('Provider did not return a FeatureCollection')
        if len(document['features']) > parameters['limit']:
            raise ValueError('Provider exceeded the requested page size')
        artifact = {'provenance':{'provider':provider,'source_url':url,'request':parameters,
                    'retrieved_on':args.retrieved_on,'data_class':'catalog_metadata_snapshot',
                    'license':license_name,'license_url':license_url,'raw_response_sha256':hashlib.sha256(raw).hexdigest(),
                    'scope':'One bounded page only. Not complete coverage. Scene footprints are not observed hazard extents; assets retain provider terms.'},
                    'feature_collection':document}
        (DATA / ('stac_'+name+'.json')).write_text(json.dumps(artifact, indent=2)+'\n', encoding='utf-8')
        print(name, len(document['features']), 'items', flush=True)
    parameters = {'service':'WFS','version':'2.0.0','request':'GetFeature',
                  'typeNames':'coral-atlas:benthic_data_verbose','bbox':'39.70,-4.10,39.82,-3.99,EPSG:4326',
                  'srsName':'EPSG:4326','count':8,'outputFormat':'application/json'}
    url='https://allencoralatlas.org/geoserver/ows?'+urlencode(parameters)
    with urlopen(Request(url, headers={'User-Agent':'geoserver-client'}), timeout=35) as response:
        raw=response.read()
    doc=json.loads(raw)
    if doc.get('type')!='FeatureCollection' or len(doc.get('features',[]))>8:
        raise ValueError('Unexpected Allen Coral Atlas response')
    artifact={'provenance':{'provider':'Allen Coral Atlas Partnership / Arizona State University',
              'source_url':url,'retrieved_on':args.retrieved_on,'data_class':'habitat_classification_subset',
              'license':'CC-BY-4.0','license_url':'https://allencoralatlas.org/resources/',
              'citation':'Allen Coral Atlas (2022). Imagery, maps and monitoring of the world’s tropical coral reefs. doi:10.5281/zenodo.3833242.',
              'raw_response_sha256':hashlib.sha256(raw).hexdigest(),
              'scope':'First eight polygons within a small Mombasa-coast bounding box. Not a representative sample, complete habitat map, bleaching observation or Planet satellite mosaic.'},'feature_collection':doc}
    (DATA/'stac_allen_mombasa.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
    print('Allen Coral Atlas',len(doc.get('features',[])),'features',flush=True)

if __name__=='__main__':main()
