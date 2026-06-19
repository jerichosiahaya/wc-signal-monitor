from pathlib import Path

from wcprob.config import Settings


def test_default_settings_use_local_sqlite():
    settings = Settings()
    assert settings.database_path.name == "wcprob.sqlite"
    assert settings.refresh_seconds == 900


def test_database_path_reads_env_when_settings_is_instantiated(monkeypatch):
    monkeypatch.setenv("WCPROB_DATABASE", "/tmp/world-cup.sqlite")

    settings = Settings()

    assert settings.database_path == Path("/tmp/world-cup.sqlite")


def test_refresh_seconds_reads_env_when_settings_is_instantiated(monkeypatch):
    monkeypatch.setenv("WCPROB_REFRESH_SECONDS", "120")

    settings = Settings()

    assert settings.refresh_seconds == 120


def test_url_settings_read_env_when_settings_is_instantiated(monkeypatch):
    monkeypatch.setenv("WCPROB_ODDS_API_URL", "https://odds.example.test")
    monkeypatch.setenv("WCPROB_MARKET_URL", "https://markets.example.test")

    settings = Settings()

    assert settings.odds_api_url == "https://odds.example.test"
    assert settings.prediction_market_url == "https://markets.example.test"
