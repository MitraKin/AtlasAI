"""Reasoning Agent — applies multi-criteria scoring to rank zones."""

import time
import logging

from app.services.scoring import WEIGHT_PROFILES, compute_zone_scores

logger = logging.getLogger(__name__)


def run_reasoning_agent(data_result: dict, strategy: str = "balanced") -> dict:
    start = time.time()
    zone_data = data_result.get("data", [])
    weights = WEIGHT_PROFILES.get(strategy, WEIGHT_PROFILES["balanced"])

    if not zone_data:
        return {
            "agent": "reasoning_agent",
            "step": "Applying multi-criteria scoring",
            "detail": "No zone data available to score.",
            "artifacts": None,
            "duration_ms": 0,
            "rankings": [],
        }

    rankings = compute_zone_scores(zone_data, weights)

    top = rankings[0] if rankings else None
    detail_parts = []
    if top:
        detail_parts.append(
            f"Top zone: {top['zone_id']} with composite score {top['composite_score']}/100. "
        )
    detail_parts.append(
        f"Weighted {len(weights)} factors: "
        + ", ".join(f"{k}={v:.0%}" for k, v in sorted(weights.items(), key=lambda x: -x[1])[:4])
        + "."
    )
    detail_parts.append(
        f"Ranked {len(rankings)} zones using {strategy.replace('_', ' ')} strategy."
    )

    duration_ms = int((time.time() - start) * 1000)

    return {
        "agent": "reasoning_agent",
        "step": "Ranking zones with multi-criteria analysis",
        "detail": " ".join(detail_parts),
        "artifacts": {
            "weights_used": weights,
            "strategy": strategy,
            "top_zone_id": top["zone_id"] if top else None,
            "top_score": top["composite_score"] if top else None,
        },
        "duration_ms": duration_ms,
        "rankings": rankings,
    }
