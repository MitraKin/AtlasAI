"""Integration tests for the Policy Agent."""

from app.agents.policy_agent import run_policy_agent
from app.services.scoring import WEIGHT_PROFILES


SAMPLE_REASONING = {
    "agent": "reasoning_agent",
    "rankings": [
        {"rank": 1, "zone_id": "Z01", "zone_name": "Zone One", "composite_score": 85.0, "confidence": 0.92,
         "scores": {"complaint_volume": 90, "severity_index": 85, "accident_rate": 80, "cost_efficiency": 70, "population_impact": 60, "forecast_trend": 50, "equity_factor": 40}},
        {"rank": 2, "zone_id": "Z02", "zone_name": "Zone Two", "composite_score": 65.0, "confidence": 0.88,
         "scores": {"complaint_volume": 50, "severity_index": 60, "accident_rate": 40, "cost_efficiency": 80, "population_impact": 30, "forecast_trend": 60, "equity_factor": 70}},
        {"rank": 3, "zone_id": "Z03", "zone_name": "Zone Three", "composite_score": 45.0, "confidence": 0.75,
         "scores": {"complaint_volume": 30, "severity_index": 20, "accident_rate": 30, "cost_efficiency": 50, "population_impact": 40, "forecast_trend": 20, "equity_factor": 80}},
    ],
    "artifacts": {"weights_used": WEIGHT_PROFILES["balanced"]},
    "duration_ms": 5,
}


class TestRunPolicyAgent:
    def test_generates_justifications(self):
        result = run_policy_agent(SAMPLE_REASONING, 5000000, "balanced")
        for r in result["rankings"]:
            assert "justification" in r
            assert len(r["justification"]) > 0

    def test_generates_citations(self):
        result = run_policy_agent(SAMPLE_REASONING, 5000000, "balanced")
        for r in result["rankings"]:
            assert "data_citations" in r
            assert len(r["data_citations"]) == 4

    def test_allocates_budget(self):
        result = run_policy_agent(SAMPLE_REASONING, 10000000, "balanced")
        for r in result["rankings"]:
            assert "suggested_budget_allocation" in r
            assert r["suggested_budget_allocation"] > 0

    def test_bias_flags_on_balanced_strategy(self):
        result = run_policy_agent(SAMPLE_REASONING, 5000000, "balanced")
        top = result["rankings"][0]
        assert isinstance(top["bias_flags"], list)

    def test_equity_checks(self):
        result = run_policy_agent(SAMPLE_REASONING, 100000000, "balanced")
        assert "Equity check" in result["detail"] or "Bias note" in result["detail"] or "passed" in result["detail"]

    def test_returns_agent_name(self):
        result = run_policy_agent(SAMPLE_REASONING, 5000000, "balanced")
        assert result["agent"] == "policy_agent"

    def test_preserves_rankings_length(self):
        result = run_policy_agent(SAMPLE_REASONING, 5000000, "balanced")
        assert len(result["rankings"]) == 3
