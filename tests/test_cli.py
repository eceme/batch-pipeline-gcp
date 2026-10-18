from datetime import UTC, date, datetime

import pytest

from ingestion.cli import parse_args


def test_parse_args_reads_date():
    args = parse_args("test", ["--date", "2026-10-16"])

    assert args.date == date(2026, 10, 16)


def test_parse_args_defaults_to_today_in_utc():
    args = parse_args("test", [])

    assert args.date == datetime.now(UTC).date()


@pytest.mark.parametrize("value", ["2026-13-01", "17-10-2026", "yesterday"])
def test_parse_args_rejects_invalid_date(value):
    with pytest.raises(SystemExit):
        parse_args("test", ["--date", value])
