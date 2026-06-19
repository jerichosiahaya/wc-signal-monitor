from wcprob.tui import format_probability


def test_format_probability():
    assert format_probability(0.214) == "21.4%"
