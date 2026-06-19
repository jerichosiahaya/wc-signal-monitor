import os
from pathlib import Path

from pydantic import BaseModel, Field


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    database_path: Path = Field(
        default_factory=lambda: Path(os.getenv("WCPROB_DATABASE", "wcprob.sqlite"))
    )
    refresh_seconds: int = Field(
        default_factory=lambda: int(os.getenv("WCPROB_REFRESH_SECONDS", "900"))
    )
    odds_api_url: str | None = Field(
        default_factory=lambda: os.getenv("WCPROB_ODDS_API_URL")
    )
    prediction_market_url: str | None = Field(
        default_factory=lambda: os.getenv("WCPROB_MARKET_URL")
    )
    odds_api_key: str | None = Field(
        default_factory=lambda: os.getenv("WCPROB_ODDS_API_KEY")
    )
    odds_api_regions: str = Field(
        default_factory=lambda: os.getenv("WCPROB_ODDS_API_REGIONS", "us")
    )
    polymarket_enabled: bool = Field(
        default_factory=lambda: _env_bool("WCPROB_POLYMARKET_ENABLED", True)
    )
    polymarket_url: str = Field(
        default_factory=lambda: os.getenv(
            "WCPROB_POLYMARKET_URL",
            "https://gamma-api.polymarket.com/events?slug=world-cup-winner",
        )
    )
    kalshi_enabled: bool = Field(
        default_factory=lambda: _env_bool("WCPROB_KALSHI_ENABLED", False)
    )
    kalshi_url: str | None = Field(default_factory=lambda: os.getenv("WCPROB_KALSHI_URL"))
