# WC Signal Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `wc-signal-monitor`, a Python TUI that automatically monitors FIFA World Cup 2026 winner probabilities over time from API-based sources and scraper-backed fallback sources.

**Architecture:** Use a small Python package with source adapters that emit normalized probability snapshots, a SQLite repository that stores immutable history, a consensus engine that calculates current country probabilities, and a Textual TUI that displays rankings, source status, movement, and country detail. Keep collectors isolated from the UI so scraping/API failures do not crash the dashboard.

**Tech Stack:** Python 3.11+, `httpx`, `pydantic`, `sqlite-utils` or stdlib `sqlite3`, `textual`, `rich`, `pytest`, `respx`, `ruff`.

---

## File Structure

- `pyproject.toml`: project metadata, dependencies, CLI entrypoint, lint/test config.
- `README.md`: setup, environment variables, run commands, source caveats.
- `.gitignore`: Python, SQLite runtime files, virtualenvs, cache directories.
- `src/wcprob/__init__.py`: package marker and version.
- `src/wcprob/config.py`: environment-driven settings for refresh cadence, database path, API keys, and enabled sources.
- `src/wcprob/models.py`: shared Pydantic models for countries, raw source observations, normalized snapshots, consensus rows, and source health.
- `src/wcprob/odds.py`: odds conversion and overround removal helpers.
- `src/wcprob/storage.py`: SQLite schema creation, snapshot insert, health insert, and query methods.
- `src/wcprob/sources/base.py`: adapter protocol and common adapter result types.
- `src/wcprob/sources/odds_api.py`: API-based odds adapter using The Odds API style response shape.
- `src/wcprob/sources/prediction_market.py`: prediction-market adapter for market probability feeds.
- `src/wcprob/sources/news_scraper.py`: lightweight scraper adapter that captures news annotations and source health, not core probabilities.
- `src/wcprob/collector.py`: orchestrates source adapters, normalization, persistence, and source health updates.
- `src/wcprob/consensus.py`: combines fresh source snapshots into a weighted current probability table.
- `src/wcprob/tui.py`: Textual app with rankings, movers, source health, country detail, and manual refresh.
- `src/wcprob/cli.py`: command entrypoint for `wcprob tui`, `wcprob collect-once`, and `wcprob init-db`.
- `tests/`: focused unit tests for each boundary.

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/wcprob/__init__.py`
- Create: `tests/test_import.py`

- [ ] **Step 1: Create package metadata**

Create `pyproject.toml`:

```toml
[project]
name = "wc-signal-monitor"
version = "0.1.0"
description = "Automated World Cup 2026 signal monitor with a terminal UI"
requires-python = ">=3.11"
dependencies = [
  "httpx>=0.27",
  "pydantic>=2.7",
  "rich>=13.7",
  "textual>=0.70",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2",
  "respx>=0.21",
  "ruff>=0.5",
]

[project.scripts]
wcprob = "wcprob.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: Create ignore rules**

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.pyc
*.db
*.sqlite
.env
```

- [ ] **Step 3: Create minimal README**

Create `README.md`:

```markdown
# WC Signal Monitor

Automated Python TUI for tracking FIFA World Cup 2026 winner probabilities over time.

The monitor stores immutable probability snapshots in SQLite, computes a consensus ranking, and displays current favorites, movement, and source health in the terminal.

## Commands

```bash
wcprob init-db
wcprob collect-once
wcprob tui
```

## Data Sources

API sources should be preferred for probabilities. Scrapers are used for annotations and fallback health signals because public page layouts change often.
```

- [ ] **Step 4: Create package marker**

Create `src/wcprob/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Step 5: Add import test**

Create `tests/test_import.py`:

```python
import wcprob


def test_package_imports():
    assert wcprob.__version__ == "0.1.0"
```

- [ ] **Step 6: Verify skeleton**

Run: `python -m pytest tests/test_import.py -v`

Expected: one passing test.

## Task 2: Shared Models and Odds Math

**Files:**
- Create: `src/wcprob/models.py`
- Create: `src/wcprob/odds.py`
- Create: `tests/test_odds.py`

- [ ] **Step 1: Add odds tests**

