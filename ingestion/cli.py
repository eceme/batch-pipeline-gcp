"""Command-line arguments shared by the ingestion scripts."""

import argparse
from datetime import UTC, date, datetime


def parse_args(description: str | None, argv: list[str] | None = None) -> argparse.Namespace:
    """Parse --date, defaulting to today in UTC."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=datetime.now(UTC).date(),
        help="Snapshot date as YYYY-MM-DD (default: today in UTC)",
    )
    return parser.parse_args(argv)  # None means sys.argv; tests pass a list.
