terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket  = "igdb-recommendation-system-tf-state"
    prefix  = "terraform/state"
  }
}

provider "google" {
  project = "igdb-recommendation-system"
  region  = "europe-west1"
}

# Test bucket to verify Terraform setup
resource "google_storage_bucket" "test_bucket" {
  name          = "igdb-recommendation-system-test"
  location      = "europe-west1"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }
}
