"""Integration tests for the data repository with SQLite."""

import pytest
from app.repositories.data_repository import DataRepository


class TestDataRepository:
    def test_init_creates_db(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        assert repo.db_path.exists()

    def test_get_zone_list(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        zones = repo.get_zone_list()
        assert len(zones) == 2
        assert zones[0]["zone_name"] == "Downtown Core"

    def test_get_zone_detail(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        zone = repo.get_zone_detail("Z01")
        assert zone is not None
        assert zone["zone_name"] == "Downtown Core"
        assert zone["population"] == 50000

    def test_get_zone_detail_missing(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        zone = repo.get_zone_detail("Z99")
        assert zone is None

    def test_get_complaint_stats_all(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        stats = repo.get_complaint_stats()
        assert len(stats) >= 1

    def test_get_complaint_stats_by_zone(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        stats = repo.get_complaint_stats("Z01")
        assert len(stats) == 1
        assert stats[0]["zone_id"] == "Z01"

    def test_get_traffic_stats(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        stats = repo.get_traffic_stats()
        assert len(stats) == 1
        assert stats[0]["total_incidents"] == 1

    def test_get_budget_stats(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        stats = repo.get_budget_stats()
        assert len(stats) == 1
        assert stats[0]["total_allocated"] == 1000000

    def test_get_demographics(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        demos = repo.get_demographics()
        assert len(demos) == 1
        assert demos[0]["poverty_rate"] == 0.15

    def test_get_infrastructure(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        infra = repo.get_infrastructure()
        assert len(infra) == 1
        assert infra[0]["asset_type"] == "road"

    def test_execute_query(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        results = repo.execute_query("SELECT * FROM zone_metadata ORDER BY zone_id")
        assert len(results) == 2

    def test_get_zone_name_map(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        name_map = repo.get_zone_name_map()
        assert name_map == {"Z01": "Downtown Core", "Z02": "Suburb"}

    def test_get_zone_geometry(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        geom = repo.get_zone_geometry("Z01")
        assert geom is not None
        assert geom["type"] == "Polygon"

    def test_get_zone_geometry_missing(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        geom = repo.get_zone_geometry("Z99")
        assert geom is None

    def test_get_complaints_by_month(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        data = repo.get_complaints_by_month()
        assert len(data) >= 1
        assert "month" in data[0]
