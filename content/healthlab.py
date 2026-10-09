"""Original, deterministic teaching arithmetic; never a clinical or flood model."""
from pathlib import Path
from datetime import date
from calendar import monthrange
import csv
import html
import json
import math

DATA = Path(__file__).resolve().parent / "data"


def finite(value, minimum=None, maximum=None):
    value = float(value)
    if not math.isfinite(value) or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        raise ValueError(f"Expected finite value in [{minimum}, {maximum}]")
    return value


def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def cases():
    return json.loads((DATA / "cases.json").read_text(encoding="utf-8"))


def kelvin_to_celsius(value):
    return finite(value, 0) - 273.15


def area_mean(values, latitudes):
    """Equal longitude, regular latitude grid approximation; not arbitrary polygons."""
    if not values or len(values) != len(latitudes):
        raise ValueError("Provide equal nonempty vectors")
    weights = [math.cos(math.radians(finite(lat, -90, 90))) for lat in latitudes]
    if sum(weights) < 1e-12:
        raise ValueError("Grid has no positive area")
    return sum(finite(v) * w for v, w in zip(values, weights)) / sum(weights)


def quantile(values, fraction):
    """Linear interpolation at (n-1)*fraction, equivalent to common type-7 quantiles."""
    values = sorted(finite(v) for v in values)
    if not values:
        raise ValueError("Quantiles require observations")
    pos = (len(values) - 1) * finite(fraction, 0, 1)
    lo = int(pos)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (pos - lo)


def longest_run(values, threshold):
    threshold = finite(threshold)
    best = current = 0
    for value in values:
        current = current + 1 if finite(value) > threshold else 0
        best = max(best, current)
    return best


def heat_indices(tmax, tmin, threshold=35):
    if not tmax or len(tmax) != len(tmin):
        raise ValueError("Paired daily maximum and minimum temperatures required")
    hi, lo = [finite(x) for x in tmax], [finite(x) for x in tmin]
    if any(a < b for a, b in zip(hi, lo)):
        raise ValueError("Daily maximum must not be below minimum")
    threshold = finite(threshold)
    return dict(TXx=max(hi), TNn=min(lo), TXn=min(hi), TNx=max(lo),
                days_above=sum(t > threshold for t in hi), longest_run=longest_run(hi, threshold))


def season_key(iso_date):
    day = date.fromisoformat(iso_date)
    season = ("DJF", "MAM", "JJA", "SON")[(day.month % 12) // 3]
    return day.year + (day.month == 12), season


def annual_hot_days(monthly, year):
    """Sum whole-day counts bounded by each month of the explicit calendar year."""
    if isinstance(year, bool) or not isinstance(year, int) or not 1 <= year <= 9999:
        raise ValueError("Provide an integer calendar year from 1 to 9999")
    if len(monthly) != 12 or any(x is None for x in monthly):
        raise ValueError("All twelve monthly counts required; missing is not zero")
    counts = [finite(x, 0, monthrange(year, month)[1]) for month, x in enumerate(monthly, 1)]
    if any(isinstance(x, bool) or not n.is_integer() for x, n in zip(monthly, counts)):
        raise ValueError("Monthly counts must be whole days")
    return sum(int(n) for n in counts)


def degree_heating_weeks(hotspots):
    """84 trailing daily HotSpot values in deg C above a stated maximum monthly mean."""
    if len(hotspots) != 84:
        raise ValueError("DHW needs exactly 84 days for this exercise")
    return sum(h for value in hotspots if (h := finite(value)) >= 1.0) / 7


def water_balance(storage_l, inflow_l, people, litres_per_person=20):
    storage_l, inflow_l = finite(storage_l, 0), finite(inflow_l, 0)
    demand = finite(people, 0) * finite(litres_per_person, 0)
    available = storage_l + inflow_l
    return dict(demand_l=demand, remaining_l=max(0, available - demand), deficit_l=max(0, demand - available))


ADAPTATIONS = {
    "baseline": dict(label="Current design", cooling_c=0, road_raise_m=0, water_add_l=0, backup_add_h=0, cost_units=0),
    "shade": dict(label="Shade + reflective roof", cooling_c=2.5, road_raise_m=0, water_add_l=0, backup_add_h=0, cost_units=2),
    "sponge": dict(label="Water harvesting + shade", cooling_c=1.5, road_raise_m=0, water_add_l=1600, backup_add_h=0, cost_units=3),
    "engineering": dict(label="Raised access + backup power", cooling_c=0, road_raise_m=0.8, water_add_l=0, backup_add_h=12, cost_units=5),
    "combined": dict(label="Combined package", cooling_c=2.5, road_raise_m=0.8, water_add_l=1600, backup_add_h=12, cost_units=8),
}


def scenario(case, heat_delta=1.5, water_m=0.6, adaptation="baseline"):
    """Fictional 1-day scenario; water/road use nearest 0.001 m, ties rounded up."""
    heat_delta, water_m = finite(heat_delta, 0, 5), finite(water_m, 0, 3)
    if adaptation not in ADAPTATIONS:
        raise ValueError("Unknown adaptation")
    a = ADAPTATIONS[adaptation]
    indoor = case["outdoor_c"] + heat_delta + case["indoor_offset_c"] - a["cooling_c"]
    water_m = math.floor(water_m * 1000 + 0.5) / 1000
    road = math.floor((case["road_m"] + a["road_raise_m"]) * 1000 + 0.5) / 1000
    # Inland cases have no marine exposure in this scenario; rainfall is not simulated.
    access = not case["coastal"] or water_m < road
    heat_fraction = max(0, min(0.5, (indoor - 30) * 0.035))
    water_fraction = min(1, (case["water_l"] + a["water_add_l"]) / (case["daily_visits"] * 20))
    power_fraction = min(1, (case["power_h"] + a["backup_add_h"]) / 24)
    capacity = math.floor(case["daily_visits"] * (1 - heat_fraction) * min(water_fraction, power_fraction) * (1 if access else 0.35))
    return dict(case_id=case["id"], city=case["city"], country=case["country"], data_type="synthetic",
                heat_delta_c=heat_delta, water_m=water_m, adaptation=adaptation,
                indoor_c=round(indoor, 2), access_open=access, road_m=road,
                water_fraction=round(water_fraction, 4), power_fraction=round(power_fraction, 4),
                capacity=capacity, unmet_visits=case["daily_visits"]-capacity,
                cost_units=a["cost_units"])


def line_svg(xs, ys, title, y_label):
    """Accessible static chart; core lessons need no plotting package or network."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("At least two paired points required")
    xs, ys = [finite(x) for x in xs], [finite(y) for y in ys]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    dx, dy = xmax - xmin or 1, ymax - ymin or 1
    points = " ".join(f"{60+650*(x-xmin)/dx:.1f},{235-190*(y-ymin)/dy:.1f}" for x,y in zip(xs,ys))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(title)}" viewBox="0 0 760 285"><rect width="760" height="285" fill="#f1f6f5"/><text x="60" y="24" fill="#123b45">{html.escape(title)}</text><path d="M60 40V235H710" fill="none" stroke="#345"/><polyline points="{points}" fill="none" stroke="#007b78" stroke-width="2.5"/><text x="8" y="55">{ymax:.2f}</text><text x="8" y="235">{ymin:.2f}</text><text x="60" y="260">{xmin:g}</text><text x="670" y="260">{xmax:g}</text><text x="310" y="280">{html.escape(y_label)}</text></svg>'''
