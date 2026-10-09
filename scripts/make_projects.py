"""Create portable JupyterGIS 0.16.7 / schema 0.6.0 guided story projects."""
from pathlib import Path
import json
import math
import copy

ROOT=Path(__file__).resolve().parents[1]


def extent(lon,lat,delta=9):
    def xy(x,y): return [6378137*math.radians(x),6378137*math.log(math.tan(math.pi/4+math.radians(y)/2))]
    return xy(lon-delta,lat-delta)+xy(lon+delta,lat+delta)


def main():
    cases=json.loads((ROOT/'content/data/cases.json').read_text())
    layers={"land":{"name":"Natural Earth land (public domain)","type":"VectorLayer","visible":True,"parameters":{"source":"land-data","opacity":0.5,"symbologyState":{}}},"sites":{"name":"SYNTHETIC clinic scenarios; city anchors only","type":"VectorLayer","visible":True,"parameters":{"source":"sites-data","opacity":1,"symbologyState":{}}}}
    sources={"land-data":{"name":"Made with Natural Earth v5.1.2","type":"GeoJSONSource","parameters":{"path":"../data/natural-earth-land.geojson","useProxy":False}},"sites-data":{"name":"Original fictional scenarios (CC0)","type":"GeoJSONSource","parameters":{"path":"../data/study-sites.geojson","useProxy":False}}}
    narratives={"mumbai":"Global warming is not a local heat index. India is included alongside African contexts. All facility values are fictional; this point is a city anchor and has no real facility funding status.","beira":"A dry building may be isolated by an access route. Compare an invented road elevation with a water plane; no tide, surge, drainage or hydrologic connectivity is modeled.","lusaka":"This inland case has no marine exposure in the toy model. Identify water and electricity bottlenecks and discuss medicine supply, staffing and referrals for HIV/TB continuity.","mombasa":"Evaluate appropriate shade, water harvesting, reliable power and access engineering. Mangroves, seagrass and reef health have local ecological context; no universal flood-protection factor is assumed.","lagos":"Discuss mobility, host communities, food/water access and equity. Climate is not a deterministic cause of conflict. Movement counts are not distinct people and do not establish legal status."}
    story_ids=[]
    for c in cases:
        if c['id'] not in narratives: continue
        sid=c['id']+'-story';story_ids.append(sid)
        layers[sid]={"name":c['city']+": climate and health","type":"StorySegmentLayer","visible":True,"parameters":{"zoom":5,"extent":extent(c['longitude'],c['latitude']),"transition":{"type":"smooth","time":1},"layerOverride":[],"content":{"contentMode":"map","markdown":f"## {c['city']}, {c['country']}\n\n{narratives[c['id']]}\n\n**Synthetic teaching scenario.** Not observations, forecasts or PEPFAR facility locations.\n\nExplore the [scenario dashboard](https://jltobias.github.io/JupyterLite-Climate-and-Health/explore/?case={c['id']})."}}}
    project={"schemaVersion":"0.6.0","options":{"longitude":45,"latitude":3,"zoom":2,"projection":"EPSG:3857","bearing":0,"pitch":0,"extent":extent(45,3,40)},"layerTree":["land","sites"]+story_ids,"layers":layers,"sources":sources,"stories":{"climate-health":{"title":"Climate and health: continuity of care","storyType":"guided","storySegments":story_ids,"presentationBgColor":"#123e3d","presentationTextColor":"#F7FBFF","showGradient":False}},"viewState":{},"metadata":{"title":"Climate & Health learning story","description":"Original synthetic scenarios; Natural Earth public-domain land. No external tiles. See data/provenance.json and the Book references.","license":"MIT project configuration; CC BY4 original prose; CC0 scenarios"}}
    out=ROOT/'content/projects';out.mkdir(parents=True,exist_ok=True)
    (out/'climate-health.jGIS').write_text(json.dumps(project,indent=2),encoding='utf-8')
    archive=copy.deepcopy(project)
    archive['sources']['sites-data']['name']='Archived Healthsites / OpenStreetMap facilities (ODbL)'
    archive['sources']['sites-data']['parameters']['path']='../data/healthsites_facilities.geojson'
    archive['layers']['sites']['name']='ARCHIVED actual map features; operation and funding unverified'
    archive['stories']['climate-health']['title']='Healthsites: inspect an archived facility map'
    archive['metadata']={'title':'Archived Healthsites context','description':'© OpenStreetMap contributors; extracted by Healthsites.io. ODbL-1.0. Non-exhaustive city samples; original extraction date unknown. No real funding or service status inferred. No synthetic impacts attached.'}
    for sid in story_ids:
        layer=archive['layers'][sid]
        layer['parameters']['content']['markdown']=f"## {layer['name'].split(':')[0]}: archived mapped facilities\n\nThese public map features are from Healthsites/OpenStreetMap. The source extraction date is unknown and this small sample is not a facility census. Presence does not establish current operation, HIV/TB services or PEPFAR support.\n\n© OpenStreetMap contributors; extracted by Healthsites.io. ODbL-1.0. See `data/healthsites_provenance.json`.\n\nDo not assign the course's fictional scenario values to these actual features."
    (out/'healthsites-context.jGIS').write_text(json.dumps(archive,indent=2),encoding='utf-8')
    print('Created offline-basemap JupyterGIS story project')


if __name__=='__main__':main()