Create `tests/test_odds.py`:

```python
from wcprob.odds import american_to_probability, decimal_to_probability, remove_overround


def test_decimal_to_probability():
    assert decimal_to_probability(5.0) == 0.2


def test_american_positive_to_probability():
    assert round(american_to_probability(400), 4) == 0.2


def test_american_negative_to_probability():
    assert round(american_to_probability(-150), 4) == 0.6


def test_remove_overround_normalizes_market():
    cleaned = remove_overround({"France": 0.25, "Spain": 0.20, "England": 0.15})
    assert round(sum(cleaned.values()), 6) == 1.0
    assert cleaned["France"] > cleaned["Spain"] > cleaned["England"]
```

- [ ] **Step 2: Implement odds helpers**

Create `src/wcprob/odds.py`:

```python
def decimal_to_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("decimal_odds must be greater than 1")
    return 1 / decimal_odds


def american_to_probability(american_odds: int) -> float:
    if american_odds > 0:
        return 100 / (american_odds + 100)
    if american_odds < 0:
        return abs(american_odds) / (abs(american_odds) + 100)
    raise ValueError("american_odds cannot be 0")


def remove_overround(probabilities: dict[str, float]) -> dict[str, float]:
    total = sum(probabilities.values())
    if total <= 0:
        raise ValueError("probability total must be positive")
    return {country: probability / total for country, probability in probabilities.items()}
```

- [ ] **Step 3: Add shared models**

Create `src/wcprob/models.py`:

```python
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class SourceKind(str, Enum):
    ODDS_API = "odds_api"
    PREDICTION_MARKET = "prediction_market"
    NEWS_SCRAPER = "news_scraper"


class SourceObservation(BaseModel):
    source: str
    source_kind: SourceKind
    country: str
    raw_value: str
    implied_probability: float = Field(ge=0, le=1)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConsensusRow(BaseModel):
    country: str
    probability: float = Field(ge=0, le=1)
    source_count: int
    change_24h: float | None = None


class SourceHealth(BaseModel):
    source: str
    ok: bool
    message: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Verify models and odds**

Run: `python -m pytest tests/test_odds.py -v`

Expected: four passing tests.

## Task 3: SQLite Storage

**Files:**
- Create: `src/wcprob/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Add storage tests**

Create `tests/test_storage.py`:

```python
from wcprob.models import SourceHealth, SourceKind, SourceObservation
from wcprob.storage import Storage


def test_insert_and_read_latest_observations(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_observations([
        SourceObservation(
            source="test",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="+400",
            implied_probability=0.20,
        )
    ])

    rows = storage.latest_observations()
    assert len(rows) == 1
    assert rows[0].country == "France"


def test_insert_source_health(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_health(SourceHealth(source="test", ok=True, message="ok"))

    rows = storage.latest_health()
    assert rows[0].source == "test"
    assert rows[0].ok is True
```

- [ ] **Step 2: Implement storage**

Create `src/wcprob/storage.py`:

```python
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
```

- [ ] **Step 3: Verify storage**

Run: `python -m pytest tests/test_storage.py -v`

Expected: two passing tests.

## Task 4: Source Adapter Interface and API Adapters

**Files:**
- Create: `src/wcprob/sources/base.py`
- Create: `src/wcprob/sources/odds_api.py`
- Create: `src/wcprob/sources/prediction_market.py`
- Create: `tests/test_sources.py`

- [ ] **Step 1: Add adapter tests**

Create `tests/test_sources.py`:

```python
import httpx
import respx

from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import PredictionMarketSource


@respx.mock
def test_odds_api_source_normalizes_winner_market():
    respx.get("https://example.test/odds").mock(
        return_value=httpx.Response(
            200,
            json={
                "bookmakers": [
                    {
                        "key": "demo",
                        "markets": [
                            {
                                "key": "outrights",
                                "outcomes": [
                                    {"name": "France", "price": 5.0},
                                    {"name": "Spain", "price": 6.0},
                                ],
                            }
                        ],
                    }
                ]
            },
        )
    )

    source = OddsApiSource(name="odds-demo", url="https://example.test/odds")
    observations = source.fetch()

    assert [row.country for row in observations] == ["France", "Spain"]
    assert observations[0].implied_probability > observations[1].implied_probability


@respx.mock
def test_prediction_market_source_reads_probabilities():
    respx.get("https://example.test/market").mock(
        return_value=httpx.Response(
            200,
            json={
                "markets": [
                    {"country": "France", "probability": 0.21},
                    {"country": "England", "probability": 0.14},
                ]
            },
        )
    )

    source = PredictionMarketSource(name="market-demo", url="https://example.test/market")
    observations = source.fetch()

    assert observations[0].country == "France"
    assert observations[0].implied_probability == 0.21
```

