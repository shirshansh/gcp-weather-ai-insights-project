# Auto-zip
data "archive_file" "weather_processor_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/weather_processor"
  output_path = "${path.module}/../zip/weather_processor.zip"
}

# Uploading ZIP to GCS bucket inside a folder for organization
resource "google_storage_bucket_object" "weather_processor_source" {
  name   = "cloud_functions/weather_processor/function-source.zip"
  bucket = google_storage_bucket.weather_data_bucket.name
  source = data.archive_file.weather_processor_zip.output_path
}

# CLOUD FUNCTION (GEN 2)
resource "google_cloudfunctions2_function" "weather_processor" {
  name     = var.process_service_name
  project  = var.project_id
  location = var.region

  build_config {
    runtime     = "python313"
    entry_point = var.process_function_name
    source {
      storage_source {
        bucket = google_storage_bucket_object.weather_processor_source.bucket
        object = google_storage_bucket_object.weather_processor_source.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.process_service_account.email

    environment_variables = {
      PROJECT_ID        = var.project_id
      GCS_BUCKET_NAME       = var.bucket_name
    }
  }

  # Event trigger
  event_trigger {
    retry_policy = "RETRY_POLICY_DO_NOT_RETRY"
    
    event_type = "google.cloud.storage.object.v1.finalized"
    trigger_region = var.region
    event_filters {
      attribute = "bucket"
      value = var.bucket_name
    }
    service_account_email = google_service_account.process_service_account.email
  }

  depends_on = [
    google_storage_bucket_object.weather_processor_source,
    google_storage_bucket_iam_member.process_sa_gcs_reader,
    google_storage_bucket_iam_member.process_sa_gcs_writer,
    google_project_iam_member.process_eventarc,
    google_project_iam_member.process_vertexai
  ]
}

# Read the underlying Cloud Run service 
data "google_cloud_run_v2_service" "weather_processor_service" {
  name     = google_cloudfunctions2_function.weather_processor.name
  project  = var.project_id
  location = var.region
}