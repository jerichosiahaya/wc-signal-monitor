from wcprob.models import SourceHealth
from wcprob.sources.base import ProbabilitySource
from wcprob.storage import Storage


class Collector:
    def __init__(self, storage: Storage, sources: list[ProbabilitySource]):
        self.storage = storage
        self.sources = sources

    def collect_once(self) -> None:
        for source in self.sources:
            try:
                observations = source.fetch()
            except Exception as exc:
                self.storage.insert_health(
                    SourceHealth(source=source.name, ok=False, message=str(exc))
                )
                continue

            self.storage.insert_observations(observations)
            self.storage.insert_health(SourceHealth(source=source.name, ok=True, message="ok"))
