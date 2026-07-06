"""Agent tools — functions callable by the agent pipeline."""


def generate_explanation(zone: dict, strategy: str) -> str:
    scores = zone.get("scores", {})
    top_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
    factor_names = [f[0].replace("_", " ") for f in top_factors]
    name = zone.get("zone_name", zone.get("zone_id", "Unknown"))
    return f"{name} ranks high due to strong {factor_names[0]} and {factor_names[1]} metrics"


def check_equity(top_zones: list[dict], total_zones: int, total_budget: float) -> list[str]:
    flags = []
    if total_zones >= 4:
        top3_budget = sum(z.get("suggested_budget_allocation", 0) for z in top_zones[:3])
        if total_budget > 0 and (top3_budget / total_budget) > 0.70:
            flags.append("Top 3 zones receive over 70% of budget — consider broader distribution")
    return flags


def check_bias(weights: dict) -> list[str]:
    flags = []
    safety = weights.get("severity_index", 0) + weights.get("accident_rate", 0)
    convenience = weights.get("complaint_volume", 0) + weights.get("cost_efficiency", 0)
    if safety > convenience * 1.5:
        flags.append(f"Safety weighted {safety/convenience:.1f}x over convenience — adjustable via strategy")
    if weights.get("equity_factor", 0) < 0.08:
        flags.append("Equity factor is low — consider increasing for underserved zone support")
    return flags


def cite_sources(zone_id: str) -> list[str]:
    return [
        f"civic_raw.complaints_311 (zone {zone_id})",
        f"civic_raw.traffic_incidents (zone {zone_id})",
        f"civic_raw.budget_historical (zone {zone_id})",
        f"civic_features.zone_complaint_density (zone {zone_id})",
    ]
