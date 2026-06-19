import pytest

from wcprob.cli import main


def test_main_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "usage: wcprob" in capsys.readouterr().out
