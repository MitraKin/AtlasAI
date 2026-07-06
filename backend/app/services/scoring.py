"""Multi-criteria scoring engine for CityPulse.

Weighs 7 factors: complaint volume, severity, accident rate,
cost efficiency, population impact, forecast trend, equity.
"""

WEIGHT_PROFILES = {
    "balanced": {
        "complaint_volume": 0.20,
        "severity_index": 0.25,
        "accident_rate": 0.20,
        "cost_efficiency": 0.10,
        "population_impact": 0.10,
        "forecast_trend": 0.10,
        "equity_factor": 0.05,
    },
    "safety_first": {
        "complaint_volume": 0.10,
        "severity_index": 0.30,
        "accident_rate": 0.30,
        "cost_efficiency": 0.05,
        "population_impact": 0.10,
        "forecast_trend": 0.10,
        "equity_factor": 0.05,
    },
    "cost_optimized": {
        "complaint_volume": 0.15,
        "severity_index": 0.15,
        "accident_rate": 0.15,
        "cost_efficiency": 0.30,
        "population_impact": 0.10,
        "forecast_trend": 0.10,
        "equity_factor": 0.05,
    },
    "equity_focused": {
        "complaint_volume": 0.15,
        "severity_index": 0.20,
        "accident_rate": 0.15,
        "cost_efficiency": 0.10,
        "population_impact": 0.15,
        "forecast_trend": 0.10,
        "equity_factor": 0.15,
    },
}


def normalize(values: list[float], invert: bool = False) -> list[float]:
    safe = [v if v is not None else 0 for v in values]
    if not safe or max(safe) == min(safe):
        return [50.0] * len(safe)
    mn, mx = min(safe), max(safe)
    normalized = [(v - mn) / (mx - mn) * 100 for v in safe]
    if invert:
        normalized = [100 - v for v in normalized]
    return [round(v, 1) for v in normalized]


def compute_zone_scores(
    zone_data: list[dict],
    weights: dict[str, float],
) -> list[dict]:
    if not zone_data:
        return []

    zids = [z["zone_id"] for z in zone_data]

    raw_complaints = [z.get("total_complaints", 0) for z in zone_data]
    raw_severity = [z.get("avg_severity", 0) for z in zone_data]
    raw_accidents = [z.get("total_incidents", 0) for z in zone_data]
    raw_cost_eff = [z.get("pct_spent", 100) or 100 for z in zone_data]
    raw_pop = [z.get("population", 0) for z in zone_data]
    raw_forecast = [z.get("forecast_trend", 0) for z in zone_data]
    raw_equity = [z.get("equity_need", 50) for z in zone_data]

    norm_complaints = normalize(raw_complaints)
    norm_severity = normalize(raw_severity)
    norm_accidents = normalize(raw_accidents)
    norm_cost_eff = normalize(raw_cost_eff, invert=True)
    norm_pop = normalize(raw_pop)
    norm_forecast = normalize(raw_forecast)
    norm_equity = normalize(raw_equity)

    results = []
    for i, zid in enumerate(zids):
        factor_scores = {
            "complaint_volume": norm_complaints[i],
            "severity_index": norm_severity[i],
            "accident_rate": norm_accidents[i],
            "cost_efficiency": norm_cost_eff[i],
            "population_impact": norm_pop[i],
            "forecast_trend": norm_forecast[i],
            "equity_factor": norm_equity[i],
        }

        total_weight = sum(weights.get(k, 0) for k in factor_scores)
        if total_weight > 0:
            composite = sum(factor_scores[k] * weights.get(k, 0) for k in factor_scores) / total_weight
        else:
            composite = 0.0
        composite = min(100.0, max(0.0, composite))

        confidence = compute_confidence(zone_data[i])

        results.append({
            "zone_id": zid,
            "zone_name": zone_data[i].get("zone_name", zid),
            "composite_score": round(composite, 1),
            "confidence": round(confidence, 2),
            "scores": factor_scores,
        })

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    for rank, r in enumerate(results, 1):
        r["rank"] = rank

    return results


def compute_confidence(zone: dict) -> float:
    sample_size = zone.get("total_complaints", 0)
    sample_factor = min(1.0, sample_size / 100)

    has_budget = zone.get("pct_spent") is not None
    has_traffic = zone.get("total_incidents") is not None
    data_completeness = sum([1, has_budget, has_traffic]) / 3

    return round(data_completeness * 0.6 + sample_factor * 0.4, 2)
