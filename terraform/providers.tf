# No credentials here: the provider uses Application Default Credentials.
provider "google" {
  project = var.project_id
  region  = var.region
}
