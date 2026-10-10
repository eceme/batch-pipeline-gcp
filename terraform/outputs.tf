output "raw_bucket_name" {
  description = "Name of the raw landing bucket"
  value       = google_storage_bucket.raw.name
}

output "pipeline_service_account_email" {
  description = "Email of the pipeline service account (used for impersonation)"
  value       = google_service_account.pipeline.email
}
