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

resource "google_storage_bucket_iam_member" "process_sa_gcs_writer" {
  bucket = google_storage_bucket.weather_data_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.process_service_account.email}"
}

resource "google_storage_bucket_iam_member" "process_sa_gcs_reader" {
  bucket = google_storage_bucket.weather_data_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.process_service_account.email}"
}

resource "google_project_iam_member" "process_eventarc" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.process_service_account.email}"
}

resource "google_project_iam_member" "process_vertexai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.process_service_account.email}"
}

resource "google_cloud_run_v2_service_iam_member" "eventarc_invoker" {
  name     = data.google_cloud_run_v2_service.weather_processor_service.name
  project  = var.project_id
  location = var.region

  role   = "roles/run.invoker"
  member = "serviceAccount:${google_service_account.process_service_account.email}"
}