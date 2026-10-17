"""Write ingestion output to Google Cloud Storage."""

import json

import google.auth
from google.auth import impersonated_credentials
from google.cloud import storage
from google.cloud.storage.retry import DEFAULT_RETRY

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def build_client(impersonate_sa: str | None = None) -> storage.Client:
    """Return a Storage client using ADC, impersonating a service account if one is given."""
    credentials, project = google.auth.default(scopes=SCOPES)
    if impersonate_sa:
        credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=impersonate_sa,
            target_scopes=SCOPES,
        )
    return storage.Client(credentials=credentials, project=project)


def upload_jsonl(client: storage.Client, bucket: str, path: str, records: list[dict]) -> str:
    """Write records as JSON Lines to gs://bucket/path, replacing any existing object."""
    data = "".join(json.dumps(record) + "\n" for record in records)
    blob = client.bucket(bucket).blob(path)
    # Uploads are not retried by default; safe here because overwriting is idempotent.
    blob.upload_from_string(data, content_type="application/x-ndjson", retry=DEFAULT_RETRY)
    return f"gs://{bucket}/{path}"
