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
