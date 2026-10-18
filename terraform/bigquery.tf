# for_each (not count) keys datasets by name, so removing one never recreates the others.
resource "google_bigquery_dataset" "datasets" {
  for_each = var.bq_datasets

  dataset_id  = each.key
  location    = var.location # Must match the bucket for load jobs.
  description = "${each.key} layer of the GitHub batch pipeline"

  # Lets `terraform destroy` remove datasets that still contain tables.
  delete_contents_on_destroy = true

  labels = {
    project = "batch-pipeline"
    layer   = each.key
  }
}

resource "google_bigquery_table" "github_repos" {
  dataset_id  = google_bigquery_dataset.datasets["raw"].dataset_id
  table_id    = "github_repos"
  description = "Daily GitHub API snapshots; payload holds the unmodified API response"

  # Off so `terraform destroy` works; plan still shows any table replacement.
  deletion_protection = false

  # One partition per day lets each load replace only its own day.
  time_partitioning {
    type  = "DAY"
    field = "snapshot_date"
  }

  schema = jsonencode([
    { name = "snapshot_date", type = "DATE", mode = "REQUIRED" },
    { name = "ingested_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "category", type = "STRING", mode = "REQUIRED" },
    { name = "payload", type = "JSON", mode = "REQUIRED" },
  ])

  labels = {
    project = "batch-pipeline"
    layer   = "raw"
  }
}
