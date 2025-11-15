resource "google_storage_bucket" "weather_data_bucket" {
  project                     = var.project_id
  name                        = var.bucket_name
  location                    = var.region
  force_destroy               = false # prevents accidental deletion of objects when destroying the bucket
  uniform_bucket_level_access = true

  storage_class = "STANDARD"
}
