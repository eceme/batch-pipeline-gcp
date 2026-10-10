# No key is created for this account; local tools impersonate it.
resource "google_service_account" "pipeline" {
  account_id   = var.service_account_name
  display_name = "Batch pipeline runner"
  description  = "Runs ingestion, dbt and Airflow jobs with least-privilege access"
}

# *_iam_member only adds one member, unlike *_iam_binding/_policy which overwrite existing access.
resource "google_project_iam_member" "pipeline_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = google_service_account.pipeline.member
}

resource "google_bigquery_dataset_iam_member" "pipeline_data_editor" {
  for_each = google_bigquery_dataset.datasets

  dataset_id = each.value.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = google_service_account.pipeline.member
}

resource "google_storage_bucket_iam_member" "pipeline_raw_object_admin" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = google_service_account.pipeline.member
}

# Lets the deployer impersonate this service account only (even an Owner needs it).
resource "google_service_account_iam_member" "deployer_token_creator" {
  service_account_id = google_service_account.pipeline.name # Full resource name, not the email.
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "user:${var.deployer_email}"
}
