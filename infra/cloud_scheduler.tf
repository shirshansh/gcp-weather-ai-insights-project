# Fetching project info for default SA
data "google_project" "project" {
  project_id = var.project_id
}

# Cloud Scheduler uses this service account by default
locals {
  scheduler_service_account = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Allowing only Scheduler SA to invoke our Cloud Function
resource "google_cloud_run_service_iam_member" "weather_collector_scheduler_invoker" {
  project  = var.project_id
  location = var.region
  service  = data.google_cloud_run_v2_service.weather_collector_service.name

  role   = "roles/run.invoker"
  member = "serviceAccount:${local.scheduler_service_account}"
}

# Cloud Scheduler
resource "google_cloud_scheduler_job" "weather_collector_scheduler" {
  name        = var.scheduler_name
  description = "Fetches and Stores weather data as raw JSON every 30 minutes"
  project     = var.project_id
  region      = var.region

  schedule  = var.schedule_frequency
  time_zone = "Asia/Calcutta"

  http_target {
    uri         = data.google_cloud_run_v2_service.weather_collector_service.uri
    http_method = "POST"

    # Generate OIDC token signed by this service account
    oidc_token {
      service_account_email = local.scheduler_service_account
    }
  }

  depends_on = [
    google_cloud_run_service_iam_member.weather_collector_scheduler_invoker
  ]
}