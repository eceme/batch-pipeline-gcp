from datetime import UTC, date, datetime
from unittest.mock import MagicMock

import pytest
import requests

from ingestion.fetch_repos import API_URL, build_record, fetch_repo, load_repos, parse_args


def test_load_repos_returns_name_category_pairs(tmp_path):
    toml_file = tmp_path / "repos.toml"
    toml_file.write_text("""
[categories]
streaming = ["apache/kafka", "apache/flink"]
olap = ["duckdb/duckdb"]
""")

    result = load_repos(toml_file)

    assert result == [
        ("apache/kafka", "streaming"),
        ("apache/flink", "streaming"),
        ("duckdb/duckdb", "olap"),
    ]


def test_fetch_repo_returns_json_body():
    session = MagicMock()
    session.get.return_value.json.return_value = {"full_name": "apache/kafka"}

    result = fetch_repo(session, "apache/kafka")

    assert result == {"full_name": "apache/kafka"}
    session.get.assert_called_once_with(f"{API_URL}/repos/apache/kafka", timeout=10)


def test_fetch_repo_raises_on_http_error():
    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

    with pytest.raises(requests.HTTPError):
        fetch_repo(session, "apache/does-not-exist")


def test_build_record_wraps_payload_with_metadata():
    repo = {"id": 1, "full_name": "apache/kafka", "stargazers_count": 100}

    before = datetime.now(UTC)
    record = build_record(repo, "streaming", "2026-10-16")
    after = datetime.now(UTC)

    assert record["snapshot_date"] == "2026-10-16"
    assert record["category"] == "streaming"
    assert record["payload"] == repo
    assert before <= datetime.fromisoformat(record["ingested_at"]) <= after


def test_parse_args_reads_date():
    args = parse_args(["--date", "2026-10-16"])

    assert args.date == date(2026, 10, 16)


def test_parse_args_defaults_to_today_in_utc():
    args = parse_args([])

    assert args.date == datetime.now(UTC).date()


@pytest.mark.parametrize("value", ["2026-13-01", "17-10-2026", "yesterday"])
def test_parse_args_rejects_invalid_date(value):
    with pytest.raises(SystemExit):
        parse_args(["--date", value])
