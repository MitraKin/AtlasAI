"""Recommendations endpoint — POST /api/v1/recommend."""

import uuid
from fastapi import APIRouter, Depends

from app.api.schemas.recommendation import (
    RecommendRequest,
    RecommendResponse,
    ZoneRecommendation,
    ReasoningStep,
    ScoreBreakdown,
    ResponseMetadata,
)
from app.api.schemas.common import Strategy
from app.services.recommendation import RecommendationService
from app.dependencies import get_recommendation_service

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("", response_model=RecommendResponse)
async def recommend(
    req: RecommendRequest,
    svc: RecommendationService = Depends(get_recommendation_service),
):
    result = svc.get_recommendations(req.question, req.strategy.value)

    recommendations = []
    for r in result["recommendations"][: req.max_results]:
        scores = r.get("scores", {})
        recommendations.append(
            ZoneRecommendation(
                rank=r["rank"],
                zone_id=r["zone_id"],
                zone_name=r.get("zone_name", r["zone_id"]),
                composite_score=min(100.0, max(0.0, round(float(r["composite_score"]), 1))),
                confidence=r["confidence"],
                suggested_budget_allocation=r.get("suggested_budget_allocation", 0),
                justification=r.get("justification", ""),
                scores=ScoreBreakdown(**scores) if scores else ScoreBreakdown(
                    complaint_volume=0, severity_index=0, accident_rate=0,
                    cost_efficiency=0, population_impact=0, forecast_trend=0, equity_factor=0,
                ),
                bias_flags=r.get("bias_flags", []),
                data_citations=r.get("data_citations", []),
            )
        )

    trace = []
    for s in result["reasoning_trace"]:
        trace.append(ReasoningStep(
            agent=s["agent"],
            step=s["step"],
            detail=s["detail"],
            artifacts=s.get("artifacts"),
            duration_ms=s["duration_ms"],
        ))

    return RecommendResponse(
        recommendations=recommendations,
        reasoning_trace=trace,
        metadata=ResponseMetadata(
            total_duration_ms=result["total_duration_ms"],
            zones_analyzed=result["zones_analyzed"],
            strategy=req.strategy,
        ),
    )