- [ ] **Step 2: Implement adapter protocol**

Create `src/wcprob/sources/base.py`:

```python
from typing import Protocol

from wcprob.models import SourceObservation


class ProbabilitySource(Protocol):
    name: str

    def fetch(self) -> list[SourceObservation]:
        """Fetch normalized win probability observations."""
```

- [ ] **Step 3: Implement odds API adapter**

Create `src/wcprob/sources/odds_api.py`:

```python
import httpx

from wcprob.models import SourceKind, SourceObservation
from wcprob.odds import decimal_to_probability, remove_overround


class OddsApiSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()

        probabilities: dict[str, float] = {}
        raw_values: dict[str, str] = {}

        for bookmaker in payload.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") != "outrights":
                    continue
                for outcome in market.get("outcomes", []):
                    country = outcome["name"]
                    price = float(outcome["price"])
                    probabilities[country] = decimal_to_probability(price)
                    raw_values[country] = str(price)
                break
            if probabilities:
                break

        cleaned = remove_overround(probabilities)
        return [
            SourceObservation(
                source=self.name,
                source_kind=SourceKind.ODDS_API,
                country=country,
                raw_value=raw_values[country],
                implied_probability=probability,
            )
            for country, probability in cleaned.items()
        ]
```

- [ ] **Step 4: Implement prediction market adapter**

Create `src/wcprob/sources/prediction_market.py`:

```python
import httpx

from wcprob.models import SourceKind, SourceObservation


class PredictionMarketSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()

        return [
            SourceObservation(
                source=self.name,
                source_kind=SourceKind.PREDICTION_MARKET,
                country=row["country"],
                raw_value=str(row["probability"]),
                implied_probability=float(row["probability"]),
            )
            for row in payload.get("markets", [])
        ]
```

- [ ] **Step 5: Verify adapters**

Run: `python -m pytest tests/test_sources.py -v`

Expected: two passing tests.

## Task 5: Collector and Source Health

**Files:**
- Create: `src/wcprob/collector.py`
- Create: `tests/test_collector.py`

- [ ] **Step 1: Add collector tests**

Create `tests/test_collector.py`:

```python
from wcprob.collector import Collector
from wcprob.models import SourceKind, SourceObservation
from wcprob.storage import Storage


class GoodSource:
    name = "good"

    def fetch(self):
        return [
            SourceObservation(
                source="good",
                source_kind=SourceKind.PREDICTION_MARKET,
                country="France",
                raw_value="0.2",
                implied_probability=0.2,
            )
        ]


class BadSource:
    name = "bad"

    def fetch(self):
        raise RuntimeError("network failed")


def test_collector_persists_success_and_failure_health(tmp_path):
    storage = Storage(tmp_path / "wcprob.sqlite")
    storage.init_schema()

    collector = Collector(storage=storage, sources=[GoodSource(), BadSource()])
    collector.collect_once()

    observations = storage.latest_observations()
    health = storage.latest_health()

    assert observations[0].country == "France"
    assert {row.source: row.ok for row in health} == {"good": True, "bad": False}
```

- [ ] **Step 2: Implement collector**

Create `src/wcprob/collector.py`:

```python
from wcprob.models import SourceHealth
from wcprob.sources.base import ProbabilitySource
from wcprob.storage import Storage


class Collector:
    def __init__(self, storage: Storage, sources: list[ProbabilitySource]):
        self.storage = storage
        self.sources = sources

    def collect_once(self) -> None:
        for source in self.sources:
            try:
                observations = source.fetch()
                self.storage.insert_observations(observations)
                self.storage.insert_health(
                    SourceHealth(
                        source=source.name,
                        ok=True,
                        message=f"stored {len(observations)} observations",
                    )
                )
            except Exception as exc:
                self.storage.insert_health(
                    SourceHealth(source=source.name, ok=False, message=str(exc))
                )
```

