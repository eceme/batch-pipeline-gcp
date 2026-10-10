resource "google_storage_bucket" "raw" {
  name     = "${var.project_id}-raw" # Bucket names are globally unique.
  location = var.location

  # Lets `terraform destroy` remove the bucket with files in it; false in production.
  force_destroy = true

  uniform_bucket_level_access = true # IAM only, no per-object ACLs.
  public_access_prevention    = "enforced"

  # Raw files are already in BigQuery, so old copies are deleted to save cost.
  lifecycle_rule {
    condition {
      age = var.raw_retention_days
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    project = "batch-pipeline"
    layer   = "raw"
  }
}
