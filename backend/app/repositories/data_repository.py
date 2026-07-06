"""Data repository using SQLite as a local BigQuery stand-in.

In production, swap this for the BigQuery client with the same interface.
All SQL is parameterized and read-only.
"""

import csv
import json
import sqlite3
import time
from pathlib import Path
from contextlib import contextmanager

import logging

logger = logging.getLogger(__name__)


class DataRepository:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "citypulse.db"
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        if self.db_path.exists():
            return

        with self._conn() as conn:
            c = conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS complaints_311 (
                    complaint_id TEXT PRIMARY KEY,
                    created_date TEXT,
                    closed_date TEXT,
                    category TEXT,
                    subcategory TEXT,
                    status TEXT,
                    zone_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    severity INTEGER,
                    resolution_days REAL,
                    description TEXT
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS traffic_incidents (
                    incident_id TEXT PRIMARY KEY,
                    date TEXT,
                    time TEXT,
                    zone_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    severity INTEGER,
                    type TEXT,
                    road_type TEXT,
                    weather_condition TEXT,
                    injuries INTEGER,
                    fatalities INTEGER
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS budget_historical (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fiscal_year INTEGER,
                    quarter INTEGER,
                    zone_id TEXT,
                    department TEXT,
                    category TEXT,
                    allocated_amount REAL,
                    spent_amount REAL,
                    project_count INTEGER,
                    completion_rate REAL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS census_demographics (
                    zone_id TEXT PRIMARY KEY,
                    population INTEGER,
                    population_growth_rate REAL,
                    median_income INTEGER,
                    poverty_rate REAL,
                    median_age REAL,
                    households INTEGER,
                    vehicle_ownership_pct REAL,
                    education_pct_college REAL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS infrastructure_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_id TEXT,
                    asset_type TEXT,
                    avg_age_years REAL,
                    pct_past_lifecycle REAL,
                    last_major_repair TEXT,
                    condition_score REAL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS utility_outages (
                    outage_id TEXT PRIMARY KEY,
                    date TEXT,
                    zone_id TEXT,
                    type TEXT,
                    duration_hours REAL,
                    affected_residents INTEGER,
                    cause TEXT,
                    latitude REAL,
                    longitude REAL
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS zone_metadata (
                    zone_id TEXT PRIMARY KEY,
                    zone_name TEXT,
                    area_sqkm REAL,
                    population INTEGER,
                    median_income INTEGER,
                    population_density INTEGER,
                    geometry TEXT
                )
            """)

            conn.commit()

        self._load_csvs()

    def _load_csvs(self):
        loaders = [
            ("complaints_311.csv", "complaints_311", "complaint_id"),
            ("traffic_incidents.csv", "traffic_incidents", "incident_id"),
            ("budget_historical.csv", "budget_historical", None),
            ("census_demographics.csv", "census_demographics", "zone_id"),
            ("infrastructure_assets.csv", "infrastructure_assets", None),
            ("utility_outages.csv", "utility_outages", "outage_id"),
        ]

        for filename, table, pk in loaders:
            path = self.data_dir / filename
            if not path.exists():
                logger.warning("missing_data_file", file=filename)
                continue

            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            with self._conn() as conn:
                c = conn.cursor()
                for row in rows:
                    cleaned = {k: (v if v != "" else None) for k, v in row.items()}
                    columns = ", ".join(cleaned.keys())
                    placeholders = ", ".join(["?" for _ in cleaned])
                    vals = list(cleaned.values())

                    if pk is None:
                        c.execute(
                            f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})",
                            vals,
                        )
                    else:
                        c.execute(
                            f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                            vals,
                        )
                conn.commit()

            logger.info("loaded_csv: %s rows=%d table=%s", filename, len(rows), table)

        self._load_zone_metadata()

    def _load_zone_metadata(self):
        path = self.data_dir / "zone_boundaries.geojson"
        if not path.exists():
            return

        with open(path) as f:
            geojson = json.load(f)

        with self._conn() as conn:
            c = conn.cursor()
            for feat in geojson["features"]:
                props = feat["properties"]
                geom = json.dumps(feat["geometry"])
                c.execute(
                    """INSERT OR REPLACE INTO zone_metadata
                       (zone_id, zone_name, area_sqkm, population, median_income, population_density, geometry)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        props["zone_id"], props["zone_name"], props["area_sqkm"],
                        props["population"], props["median_income"], props["population_density"],
                        geom,
                    ),
                )
            conn.commit()

    def execute_query(self, sql: str, params: tuple = ()) -> list[dict]:
        start = time.time()
        with self._conn() as conn:
            c = conn.cursor()
            try:
                c.execute(sql, params)
                rows = c.fetchall()
                elapsed = (time.time() - start) * 1000
                logger.info("query_executed: %sms %d rows", round(elapsed, 2), len(rows))
                return [dict(r) for r in rows]
            except sqlite3.Error as e:
                logger.error("query_error", error=str(e), sql=sql[:200])
                raise

    def get_zone_list(self) -> list[dict]:
        return self.execute_query("SELECT * FROM zone_metadata ORDER BY zone_id")

    def get_zone_name_map(self) -> dict[str, str]:
        rows = self.execute_query("SELECT zone_id, zone_name FROM zone_metadata")
        return {r["zone_id"]: r["zone_name"] for r in rows}

    def get_zone_detail(self, zone_id: str) -> dict | None:
        rows = self.execute_query(
            "SELECT * FROM zone_metadata WHERE zone_id = ?", params=(zone_id,)
        )
        # execute_query doesn't support params, use _conn directly
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM zone_metadata WHERE zone_id = ?", (zone_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_complaint_stats(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(f"""
                SELECT
                    zone_id,
                    COUNT(*) as total_complaints,
                    AVG(severity) as avg_severity,
                    SUM(CASE WHEN severity >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pct_critical,
                    AVG(CASE WHEN resolution_days IS NOT NULL THEN resolution_days END) as avg_resolution_days,
                    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_backlog
                FROM complaints_311
                {where}
                GROUP BY zone_id
                ORDER BY total_complaints DESC
            """, params).fetchall()
        return [dict(r) for r in rows]

    def get_complaints_by_month(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(f"""
                SELECT
                    zone_id,
                    substr(created_date, 1, 7) as month,
                    COUNT(*) as total,
                    AVG(severity) as avg_severity
                FROM complaints_311
                {where}
                GROUP BY zone_id, month
                ORDER BY zone_id, month
            """, params).fetchall()
        return [dict(r) for r in rows]

    def get_traffic_stats(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(f"""
                SELECT
                    zone_id,
                    COUNT(*) as total_incidents,
                    AVG(severity) as avg_severity,
                    SUM(injuries) as total_injuries,
                    SUM(fatalities) as total_fatalities
                FROM traffic_incidents
                {where}
                GROUP BY zone_id
                ORDER BY total_incidents DESC
            """, params).fetchall()
        return [dict(r) for r in rows]

    def get_budget_stats(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(f"""
                SELECT
                    zone_id,
                    SUM(allocated_amount) as total_allocated,
                    SUM(spent_amount) as total_spent,
                    SUM(spent_amount) * 100.0 / NULLIF(SUM(allocated_amount), 0) as pct_spent,
                    AVG(completion_rate) as avg_completion_rate
                FROM budget_historical
                {where}
                GROUP BY zone_id
            """, params).fetchall()
        return [dict(r) for r in rows]

    def get_demographics(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM census_demographics {where}", params
            ).fetchall()
        return [dict(r) for r in rows]

    def get_infrastructure(self, zone_id: str | None = None) -> list[dict]:
        where = "WHERE zone_id = ?" if zone_id else ""
        params = (zone_id,) if zone_id else ()
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM infrastructure_assets {where}", params
            ).fetchall()
        return [dict(r) for r in rows]

    def get_zone_geometry(self, zone_id: str) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT geometry FROM zone_metadata WHERE zone_id = ?", (zone_id,)
            ).fetchone()
        return json.loads(row["geometry"]) if row and row["geometry"] else None
