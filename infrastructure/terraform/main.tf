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

# IAM bindings for Cloud Run Jobs to access existing secrets
resource "google_secret_manager_secret_iam_member" "ingestion_job_secret_access" {
  secret_id = "IGDB_CLIENT_ID"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:18815352760-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "ingestion_job_secret_access_secret" {
  secret_id = "IGDB_CLIENT_SECRET"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:18815352760-compute@developer.gserviceaccount.com"
}

# GCS Buckets for data and models
resource "google_storage_bucket" "data_bucket" {
  name          = "igdb-recommendation-system-data"
  location      = "europe-west1"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "models_bucket" {
  name          = "igdb-recommendation-system-models"
  location      = "europe-west1"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Cloud Run Jobs for pipeline steps
resource "google_cloud_run_v2_job" "ingestion_job" {
  name     = "igdb-ingestion"
  location = "europe-west1"

  template {
    template {
      containers {
        image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-ingestion:latest"
        env {
          name  = "DATA_BUCKET"
          value = google_storage_bucket.data_bucket.name
        }
        env {
          name  = "GCS_PREFIX"
          value = "raw/"
        }
        env {
          name = "IGDB_CLIENT_ID"
          value_source {
            secret_key_ref {
              secret  = "IGDB_CLIENT_ID"
              version = "latest"
            }
          }
        }
        env {
          name = "IGDB_CLIENT_SECRET"
          value_source {
            secret_key_ref {
              secret  = "IGDB_CLIENT_SECRET"
              version = "latest"
            }
          }
        }
        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }
      timeout = "3600s"  # 1 hour timeout
    }
  }
}

resource "google_cloud_run_v2_job" "processing_job" {
  name     = "igdb-processing"
  location = "europe-west1"

  template {
    template {
      containers {
        image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-processing:latest"
        env {
          name  = "DATA_BUCKET"
          value = google_storage_bucket.data_bucket.name
        }
        env {
          name  = "GCS_PREFIX"
          value = "processed/"
        }
        resources {
          limits = {
            cpu    = "1"
            memory = "1Gi"
          }
        }
      }
      timeout = "1800s"  # 30 minutes timeout
    }
  }
}

resource "google_cloud_run_v2_job" "training_job" {
  name     = "igdb-training"
  location = "europe-west1"

  template {
    template {
      containers {
        image = "europe-west1-docker.pkg.dev/igdb-recommendation-system/igdb-repo/igdb-training:latest"
        env {
          name  = "DATA_BUCKET"
          value = google_storage_bucket.data_bucket.name
        }
        env {
          name  = "MODEL_BUCKET"
          value = google_storage_bucket.models_bucket.name
        }
        env {
          name  = "GCS_PREFIX"
          value = "processed/"
        }
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
      timeout = "3600s"  # 1 hour timeout
    }
  }
}

# Cloud Scheduler for daily data ingestion
resource "google_cloud_scheduler_job" "ingestion_scheduler" {
  name        = "igdb-ingestion-scheduler"
  description = "Daily IGDB data ingestion at 02:00 Europe/Stockholm"
  schedule    = "0 2 * * *"
  time_zone   = "Europe/Stockholm"
  region      = "europe-west1"

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_job.ingestion_job.location}-run.googleapis.com/v2/projects/${google_cloud_run_v2_job.ingestion_job.project}/locations/${google_cloud_run_v2_job.ingestion_job.location}/jobs/${google_cloud_run_v2_job.ingestion_job.name}:run"
    oidc_token {
      service_account_email = "github-actions@igdb-recommendation-system.iam.gserviceaccount.com"
    }
  }
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

output "data_bucket_name" {
  description = "Name of the data storage bucket"
  value       = google_storage_bucket.data_bucket.name
}

output "models_bucket_name" {
  description = "Name of the models storage bucket"
  value       = google_storage_bucket.models_bucket.name
}

output "ingestion_job_name" {
  description = "Name of the ingestion Cloud Run job"
  value       = google_cloud_run_v2_job.ingestion_job.name
}

output "processing_job_name" {
  description = "Name of the processing Cloud Run job"
  value       = google_cloud_run_v2_job.processing_job.name
}

output "training_job_name" {
  description = "Name of the training Cloud Run job"
  value       = google_cloud_run_v2_job.training_job.name
}
