import json
from unittest.mock import MagicMock

from ingestion.gcs import upload_jsonl


def test_upload_jsonl_writes_one_json_line_per_record():
    client = MagicMock()
    records = [{"repo": "apache/kafka", "stars": 1}, {"repo": "apache/flink", "stars": 2}]

    uri = upload_jsonl(client, "my-bucket", "raw/github/dt=2026-10-16/repos.jsonl", records)

    client.bucket.assert_called_once_with("my-bucket")
    client.bucket.return_value.blob.assert_called_once_with("raw/github/dt=2026-10-16/repos.jsonl")

    upload = client.bucket.return_value.blob.return_value.upload_from_string
    data = upload.call_args.args[0]
    lines = data.splitlines()
    assert data.endswith("\n")
    assert [json.loads(line) for line in lines] == records
    assert upload.call_args.kwargs["content_type"] == "application/x-ndjson"

    assert uri == "gs://my-bucket/raw/github/dt=2026-10-16/repos.jsonl"
