"""Google Cloud credentials shared by the ingestion scripts."""

import google.auth
from google.auth import impersonated_credentials
from google.auth.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def get_credentials(impersonate_sa: str | None = None) -> tuple[Credentials, str | None]:
    """Return ADC credentials and project, impersonating a service account if one is given."""
    credentials, project = google.auth.default(scopes=SCOPES)
    if impersonate_sa:
        credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=impersonate_sa,
            target_scopes=SCOPES,
        )
    return credentials, project
