from wcprob.collector import Collector
from wcprob.models import SourceKind, SourceObservation
from wcprob.storage import Storage


class GoodSource:
    name = "good"

    def fetch(self):
        return [
            SourceObservation(
                source="good",
                source_kind=SourceKind.PREDICTION_MARKET,
                country="France",
                raw_value="0.2",
                implied_probability=0.2,
            )
        ]


class BadSource:
    name = "bad"

    def fetch(self):
        raise RuntimeError("network failed")


def test_collector_persists_success_and_failure_health(tmp_path):
    storage = Storage(tmp_path / "wcprob.sqlite")
    storage.init_schema()

    collector = Collector(storage=storage, sources=[GoodSource(), BadSource()])
    collector.collect_once()

    observations = storage.latest_observations()
    health = storage.latest_health()

    assert observations[0].country == "France"
    assert {row.source: row.ok for row in health} == {"good": True, "bad": False}