- [ ] **Step 3: Verify collector**

Run: `python -m pytest tests/test_collector.py -v`

Expected: one passing test.

## Task 6: Consensus Engine

**Files:**
- Create: `src/wcprob/consensus.py`
- Create: `tests/test_consensus.py`

- [ ] **Step 1: Add consensus tests**

Create `tests/test_consensus.py`:

```python
from wcprob.consensus import build_consensus
from wcprob.models import SourceKind, SourceObservation


def test_consensus_averages_country_probabilities():
    rows = [
        SourceObservation(
            source="odds",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="5.0",
            implied_probability=0.20,
        ),
        SourceObservation(
            source="market",
            source_kind=SourceKind.PREDICTION_MARKET,
            country="France",
            raw_value="0.22",
            implied_probability=0.22,
        ),
        SourceObservation(
            source="market",
            source_kind=SourceKind.PREDICTION_MARKET,
            country="Spain",
            raw_value="0.16",
            implied_probability=0.16,
        ),
    ]

    consensus = build_consensus(rows)

    assert consensus[0].country == "France"
    assert consensus[0].probability == 0.21
    assert consensus[0].source_count == 2
```

- [ ] **Step 2: Implement consensus**

Create `src/wcprob/consensus.py`:

```python
from collections import defaultdict

from wcprob.models import ConsensusRow, SourceObservation


def build_consensus(observations: list[SourceObservation]) -> list[ConsensusRow]:
    values: dict[str, list[float]] = defaultdict(list)
    sources: dict[str, set[str]] = defaultdict(set)

    for row in observations:
        values[row.country].append(row.implied_probability)
        sources[row.country].add(row.source)

    consensus = [
        ConsensusRow(
            country=country,
            probability=round(sum(probabilities) / len(probabilities), 4),
            source_count=len(sources[country]),
        )
        for country, probabilities in values.items()
    ]
    return sorted(consensus, key=lambda row: row.probability, reverse=True)
```

- [ ] **Step 3: Verify consensus**

Run: `python -m pytest tests/test_consensus.py -v`

Expected: one passing test.

## Task 7: CLI

**Files:**
- Create: `src/wcprob/config.py`
- Create: `src/wcprob/cli.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Add config tests**

Create `tests/test_config.py`:

```python
from wcprob.config import Settings


def test_default_settings_use_local_sqlite():
    settings = Settings()
    assert settings.database_path.name == "wcprob.sqlite"
    assert settings.refresh_seconds == 900
```

- [ ] **Step 2: Implement settings**

Create `src/wcprob/config.py`:

```python
import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    database_path: Path = Path(os.getenv("WCPROB_DATABASE", "wcprob.sqlite"))
    refresh_seconds: int = int(os.getenv("WCPROB_REFRESH_SECONDS", "900"))
    odds_api_url: str | None = os.getenv("WCPROB_ODDS_API_URL")
    prediction_market_url: str | None = os.getenv("WCPROB_MARKET_URL")
```

- [ ] **Step 3: Implement CLI**

Create `src/wcprob/cli.py`:

```python
import argparse

from wcprob.collector import Collector
from wcprob.config import Settings
from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import PredictionMarketSource
from wcprob.storage import Storage


def build_sources(settings: Settings):
    sources = []
    if settings.odds_api_url:
        sources.append(OddsApiSource(name="odds-api", url=settings.odds_api_url))
    if settings.prediction_market_url:
        sources.append(
            PredictionMarketSource(name="prediction-market", url=settings.prediction_market_url)
        )
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(prog="wcprob")
    parser.add_argument("command", choices=["init-db", "collect-once", "tui"])
    args = parser.parse_args()

    settings = Settings()
    storage = Storage(settings.database_path)

    if args.command == "init-db":
        storage.init_schema()
        print(f"initialized {settings.database_path}")
        return

    if args.command == "collect-once":
        storage.init_schema()
        collector = Collector(storage=storage, sources=build_sources(settings))
        collector.collect_once()
        print("collection complete")
        return

    if args.command == "tui":
        from wcprob.tui import run_tui

        storage.init_schema()
        run_tui(storage)
