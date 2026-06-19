import pytest

from wcprob.odds import american_to_probability, decimal_to_probability, remove_overround


def test_decimal_to_probability():
    assert decimal_to_probability(5.0) == 0.2


def test_american_positive_to_probability():
    assert round(american_to_probability(400), 4) == 0.2


def test_american_negative_to_probability():
    assert round(american_to_probability(-150), 4) == 0.6


def test_remove_overround_normalizes_market():
    cleaned = remove_overround({"France": 0.25, "Spain": 0.20, "England": 0.15})
    assert round(sum(cleaned.values()), 6) == 1.0
    assert cleaned["France"] > cleaned["Spain"] > cleaned["England"]


def test_remove_overround_rejects_negative_probability():
    with pytest.raises(ValueError):
        remove_overround({"A": 0.5, "B": -0.1})


def test_remove_overround_rejects_probability_greater_than_one():
    with pytest.raises(ValueError):
        remove_overround({"A": 1.2})
