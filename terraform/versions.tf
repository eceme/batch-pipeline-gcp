terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0" # Any 7.x, never a breaking 8.0.
    }
  }
}
