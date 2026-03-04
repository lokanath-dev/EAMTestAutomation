"""SQLite metadata database helper."""

from __future__ import annotations

from pathlib import Path
import json
import sqlite3


class MetadataDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS run_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_case TEXT NOT NULL,
                    dataset TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_cases (
                    name TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def record_run(self, test_case: str, dataset: str, environment: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO run_history(test_case, dataset, environment, status) VALUES(?, ?, ?, ?)",
                (test_case, dataset, environment, status),
            )
            conn.commit()

    def upsert_test_case(self, name: str, payload: dict) -> None:
        payload_json = json.dumps(payload)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO test_cases(name, payload_json, updated_at)
                VALUES(?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    payload_json=excluded.payload_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (name, payload_json),
            )
            conn.commit()

    def get_test_case(self, name: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM test_cases WHERE name = ?",
                (name,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])
