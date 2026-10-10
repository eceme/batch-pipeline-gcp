variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Default region for regional resources"
  type        = string
  default     = "europe-west3" # Frankfurt
}

variable "location" {
  description = "Multi-region for GCS and BigQuery. Must match so BigQuery can load from the bucket."
  type        = string
  default     = "EU"
}

variable "bq_datasets" {
  description = "BigQuery datasets, one per pipeline layer"
  type        = set(string)
  default     = ["raw", "staging", "marts"]
}

variable "raw_retention_days" {
  description = "Days before raw files in GCS are deleted automatically"
  type        = number
  default     = 30
}

variable "service_account_name" {
  description = "Account ID of the pipeline service account (6-30 chars: lowercase letters, digits, hyphens)"
  type        = string
  default     = "pipeline-sa"
}

variable "deployer_email" {
  description = "Google account that deploys the infrastructure and impersonates the pipeline service account"
  type        = string
}
