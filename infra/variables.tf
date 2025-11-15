variable "project_id" {
  description = "The GCP Project ID"
  type        = string
  default     = "cme-weather-project"
}

variable "region" {
  description = "Region for all resources"
  type        = string
  default     = "asia-south1"
}

variable "bucket_name" {
  description = "Name of the storage bucket for weather data"
  type        = string
  default     = "weather-data-openweather"
}

# Functions' Entry Point Name
variable "fetch_function_name" {
  description = "Name of the entry point of the Cloud Function that fetches weather data"
  type        = string
  default     = "fetch_and_upload_weather_data"
}

# Services Name
variable "fetch_service_name" {
  description = "Name of the Cloud Function that fetches weather data"
  type        = string
  default     = "fetch-and-upload-weather-data"
}

#  Service Accounts Name
variable "weather_fetch_sa_name" {
  description = "Name of the Service Account primarily responsible for fetching weather data"
  type        = string
  default     = "weather-fetch-sa"
}

variable "scheduler_name" {
  description = "Name of the Cloud Scheduler job"
  type        = string
  default     = "weather-data-ingestion-job"
}

variable "schedule_frequency" {
  description = "Cron schedule expression (every 30 minutes)"
  type        = string
  default     = "*/30 * * * *"
}

variable "openweathermap_api_key" {
  description = "Openweathermap API key"
  type        = string
  sensitive   = true
}
