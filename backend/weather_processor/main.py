import os
import json
from datetime import datetime, timezone
from google.cloud import storage
from google import genai

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
RAW_PREFIX = "raw_weather_data/"
PROCESSED_PREFIX = "processed_weather_data/"
MODEL_NAME = "gemini-2.5-flash"
LOCATION = "asia-south1"

# Intialized Clients
storage_client = storage.Client()
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def build_prompt(raw_data):
    """
    Builds the strict JSON-only prompt used for weather mood summarization.
    """

    prompt = (
        "You are an AI weather analyst. Analyze the following weather data (in JSON) "
        "for each city and produce a structured output (JSON).\n\n"

        "Return **ONLY a JSON object** with the following keys:\n"
        "{\"city\":{\"mood\":\"<a short human emotion or phrase describing the weather mood>\","
        "\"summary\":\"<1-2 sentence friendly description of the weather, in natural English>\"}}\n\n"

        "Example of a response:\n"
        "{\"London\":{\"mood\":\"calm\",\"summary\":\"Clear sky with gentle breeze.\"},"
        "\"Tokyo\":{\"mood\":\"humid\",\"summary\":\"Warm and slightly cloudy.\"}}\n\n"

        "**Requirements (do not ignore):**"
        "1. **Respond ONLY with valid JSON.** No explanation, no markdown, no backticks, no extra text. "
        "2. Use double quotes for strings. "
        "3. Output must be a single JSON object whose top-level keys are the city names. "
        "4. If you must guess missing fields, infer sensibly but don’t invent numeric values.\n\n"

        "Guidelines:\n"
        "- Use clear, neutral, and descriptive language (avoid exaggeration).\n"
        "- Keep the mood short (only 1 word).\n"
        "- Ensure the summary sounds like a natural weather report summary.\n"
        "- If data is missing, infer based on available information logically.\n\n"

        "Weather data:\n"
        f"{json.dumps(raw_data, indent=2)}"
    )
    return prompt

def process_weather_data(event, context):
    """
    Cloud Function triggered when a new raw weather JSON is uploaded.
    Reads the file, calls Vertex AI to summarize, and saves processed JSON to GCS.
    """
    
    if not PROJECT_ID:
        raise RuntimeError("PROJECT_ID not set")
    if not BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME not set")
    
    try:
        bucket_name = event.get("bucket")
        file_name = event.get("name")
        print(f"Triggered by file: gs://{bucket_name}/{file_name}")

        # Checking that this is from our intended bucket and folder
        if bucket_name != BUCKET_NAME or not file_name.startswith(RAW_PREFIX):
            print("Skipping unrelated file or bucket.")
            return ("ignored", 200)
        
        # Loading raw data
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        raw_data = json.loads(blob.download_as_text())
        print("✅ Raw weather data loaded successfully.")

        prompt = build_prompt(raw_data)
        print("Sending prompt to Vertex AI...")

        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        result_text = response.text.strip()
        print("Model Response Received.")

        processed_json = json.loads(result_text)

        # Prepare processed result object
        out_payload = {
            "source_file": file_name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL_NAME,
            "result": processed_json
        }

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        output_name = f"{PROCESSED_PREFIX}processed-{timestamp}.json"
        bucket.blob(output_name).upload_from_string(
            json.dumps(out_payload, indent=2),
            content_type="application/json"
        )

        print(f"✅ Processed file saved to gs://{bucket_name}/{output_name}")
        return {"status": "ok", "file": output_name}
    
    except json.JSONDecodeError:
        print("⚠️ Model output was not valid JSON.")

        # Saving the invalid output
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        debug_name = f"{PROCESSED_PREFIX}invalid-json-{timestamp}.txt"
        bucket = storage_client.bucket(BUCKET_NAME)
        bucket.blob(debug_name).upload_from_string(result_text, content_type="text/plain")
        print(f"⚠️ Saved invalid output to gs://{BUCKET_NAME}/{debug_name}")
        return {"error": "invalid_json", "debug_file": debug_name}, 500

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": f"{e}"}, 500
        
