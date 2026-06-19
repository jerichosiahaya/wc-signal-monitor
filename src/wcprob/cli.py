import argparse

from wcprob.collector import Collector
from wcprob.config import Settings
from wcprob.sources.base import ProbabilitySource
from wcprob.sources.odds_api import OddsApiSource, build_the_odds_api_url
from wcprob.sources.prediction_market import (
    KalshiMarketSource,
    PolymarketGammaSource,
    PredictionMarketSource,
)
from wcprob.storage import Storage


def build_sources(settings: Settings) -> list[ProbabilitySource]:
    sources: list[ProbabilitySource] = []
    if settings.odds_api_url:
        sources.append(OddsApiSource(name="odds-api", url=settings.odds_api_url))
    elif settings.odds_api_key:
        sources.append(
            OddsApiSource(
                name="the-odds-api",
                url=build_the_odds_api_url(
                    api_key=settings.odds_api_key,
                    regions=settings.odds_api_regions,
                ),
            )
        )
    if settings.prediction_market_url:
        sources.append(
            PredictionMarketSource(
                name="prediction-market",
                url=settings.prediction_market_url,
            )
        )
    if settings.polymarket_enabled:
        sources.append(PolymarketGammaSource(name="polymarket", url=settings.polymarket_url))
    if settings.kalshi_enabled and settings.kalshi_url:
        sources.append(KalshiMarketSource(name="kalshi", url=settings.kalshi_url))
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
        run_tui(storage, refresh_seconds=settings.refresh_seconds)
