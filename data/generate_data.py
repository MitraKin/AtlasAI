"""Synthetic civic data generator for CityPulse.

Generates realistic datasets for 15 zones over 12 months:
- 311 complaints (10,000+ rows)
- Traffic incidents (3,000+ rows)
- Budget records (3 years quarterly)
- Zone boundaries (GeoJSON)
- Census demographics
- Infrastructure assets
"""

import csv
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

HERE = Path(__file__).parent
OUT = HERE / "datasets"
OUT.mkdir(parents=True, exist_ok=True)

# ── Zones ──────────────────────────────────────────────────────────────────
ZONES = [
    {"id": "Z01", "name": "Downtown Core", "area": 12.5, "pop": 85000, "income": 72000, "density": 6800},
    {"id": "Z02", "name": "North Hills", "area": 18.3, "pop": 62000, "income": 55000, "density": 3388},
    {"id": "Z03", "name": "East Junction", "area": 22.1, "pop": 78000, "income": 48000, "density": 3529},
    {"id": "Z04", "name": "South Market", "area": 15.7, "pop": 95000, "income": 41000, "density": 6051},
    {"id": "Z05", "name": "West Gate", "area": 20.4, "pop": 72000, "income": 65000, "density": 3529},
    {"id": "Z06", "name": "Riverside", "area": 14.2, "pop": 58000, "income": 68000, "density": 4085},
    {"id": "Z07", "name": "Old Town", "area": 11.8, "pop": 68000, "income": 39000, "density": 5763},
    {"id": "Z08", "name": "Tech Park", "area": 19.6, "pop": 52000, "income": 105000, "density": 2653},
    {"id": "Z09", "name": "Lakeview", "area": 16.3, "pop": 61000, "income": 59000, "density": 3742},
    {"id": "Z10", "name": "Industrial Zone", "area": 25.8, "pop": 45000, "income": 36000, "density": 1744},
    {"id": "Z11", "name": "Greenfield", "area": 21.5, "pop": 71000, "income": 78000, "density": 3302},
    {"id": "Z12", "name": "Harbour Point", "area": 13.9, "pop": 56000, "income": 62000, "density": 4029},
    {"id": "Z13", "name": "University District", "area": 17.2, "pop": 88000, "income": 44000, "density": 5116},
    {"id": "Z14", "name": "Hilltop", "area": 24.1, "pop": 49000, "income": 92000, "density": 2033},
    {"id": "Z15", "name": "Central Park", "area": 13.5, "pop": 75000, "income": 56000, "density": 5556},
]

ZONE_IDS = [z["id"] for z in ZONES]
ZONE_LOOKUP = {z["id"]: z for z in ZONES}
TOTAL_POP = sum(z["pop"] for z in ZONES)

CATEGORIES = ["pothole", "streetlight", "water", "noise", "trash", "sanitation"]
SUB_CATEGORIES = {
    "pothole": ["major_road", "residential_street", "highway", "alley"],
    "streetlight": ["broken", "flickering", "missing", "pole_damaged"],
    "water": ["main_break", "low_pressure", "discolored", "no_water", "leak"],
    "noise": ["construction", "traffic", "nightlife", "industrial"],
    "trash": ["missed_pickup", "illegal_dumping", "overflow_bin", "hazardous"],
    "sanitation": ["sewer_backup", "drain_clogged", "manhole_overflow", "odor"],
}
TRAFFIC_TYPES = ["collision", "pedestrian", "cyclist", "single_vehicle", "multi_vehicle"]
ROAD_TYPES = ["highway", "arterial", "collector", "local"]
WEATHER = ["clear", "rain", "fog", "storm"]
OUTAGE_TYPES = ["power", "water", "sewer", "gas"]
OUTAGE_CAUSES = ["aging_infra", "storm_damage", "construction", "equipment_failure", "overload"]
ASSET_TYPES = ["road", "water_pipe", "sewer", "bridge", "streetlight"]

# ── Helpers ─────────────────────────────────────────────────────────────────

def date_range(start: str, end: str):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    days = (e - s).days
    return [s + timedelta(days=i) for i in range(days + 1)]

DATES = date_range("2025-01-01", "2025-12-31")
MONTHS = sorted(set(d.strftime("%Y-%m") for d in DATES))

def gauss(mu, sigma):
    return max(0, random.gauss(mu, sigma))

def pick_zone(weighted=True):
    if weighted:
        pops = [z["pop"] for z in ZONES]
        return random.choices(ZONE_IDS, weights=pops, k=1)[0]
    return random.choice(ZONE_IDS)

def seasonal_factor(month: int, category: str) -> float:
    factors = {
        "pothole": {6: 1.5, 7: 1.8, 8: 1.6, 9: 1.4, 12: 0.6, 1: 0.5},
        "streetlight": {12: 1.3, 1: 1.2, 11: 1.1},
        "water": {5: 1.3, 6: 1.2, 3: 0.8},
        "sanitation": {6: 1.4, 7: 1.5, 8: 1.3},
    }
    return factors.get(category, {}).get(month, 1.0)


