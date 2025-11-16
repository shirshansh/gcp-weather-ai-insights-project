# gke cluster (autopilot)
resource "google_container_cluster" "frontend_cluster" {
  name               = var.gke_name
  project            = var.project_id
  location           = var.region

  enable_autopilot   = true
}

# Cluster credentials for Kubernetes provider
data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = google_container_cluster.frontend_cluster.endpoint
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.frontend_cluster.master_auth[0].cluster_ca_certificate
  )
}