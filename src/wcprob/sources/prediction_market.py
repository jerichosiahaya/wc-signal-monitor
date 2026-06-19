import httpx

from wcprob.models import SourceKind, SourceObservation


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
