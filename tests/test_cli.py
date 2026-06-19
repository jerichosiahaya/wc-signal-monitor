import pytest

from wcprob.cli import build_sources, main
from wcprob.config import Settings
from wcprob.sources.news import NewsSignalSource
from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import (
    KalshiMarketSource,
    PolymarketGammaSource,
    PredictionMarketSource,
)


def test_main_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "usage: wcprob" in capsys.readouterr().out


def test_build_sources_uses_configured_urls(tmp_path):
    settings = Settings(
        database_path=tmp_path / "wcprob.sqlite",
        odds_api_url="https://example.test/odds",
        prediction_market_url="https://example.test/markets",
        polymarket_enabled=False,
        kalshi_enabled=False,
        news_enabled=False,
    )

    sources = build_sources(settings)

    assert len(sources) == 2
    assert isinstance(sources[0], OddsApiSource)
    assert sources[0].name == "odds-api"
    assert sources[0].url == "https://example.test/odds"
    assert isinstance(sources[1], PredictionMarketSource)
    assert sources[1].name == "prediction-market"
    assert sources[1].url == "https://example.test/markets"


def test_build_sources_adds_builtin_providers(tmp_path):
    settings = Settings(
        database_path=tmp_path / "wcprob.sqlite",
        odds_api_key="odds-key",
        odds_api_regions="eu",
        polymarket_url="https://example.test/polymarket",
        kalshi_enabled=True,
        kalshi_url="https://example.test/kalshi",
        news_url="https://example.test/news.xml",
    )

    sources = build_sources(settings)

    assert len(sources) == 4
    assert isinstance(sources[0], OddsApiSource)
    assert sources[0].name == "the-odds-api"
    assert "apiKey=odds-key" in sources[0].url
    assert "regions=eu" in sources[0].url
    assert isinstance(sources[1], PolymarketGammaSource)
    assert sources[1].url == "https://example.test/polymarket"
    assert isinstance(sources[2], KalshiMarketSource)
    assert sources[2].url == "https://example.test/kalshi"
    assert isinstance(sources[3], NewsSignalSource)
    assert sources[3].url == "https://example.test/news.xml"


def test_build_sources_skips_kalshi_without_specific_url(tmp_path):
    settings = Settings(
        database_path=tmp_path / "wcprob.sqlite",
        polymarket_enabled=False,
        kalshi_enabled=True,
        kalshi_url=None,
        news_enabled=False,
    )

    assert build_sources(settings) == []


def test_init_db_command_initializes_configured_database(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "wcprob.sqlite"
    monkeypatch.setattr(
        "wcprob.cli.Settings",
        lambda: Settings(database_path=db_path),
    )

    main(["init-db"])

    assert db_path.exists()
    assert f"initialized {db_path}" in capsys.readouterr().out


def test_tui_command_uses_configured_refresh_seconds(tmp_path, monkeypatch):
    import wcprob.tui

    db_path = tmp_path / "wcprob.sqlite"
    run_args = {}

    def fake_run_tui(storage, refresh_seconds):
        run_args["storage"] = storage
        run_args["refresh_seconds"] = refresh_seconds

    monkeypatch.setattr(
        "wcprob.cli.Settings",
        lambda: Settings(database_path=db_path, refresh_seconds=17),
    )
    monkeypatch.setattr(wcprob.tui, "run_tui", fake_run_tui)

    main(["tui"])

    assert run_args["storage"].db_path == db_path
    assert run_args["refresh_seconds"] == 17
