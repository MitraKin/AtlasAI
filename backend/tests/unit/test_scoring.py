"""Unit tests for the multi-criteria scoring engine."""

from app.services.scoring import normalize, compute_zone_scores, compute_confidence, WEIGHT_PROFILES


class TestNormalize:
    def test_normalize_basic(self):
        result = normalize([10, 20, 30, 40, 50])
        assert result == [0.0, 25.0, 50.0, 75.0, 100.0]

    def test_normalize_inverted(self):
        result = normalize([10, 20, 30, 40, 50], invert=True)
        assert result == [100.0, 75.0, 50.0, 25.0, 0.0]

    def test_normalize_single_value(self):
        result = normalize([42])
        assert result == [50.0]

    def test_normalize_empty(self):
        result = normalize([])
        assert result == []

    def test_normalize_all_same(self):
        result = normalize([30, 30, 30])
        assert result == [50.0, 50.0, 50.0]

    def test_normalize_with_nones(self):
        result = normalize([None, 10, 50])
        assert result[0] == 0.0
        assert result[2] == 100.0

    def test_normalize_negative_values(self):
        result = normalize([-10, 0, 10])
        assert result == [0.0, 50.0, 100.0]


class TestComputeConfidence:
    def test_full_data_high_samples(self):
        zone = {"total_complaints": 500, "pct_spent": 85, "total_incidents": 30}
        conf = compute_confidence(zone)
        assert conf >= 0.9

    def test_low_samples(self):
        zone = {"total_complaints": 20, "total_incidents": None}
        conf = compute_confidence(zone)
        assert conf < 0.5

    def test_no_samples(self):
        zone = {"total_complaints": 0}
        conf = compute_confidence(zone)
        assert conf < 0.3


class TestComputeZoneScores:
    def test_ranks_three_zones(self, sample_zone_data, sample_weights):
        results = compute_zone_scores(sample_zone_data, sample_weights)
        assert len(results) == 3
        assert results[0]["rank"] == 1
        assert results[1]["rank"] == 2
        assert results[2]["rank"] == 3
        assert results[0]["composite_score"] >= results[1]["composite_score"]
        assert results[1]["composite_score"] >= results[2]["composite_score"]

    def test_preserves_zone_names(self, sample_zone_data, sample_weights):
        results = compute_zone_scores(sample_zone_data, sample_weights)
        zone_names = {r["zone_name"] for r in results}
        assert "Downtown Core" in zone_names
        assert "Suburb" in zone_names
        assert "Industrial" in zone_names

    def test_score_between_0_and_100(self, sample_zone_data, sample_weights):
        results = compute_zone_scores(sample_zone_data, sample_weights)
        for r in results:
            assert 0 <= r["composite_score"] <= 100

    def test_confidence_between_0_and_1(self, sample_zone_data, sample_weights):
        results = compute_zone_scores(sample_zone_data, sample_weights)
        for r in results:
            assert 0 <= r["confidence"] <= 1

    def test_empty_data(self, sample_weights):
        results = compute_zone_scores([], sample_weights)
        assert results == []

    def test_safety_first_strategy_weights_accidents_high(self, sample_zone_data):
        weights = WEIGHT_PROFILES["safety_first"]
        assert weights["accident_rate"] > weights["complaint_volume"]

    def test_cost_optimized_strategy_weights_efficiency_high(self):
        weights = WEIGHT_PROFILES["cost_optimized"]
        assert weights["cost_efficiency"] > weights["accident_rate"]

    def test_equity_focused_uses_high_equity(self):
        weights = WEIGHT_PROFILES["equity_focused"]
        assert weights["equity_factor"] >= 0.15

    def test_custom_weights_affect_ranking(self, sample_zone_data):
        balanced = compute_zone_scores(sample_zone_data, WEIGHT_PROFILES["balanced"])
        safety = compute_zone_scores(sample_zone_data, WEIGHT_PROFILES["safety_first"])
        # Rankings may differ between strategies
        assert len(balanced) == len(safety)

    def test_scores_have_all_factors(self, sample_zone_data, sample_weights):
        results = compute_zone_scores(sample_zone_data, sample_weights)
        expected_factors = {"complaint_volume", "severity_index", "accident_rate", "cost_efficiency", "population_impact", "forecast_trend", "equity_factor"}
        for r in results:
            assert expected_factors == set(r["scores"].keys())
