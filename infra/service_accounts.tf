resource "google_service_account" "fetch_service_account" {
  project      = var.project_id
  account_id   = var.weather_fetch_sa_name
  display_name = "Weather Fetch Service Account"
}
