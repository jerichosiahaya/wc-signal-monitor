from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc)


class SourceKind(str, Enum):
    ODDS_API = "odds_api"
    PREDICTION_MARKET = "prediction_market"
    NEWS_SCRAPER = "news_scraper"


class SourceObservation(BaseModel):
    source: str
    source_kind: SourceKind
    country: str
    raw_value: str
    implied_probability: float = Field(ge=0, le=1)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("captured_at")
    @classmethod
    def captured_at_must_be_utc(cls, value: datetime) -> datetime:
        return _ensure_utc(value)


class ConsensusRow(BaseModel):
    country: str
    probability: float = Field(ge=0, le=1)
    source_count: int
    change_24h: float | None = None


class SourceHealth(BaseModel):
    source: str
    ok: bool
    message: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("checked_at")
    @classmethod
    def checked_at_must_be_utc(cls, value: datetime) -> datetime:
        return _ensure_utc(value)
