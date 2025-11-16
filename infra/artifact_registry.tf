resource "google_artifact_registry_repository" "frontend_repo" {
  provider = google
  project  = var.project_id

  location      = var.region
  repository_id = "frontend"
  description   = "Artifact Registry repo for frontend Docker images"

  format = "DOCKER"
}
