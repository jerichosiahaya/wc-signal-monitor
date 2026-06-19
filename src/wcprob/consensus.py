from collections import defaultdict

from wcprob.models import ConsensusRow, SourceObservation


def build_consensus(observations: list[SourceObservation]) -> list[ConsensusRow]:
    latest_by_country_source: dict[tuple[str, str], SourceObservation] = {}

    for row in observations:
        latest_by_country_source[(row.country, row.source)] = row

    values: dict[str, list[float]] = defaultdict(list)
    sources: dict[str, set[str]] = defaultdict(set)

    for row in latest_by_country_source.values():
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
