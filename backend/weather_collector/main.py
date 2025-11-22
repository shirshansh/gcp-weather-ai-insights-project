import requests
import json
import os
from datetime import datetime, timezone
from google.cloud import storage
from google.cloud import secretmanager

def log_json(message: dict):
    """
    Logs a dictionary as JSON to stdout for Cloud Logging.
    """

    print(json.dumps(message), flush=True)

def get_secret():
    """
    Fetches a secret's latest version value from Google Secret Manager.
    """

    log_json({"event": "secret_access_start"})
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = os.getenv("SECRET_RESOURCE")
        response = client.access_secret_version(request={"name": name})

        log_json({"event": "secret_access_success"})
        return response.payload.data.decode("UTF-8").strip()

    except Exception as e:
        log_json({"event": "secret_access_error", "error": str(e)})
        raise

API_KEY = get_secret()
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
CITIES = ["London", "New York", "Tokyo", "Delhi", "Sydney"]

def fetch_and_upload_weather_data(request):
    """
    Fetch weather data for 5 global cities and upload it to Google Cloud Storage.
    """

    log_json({"event": "collector_start"})

    if not API_KEY:
        log_json({"event": "no_api_key", "error": "API_KEY missing"})
        return {"error": "API_KEY not set"}, 500
    if not BUCKET_NAME:
        log_json({"event": "no_bucket", "error": "BUCKET_NAME missing"})
        return {"error": "GCS_BUCKET_NAME not set"}, 500
    
    all_weather = {}
    errors = []

    # Fetching weather data
    for city in CITIES:
        try:
            log_json({"event": "fetch_weather_start", "city": city})

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raising an exception for 4xx and 5xx status codes
            all_weather[city] = response.json()

            log_json({"event": "fetch_weather_success", "city": city})

        except Exception as e:
            log_json({"event": "fetch_weather_error", "city": city, "error": str(e)})
            errors.append(f"Failed to fetch {city}: {e}")

    if not all_weather:
        log_json({"event": "collector_no_data"})
        return {"error": "No data fetched"}, 500
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"raw_weather_data/weather-{timestamp}.json"

    # Uploading fetched weather data to GCS
    try:
        log_json({"event": "upload_start", "file": filename})

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(json.dumps(all_weather), content_type="application/json")
        
        log_json({"event": "upload_success", "file": filename})

    except Exception as e:
        log_json({"event": "upload_error", "file": filename, "error": str(e)})
        return {"error": f"Upload failed: {e}"}, 500

    result = {
        "status": "success",
        "uploaded_file": filename,
        "cities_fetched": list(all_weather.keys()),
        "errors": errors if errors else "none"
    }

    log_json({"event": "collector_complete", "file": filename})
    return result, 200