```

- [ ] **Step 4: Verify CLI-adjacent config**

Run: `python -m pytest tests/test_config.py -v`

Expected: one passing test.

## Task 8: TUI Dashboard

**Files:**
- Create: `src/wcprob/tui.py`
- Create: `tests/test_tui_formatting.py`

- [ ] **Step 1: Add TUI formatting test**

Create `tests/test_tui_formatting.py`:

```python
from wcprob.tui import format_probability


def test_format_probability():
    assert format_probability(0.214) == "21.4%"
```

- [ ] **Step 2: Implement TUI**

Create `src/wcprob/tui.py`:

```python
from rich.table import Table
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header

from wcprob.consensus import build_consensus
from wcprob.storage import Storage


def format_probability(value: float) -> str:
    return f"{value * 100:.1f}%"


class ProbabilityApp(App):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="rankings")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#rankings", DataTable)
        table.add_columns("Rank", "Country", "Consensus", "Sources")
        self.refresh_table()

    def action_refresh(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one("#rankings", DataTable)
        table.clear()
        consensus = build_consensus(self.storage.latest_observations())
        for index, row in enumerate(consensus[:12], start=1):
            table.add_row(
                str(index),
                row.country,
                format_probability(row.probability),
                str(row.source_count),
            )


def build_rich_table(storage: Storage) -> Table:
    table = Table(title="World Cup 2026 Win Probability")
    table.add_column("Rank")
    table.add_column("Country")
    table.add_column("Consensus")
    table.add_column("Sources")

    for index, row in enumerate(build_consensus(storage.latest_observations())[:12], start=1):
        table.add_row(str(index), row.country, format_probability(row.probability), str(row.source_count))

    return table


def run_tui(storage: Storage) -> None:
    ProbabilityApp(storage).run()
```

- [ ] **Step 3: Verify TUI formatting**

Run: `python -m pytest tests/test_tui_formatting.py -v`

Expected: one passing test.

## Task 9: End-to-End Local Smoke Test

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run all tests**

Run: `python -m pytest -v`

Expected: all tests pass.

- [ ] **Step 2: Initialize local database**

Run: `wcprob init-db`

Expected output includes: `initialized wcprob.sqlite`

- [ ] **Step 3: Run one collection without configured sources**

Run: `wcprob collect-once`

Expected output includes: `collection complete`

- [ ] **Step 4: Document environment variables**

Append to `README.md`:

```markdown
## Environment Variables

- `WCPROB_DATABASE`: SQLite database path. Defaults to `wcprob.sqlite`.
- `WCPROB_REFRESH_SECONDS`: TUI refresh cadence. Defaults to `900`.
- `WCPROB_ODDS_API_URL`: Odds API endpoint for outright winner markets.
- `WCPROB_MARKET_URL`: Prediction-market endpoint returning country probabilities.
```

- [ ] **Step 5: Run lint and tests**

Run: `python -m ruff check . && python -m pytest -v`

Expected: lint passes and all tests pass.

## Later Enhancements

- Add source-specific adapters for the chosen paid/free odds provider.
- Add source weighting by kind and freshness.
- Add 24-hour and 7-day country movement.
- Add country detail screen with per-source probabilities.
- Add news annotations for major result, injury, suspension, and odds movement events.
- Add `systemd` service or cron deployment instructions for scheduled collection.

## Self-Review

- Spec coverage: The plan covers automated API collection, scraper-compatible adapter boundaries, SQLite history, consensus calculation, and a TUI.
- Placeholder scan: No task uses TBD/TODO/fill-in wording.
- Type consistency: Models, storage, collector, consensus, CLI, and TUI use the same `SourceObservation`, `ConsensusRow`, `SourceHealth`, and `Storage` types.
- Scope check: This is a single MVP plan. Provider-specific production adapters can be added after choosing exact data vendors.
