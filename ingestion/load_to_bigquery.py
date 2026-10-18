"""Load one day's raw GitHub file from GCS into its partition of raw.github_repos."""

import logging
import os
from datetime import date

from google.cloud import bigquery

from ingestion import cli, gcs
from ingestion.auth import get_credentials

TABLE = "raw.github_repos"

logger = logging.getLogger(__name__)


def build_client(impersonate_sa: str | None = None) -> bigquery.Client:
    """Return a BigQuery client, impersonating a service account if one is given."""
    credentials, project = get_credentials(impersonate_sa)
    return bigquery.Client(credentials=credentials, project=project)


def load_partition(
    client: bigquery.Client, uri: str, table: str, snapshot_date: date
) -> bigquery.LoadJob:
    """Replace one day's partition of table with the JSON Lines file at uri."""
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        create_disposition=bigquery.CreateDisposition.CREATE_NEVER,  # Terraform owns the table.
    )
    # The $YYYYMMDD decorator limits WRITE_TRUNCATE to that day's partition.
    destination = f"{table}${snapshot_date:%Y%m%d}"
    job = client.load_table_from_uri(uri, destination, job_config=job_config)
    job.result()  # Waits for the job and raises if it failed.
    return job


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = cli.parse_args(__doc__)

    bucket = os.environ["GCS_BUCKET"]
    client = build_client(os.environ.get("IMPERSONATE_SA"))

    uri = f"gs://{bucket}/{gcs.raw_path(args.date.isoformat())}"
    job = load_partition(client, uri, TABLE, args.date)
    logger.info("Loaded %d rows from %s into %s (job %s)", job.output_rows, uri, TABLE, job.job_id)


if __name__ == "__main__":
    main()
