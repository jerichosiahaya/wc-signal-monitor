import httpx

from wcprob.models import SourceKind, SourceObservation
from wcprob.odds import decimal_to_probability, remove_overround


class OddsApiSource:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> list[SourceObservation]:
        response = httpx.get(self.url, timeout=20)
        response.raise_for_status()
        payload = response.json()

        probabilities: dict[str, float] = {}
        raw_values: dict[str, str] = {}

        for bookmaker in payload.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") != "outrights":
                    continue
                for outcome in market.get("outcomes", []):
                    country = outcome["name"]
                    price = float(outcome["price"])
                    probabilities[country] = decimal_to_probability(price)
                    raw_values[country] = str(price)
                break
            if probabilities:
                break

        cleaned = remove_overround(probabilities)
        return [
            SourceObservation(
                source=self.name,
                source_kind=SourceKind.ODDS_API,
                country=country,
                raw_value=raw_values[country],
                implied_probability=probability,
            )
            for country, probability in cleaned.items()
        ]
