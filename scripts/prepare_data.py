"""Regenerate original teaching fixtures. Refresh observational snapshot only on request."""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content/data"
NASA = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_land.geojson"


def dump(name, value):
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def annual_temperature_rows(raw):
    """Extract only finite J-D annual anomalies; incomplete annual rows are omitted."""
    rows = csv.DictReader(io.StringIO(raw[raw.index("Year,"):]))
    annual = []
    for row in rows:
        try:
            year, anomaly = int(row["Year"]), float(row["J-D"])
        except (ValueError, TypeError, KeyError):
            continue
        if math.isfinite(anomaly):
            annual.append((year, anomaly, "observed"))
    return annual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Download current NASA snapshot and pinned Natural Earth; updates retrieval date")
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    retrieved = "2026-10-09"
    if args.refresh:
        for name, url in [("nasa-gistemp-raw.csv", NASA), ("natural-earth-land.geojson", NE)]:
            (DATA / name).write_bytes(urllib.request.urlopen(url, timeout=60).read())
        retrieved = date.today().isoformat()
    elif (DATA / "provenance.json").exists():
        retrieved = json.loads((DATA / "provenance.json").read_text())["observed"]["retrieved_on"]
    raw = (DATA / "nasa-gistemp-raw.csv").read_text(encoding="utf-8-sig")
    with (DATA / "global-temperature.csv").open("w", newline="", encoding="utf-8") as f:
        out = csv.writer(f); out.writerow(["year", "anomaly_c", "data_type"])
        out.writerows(annual_temperature_rows(raw))
    # Geographic anchors are approximate city centers; all facility attributes are invented.
    parameters = [
        ("mumbai", "Mumbai", "India", 72.88, 19.08, True, 33.5, 2.2, 0.9, 2.1, 140, 1800, 16),
        ("beira", "Beira", "Mozambique", 34.84, -19.83, True, 31.0, 2.0, 0.55, 1.4, 100, 1400, 12),
        ("durban", "Durban", "South Africa", 31.02, -29.86, True, 29.0, 2.1, 1.4, 2.6, 120, 2400, 18),
        ("mombasa", "Mombasa", "Kenya", 39.67, -4.04, True, 32.0, 1.8, 1.1, 2.0, 90, 1200, 14),
        ("lusaka", "Lusaka", "Zambia", 28.28, -15.39, False, 30.0, 2.5, 1.5, 3.0, 110, 1600, 10),
        ("kampala", "Kampala", "Uganda", 32.58, 0.35, False, 28.0, 2.0, 1.3, 2.5, 100, 1500, 16),
        ("lagos", "Lagos", "Nigeria", 3.38, 6.52, True, 32.5, 2.4, 0.7, 1.8, 160, 2000, 14),
    ]
    keys = ["id","city","country","longitude","latitude","coastal","outdoor_c","indoor_offset_c","road_m","floor_m","daily_visits","water_l","power_h"]
    cases = [dict(zip(keys, p), data_type="synthetic", source="Original teaching scenario; no real facility or funding status", coordinate_role="Approximate city context only") for p in parameters]
    dump("cases.json", cases)
    features = [dict(type="Feature", geometry=dict(type="Point",coordinates=[c["longitude"],c["latitude"]]), properties=c) for c in cases]
    dump("study-sites.geojson", dict(type="FeatureCollection", features=features))
    with (DATA / "daily-heat.csv").open("w", newline="", encoding="utf-8") as f:
        out=csv.writer(f); out.writerow(["case_id","date","tmax_c","tmin_c","data_type"])
        for i,c in enumerate(cases):
            for d in range(365):
                seasonal=3.8*math.sin(2*math.pi*(d-80+182*(c["latitude"]<0))/365)
                pulse=1.5*math.sin(d*0.61+i)
                hi=round(c["outdoor_c"]+seasonal+pulse,2)
                out.writerow([c["id"],(date(2025,1,1)+timedelta(days=d)).isoformat(),hi,round(hi-8-0.5*math.sin(d),2),"synthetic"])
    dump("mobility.json", {"data_type":"synthetic","period":"fictional 30 days","movements":[{"origin":"Coast community","destination":"Inland host community","events":120,"distinct_persons":95},{"origin":"Inland host community","destination":"Coast community","events":35,"distinct_persons":30}],"unique_people_across_all_routes":110,"note":"Repeated movement and overlap mean route persons cannot be summed to unique people. No legal status inferred."})
    import sys
    sys.path.insert(0,str(ROOT/"content"))
    from healthlab import ADAPTATIONS, scenario
    dump("adaptations.json", ADAPTATIONS)
    dump("scenario-checks.json",[scenario(c,h,w,a) for c in cases for h in [0,1.5,5] for w in [0,0.6,3] for a in ADAPTATIONS])
    dump("provenance.json", {
        "observed":{"title":"NASA GISTEMP v4 global land-ocean temperature index", "source_url":NASA,"citation":"GISTEMP Team (2026); Lenssen et al. (2024), doi:10.1029/2023JD040179", "retrieved_on":retrieved,"units":"degrees Celsius anomaly relative to 1951-1980", "transform":"Read J-D annual column; exclude incomplete/non-numeric years. No interpolation.","license":"US government NASA data; freely available with acknowledgement; no endorsement", "sha256":hashlib.sha256((DATA/"nasa-gistemp-raw.csv").read_bytes()).hexdigest()},
        "geography":{"title":"Natural Earth land 1:110m", "version":"5.1.2", "source_url":NE,"license":"Public domain", "attribution":"Made with Natural Earth", "sha256":hashlib.sha256((DATA/"natural-earth-land.geojson").read_bytes()).hexdigest(),"limitation":"Coarse reference geometry, not a local coastline or boundary adjudication"},
        "synthetic":{"title":"Original fictional climate-health scenarios", "generator":"scripts/prepare_data.py", "license":"CC0-1.0", "seed":"No randomness; explicit constants and sinusoidal daily series", "reference_period":"Synthetic 2025 daily calendar, one-day service event", "limitation":"Not observations, forecasts, PEPFAR facilities, epidemiologic or causal estimates"}})
    print("Prepared compact NASA observation, Natural Earth geometry and original synthetic teaching fixtures")


if __name__ == "__main__": main()
