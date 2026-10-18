from datetime import date
from unittest.mock import MagicMock

from google.cloud import bigquery

from ingestion.load_to_bigquery import load_partition


def test_load_partition_replaces_only_that_days_partition():
    client = MagicMock()
    uri = "gs://my-bucket/raw/github/dt=2026-10-16/repos.jsonl"

    job = load_partition(client, uri, "raw.github_repos", date(2026, 10, 16))

    source, destination = client.load_table_from_uri.call_args.args
    assert source == uri
    assert destination == "raw.github_repos$20261016"

    config = client.load_table_from_uri.call_args.kwargs["job_config"]
    assert config.source_format == bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    assert config.write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE
    assert config.create_disposition == bigquery.CreateDisposition.CREATE_NEVER

    job.result.assert_called_once()
