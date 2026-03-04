"""SQLite metadata database helper."""

from pathlib import Path
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
            conn.commit()

    def record_run(self, test_case: str, dataset: str, environment: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO run_history(test_case, dataset, environment, status) VALUES(?, ?, ?, ?)",
                (test_case, dataset, environment, status),
            )
            conn.commit()
