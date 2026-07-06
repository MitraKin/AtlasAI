"""Policy Agent — checks equity, bias, and generates explanations."""

import time
import logging

from app.agents.tools.policy_tools import generate_explanation, check_equity, check_bias, cite_sources

logger = logging.getLogger(__name__)

STRATEGY_PERCENTAGES = {
    "balanced": 0.15,
    "safety_first": 0.25,
    "cost_optimized": 0.10,
    "equity_focused": 0.20,
}


def run_policy_agent(reasoning_result: dict, budget: float | None, strategy: str) -> dict:
    start = time.time()
    rankings = reasoning_result.get("rankings", [])
    weights = reasoning_result.get("artifacts", {}).get("weights_used", {})

    total_budget = budget or 5_000_000
    zone_count = len(rankings)
    pct = STRATEGY_PERCENTAGES.get(strategy, 0.15)

    for r in rankings:
        r["suggested_budget_allocation"] = round(total_budget * pct)

    bias_flags = check_bias(weights)

    top_zones = rankings[:3] if rankings else []
    equity_flags = check_equity(top_zones, zone_count, total_budget)
    all_flags = bias_flags + equity_flags

    for i, r in enumerate(rankings):
        zone_name = r.get("zone_name", r["zone_id"])
        r["justification"] = generate_explanation(
            {"zone_id": r["zone_id"], "zone_name": zone_name, "scores": r.get("scores", {})},
            strategy,
        )
        r["data_citations"] = cite_sources(r["zone_id"])
        r["bias_flags"] = all_flags if i < 3 else []

    detail_parts = []
    if equity_flags:
        detail_parts.append("Equity concern: " + "; ".join(equity_flags))
    if bias_flags:
        detail_parts.append("Bias note: " + "; ".join(bias_flags))
    if not detail_parts:
        detail_parts.append("Equity check passed. No bias flags raised.")
    detail_parts.append(f"Generated justifications for {len(rankings)} zones.")

    duration_ms = int((time.time() - start) * 1000)

    return {
        "agent": "policy_agent",
        "step": "Checking equity, bias, and generating explanations",
        "detail": " ".join(detail_parts),
        "artifacts": {
            "equity_flags": equity_flags,
            "bias_flags": bias_flags,
            "top_zones_checked": len(top_zones),
        },
        "duration_ms": duration_ms,
        "rankings": rankings,
    }
