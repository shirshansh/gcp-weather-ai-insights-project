from flask import Flask, jsonify
from flask_cors import CORS
from google.cloud import storage
import os, json

app = Flask(__name__)
CORS(app)

PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
PROCESSED_PREFIX = "processed_weather_data/"

@app.route("/weather", methods=["GET"])
def get_latest_weather():
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blobs = list(bucket.list_blobs(prefix=PROCESSED_PREFIX))

        if not blobs:
            return jsonify({"error": "No processed weather files found."}), 404

        latest_blob = sorted(blobs, key=lambda b: b.time_created, reverse=True)[0]
        data = json.loads(latest_blob.download_as_text())

        return jsonify({
            "status": "success",
            "source": latest_blob.name,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

# CI/CD test trigger