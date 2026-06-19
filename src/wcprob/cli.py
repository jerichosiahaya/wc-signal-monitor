import argparse


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="wcprob",
        description="World Cup 2026 signal monitor",
    )
    parser.parse_args(argv)
