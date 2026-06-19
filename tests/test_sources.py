import httpx
import pytest
import respx

from wcprob.sources.odds_api import OddsApiSource
from wcprob.sources.prediction_market import (
    KalshiMarketSource,
    PolymarketGammaSource,
    PredictionMarketSource,
)


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
def test_odds_api_source_handles_the_odds_api_list_payload():
    respx.get("https://example.test/odds").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "world-cup-outright",
                    "bookmakers": [
                        {
                            "key": "demo",
                            "markets": [
                                {
                                    "key": "outrights",
                                    "outcomes": [
                                        {"name": "France", "price": 4.0},
                                        {"name": "Spain", "price": 5.0},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        )
    )

    source = OddsApiSource(name="the-odds-api", url="https://example.test/odds")
    observations = source.fetch()

    assert [row.country for row in observations] == ["France", "Spain"]
    assert observations[0].source == "the-odds-api"


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


@respx.mock
@pytest.mark.parametrize(
    "payload",
    [
        {"markets": []},
        {},
        {"markets": {}},
    ],
)
def test_prediction_market_source_rejects_payload_without_markets(payload):
    respx.get("https://example.test/market").mock(
        return_value=httpx.Response(200, json=payload)
    )

    source = PredictionMarketSource(name="market-demo", url="https://example.test/market")

    with pytest.raises(ValueError, match="prediction market payload has no markets"):
        source.fetch()


@respx.mock
def test_polymarket_source_reads_binary_winner_markets():
    respx.get("https://example.test/polymarket").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "markets": [
                        {
                            "question": "Will France win the 2026 FIFA World Cup?",
                            "outcomes": '["Yes", "No"]',
                            "outcomePrices": '["0.21", "0.79"]',
                        }
                    ]
                }
            ],
        )
    )

    source = PolymarketGammaSource(
        name="polymarket", url="https://example.test/polymarket"
    )
    observations = source.fetch()

    assert observations[0].country == "France"
    assert observations[0].implied_probability == 0.21


@respx.mock
def test_polymarket_source_reads_categorical_winner_market():
    respx.get("https://example.test/polymarket").mock(
        return_value=httpx.Response(
            200,
            json={
                "markets": [
                    {
                        "outcomes": '["France", "Spain"]',
                        "outcomePrices": '["0.21", "0.16"]',
                    }
                ]
            },
        )
    )

    source = PolymarketGammaSource(
        name="polymarket", url="https://example.test/polymarket"
    )
    observations = source.fetch()

    assert [row.country for row in observations] == ["France", "Spain"]


@respx.mock
def test_kalshi_source_reads_winner_markets():
    respx.get("https://example.test/kalshi").mock(
        return_value=httpx.Response(
            200,
            json={
                "markets": [
                    {
                        "title": "Will France win the 2026 FIFA World Cup?",
                        "yes_bid": 20,
                        "yes_ask": 22,
                    }
                ]
            },
        )
    )

    source = KalshiMarketSource(name="kalshi", url="https://example.test/kalshi")
    observations = source.fetch()

    assert observations[0].country == "France"
    assert observations[0].implied_probability == 0.21
