# Auto-zip
data "archive_file" "weather_collector_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/weather_collector"
  output_path = "${path.module}/../zip/weather_collector.zip"
}

# Uploading ZIP to GCS bucket inside a folder for organization
resource "google_storage_bucket_object" "weather_collector_source" {
  name   = "cloud_functions/weather_collector/function-source.zip"
  bucket = google_storage_bucket.weather_data_bucket.name
  source = data.archive_file.weather_collector_zip.output_path
}

# Deploy Cloud Function Gen2 for weather_collector
resource "google_cloudfunctions2_function" "weather_collector" {
  name     = var.fetch_service_name
  project  = var.project_id
  location = var.region

  build_config {
    runtime     = "python313"
    entry_point = var.fetch_function_name

    source {
      storage_source {
        bucket = google_storage_bucket.weather_data_bucket.name
        object = google_storage_bucket_object.weather_collector_source.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.fetch_service_account.email

    environment_variables = {
      GCS_BUCKET_NAME = var.bucket_name
      SECRET_RESOURCE = google_secret_manager_secret_version.owm_api_key_version.name
    }
  }
}

# Read the underlying Cloud Run service (mandatory for scheduler invocation later)
data "google_cloud_run_v2_service" "weather_collector_service" {
  name     = google_cloudfunctions2_function.weather_collector.name
  project  = var.project_id
  location = var.region
}
