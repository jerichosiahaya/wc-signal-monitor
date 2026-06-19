from wcprob.models import SourceHealth, SourceKind, SourceObservation
from wcprob.storage import Storage


def test_insert_and_read_latest_observations(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_observations(
        [
            SourceObservation(
                source="test",
                source_kind=SourceKind.ODDS_API,
                country="France",
                raw_value="+400",
                implied_probability=0.20,
            )
        ]
    )

    rows = storage.latest_observations()
    assert len(rows) == 1
    assert rows[0].country == "France"


def test_insert_source_health(tmp_path):
    db_path = tmp_path / "wcprob.sqlite"
    storage = Storage(db_path)
    storage.init_schema()

    storage.insert_health(SourceHealth(source="test", ok=True, message="ok"))

    rows = storage.latest_health()
    assert rows[0].source == "test"
    assert rows[0].ok is True
