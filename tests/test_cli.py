import pytest

from wcprob.cli import build_sources, main
from wcprob.config import Settings
from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import PredictionMarketSource


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
    )

    sources = build_sources(settings)

    assert len(sources) == 2
    assert isinstance(sources[0], OddsApiSource)
    assert sources[0].name == "odds-api"
    assert sources[0].url == "https://example.test/odds"
    assert isinstance(sources[1], PredictionMarketSource)
    assert sources[1].name == "prediction-market"
    assert sources[1].url == "https://example.test/markets"


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
