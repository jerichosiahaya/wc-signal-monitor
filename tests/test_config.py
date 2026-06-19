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
    monkeypatch.setenv("WCPROB_ODDS_API_KEY", "odds-key")
    monkeypatch.setenv("WCPROB_ODDS_API_REGIONS", "eu")
    monkeypatch.setenv("WCPROB_POLYMARKET_ENABLED", "false")
    monkeypatch.setenv("WCPROB_POLYMARKET_URL", "https://poly.example.test")
    monkeypatch.setenv("WCPROB_KALSHI_ENABLED", "false")
    monkeypatch.setenv("WCPROB_KALSHI_URL", "https://kalshi.example.test")
    monkeypatch.setenv("WCPROB_NEWS_ENABLED", "false")
    monkeypatch.setenv("WCPROB_NEWS_URL", "https://news.example.test/rss")

    settings = Settings()

    assert settings.odds_api_url == "https://odds.example.test"
    assert settings.prediction_market_url == "https://markets.example.test"
    assert settings.odds_api_key == "odds-key"
    assert settings.odds_api_regions == "eu"
    assert settings.polymarket_enabled is False
    assert settings.polymarket_url == "https://poly.example.test"
    assert settings.kalshi_enabled is False
    assert settings.kalshi_url == "https://kalshi.example.test"
    assert settings.news_enabled is False
    assert settings.news_url == "https://news.example.test/rss"


def test_kalshi_is_disabled_without_specific_url():
    settings = Settings()

    assert settings.kalshi_enabled is False
    assert settings.kalshi_url is None
