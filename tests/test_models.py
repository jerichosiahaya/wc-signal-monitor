from datetime import timezone

import pytest
from pydantic import ValidationError

from wcprob.models import SourceHealth, SourceKind, SourceObservation


def test_source_observation_rejects_naive_captured_at():
    with pytest.raises(ValidationError):
        SourceObservation(
            source="test",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="2.0",
            implied_probability=0.5,
            captured_at="2026-06-19T12:34:56",
        )


def test_source_health_normalizes_checked_at_to_utc():
    health = SourceHealth(
        source="test",
        ok=True,
        message="ok",
        checked_at="2026-06-19T12:34:56+07:00",
    )

    assert health.checked_at.hour == 5
    assert health.checked_at.tzinfo == timezone.utc
