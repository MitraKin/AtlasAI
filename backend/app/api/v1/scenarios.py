"""Scenarios endpoint — what-if weight adjustments."""

from fastapi import APIRouter, Depends

from app.api.schemas.recommendation import ScenarioRequest, RecommendResponse, ZoneRecommendation, ScoreBreakdown, ResponseMetadata
from app.api.schemas.common import Strategy
from app.services.scoring import compute_zone_scores
from app.repositories.data_repository import DataRepository
from app.agents.tools.policy_tools import generate_explanation, cite_sources
from app.dependencies import get_repo

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("", response_model=RecommendResponse)
async def run_scenario(req: ScenarioRequest, repo: DataRepository = Depends(get_repo)):
    complaints = repo.get_complaint_stats()
    traffic = repo.get_traffic_stats()
    budget = repo.get_budget_stats()
    demog = repo.get_demographics()

    t_lookup = {t["zone_id"]: t for t in traffic}
    b_lookup = {b["zone_id"]: b for b in budget}
    d_lookup = {d["zone_id"]: d for d in demog}

    zone_data = []
    name_map = repo.get_zone_name_map()
    for c in complaints:
        zid = c["zone_id"]
        zone_data.append({
            "zone_id": zid,
            "zone_name": name_map.get(zid, zid),
            "total_complaints": c["total_complaints"],
            "avg_severity": c["avg_severity"] or 0,
            "total_incidents": t_lookup.get(zid, {}).get("total_incidents", 0),
            "pct_spent": b_lookup.get(zid, {}).get("pct_spent", 50),
            "population": d_lookup.get(zid, {}).get("population", 0),
            "forecast_trend": 0,
            "equity_need": 80 if d_lookup.get(zid, {}).get("poverty_rate", 0) > 0.20 else 50,
        })

    rankings = compute_zone_scores(zone_data, req.weights)

    for r in rankings:
        r["justification"] = generate_explanation(r, "custom")
        r["data_citations"] = cite_sources(r["zone_id"])
        r["bias_flags"] = []
        r["suggested_budget_allocation"] = 750000

    recommendations = []
    for i, r in enumerate(rankings[:req.max_results]):
        scores = r.get("scores", {})
        recommendations.append(ZoneRecommendation(
            rank=i + 1,
            zone_id=r["zone_id"],
            zone_name=r.get("zone_name", r["zone_id"]),
            composite_score=min(100.0, max(0.0, round(float(r["composite_score"]), 1))),
            confidence=r["confidence"],
            suggested_budget_allocation=r["suggested_budget_allocation"],
            justification=r["justification"],
            scores=ScoreBreakdown(**scores),
            bias_flags=[],
            data_citations=r.get("data_citations", []),
        ))

    return RecommendResponse(
        recommendations=recommendations,
        reasoning_trace=[],
        metadata=ResponseMetadata(
            total_duration_ms=50,
            zones_analyzed=len(recommendations),
            strategy=Strategy.CUSTOM,
        ),
    )
