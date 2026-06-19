from typing import Protocol

from wcprob.models import SourceObservation


class ProbabilitySource(Protocol):
    name: str

    def fetch(self) -> list[SourceObservation]:
        """Fetch normalized win probability observations."""
