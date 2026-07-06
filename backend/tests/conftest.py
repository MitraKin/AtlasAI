import pytest
import sqlite3
import tempfile
import json
import csv
from pathlib import Path


@pytest.fixture
def sample_zone_data():
    return [
        {"zone_id": "Z01", "zone_name": "Downtown Core", "total_complaints": 100, "avg_severity": 3.5, "total_incidents": 20, "pct_spent": 85, "population": 50000, "forecast_trend": 5, "equity_need": 50},
        {"zone_id": "Z02", "zone_name": "Suburb", "total_complaints": 50, "avg_severity": 2.0, "total_incidents": 10, "pct_spent": 90, "population": 30000, "forecast_trend": -2, "equity_need": 80},
        {"zone_id": "Z03", "zone_name": "Industrial", "total_complaints": 200, "avg_severity": 4.5, "total_incidents": 30, "pct_spent": 70, "population": 20000, "forecast_trend": 10, "equity_need": 30},
    ]


@pytest.fixture
def sample_weights():
    return {
        "complaint_volume": 0.20,
        "severity_index": 0.25,
        "accident_rate": 0.20,
        "cost_efficiency": 0.10,
        "population_impact": 0.10,
        "forecast_trend": 0.10,
        "equity_factor": 0.05,
    }


@pytest.fixture
def temp_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create minimal CSV files
        complaints = [
            {"complaint_id": "CMP-000001", "created_date": "2025-01-15T10:00:00", "closed_date": "2025-01-20T10:00:00",
             "category": "pothole", "subcategory": "major_road", "status": "closed", "zone_id": "Z01",
             "latitude": 17.4, "longitude": 78.45, "severity": 3, "resolution_days": 5, "description": "pothole"},
            {"complaint_id": "CMP-000002", "created_date": "2025-02-10T10:00:00", "closed_date": "",
             "category": "water", "subcategory": "leak", "status": "open", "zone_id": "Z02",
             "latitude": 17.41, "longitude": 78.46, "severity": 4, "resolution_days": "", "description": "water leak"},
        ]
        with open(tmp / "complaints_311.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(complaints[0].keys()))
            w.writeheader()
            w.writerows(complaints)

        traffic = [
            {"incident_id": "INC-000001", "date": "2025-01-15", "time": "14:00", "zone_id": "Z01",
             "latitude": 17.4, "longitude": 78.45, "severity": 3, "type": "collision",
             "road_type": "highway", "weather_condition": "clear", "injuries": 2, "fatalities": 0},
        ]
        with open(tmp / "traffic_incidents.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(traffic[0].keys()))
            w.writeheader()
            w.writerows(traffic)

        budget = [
            {"fiscal_year": 2024, "quarter": 1, "zone_id": "Z01", "department": "infrastructure",
             "category": "infrastructure", "allocated_amount": 1000000, "spent_amount": 800000,
             "project_count": 5, "completion_rate": 0.8},
        ]
        with open(tmp / "budget_historical.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(budget[0].keys()))
            w.writeheader()
            w.writerows(budget)

        demo = [
            {"zone_id": "Z01", "population": 50000, "population_growth_rate": 0.02, "median_income": 60000,
             "poverty_rate": 0.15, "median_age": 35.0, "households": 16000,
             "vehicle_ownership_pct": 0.7, "education_pct_college": 0.5},
        ]
        with open(tmp / "census_demographics.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(demo[0].keys()))
            w.writeheader()
            w.writerows(demo)

        infra = [
            {"zone_id": "Z01", "asset_type": "road", "avg_age_years": 20, "pct_past_lifecycle": 0.5,
             "last_major_repair": "2023-01-01", "condition_score": 6},
        ]
        with open(tmp / "infrastructure_assets.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(infra[0].keys()))
            w.writeheader()
            w.writerows(infra)

        outages = [
            {"outage_id": "OUT-000001", "date": "2025-01-15", "zone_id": "Z01", "type": "power",
             "duration_hours": 3.0, "affected_residents": 200, "cause": "storm_damage",
             "latitude": 17.4, "longitude": 78.45},
        ]
        with open(tmp / "utility_outages.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(outages[0].keys()))
            w.writeheader()
            w.writerows(outages)

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"zone_id": "Z01", "zone_name": "Downtown Core", "area_sqkm": 12.5, "population": 50000, "median_income": 60000, "population_density": 4000},
                    "geometry": {"type": "Polygon", "coordinates": [[[78.4, 17.3], [78.5, 17.3], [78.5, 17.4], [78.4, 17.4], [78.4, 17.3]]]},
                },
                {
                    "type": "Feature",
                    "properties": {"zone_id": "Z02", "zone_name": "Suburb", "area_sqkm": 18.0, "population": 30000, "median_income": 45000, "population_density": 1667},
                    "geometry": {"type": "Polygon", "coordinates": [[[78.5, 17.3], [78.6, 17.3], [78.6, 17.4], [78.5, 17.4], [78.5, 17.3]]]},
                },
            ],
        }
        with open(tmp / "zone_boundaries.geojson", "w") as f:
            json.dump(geojson, f)

        yield str(tmp)
