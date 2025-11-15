resource "google_secret_manager_secret_iam_member" "fetch_sa_secret_access" {
  secret_id = google_secret_manager_secret.owm_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.fetch_service_account.email}"
}

resource "google_storage_bucket_iam_member" "fetch_sa_gcs_writer" {
  bucket = google_storage_bucket.weather_data_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.fetch_service_account.email}"
}
