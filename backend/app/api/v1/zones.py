"""Zones endpoints — list and detail."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.zone import ZoneSummary, ZoneDetail
from app.repositories.data_repository import DataRepository
from app.dependencies import get_repo

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=list[ZoneSummary])
async def list_zones(repo: DataRepository = Depends(get_repo)):
    zones = repo.get_zone_list()
    complaints = repo.get_complaint_stats()
    comp_lookup = {c["zone_id"]: c for c in complaints}

    results = []
    for z in zones:
        c = comp_lookup.get(z["zone_id"], {})
        results.append(ZoneSummary(
            zone_id=z["zone_id"],
            zone_name=z["zone_name"],
            population=z["population"],
            area_sqkm=z["area_sqkm"],
            median_income=z["median_income"],
            complaint_count=c.get("total_complaints", 0),
            avg_severity=round(c.get("avg_severity", 0) or 0, 2),
        ))
    return results


@router.get("/{zone_id}", response_model=ZoneDetail)
async def get_zone(zone_id: str, repo: DataRepository = Depends(get_repo)):
    zone = repo.get_zone_detail(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

    complaints = repo.get_complaint_stats(zone_id)
    comp_stats = complaints[0] if complaints else {}

    budget_raw = repo.get_budget_stats(zone_id)
    budget_history = [
        {"zone_id": b["zone_id"], "total_allocated": b["total_allocated"],
         "total_spent": b["total_spent"], "pct_spent": b.get("pct_spent"),
         "avg_completion_rate": b.get("avg_completion_rate")}
        for b in budget_raw
    ]

    infra = repo.get_infrastructure(zone_id)
    infra_list = [
        {"asset_type": i["asset_type"], "avg_age_years": i["avg_age_years"],
         "condition_score": i["condition_score"], "pct_past_lifecycle": i["pct_past_lifecycle"]}
        for i in infra
    ]

    demo = repo.get_demographics(zone_id)
    demog = demo[0] if demo else {}

    return ZoneDetail(
        zone_id=zone["zone_id"],
        zone_name=zone["zone_name"],
        population=zone["population"],
        area_sqkm=zone["area_sqkm"],
        median_income=zone["median_income"],
        population_density=zone["population_density"],
        poverty_rate=demog.get("poverty_rate", 0),
        complaint_stats={
            "total_complaints": comp_stats.get("total_complaints", 0),
            "avg_severity": round(comp_stats.get("avg_severity", 0) or 0, 2),
            "pct_critical": round(comp_stats.get("pct_critical", 0) or 0, 1),
            "open_backlog": comp_stats.get("open_backlog", 0),
        },
        budget_history=budget_history,
        infrastructure=infra_list,
    )
