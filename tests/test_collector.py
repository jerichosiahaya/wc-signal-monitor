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
    health_by_source = {row.source: row for row in health}

    assert len(observations) == 1
    assert observations[0].country == "France"
    assert health_by_source["good"].ok is True
    assert health_by_source["good"].message == "stored 1 observations"
    assert health_by_source["bad"].ok is False
    assert health_by_source["bad"].message == "network failed"
