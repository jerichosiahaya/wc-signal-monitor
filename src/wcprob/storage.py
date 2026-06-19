from contextlib import closing
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
        with closing(self.connect()) as conn:
            with conn:
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
        with closing(self.connect()) as conn:
            with conn:
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
        with closing(self.connect()) as conn:
            rows = conn.execute(
                """
                SELECT
                    observations.source,
                    observations.source_kind,
                    observations.country,
                    observations.raw_value,
                    observations.implied_probability,
                    observations.captured_at
                FROM observations
                INNER JOIN (
                    SELECT source, country, MAX(captured_at) AS captured_at
                    FROM observations
                    GROUP BY source, country
                ) latest
                    ON observations.source = latest.source
                    AND observations.country = latest.country
                    AND observations.captured_at = latest.captured_at
                ORDER BY observations.captured_at DESC
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

    def observation_history(self, limit: int = 500) -> list[SourceObservation]:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                """
                SELECT source, source_kind, country, raw_value, implied_probability, captured_at
                FROM observations
                ORDER BY captured_at DESC
                LIMIT ?
                """,
                (limit,),
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
        with closing(self.connect()) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO source_health (source, ok, message, checked_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        health.source,
                        int(health.ok),
                        health.message,
                        health.checked_at.isoformat(),
                    ),
                )

    def latest_health(self) -> list[SourceHealth]:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                """
                SELECT
                    source_health.source,
                    source_health.ok,
                    source_health.message,
                    source_health.checked_at
                FROM source_health
                INNER JOIN (
                    SELECT source, MAX(checked_at) AS checked_at
                    FROM source_health
                    GROUP BY source
                ) latest
                    ON source_health.source = latest.source
                    AND source_health.checked_at = latest.checked_at
                ORDER BY source_health.checked_at DESC
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
