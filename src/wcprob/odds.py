def decimal_to_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("decimal_odds must be greater than 1")
    return 1 / decimal_odds


def american_to_probability(american_odds: int) -> float:
    if american_odds > 0:
        return 100 / (american_odds + 100)
    if american_odds < 0:
        return abs(american_odds) / (abs(american_odds) + 100)
    raise ValueError("american_odds cannot be 0")


def remove_overround(probabilities: dict[str, float]) -> dict[str, float]:
    total = sum(probabilities.values())
    if total <= 0:
        raise ValueError("probability total must be positive")
    return {
        country: probability / total
        for country, probability in probabilities.items()
    }
