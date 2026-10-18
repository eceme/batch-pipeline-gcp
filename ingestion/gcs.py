"""Write ingestion output to Google Cloud Storage."""

import json

from google.cloud import storage
from google.cloud.storage.retry import DEFAULT_RETRY

from ingestion.auth import get_credentials


def build_client(impersonate_sa: str | None = None) -> storage.Client:
    """Return a Storage client, impersonating a service account if one is given."""
    credentials, project = get_credentials(impersonate_sa)
    return storage.Client(credentials=credentials, project=project)


def raw_path(snapshot_date: str) -> str:
    """Return the object path of one day's raw GitHub file."""
    return f"raw/github/dt={snapshot_date}/repos.jsonl"


def upload_jsonl(client: storage.Client, bucket: str, path: str, records: list[dict]) -> str:
    """Write records as JSON Lines to gs://bucket/path, replacing any existing object."""
    data = "".join(json.dumps(record) + "\n" for record in records)
    blob = client.bucket(bucket).blob(path)
    # Uploads are not retried by default; safe here because overwriting is idempotent.
    blob.upload_from_string(data, content_type="application/x-ndjson", retry=DEFAULT_RETRY)
    return f"gs://{bucket}/{path}"
