import argparse

from wcprob.collector import Collector
from wcprob.config import Settings
from wcprob.sources.base import ProbabilitySource
from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import PredictionMarketSource
from wcprob.storage import Storage


def build_sources(settings: Settings) -> list[ProbabilitySource]:
    sources: list[ProbabilitySource] = []
    if settings.odds_api_url:
        sources.append(OddsApiSource(name="odds-api", url=settings.odds_api_url))
    if settings.prediction_market_url:
        sources.append(
            PredictionMarketSource(
                name="prediction-market",
                url=settings.prediction_market_url,
            )
        )
    return sources


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="wcprob",
        description="World Cup 2026 signal monitor",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db")
    subparsers.add_parser("collect-once")
    subparsers.add_parser("tui")

    args = parser.parse_args(argv)
    settings = Settings()
    storage = Storage(settings.database_path)

    if args.command == "init-db":
        storage.init_schema()
        print(f"initialized {settings.database_path}")
        return

    if args.command == "collect-once":
        storage.init_schema()
        Collector(storage=storage, sources=build_sources(settings)).collect_once()
        print("collection complete")
        return

    if args.command == "tui":
        from wcprob.tui import run_tui

        storage.init_schema()
        run_tui(storage)
