"""Integration tests for the Reasoning Agent."""

from app.agents.reasoning_agent import run_reasoning_agent


SAMPLE_DATA_RESULT = {
    "agent": "data_agent",
    "data": [
        {"zone_id": "Z01", "zone_name": "Zone One", "total_complaints": 100, "avg_severity": 3.5, "total_incidents": 20, "pct_spent": 85, "population": 50000, "forecast_trend": 5, "equity_need": 50},
        {"zone_id": "Z02", "zone_name": "Zone Two", "total_complaints": 50, "avg_severity": 2.0, "total_incidents": 10, "pct_spent": 90, "population": 30000, "forecast_trend": -2, "equity_need": 80},
    ],
    "budget": 5000000,
    "category": "infrastructure",
}


class TestRunReasoningAgent:
    def test_returns_structured_result(self):
        result = run_reasoning_agent(SAMPLE_DATA_RESULT, "balanced")
        assert result["agent"] == "reasoning_agent"
        assert "rankings" in result
        assert len(result["rankings"]) == 2

    def test_rankings_ordered_by_score(self):
        result = run_reasoning_agent(SAMPLE_DATA_RESULT, "balanced")
        rankings = result["rankings"]
        assert rankings[0]["composite_score"] >= rankings[1]["composite_score"]

    def test_rankings_include_rank_field(self):
        result = run_reasoning_agent(SAMPLE_DATA_RESULT, "balanced")
        assert result["rankings"][0]["rank"] == 1
        assert result["rankings"][1]["rank"] == 2

    def test_different_strategies_produce_valid_rankings(self):
        balanced = run_reasoning_agent(SAMPLE_DATA_RESULT, "balanced")
        safety = run_reasoning_agent(SAMPLE_DATA_RESULT, "safety_first")

        assert len(balanced["rankings"]) == len(safety["rankings"])
        assert len(balanced["rankings"]) == 2
        assert balanced["artifacts"]["strategy"] == "balanced"
        assert safety["artifacts"]["strategy"] == "safety_first"

    def test_empty_data(self):
        result = run_reasoning_agent({"data": []}, "balanced")
        assert result["rankings"] == []

    def test_artifacts_include_strategy(self):
        result = run_reasoning_agent(SAMPLE_DATA_RESULT, "cost_optimized")
        assert result["artifacts"]["strategy"] == "cost_optimized"

    def test_detail_mentions_top_zone(self):
        result = run_reasoning_agent(SAMPLE_DATA_RESULT, "balanced")
        if result["rankings"]:
            assert "Zone One" in result["detail"] or "Z01" in result["detail"]
