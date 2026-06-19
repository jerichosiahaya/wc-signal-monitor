from datetime import datetime, timezone

from wcprob.models import SourceHealth, SourceKind, SourceObservation
from wcprob.storage import Storage


def test_insert_and_read_latest_observations(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_observations(
        [
            SourceObservation(
                source="test",
                source_kind=SourceKind.ODDS_API,
                country="France",
                raw_value="+400",
                implied_probability=0.20,
                captured_at=datetime(2026, 6, 19, 9, 0, tzinfo=timezone.utc),
            ),
            SourceObservation(
                source="test",
                source_kind=SourceKind.ODDS_API,
                country="France",
                raw_value="+350",
                implied_probability=0.22,
                captured_at=datetime(2026, 6, 19, 10, 0, tzinfo=timezone.utc),
            ),
            SourceObservation(
                source="test",
                source_kind=SourceKind.PREDICTION_MARKET,
                country="Spain",
                raw_value="0.18",
                implied_probability=0.18,
                captured_at=datetime(2026, 6, 19, 9, 30, tzinfo=timezone.utc),
            ),
        ]
    )

    rows = storage.latest_observations()
    by_country = {row.country: row for row in rows}

    assert len(rows) == 2
    assert by_country["France"].source == "test"
    assert by_country["France"].source_kind == SourceKind.ODDS_API
    assert by_country["France"].raw_value == "+350"
    assert by_country["France"].implied_probability == 0.22
    assert by_country["France"].captured_at == datetime(
        2026, 6, 19, 10, 0, tzinfo=timezone.utc
    )
    assert by_country["France"].captured_at.tzinfo == timezone.utc
    assert by_country["Spain"].source_kind == SourceKind.PREDICTION_MARKET
    assert by_country["Spain"].captured_at.tzinfo == timezone.utc


def test_insert_source_health(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_health(
        SourceHealth(
            source="test",
            ok=True,
            message="ok",
            checked_at=datetime(2026, 6, 19, 8, 0, tzinfo=timezone.utc),
        )
    )
    storage.insert_health(
        SourceHealth(
            source="test",
            ok=False,
            message="timeout",
            checked_at=datetime(2026, 6, 19, 8, 5, tzinfo=timezone.utc),
        )
    )
    storage.insert_health(
        SourceHealth(
            source="other",
            ok=True,
            message="ok",
            checked_at=datetime(2026, 6, 19, 8, 3, tzinfo=timezone.utc),
        )
    )

    rows = storage.latest_health()
    by_source = {row.source: row for row in rows}

    assert len(rows) == 2
    assert by_source["test"].ok is False
    assert by_source["test"].message == "timeout"
    assert by_source["test"].checked_at == datetime(
        2026, 6, 19, 8, 5, tzinfo=timezone.utc
    )
    assert by_source["test"].checked_at.tzinfo == timezone.utc
    assert by_source["other"].ok is True
    assert by_source["other"].message == "ok"
    assert by_source["other"].checked_at.tzinfo == timezone.utc
