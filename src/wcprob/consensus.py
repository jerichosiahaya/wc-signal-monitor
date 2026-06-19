from collections import defaultdict

from wcprob.models import ConsensusRow, SourceObservation


def build_consensus(observations: list[SourceObservation]) -> list[ConsensusRow]:
    values: dict[str, list[float]] = defaultdict(list)
    sources: dict[str, set[str]] = defaultdict(set)

    for row in observations:
        values[row.country].append(row.implied_probability)
        sources[row.country].add(row.source)

    consensus = [
        ConsensusRow(
            country=country,
            probability=round(sum(probabilities) / len(probabilities), 4),
            source_count=len(sources[country]),
        )
        for country, probabilities in values.items()
    ]
    return sorted(consensus, key=lambda row: row.probability, reverse=True)
