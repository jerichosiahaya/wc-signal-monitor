import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    database_path: Path = Path(os.getenv("WCPROB_DATABASE", "wcprob.sqlite"))
    refresh_seconds: int = int(os.getenv("WCPROB_REFRESH_SECONDS", "900"))
    odds_api_url: str | None = os.getenv("WCPROB_ODDS_API_URL")
    prediction_market_url: str | None = os.getenv("WCPROB_MARKET_URL")
