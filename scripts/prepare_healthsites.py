"""Extract a small ODbL teaching database from an existing Healthsites point archive.

Maintainer-only: python scripts/prepare_healthsites.py --source-root ../2024-Climate-Heat-Stress
No network, API key, GIS dependency or modification of the source archive is needed.
The shipped subset is sufficient for all learner activities.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
CONTEXTS = [
    ("mumbai", "Mumbai", "India", 72.88, 19.08),
    ("beira", "Beira", "Mozambique", 34.84, -19.83),
    ("durban", "Durban", "South Africa", 31.02, -29.86),
    ("mombasa", "Mombasa", "Kenya", 39.67, -4.04),
    ("lusaka", "Lusaka", "Zambia", 28.28, -15.39),
    ("kampala", "Kampala", "Uganda", 32.58, 0.35),
    ("lagos", "Lagos", "Nigeria", 3.38, 6.52),
]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def points(path):
    """Yield the physical DBF row index and coordinates from Point shapefiles."""
    with path.open("rb") as stream:
        header = stream.read(100)
        if len(header) != 100 or struct.unpack(">i", header[:4])[0] != 9994:
            raise ValueError("Invalid shapefile header")
        if struct.unpack("<i", header[32:36])[0] != 1:
            raise ValueError("This extractor accepts Point shapefiles only")
        index = 0
        while record_header := stream.read(8):
            if len(record_header) != 8:
                raise ValueError("Truncated shapefile record")
            _, words = struct.unpack(">2i", record_header)
            payload = stream.read(words * 2)
            if len(payload) != words * 2:
                raise ValueError("Truncated point record")
            if len(payload) >= 20 and struct.unpack("<i", payload[:4])[0] == 1:
                lon, lat = struct.unpack("<2d", payload[4:20])
                if math.isfinite(lon) and math.isfinite(lat):
                    yield index, lon, lat
            index += 1


def dbf_reader(stream):
    header = stream.read(32)
    header_size, row_size = struct.unpack("<2H", header[8:12])
    fields, offset = {}, 1
    while True:
        first = stream.read(1)
        if first == b"\r":
            break
        descriptor = first + stream.read(31)
        if len(descriptor) != 32:
            raise ValueError("Invalid DBF field header")
        name = descriptor[:11].split(b"\0")[0].decode("ascii")
        width = descriptor[16]
        fields[name] = (offset, width)
        offset += width

    def read(index):
        stream.seek(header_size + index * row_size)
        row = stream.read(row_size)
        if len(row) != row_size or row[:1] == b"*":
            return None
        result = {}
        for name in ("osm_id", "name", "amenity", "healthcare"):
            if name in fields:
                start, width = fields[name]
                result[name] = row[start:start + width].decode("utf-8", errors="replace").strip() or None
        return result
    return read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--per-context", type=int, default=24)
    args = parser.parse_args()
    if not 1 <= args.per_context <= 100:
        parser.error("--per-context must be from 1 to 100")
    source = args.source_root.resolve() / "World/World-node.shp"
    dbf = source.with_suffix(".dbf")
    projection = source.with_suffix(".prj").read_text()
    if "WGS_1984" not in projection or "PROJCS" in projection:
        raise ValueError("Expected the archived geographic WGS84 CRS")
    matches = {case[0]: [] for case in CONTEXTS}
    for index, lon, lat in points(source):
        for case_id, _, _, x, y in CONTEXTS:
            if abs(lon - x) <= 0.25 and abs(lat - y) <= 0.20:
                distance = ((lon - x) * math.cos(math.radians(y))) ** 2 + (lat - y) ** 2
                matches[case_id].append((distance, index, lon, lat))
    features, summary, seen_ids = [], [], set()
    with dbf.open("rb") as stream:
        read = dbf_reader(stream)
        for case_id, city, country, x, y in CONTEXTS:
            selected, duplicates = [], 0
            for _, index, lon, lat in sorted(matches[case_id]):
                props = read(index)
                if not props or not props.get("osm_id"):
                    continue
                osm_id = props["osm_id"].split(".")[0]
                if not osm_id.isdigit():
                    raise ValueError("Unexpected OSM identifier")
                if osm_id in seen_ids:
                    duplicates += 1
                    continue
                seen_ids.add(osm_id)
                props.update(osm_id=osm_id, osm_type="node", case_id=case_id,
                             context_city=city, country=country, data_type="archived_osm",
                             source="Healthsites.io / OpenStreetMap", license="ODbL-1.0",
                             osm_url="https://www.openstreetmap.org/node/" + osm_id)
                selected.append({"type": "Feature", "id": "node/" + osm_id,
                                 "geometry": {"type": "Point", "coordinates": [lon, lat]},
                                 "properties": props})
                if len(selected) == args.per_context:
                    break
            features.extend(selected)
            summary.append({"case_id": case_id, "city": city, "bbox": [x-.25,y-.20,x+.25,y+.20],
                            "candidate_points": len(matches[case_id]), "included_points": len(selected),
                            "duplicate_ids_skipped_before_limit": duplicates})
    if len({f["id"] for f in features}) != len(features):
        raise ValueError("Duplicate OSM identifiers across teaching contexts")
    output = ROOT / "content/data"
    output.mkdir(parents=True, exist_ok=True)
    geojson = {"type": "FeatureCollection", "features": features,
               "attribution": "© OpenStreetMap contributors; Healthsites.io extract; ODbL 1.0",
               "license": "https://opendatacommons.org/licenses/odbl/1-0/",
               "source_id": "healthsites-legacy-subset"}
    target = output / "healthsites_facilities.geojson"
    target.write_text(json.dumps(geojson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance = {
        "id": "healthsites-legacy-subset", "data_class": "archived mapped facilities",
        "provider": "Healthsites.io, derived from OpenStreetMap contributors",
        "source_url": "https://healthsites.io/", "upstream_source_url": "https://www.openstreetmap.org/",
        "processed_on": "2026-10-09", "original_extract_date": None,
        "date_note": "Exact upstream extraction date is not recorded. Source is the user's legacy 2024 project archive; processed date is not data currency.",
        "crs": "EPSG:4326", "license": "ODbL-1.0",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "attribution": "© OpenStreetMap contributors; extracted by Healthsites.io",
        "source_files": [{"file": "World/"+p.name, "bytes": p.stat().st_size, "sha256": digest(p)}
                         for p in [source, dbf, source.with_suffix('.prj')]],
        "transform": f"Point records only; ±0.25° longitude/±0.20° latitude boxes around approximate city centers; select up to {args.per_context} unique OSM nodes nearest by longitude distance scaled by cosine(latitude), with physical row index as stable tie-breaker. Duplicate OSM IDs keep the first record in that order, not necessarily the latest version. Retain only OSM identifiers, name, amenity, healthcare and coordinates. No inference or imputation of service/support status.",
        "selection": summary, "feature_count": len(features), "output_sha256": digest(target),
        "limitations": ["Not exhaustive or representative samples; counts are not city facility totals.",
                        "Point-only selection omits mapped building polygons and unmapped facilities.",
                        "Archived locations/tags may be outdated, incorrect or incomplete.",
                        "Presence does not establish current operation, HIV/TB services or PEPFAR support.",
                        "No patient, workforce, contact or observer identifiers are included."]}
    (output / "healthsites_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (output / "healthsites_ODbL-1.0.txt").write_bytes((args.source_root / "World/LICENSE.txt").read_bytes())
    print(json.dumps({"features": len(features), "contexts": summary}))


if __name__ == "__main__":
    main()
