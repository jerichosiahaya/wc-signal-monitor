import sqlite3
from pathlib import Path

from wcprob.models import SourceHealth, SourceKind, SourceObservation


class Storage:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    country TEXT NOT NULL,
                    raw_value TEXT NOT NULL,
                    implied_probability REAL NOT NULL,
                    captured_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS source_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    ok INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    checked_at TEXT NOT NULL
                );
                """
            )

    def insert_observations(self, observations: list[SourceObservation]) -> None:
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO observations
                (source, source_kind, country, raw_value, implied_probability, captured_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.source,
                        row.source_kind.value,
                        row.country,
                        row.raw_value,
                        row.implied_probability,
                        row.captured_at.isoformat(),
                    )
                    for row in observations
                ],
            )

    def latest_observations(self) -> list[SourceObservation]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT source, source_kind, country, raw_value, implied_probability, captured_at
                FROM observations
                ORDER BY captured_at DESC
                """
            ).fetchall()
        return [
            SourceObservation(
                source=row["source"],
                source_kind=SourceKind(row["source_kind"]),
                country=row["country"],
                raw_value=row["raw_value"],
                implied_probability=row["implied_probability"],
                captured_at=row["captured_at"],
            )
            for row in rows
        ]

    def insert_health(self, health: SourceHealth) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO source_health (source, ok, message, checked_at)
                VALUES (?, ?, ?, ?)
                """,
                (health.source, int(health.ok), health.message, health.checked_at.isoformat()),
            )

    def latest_health(self) -> list[SourceHealth]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT source, ok, message, checked_at
                FROM source_health
                ORDER BY checked_at DESC
                """
            ).fetchall()
        return [
            SourceHealth(
                source=row["source"],
                ok=bool(row["ok"]),
                message=row["message"],
                checked_at=row["checked_at"],
            )
            for row in rows
        ]
