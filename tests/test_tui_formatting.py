from datetime import datetime, timezone

from wcprob.models import SourceHealth, SourceKind, SourceObservation
from wcprob.tui import (
    ProbabilityApp,
    country_history,
    format_probability,
    format_source_health,
    sparkline,
)


def test_format_probability():
    assert format_probability(0.214) == "21.4%"


def test_format_source_health_empty():
    assert format_source_health([]) == "Sources: none"


def test_format_source_health_ok_and_failed():
    health = [
        SourceHealth(source="good", ok=True, message="stored 1 observations"),
        SourceHealth(source="bad", ok=False, message="network failed"),
    ]

    assert format_source_health(health) == "Sources: good ok; bad failed: network failed"


def test_probability_app_stores_refresh_seconds(tmp_path):
    app = ProbabilityApp(storage=object(), refresh_seconds=17)

    assert app.refresh_seconds == 17


def test_sparkline_formats_probability_trend():
    assert sparkline([0.1, 0.2, 0.3]) == "▁▅█"


def test_country_history_orders_values_by_time():
    observations = [
        SourceObservation(
            source="odds",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="0.3",
            implied_probability=0.3,
            captured_at=datetime(2026, 6, 19, 2, tzinfo=timezone.utc),
        ),
        SourceObservation(
            source="odds",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="0.1",
            implied_probability=0.1,
            captured_at=datetime(2026, 6, 19, 1, tzinfo=timezone.utc),
        ),
    ]

    assert country_history(observations, "France") == [0.1, 0.3]
