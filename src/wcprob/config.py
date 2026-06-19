import os
from pathlib import Path

from pydantic import BaseModel, Field


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
