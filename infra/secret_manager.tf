resource "google_secret_manager_secret" "owm_api_key" {
  project   = var.project_id
  secret_id = "openweather_api_key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "owm_api_key_version" {
  secret      = google_secret_manager_secret.owm_api_key.id
  secret_data = var.openweathermap_api_key
}
