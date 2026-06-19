from wcprob.consensus import build_consensus
from wcprob.models import SourceKind, SourceObservation


def test_consensus_averages_country_probabilities():
    rows = [
        SourceObservation(
            source="odds",
            source_kind=SourceKind.ODDS_API,
            country="France",
            raw_value="5.0",
            implied_probability=0.20,
        ),
        SourceObservation(
            source="market",
            source_kind=SourceKind.PREDICTION_MARKET,
            country="France",
            raw_value="0.22",
            implied_probability=0.22,
        ),
        SourceObservation(
            source="market",
            source_kind=SourceKind.PREDICTION_MARKET,
            country="Spain",
            raw_value="0.16",
            implied_probability=0.16,
        ),
    ]

    consensus = build_consensus(rows)

    assert consensus[0].country == "France"
    assert consensus[0].probability == 0.21
    assert consensus[0].source_count == 2
