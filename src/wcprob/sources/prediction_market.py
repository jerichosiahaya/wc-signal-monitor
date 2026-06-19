import json
import re

import httpx

from wcprob.models import SourceKind, SourceObservation


YES_VALUES = {"yes", "y"}
NO_VALUES = {"no", "n"}


class PredictionMarketSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()
        markets = payload.get("markets")
        if not isinstance(markets, list) or not markets:
            raise ValueError("prediction market payload has no markets")

        return [
            SourceObservation(
                source=self.name,
                source_kind=SourceKind.PREDICTION_MARKET,
                country=row["country"],
                raw_value=str(row["probability"]),
                implied_probability=float(row["probability"]),
            )
            for row in markets
        ]


class PolymarketGammaSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()

        observations: list[SourceObservation] = []
        for market in _polymarket_markets(payload):
            observations.extend(self._market_observations(market))

        if not observations:
            raise ValueError("polymarket payload has no outcome prices")
        return observations

    def _market_observations(self, market: dict) -> list[SourceObservation]:
        outcomes = _json_list(market.get("outcomes"))
        prices = _json_list(market.get("outcomePrices") or market.get("outcome_prices"))
        if not outcomes or not prices or len(outcomes) != len(prices):
            return []

        normalized_outcomes = [str(outcome).strip().lower() for outcome in outcomes]
        if any(outcome in YES_VALUES for outcome in normalized_outcomes):
            country = _country_from_question(
                str(market.get("question") or market.get("title") or "")
            )
            if not country:
                return []
            yes_index = next(
                index
                for index, outcome in enumerate(normalized_outcomes)
                if outcome in YES_VALUES
            )
            return [
                SourceObservation(
                    source=self.name,
                    source_kind=SourceKind.PREDICTION_MARKET,
                    country=country,
                    raw_value=str(prices[yes_index]),
                    implied_probability=float(prices[yes_index]),
                )
            ]

        observations = []
        for country, price in zip(outcomes, prices, strict=True):
            country_name = str(country).strip()
            if country_name.lower() in YES_VALUES | NO_VALUES:
                continue
            observations.append(
                SourceObservation(
                    source=self.name,
                    source_kind=SourceKind.PREDICTION_MARKET,
                    country=country_name,
                    raw_value=str(price),
                    implied_probability=float(price),
                )
            )
        return observations


class KalshiMarketSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()
        markets = payload.get("markets")
        if not isinstance(markets, list) or not markets:
            raise ValueError("kalshi payload has no markets")

        observations = []
        for market in markets:
            if not isinstance(market, dict):
                continue
            country = _country_from_question(
                str(
                    market.get("title")
                    or market.get("subtitle")
                    or market.get("event_title")
                    or ""
                )
            )
            probability = _kalshi_probability(market)
            if country is None or probability is None:
                continue
            observations.append(
                SourceObservation(
                    source=self.name,
                    source_kind=SourceKind.PREDICTION_MARKET,
                    country=country,
                    raw_value=str(probability),
                    implied_probability=probability,
                )
            )

        if not observations:
            raise ValueError("kalshi payload has no usable winner markets")
        return observations


def _polymarket_markets(payload: object) -> list[dict]:
    if isinstance(payload, list):
        markets = []
        for item in payload:
            if isinstance(item, dict):
                markets.extend(_polymarket_markets(item))
        return markets
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("markets"), list):
        return [market for market in payload["markets"] if isinstance(market, dict)]
    if "outcomes" in payload and (
        "outcomePrices" in payload or "outcome_prices" in payload
    ):
        return [payload]
    return []


def _json_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    return []


def _country_from_question(question: str) -> str | None:
    cleaned = question.strip().strip("?")
    patterns = [
        r"will\s+(.+?)\s+win\b",
        r"(.+?)\s+to\s+win\b",
        r"(.+?)\s+wins?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return _clean_country(match.group(1))
    return None


def _clean_country(value: str) -> str:
    return re.sub(r"^(the\s+)?", "", value, flags=re.IGNORECASE).strip()


def _kalshi_probability(market: dict) -> float | None:
    bid = market.get("yes_bid")
    ask = market.get("yes_ask")
    last_price = market.get("last_price")
    if bid is not None and ask is not None:
        return _kalshi_price((float(bid) + float(ask)) / 2)
    if last_price is not None:
        return _kalshi_price(float(last_price))
    return None


def _kalshi_price(value: float) -> float:
    if value > 1:
        return value / 100
    return value
