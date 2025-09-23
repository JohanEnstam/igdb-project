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

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "igdb_repo" {
  location      = "europe-west1"
  repository_id  = "igdb-repo"
  description   = "Docker repository for IGDB recommendation system"
  format        = "DOCKER"
}

# Frontend Cloud Run Service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "igdb-frontend"
  location = "europe-west1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    containers {
      image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-frontend:latest"
      ports {
        container_port = 8080
      }
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = "https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app"
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }
}

# Public access for frontend
resource "google_cloud_run_service_iam_member" "frontend_public_access" {
  project  = "igdb-recommendation-system"
  location = "europe-west1"
  service  = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "artifact_registry_url" {
  description = "URL of the Artifact Registry repository"
  value       = google_artifact_registry_repository.igdb_repo.name
}