# ── 1. 311 Complaints ──────────────────────────────────────────────────────

def generate_complaints():
    rows = []
    complaint_id = 1

    for date in DATES:
        base_count = 25 + random.randint(-5, 5)
        m = date.month
        day_of_week = date.weekday()

        for _ in range(base_count):
            cat = random.choice(CATEGORIES)
            zone = pick_zone(weighted=True)

            if zone in ("Z07", "Z03"):
                if random.random() < 0.35:
                    continue

            severity_weights = [0.05, 0.25, 0.35, 0.25, 0.10]
            severity = random.choices([1, 2, 3, 4, 5], weights=severity_weights, k=1)[0]

            if cat == "pothole" and random.random() < 0.2:
                severity = min(5, severity + 1)
            if cat == "sanitation" and random.random() < 0.15:
                severity = min(5, severity + 1)

            created = date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            resolution_days = int(gauss(5, 3)) if severity <= 3 else int(gauss(12, 5))
            closed = created + timedelta(days=min(resolution_days, random.randint(1, 30)))
            if random.random() < 0.08:
                closed = None

            status = "open" if closed is None else "closed"

            z = ZONE_LOOKUP[zone]
            rows.append({
                "complaint_id": f"CMP-{complaint_id:06d}",
                "created_date": created.isoformat(),
                "closed_date": closed.isoformat() if closed else "",
                "category": cat,
                "subcategory": random.choice(SUB_CATEGORIES[cat]),
                "status": status,
                "zone_id": zone,
                "latitude": round(random.uniform(17.3, 17.5), 6),
                "longitude": round(random.uniform(78.4, 78.6), 6),
                "severity": severity,
                "resolution_days": resolution_days if closed else "",
                "description": f"{cat.replace('_',' ')} issue reported near {z['name']}",
            })
            complaint_id += 1

    return rows


# ── 2. Traffic Incidents ───────────────────────────────────────────────────

def generate_traffic():
    rows = []
    inc_id = 1

    for date in DATES:
        n = 7 + random.randint(-2, 3)
        for _ in range(n):
            zone = pick_zone(weighted=True)
            incident_type = random.choice(TRAFFIC_TYPES)
            road = random.choice(ROAD_TYPES)
            weather = random.choices(WEATHER, weights=[0.6, 0.2, 0.1, 0.1], k=1)[0]

            sev_weights = [0.15, 0.30, 0.30, 0.18, 0.07]
            if incident_type == "pedestrian":
                sev_weights = [0.05, 0.15, 0.30, 0.30, 0.20]
            severity = random.choices([1, 2, 3, 4, 5], weights=sev_weights, k=1)[0]

            if zone == "Z03" and random.random() < 0.4:
                severity = min(5, severity + 1)

            injuries = random.randint(0, severity)
            fatalities = 1 if severity == 5 and random.random() < 0.3 else 0

            rows.append({
                "incident_id": f"INC-{inc_id:06d}",
                "date": date.strftime("%Y-%m-%d"),
                "time": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
                "zone_id": zone,
                "latitude": round(random.uniform(17.3, 17.5), 6),
                "longitude": round(random.uniform(78.4, 78.6), 6),
                "severity": severity,
                "type": incident_type,
                "road_type": road,
                "weather_condition": weather,
                "injuries": injuries,
                "fatalities": fatalities,
            })
            inc_id += 1

    return rows


# ── 3. Budget Records ──────────────────────────────────────────────────────

def generate_budget():
    rows = []
    departments = ["infrastructure", "safety", "sanitation", "parks", "education"]
    quarters = [(2022, q) for q in range(1, 5)] + [(2023, q) for q in range(1, 5)] + [(2024, q) for q in range(1, 5)]

    for zone in ZONES:
        base_budget = zone["pop"] * 450 + zone["income"] * 1.2
        for fy, q in quarters:
            for dept in departments:
                allocated = base_budget * random.uniform(0.15, 0.35)
                if dept == "infrastructure":
                    allocated *= 1.4
                if zone in ("Z07", "Z10") and dept in ("infrastructure", "safety"):
                    allocated *= random.uniform(0.6, 0.85)

                spent = allocated * random.uniform(0.70, 1.05)
                projects = max(1, int(allocated / 500000))
                completion = round(random.uniform(0.55, 1.0), 2)

                rows.append({
                    "fiscal_year": fy,
                    "quarter": q,
                    "zone_id": zone["id"],
                    "department": dept,
                    "category": dept,
                    "allocated_amount": round(allocated, 2),
                    "spent_amount": round(spent, 2),
                    "project_count": projects,
                    "completion_rate": completion,
                })

    return rows


