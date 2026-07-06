"""Unit tests for policy tools — explanations, bias checks, equity, citations."""

from app.agents.tools.policy_tools import generate_explanation, check_equity, check_bias, cite_sources
from app.services.scoring import WEIGHT_PROFILES


class TestGenerateExplanation:
    def test_generates_reasoning_text(self):
        zone = {"zone_id": "Z07", "zone_name": "Old Town", "scores": {"complaint_volume": 90, "severity_index": 85, "accident_rate": 50, "cost_efficiency": 40, "population_impact": 60, "forecast_trend": 30, "equity_factor": 20}}
        result = generate_explanation(zone, "balanced")
        assert "Old Town" in result
        assert "complaint volume" in result

    def test_falls_back_to_zone_id(self):
        zone = {"zone_id": "Z99", "scores": {"complaint_volume": 50, "severity_index": 80, "accident_rate": 50, "cost_efficiency": 40, "population_impact": 60, "forecast_trend": 30, "equity_factor": 20}}
        result = generate_explanation(zone, "balanced")
        assert "Z99" in result

    def test_uses_top_two_factors(self):
        zone = {"zone_id": "Z01", "zone_name": "Test", "scores": {"complaint_volume": 90, "severity_index": 85, "accident_rate": 50, "cost_efficiency": 40, "population_impact": 60, "forecast_trend": 30, "equity_factor": 20}}
        result = generate_explanation(zone, "balanced")
        assert "complaint volume" in result
        assert "severity index" in result


class TestCheckEquity:
    def test_flags_top3_heavy_concentration(self):
        zones = [
            {"suggested_budget_allocation": 2500000},
            {"suggested_budget_allocation": 2500000},
            {"suggested_budget_allocation": 2500000},
            {"suggested_budget_allocation": 500000},
        ]
        flags = check_equity(zones, 4, 8000000)
        assert len(flags) == 1
        assert "70%" in flags[0]

    def test_no_flag_on_balanced_distribution(self):
        zones = [
            {"suggested_budget_allocation": 1000000},
            {"suggested_budget_allocation": 1000000},
            {"suggested_budget_allocation": 1000000},
            {"suggested_budget_allocation": 1500000},
        ]
        flags = check_equity(zones, 4, 5500000)
        assert len(flags) == 0

    def test_no_flag_on_fewer_than_4_zones(self):
        zones = [
            {"suggested_budget_allocation": 3000000},
        ]
        flags = check_equity(zones, 1, 3000000)
        assert len(flags) == 0

    def test_no_flag_on_zero_budget(self):
        zones = [{"suggested_budget_allocation": 100}]
        flags = check_equity(zones, 4, 0)
        assert len(flags) == 0


class TestCheckBias:
    def test_flags_safety_heavy_bias(self):
        weights = {"severity_index": 0.30, "accident_rate": 0.30, "complaint_volume": 0.10, "cost_efficiency": 0.05, "population_impact": 0.10, "forecast_trend": 0.10, "equity_factor": 0.05}
        flags = check_bias(weights)
        assert any("Safety weighted" in f for f in flags)

    def test_flags_low_equity(self):
        weights = WEIGHT_PROFILES["safety_first"]
        flags = check_bias(weights)
        assert any("Equity factor is low" in f for f in flags)

    def test_no_flags_on_balanced(self):
        weights = WEIGHT_PROFILES["balanced"]
        flags = check_bias(weights)
        assert not any("Safety weighted" in f for f in flags)


class TestCiteSources:
    def test_returns_four_sources(self):
        citations = cite_sources("Z07")
        assert len(citations) == 4
        assert all("Z07" in c for c in citations)

    def test_sources_are_strings(self):
        citations = cite_sources("Z01")
        assert all(isinstance(c, str) for c in citations)
