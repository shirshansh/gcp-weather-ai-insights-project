import re
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

def log_json(message: dict):
    """
    Logs a dictionary as JSON to stdout for Cloud Logging.
    """

    print(json.dumps(message), flush=True)

def clean_json_response(text):
    """
    Cleans model output to extract valid JSON from Markdown or noisy responses.
    Handles cases like:
    ```json
    {...}
    ```
    or extra whitespace / comments.
    """

    if not text:
        return None

    # Remove Markdown code fences like ```json ... ```
    text = re.sub(r"```(?:json)?", "", text)
    text = text.replace("```", "").strip()

    # Try to extract first {...} JSON block only
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    return text

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

    log_json({"event": "processor_start", "bucket": event.get("bucket"), "file": event.get("name")})
    
    if not PROJECT_ID:
        log_json({"event": "missing_env", "variable": "PROJECT_ID"})
        raise RuntimeError("PROJECT_ID not set")
    if not BUCKET_NAME:
        log_json({"event": "missing_env", "variable": "GCS_BUCKET_NAME"})
        raise RuntimeError("GCS_BUCKET_NAME not set")
    
    try:
        bucket_name = event.get("bucket")
        file_name = event.get("name")
        log_json({"event": "triggered_by_file", "bucket": bucket_name, "file": file_name})

        # Checking that this is from our intended bucket and folder
        if bucket_name != BUCKET_NAME or not file_name.startswith(RAW_PREFIX):
            log_json({"event": "ignored_file", "bucket": bucket_name, "file": file_name})
            return ("ignored", 200)
        
        # Loading raw data
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        raw_data = json.loads(blob.download_as_text())
        log_json({"event": "raw_load_success", "file": file_name})

        prompt = build_prompt(raw_data)
        log_json({"event": "vertex_request_start", "model": MODEL_NAME})

        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        result_text = response.text.strip()
        log_json({"event": "vertex_response_received"})

        result_text = clean_json_response(result_text)

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

        log_json({"event": "processor_success", "output_file": output_name})
        return {"status": "ok", "file": output_name}
    
    except json.JSONDecodeError:
        log_json({"event": "invalid_json_output", "raw_output": result_text})

        # Saving the invalid output
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        debug_name = f"{PROCESSED_PREFIX}invalid-json-{timestamp}.txt"
        bucket = storage_client.bucket(BUCKET_NAME)
        bucket.blob(debug_name).upload_from_string(result_text, content_type="text/plain")
        log_json({"event": "debug_saved", "debug_file": debug_name})
        return {"error": "invalid_json", "debug_file": debug_name}, 500

    except Exception as e:
        log_json({"event": "processor_error", "error": str(e)})
        return {"error": f"{e}"}, 500
        