# ── 4. Zone Boundaries GeoJSON ─────────────────────────────────────────────

def generate_geojson():
    features = []
    grid_cols = 5
    grid_rows = 3
    lat_start, lon_start = 17.35, 78.42
    lat_step, lon_step = 0.06, 0.04

    for i, zone in enumerate(ZONES):
        row, col = divmod(i, grid_cols)
        lat0 = lat_start + row * lat_step
        lon0 = lon_start + col * lon_step
        lat1 = lat0 + lat_step * 0.9
        lon1 = lon0 + lon_step * 0.9

        polygon = [[
            [lon0, lat0],
            [lon1, lat0],
            [lon1, lat1],
            [lon0, lat1],
            [lon0, lat0],
        ]]

        features.append({
            "type": "Feature",
            "properties": {
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "area_sqkm": zone["area"],
                "population": zone["pop"],
                "median_income": zone["income"],
                "population_density": zone["density"],
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon,
            },
        })

    return {"type": "FeatureCollection", "features": features}


# ── 5. Census Demographics ─────────────────────────────────────────────────

def generate_demographics():
    rows = []
    for zone in ZONES:
        rows.append({
            "zone_id": zone["id"],
            "population": zone["pop"],
            "population_growth_rate": round(random.uniform(-0.02, 0.05), 3),
            "median_income": zone["income"],
            "poverty_rate": round(max(0.02, min(0.35, 0.35 - (zone["income"] - 36000) / 200000)), 2),
            "median_age": round(random.uniform(28, 42), 1),
            "households": zone["pop"] // 3,
            "vehicle_ownership_pct": round(min(0.95, max(0.25, zone["income"] / 120000)), 2),
            "education_pct_college": round(min(0.85, max(0.15, zone["income"] / 110000)), 2),
        })
    return rows


# ── 6. Infrastructure Assets ───────────────────────────────────────────────

def generate_infrastructure():
    rows = []
    for zone in ZONES:
        for asset in ASSET_TYPES:
            age = int(gauss(25, 12))
            if zone["id"] in ("Z07", "Z10"):
                age += random.randint(5, 20)
            condition = max(1, min(10, int(10 - age / 6 + random.gauss(0, 1))))
            past_lifecycle = 1.0 if age > 40 else age / 40

            rows.append({
                "zone_id": zone["id"],
                "asset_type": asset,
                "avg_age_years": age,
                "pct_past_lifecycle": round(min(1.0, past_lifecycle), 2),
                "last_major_repair": (datetime.now() - timedelta(days=random.randint(100, 3000))).strftime("%Y-%m-%d"),
                "condition_score": condition,
            })
    return rows


# ── 7. Utility Outages ─────────────────────────────────────────────────────

def generate_outages():
    rows = []
    oid = 1
    for date in DATES:
        if random.random() < 0.4:
            continue
        n = random.randint(1, 3)
        for _ in range(n):
            zone = pick_zone(weighted=True)
            outage_type = random.choice(OUTAGE_TYPES)
            cause = random.choice(OUTAGE_CAUSES)

            if zone in ("Z07", "Z10") and random.random() < 0.3:
                cause = "aging_infra"

            rows.append({
                "outage_id": f"OUT-{oid:06d}",
                "date": date.strftime("%Y-%m-%d"),
                "zone_id": zone,
                "type": outage_type,
                "duration_hours": round(gauss(4, 3), 1),
                "affected_residents": random.randint(50, max(100, ZONE_LOOKUP[zone]["pop"] // 20)),
                "cause": cause,
                "latitude": round(random.uniform(17.3, 17.5), 6),
                "longitude": round(random.uniform(78.4, 78.6), 6),
            })
            oid += 1
    return rows


# ── Write CSV ───────────────────────────────────────────────────────────────

def write_csv(filename, rows):
    if not rows:
        return
    with open(OUT / filename, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {filename}: {len(rows)} rows")


if __name__ == "__main__":
    print("CityPulse — Synthetic Data Generator\n")

    complaints = generate_complaints()
    write_csv("complaints_311.csv", complaints)

    traffic = generate_traffic()
    write_csv("traffic_incidents.csv", traffic)

    budget = generate_budget()
    write_csv("budget_historical.csv", budget)

    geo = generate_geojson()
    with open(OUT / "zone_boundaries.geojson", "w") as f:
        json.dump(geo, f, indent=2)
    print(f"  ✓ zone_boundaries.geojson: {len(geo['features'])} zones")

    demog = generate_demographics()
    write_csv("census_demographics.csv", demog)

    infra = generate_infrastructure()
    write_csv("infrastructure_assets.csv", infra)

    outages = generate_outages()
    write_csv("utility_outages.csv", outages)

    print(f"\nDone! All datasets in {OUT}/")
