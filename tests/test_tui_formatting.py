from wcprob.models import SourceHealth
from wcprob.tui import ProbabilityApp, format_probability, format_source_health


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
