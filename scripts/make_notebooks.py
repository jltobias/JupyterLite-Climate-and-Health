"""Author the canonical lessons. All calculations use small bundled fixtures."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content/notebooks"
BOOT = '''from pathlib import Path
import sys, json, statistics
root = next((p for p in (Path.cwd(), *Path.cwd().parents) if (p / "healthlab.py").exists()), None)
if root is None:
    raise RuntimeError("Open this notebook inside the bundled content folder; healthlab.py and data/ are required.")
if str(root) not in sys.path: sys.path.insert(0, str(root))
import healthlab as h
from IPython.display import display, SVG
cases = h.cases()
print("Loaded", len(cases), "fictional facility scenarios; city coordinates are context only.")'''

# title, objectives/context, executable analyses, exercise, interpretation, source/limitation
LESSONS = [
("00_start_here", "Start here: climate, health and evidence", "Distinguish hazard, exposure, vulnerability and service continuity. This course is for public-health students and practitioners. India appears alongside African teaching contexts; neither this selection nor a city marker establishes a program-country roster or facility funding. A hazard can interrupt treatment through transport, staffing, water or power even when a clinic building remains dry.", [
'''provenance = json.loads((h.DATA / "provenance.json").read_text())
for kind, item in provenance.items():
    print(kind.upper(), "|", item["title"], "|", item["license"])
assert {c["country"] for c in cases} >= {"India", "Mozambique", "Kenya"}''',
'''facilities=json.loads((h.DATA/"healthsites_facilities.geojson").read_text())
archive=json.loads((h.DATA/"healthsites_provenance.json").read_text())
print("Archived mapped features:",len(facilities["features"]))
print("License:",archive["license"],"original extract date:",archive["original_extract_date"])
print("Processed on:",archive["processed_on"],"is NOT a data-currency date")
for case in cases:
    count=sum(f["properties"]["case_id"]==case["id"] for f in facilities["features"])
    print(case["city"],count,"sampled mapped features; not a city facility total")
print("Actual mapped features are never assigned the fictional scenario impacts.")''',
'''case = cases[0]
result = h.scenario(case)
print(case["city"], "fictional daily demand:", case["daily_visits"])
print("Illustrative capacity:", result["capacity"], "visits; unmet:", result["unmet_visits"])
assert result["capacity"] + result["unmet_visits"] == case["daily_visits"]'''],
"Change `case = cases[0]` to another case and rerun. List one measured climate variable, one fictional assumption and one missing service dependency. Download your edited notebook through File → Save and Export Notebook As; browser storage is not a backup.",
"Hazard is not impact. The remaining lessons make each assumption visible. This toy capacity is a count of possible visits in a single invented day, not patients harmed or HIV/TB outcomes.",
"WHO climate and health: https://www.who.int/news-room/fact-sheets/detail/climate-change-and-health ; CDC India: https://www.cdc.gov/global-hiv-tb/php/where-we-work/india.html . These are learning examples, not clinical guidance."),
("01_global_temperature", "A global signal is not local heat exposure", "Read a real global annual temperature anomaly series, check the baseline and compare periods. NASA GISTEMP v4 blends global land and ocean information; the anomaly is relative to 1951–1980. It is neither absolute temperature nor a European regional mean.", [
'''rows = h.read_csv("global-temperature.csv")
years = [int(r["year"]) for r in rows]
anomalies = [float(r["anomaly_c"]) for r in rows]
assert len(years) == len(set(years)) and all(r["data_type"] == "observed" for r in rows)
print("Observed annual coverage:", min(years), "to", max(years))
display(SVG(h.line_svg(years, anomalies, "Observed NASA global temperature anomaly", "Year; anomaly in degrees C, baseline 1951–1980")))''',
'''def period_mean(start, end):
    values = [a for y,a in zip(years, anomalies) if start <= y <= end]
    if len(values) != end-start+1: raise ValueError("Incomplete annual period")
    return statistics.mean(values)
early, recent = period_mean(1951,1980), period_mean(1991,2020)
print(f"1951–1980: {early:.3f} °C; 1991–2020: {recent:.3f} °C; difference: {recent-early:.3f} °C")'''],
"Compare 1981–2010 with 1991–2020. Explain why overlapping periods are not independent samples. Name the local humidity, nighttime heat and occupational-exposure data needed for a heat-health question.",
"A baseline changes the zero, not the underlying warming difference. The annual global mean cannot identify heatwaves in Mumbai, Beira or Lagos. The snapshot is fixed at its acquisition date, and incomplete annual rows were excluded.",
"GISTEMP Team (2026), https://data.giss.nasa.gov/gistemp/ ; Lenssen et al. (2024), https://doi.org/10.1029/2023JD040179 . See data/provenance.json for retrieval date and raw SHA-256. Observational uncertainty is not represented by this one-series plot."),
("02_climate_data_literacy", "Units, area weights and model ensembles", "Use a small fictional grid to practice Kelvin conversion, approximate latitude weighting and ensemble summaries. Equal longitude/latitude cells have unequal areas. A scenario is a conditional pathway; different climate models are not interchangeable with different scenarios.", [
'''kelvin = [300.15, 293.15, 281.15]
latitudes = [0, 30, 60]
celsius = [h.kelvin_to_celsius(k) for k in kelvin]
plain, weighted = statistics.mean(celsius), h.area_mean(celsius,latitudes)
print("Synthetic grid °C:", celsius)
print(f"Unweighted {plain:.3f}; cosine-latitude weighted {weighted:.3f}")''',
'''members = [21, 26, 31, 38, 44]  # fictional annual days above 35 °C, same cell/pathway/year
summary = {f"q{int(q*100)}": h.quantile(members,q) for q in [0.1,0.5,0.9]}
print("Member values:", members, "ensemble:", summary)
print("One selected member:", members[0], "is not the ensemble median", summary["q50"])
assert summary["q10"] <= summary["q50"] <= summary["q90"]''',
'''complete_months = [0,0,2,5,9,12,10,7,3,1,0,0]
print("Synthetic annual count for 2025:", h.annual_hot_days(complete_months, year=2025))
try: h.annual_hot_days(complete_months[:-1] + [None], year=2025)
except ValueError as error: print("Missingness check:", error)'''],
"Replace one ensemble value with 90. Compare changes to the median and 90th percentile. Explain why these five equally weighted models do not make the interval a calibrated probability forecast. Keep identical member/scenario/year choices in any map and facility table.",
"This grid only illustrates arithmetic. Real model processing also requires calendars, cell bounds, masks, units, daily/monthly definitions and weighting decisions. SSP labels describe socioeconomic pathways and RCP labels radiative forcing pathways; do not equate them.",
"Original NB02B inspired the grid/ensemble lab. IPCC AR6: https://www.ipcc.ch/report/ar6/wg1/ . Quantiles use linear interpolation at (n−1)q. All values here are synthetic."),
("03_daily_heat", "Daily heat: counts, runs and nighttime exposure", "Calculate daily extremes with correct definitions: TXx=max(Tmax), TNn=min(Tmin), TXn=min(Tmax), TNx=max(Tmin). Count days above a chosen threshold separately from the longest consecutive run. A temperature threshold is not a mortality threshold.", [
'''daily = [r for r in h.read_csv("daily-heat.csv") if r["case_id"] == "mumbai"]
tmax, tmin = [float(r["tmax_c"]) for r in daily], [float(r["tmin_c"]) for r in daily]
print(h.heat_indices(tmax,tmin,threshold=35))
display(SVG(h.line_svg(list(range(1,366)), tmax, "Synthetic Mumbai-context daily Tmax", "Day of synthetic 2025; degrees C")))''',
'''a, b = [36,36,34,34,36,36], [36,36,36,36,34,34]
print("Same hot-day count:", sum(x>35 for x in a), sum(x>35 for x in b))
print("Different longest runs:", h.longest_run(a,35), h.longest_run(b,35))
print("Season-year keys:", h.season_key("2024-12-15"), h.season_key("2025-01-15"))
assert h.season_key("2024-12-15") == h.season_key("2025-01-15")'''],
"Calculate results at 34 and 36 °C. Repeat for Durban. Compare nighttime minima and daytime maxima. Explain why monthly hot-day counts alone cannot reconstruct a daily sequence. Use DJF/MAM/JJA/SON rather than globally labeling DJF winter.",
"The same number of hot days can occur as isolated days or persistent runs. Humidity, work intensity, housing, acclimatization and health conditions affect exposure; none is captured by these invented daily temperatures.",
"WHO heat and health: https://www.who.int/news-room/fact-sheets/detail/climate-change-heat-and-health . Original NB01/NB02/NB02B activities adapted with deterministic daily data; no observed local heat claims."),
("04_urban_cooling", "Shade, albedo and the urban environment", "Separate a surface energy calculation from personal heat exposure. Shade, vegetation, ventilation and reflective roofs can change energy exchange and access to cooler spaces. Equitable access, water needs and maintenance matter.", [
'''sunlight_w_m2 = 700
albedos = {"dark roof":0.15, "reflective roof":0.65}
absorbed = {name:(1-a)*sunlight_w_m2 for name,a in albedos.items()}
print("Synthetic absorbed shortwave flux W/m²:", absorbed)
print("Flux reduction W/m²:", absorbed["dark roof"]-absorbed["reflective roof"])''',
'''mumbai = next(c for c in cases if c["id"]=="mumbai")
for package in ["baseline","shade","sponge"]:
    s = h.scenario(mumbai,heat_delta=2,adaptation=package)
    print(package, "indoor °C",s["indoor_c"],"capacity",s["capacity"],"assumed cost units",s["cost_units"])'''],
"Change albedo to 0.45 and sunlight to 500 W/m². Explain why the flux difference cannot directly predict air temperature. In the scenario explorer, compare shade with water harvesting and record the limiting service dependency.",
"Cooling in the service model is an explicit invented temperature offset, not a result derived from the roof flux calculation. Trees may offer shade and co-benefits but require suitable species, space, establishment time and maintenance. A cooler roof does not guarantee safe indoor conditions.",
"WHO climate-resilient facilities (2020): https://www.who.int/publications/i/item/9789240012226 ; IUCN nature-based solutions: https://iucn.org/our-work/nature-based-solutions . NB01 Singapore/albedo and NB04 green-infrastructure ideas are reworked here."),
("05_coastal_access", "Coastal water levels and a dry but isolated clinic", "Use an invented common vertical datum to compare a road threshold with a water plane. Annual mean sea level (MSL), mean higher high water (MHHW), highest astronomical tide (HAT), storm surge and long-term sea-level change are different quantities.", [
'''beira = next(c for c in cases if c["id"]=="beira")
for water in [0.2,0.55,0.8,1.4]:
    s=h.scenario(beira,water_m=water)
    print("Water m:",water,"road open:",s["access_open"],"floor above water:",beira["floor_m"]>water,"toy visits:",s["capacity"])''',
'''water = 0.6
uncertainty_m = 0.2
for road in [beira["road_m"]-uncertainty_m, beira["road_m"], beira["road_m"]+uncertainty_m]:
    print("Assumed road elevation:",round(road,2),"water below road:",water<road)
print("With engineered access:", h.scenario(beira,water_m=water,adaptation="engineering"))'''],
"Find a water level where the fictional clinic floor is above water but the road is closed. Change elevation uncertainty to ±0.4 m. List the data needed to assess a real transport route, including a shared vertical datum and hydrologic connection.",
"The threshold treats equality as closure. It is a conceptual access exercise, not an inundation forecast: no connectivity, tides, waves, drainage, bathymetry or land motion is modeled. A 2025 tidal datum file is not a 2025–2100 sea-level projection. Inland cases ignore marine water in this toy model.",
"Inspired by James L. Tobias and contributors, https://github.com/jltobias/JupyterLite-Sea-Level-Rise ; NASA AR6 projection attribution guidance: https://sealevel.nasa.gov/data/tools/ipcc-ar6-projections-licensing-and-acknowledgements . No NASA SLR projections or original PEPFAR facility data are used."),
("06_service_continuity", "HIV/TB service continuity: dependencies and bottlenecks", "Plan continuity through water, power, transport, storage, staff and referral pathways. This exercise models the ability to deliver visits rather than predicting HIV transmission, TB incidence, adherence, treatment failure or mortality. Maintain infection-prevention and medicine-storage practices using local clinical guidance.", [
'''case = next(c for c in cases if c["id"]=="lusaka")
for adaptation in h.ADAPTATIONS:
    s=h.scenario(case,heat_delta=2.5,adaptation=adaptation)
    print(adaptation, "water fraction",s["water_fraction"],"power fraction",s["power_fraction"],"capacity",s["capacity"])
print("Invented daily demand:",case["daily_visits"])''',
'''inventory_doses, doses_per_day, delay_days = 1800, 120, 18
cover_days = inventory_doses/doses_per_day
gap_doses = max(0,delay_days*doses_per_day-inventory_doses)
print("Stock cover days:",cover_days,"illustrative supply gap doses:",gap_doses)
print("Planning input only; no individual regimen or clinical advice.")'''],
"Increase backup power but leave water unchanged. Explain why the min(water fraction, power fraction) dependency limits improvement. Propose three locally appropriate continuity actions and specify who must validate them. Include patient privacy and accessible transport.",
"The heat penalty is capped at 50%; daily capacity is floored after multiplying the service fractions. Access closure leaves an arbitrary 35% alternative-service fraction. These constants are pedagogical assumptions, not empirical estimates. A visit is not a distinct person.",
"WHO facilities (2020): https://www.who.int/publications/i/item/9789240012226 ; WHO operational framework (2023): https://www.who.int/publications/b/70453 . Original NB03/NB04 HIV/TB and operational-planning themes."),
("07_mobility", "Displacement, migration and continuity across places", "Movement can be an adaptation strategy, a constrained choice or forced displacement. Climate-related hazards interact with livelihoods, housing, policy, security and family networks. Never infer legal status or disease transmission from a flow arrow.", [
'''flows=json.loads((h.DATA/"mobility.json").read_text())
events=sum(r["events"] for r in flows["movements"])
route_people=sum(r["distinct_persons"] for r in flows["movements"])
print("Synthetic movement events:",events,"sum of route-specific people:",route_people)
print("Unique people across routes:",flows["unique_people_across_all_routes"])
assert events >= route_people >= flows["unique_people_across_all_routes"]''',
'''host_baseline_visits, additional_visits, staffed_capacity = 80, 30, 95
total_demand=host_baseline_visits+additional_visits
print("Invented host demand:",total_demand,"capacity:",staffed_capacity,"unmet visits:",max(0,total_demand-staffed_capacity))
print("If hours add capacity for 20 visits:", max(0,total_demand-(staffed_capacity+20)))'''],
"Change return movement events without assuming new people. Explain why IDMC event totals cannot be interpreted as unique persons or people still displaced. Draft a privacy-preserving referral handoff without names, GPS tracks or immigration assumptions.",
"Movement events, people ever displaced and the stock of people currently displaced use different denominators and time windows. 'Climate refugee' does not automatically confer legal status. Service continuity should consider host communities and people unable to move, not only visible migrants.",
"UNHCR: https://www.unhcr.org/what-we-do/build-better-futures/climate-change-and-displacement ; IDMC definitions: https://www.internal-displacement.org/monitoring-tools/data-model/ ; IPCC WGII chapter 7: https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-7/ . Synthetic flows only; no mobility observations copied."),
("08_coral_bleaching", "Coral thermal stress and coastal livelihoods", "Calculate a teaching analogue of NOAA Coral Reef Watch Degree Heating Weeks (DHW). For this exercise, a daily HotSpot is SST minus a specified maximum monthly mean. Only HotSpots ≥1 °C contribute; sum the previous 84 daily values and divide by 7.", [
'''hotspots = [0.5]*28 + [1.0]*28 + [2.0]*28
dhw=h.degree_heating_weeks(hotspots)
print("Synthetic 84-day DHW:",dhw,"°C-weeks")
assert dhw == 12
print("After replacing 28 days at 2 °C with 0.9 °C:",h.degree_heating_weeks(hotspots[:56]+[0.9]*28))''',
'''series=[max(0,0.8+1.0*__import__("math").sin(i/25)) for i in range(140)]
rolling=[h.degree_heating_weeks(series[i-83:i+1]) for i in range(83,len(series))]
display(SVG(h.line_svg(list(range(84,141)),rolling,"Synthetic trailing coral thermal stress","Day; DHW in °C-weeks")))'''],
"Replace 1.0 with 0.99 °C and explain the discontinuity. Why can a high DHW indicate accumulated thermal stress without establishing observed bleaching? Trace a possible reef → fisheries/tourism → household income → food/service-access pathway, identifying evidence needed at each step.",
"This is a method exercise, not a NOAA operational product or reef assessment. Bleaching and recovery depend on species, acclimatization and local pressures. Nature-based coastal protection also depends on ecosystem condition; invented DHW cannot quantify health impacts.",
"NOAA CRW methodology: https://coralreefwatch.noaa.gov/product/5km/methodology.php ; citation guidance: https://coralreefwatch.noaa.gov/satellite/docs/recommendations_crw_citation.php . No NOAA satellite values or figures distributed."),
("09_food_water", "Food and water insecurity: a transparent mass balance", "Track a daily water balance and examine how supply shocks can affect food access and clinic operations. Litres per person in this exercise are arbitrary scenario assumptions, not a humanitarian or clinical standard. Quantity alone does not establish water safety.", [
'''storage=2200
inflows=[900,700,300,0,500,1400,1800]
history=[]
for day,inflow in enumerate(inflows,1):
    result=h.water_balance(storage,inflow,people=100,litres_per_person=20)
    storage=result["remaining_l"]
    history.append(result)
    print(day,result)
print("Total deficit L:",sum(r["deficit_l"] for r in history))''',
'''weekly_income, food_share = 100, 0.55
base_food_cost=weekly_income*food_share
for price_multiplier in [1,1.2,1.5]:
    food_cost=base_food_cost*price_multiplier
    print("Synthetic price multiplier:",price_multiplier,"remaining budget:",weekly_income-food_cost)'''],
"Add 1600 L initial harvested water and recompute the seven days. Describe contamination controls and dry-season limitations. Change income alongside prices and identify which household decisions this budget exercise cannot capture.",
"Storage never becomes negative; deficits are reported separately rather than silently becoming debt. Crop failure, market access, affordability, dietary quality and care responsibilities are distinct mechanisms. No disease case counts follow from this balance.",
"WHO climate and health: https://www.who.int/news-room/fact-sheets/detail/climate-change-and-health ; IPCC Africa: https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-9/ . Original synthetic mass-balance and budget examples."),
("10_compound_hazards", "Compound hazards without a conflict prediction score", "Explore a service dependency graph when heat, smoke, storms, flooding or insecurity disrupt operations. Air pollution can affect respiratory health, but this lab does not estimate TB incidence or infer HIV progression. Conflict depends on social, political and economic context; climate is not a deterministic cause.", [
'''services={"routine visits":{"staff","power","water","road"}, "remote follow-up":{"staff","power","telecom"}, "sample transport":{"staff","road","cold-chain"}}
events={"heat + outage":{"power"},"cyclone + route closure":{"road","telecom"},"security interruption":{"road","staff"}}
for event, failed in events.items():
    available=[service for service,deps in services.items() if not deps.intersection(failed)]
    print(event, "fully available services:",available or "none under strict assumptions")''',
'''failed={"power","road"}
restored={"power"}
before=sum(not deps.intersection(failed) for deps in services.values())
after=sum(not deps.intersection(failed-restored) for deps in services.values())
print("Available before/after power restoration:",before,after)
print("No probabilities, conflict scores or disease forecasts assigned.")'''],
"Add an oxygen-dependent service or safe medicine-storage dependency and justify it with local experts. Model a common-cause failure that affects power and telecom together. Explain why multiplying independent failure probabilities would be inappropriate without evidence.",
"The graph uses strict all-or-nothing dependencies and omits partial service, redundancy and time to recovery. It supports discussion and incident planning, not prediction or country risk ranking. The absence of a service in the available list means only that the toy assumptions mark a dependency failed.",
"WHO operational framework: https://www.who.int/publications/b/70453 ; IPCC health, wellbeing and changing community structure: https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-7/ . Extends original NBXX air-pollution and disaster outlines."),
("11_adaptation", "Adaptation portfolios, equity and maladaptation", "Compare invented packages on transparent capacity and cost assumptions. Include nature-based measures such as appropriate shade, rainwater capture, wetland/mangrove restoration and seagrass protection alongside drainage, raised routes, reliable power and heat-safe design. Ecosystem measures are place-specific and should not be assigned universal protection factors.", [
'''case=next(c for c in cases if c["id"]=="beira")
results=[h.scenario(case,heat_delta=2,water_m=0.8,adaptation=a) for a in h.ADAPTATIONS]
baseline=results[0]["capacity"]
for result in results:
    gain=result["capacity"]-baseline
    ratio=gain/result["cost_units"] if result["cost_units"] else None
    print(result["adaptation"],"capacity",result["capacity"],"gain",gain,"gain/cost",ratio)''',
'''budget=5
feasible=[r for r in results if r["cost_units"]<=budget]
best=max(feasible,key=lambda r:r["capacity"])
print("Highest toy capacity within budget:",best["adaptation"])
print("Repeat when route water is lower:")
for adaptation in h.ADAPTATIONS:
    print(adaptation,h.scenario(case,heat_delta=2,water_m=0.2,adaptation=adaptation)["capacity"])''',
'''# Original sponge-city arithmetic: a fictional event volume, not a hydrologic forecast.
rain_mm, area_m2 = 40, 10000
def event_runoff(impervious_fraction):
    impervious_fraction=h.finite(impervious_fraction,0,1)
    coefficient=0.9*impervious_fraction+0.2*(1-impervious_fraction)
    return rain_mm/1000*area_m2*coefficient
before,after=event_runoff(0.8),event_runoff(0.5)
print("Invented runoff m³ before/after permeable-area change:",before,after)
print("Difference m³:",before-after,"(not guaranteed capture or safe water)")
print("Missing: soil infiltration, saturation, drainage connectivity, storm duration, maintenance and water quality.")'''],
"Change the budget and water level. Does the favored package change? Write an equity constraint (such as accessible transport for low-income neighborhoods) that this score omits. Give a maladaptation example: a wall shifting water to neighbors, cooling increasing energy dependence, or planting unsuitable high-water-demand trees.",
"Cost units are arbitrary and cannot support procurement. The explorer compares designs for one fictional facility; it never ranks country risk. Maintenance, participation, habitat, tenure, time horizon and distribution of benefits can change a decision. More capacity alone is not an adequate public-health objective.",
"IUCN NbS: https://iucn.org/our-work/nature-based-solutions ; WHO resilient facilities: https://www.who.int/publications/i/item/9789240012226 . NB04 nature-based adaptation and NB05 what-if/maladaptation themes are completed here."),
("12_capstone", "Capstone: tell a defensible climate-health story", "Produce a five-stop briefing: evidence, local context, service dependency, adaptation comparison and uncertainty. Use the web story tour or the bundled JupyterGIS guided story as a starting point. A conceptual scenario is not a validated digital twin.", [
'''case=next(c for c in cases if c["id"]=="mumbai")
selected_package="combined"
before=h.scenario(case,heat_delta=2,water_m=1.0)
after=h.scenario(case,heat_delta=2,water_m=1.0,adaptation=selected_package)
brief={"context":case["city"]+", "+case["country"],"data_type":"synthetic", "assumptions":{"case_inputs":case,"heat_delta_c":2,"water_m":1.0,"adaptation":selected_package,"baseline_package":h.ADAPTATIONS["baseline"],"selected_package":h.ADAPTATIONS[selected_package],"elevation_precision_m":0.001},"before":before,"after":after,"baseline_capacity":before["capacity"],"adapted_capacity":after["capacity"],"capacity_gain":after["capacity"]-before["capacity"],"uncertainty":"Uncalibrated dependencies, arbitrary effects, no hydrology or disease outcomes"}
print(json.dumps(brief,indent=2))''',
'''# A local output only: download it from the Lab file browser to preserve your work.
output=Path("my-climate-health-brief.json")
output.write_text(json.dumps(brief,indent=2),encoding="utf-8")
print("Saved",output,"in this notebook folder; no data sent to a server.")
rubric={"label evidence vs scenario":2,"show units and datum":2,"verify calculations":2,"consider equity and uncertainty":2,"cite sources and licensing":2}
print("Self-assessment rubric:",rubric,"possible points:",sum(rubric.values()))'''],
"Choose India or an African context, run two adaptations and prepare a 200-word briefing. Include a map/table caption, a quantitative comparison, a missing-data request and a community-engagement question. Use the rubric to exchange peer feedback; this course offers no official or accredited certificate.",
"Worked check: capacity cannot exceed invented demand; increasing a beneficial package cannot reduce capacity under these specific assumptions. That is a property of this model, not proof that an intervention works. Preserve uncertainty and provenance in every exported story.",
"Course references are in the Book reference desk. Story authoring: https://jupytergis.readthedocs.io/en/latest/user_guide/how-tos/story-maps.html . Original NB06 reflection and quiz ideas adapted as formative self-assessment."),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug,title,context,code,exercise,interpretation,source in LESSONS:
        cells=[nbf.v4.new_markdown_cell(f"# {title}\n\n**Climate & Health · Lesson {slug[:2]} · 20–35 minutes**\n\n[Run this lesson in Python Lab](https://jltobias.github.io/JupyterLite-Climate-and-Health/lite/lab/index.html?path=notebooks/{slug}.ipynb)\n\n{context}\n\n**Learning goal:** Run the analysis, explain its units and assumptions, then adapt the exercise.\n\nData labels: **observed NASA** appears in lesson 01. Fictional facility scenarios, local temperatures, costs, flows and modeled impacts are **synthetic teaching data**. The separate **archived Healthsites / OpenStreetMap points** are actual public map records with unverified current services; no synthetic impacts or funding claims apply to them."),nbf.v4.new_code_cell(BOOT)]
        for i,block in enumerate(code):
            cells += [nbf.v4.new_markdown_cell(f"## Analysis {i+1}\n\nRun this cell, then inspect the units and result before continuing."),nbf.v4.new_code_cell(block)]
        cells += [nbf.v4.new_markdown_cell(f"## Interpretation\n\n{interpretation}\n\n## Your exercise\n\n{exercise}\n\n## Worked reasoning check\n\nBefore trusting a changed result, identify the input you changed, predict the direction, and compare with the printed baseline. Explain any threshold or missing-data behavior; a valid calculation alone does not validate a real-world claim.\n\n## Source and limitation\n\n{source}\n\nOriginal educational text: CC BY 4.0, James L. Tobias and contributors. Original synthetic fixtures: CC0. Original calculation code: MIT.")]
        nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"display_name":"Python (Pyodide)","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.13"},"license":"CC-BY-4.0"})
        nbf.write(nb,OUT/(slug+".ipynb"))
    print(f"Authored {len(LESSONS)} lessons")


if __name__=="__main__": main()
