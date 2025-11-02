import requests
import json
import os
from datetime import datetime, timezone
from google.cloud import storage

API_KEY = os.getenv("API_KEY")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
CITIES = ["London", "New York", "Tokyo", "Delhi", "Sydney"]

def fetch_and_upload_weather_data(request):
    """
    Fetch weather data for 5 global cities and upload it to Google Cloud Storage.
    """

    if not API_KEY:
        return {"error": "API_KEY not set"}, 500
    if not BUCKET_NAME:
        return {"error": "GCS_BUCKET_NAME not set"}, 500
    
    all_weather = {}
    errors = []

    # Fetching weather data
    for city in CITIES:
        try:
            print(f"Fetching weather data for {city}")

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raising an exception for 4xx and 5xx status codes
            all_weather[city] = response.json()

            print(f"✅ Successfully fetched weather data for {city}")

        except Exception as e:
            error_msg = f"⚠️ Failed to fetch {city}: {e}"
            print(error_msg)
            errors.append(error_msg)

    if not all_weather:
        print("❌ No weather data fetched. Aborting upload.")
        return {"error": "No data fetched"}, 500
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"raw_weather_data/weather-{timestamp}.json"

    # Uploading fetched weather data to GCS
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(json.dumps(all_weather), content_type="application/json")
        print(f"✅ Uploaded {filename}")

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return {"error": f"Upload failed: {e}"}, 500

    result = {
        "status": "success",
        "uploaded_file": filename,
        "cities_fetched": list(all_weather.keys()),
        "errors": errors if errors else "none"
    }
    return result, 200