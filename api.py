from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import json
from model_utils import load_model

app = Flask(__name__)

# Load model and encoder
print("Loading model...")
model, le = load_model()
if model:
    print("Model loaded successfully.")
else:
    print("Model not found! Make sure to run `model_utils.py` first.")

# Load config
with open("parking_config.json", "r") as f:
    PARKING_CONFIG = json.load(f)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "running", "endpoints": ["/predict", "/areas"]})

@app.route("/areas", methods=["GET"])
def get_areas():
    return jsonify(PARKING_CONFIG)

@app.route("/predict", methods=["GET"])
def predict():
    """
    Query Params:
    - area_name: str (e.g., 'area1')
    - timestamp: str (ISO format, e.g., '2025-12-12T14:30:00')
    """
    if not model or not le:
        return jsonify({"error": "Model not loaded"}), 500

    area_name = request.args.get("area_name")
    timestamp_str = request.args.get("timestamp")

    if not area_name or not timestamp_str:
        return jsonify({"error": "Missing area_name or timestamp"}), 400

    try:
        dt = datetime.fromisoformat(timestamp_str)
        hour = dt.hour
        day = dt.day
        weekday = dt.weekday()

        # Prepare input for model
        input_data = pd.DataFrame([{
            "hour": hour,
            "day": day,
            "weekday": weekday
        }])

        # --- IMPORTANT ---
        # The current model predicts just a "class" (0 or 1) based on time features alone.
        # However, a real model would likely take a slot_id too. 
        # Since the current notebook training dropped 'slot_id' from feature_cols = ["hour", "day", "weekday"],
        # the model predicts the general unavailability trend or status for effectively "any" slot at this time.
        # This is a simplification from the notebook code.
        
        prediction_idx = model.predict(input_data)[0]
        
        # XGBoost output might be raw or label-encoded.
        # In notebook: classes=['Present' 'Unoccupied'] -> [1, 0] typically if sorted alphabetically?
        # Check le.classes_
        status_label = "Unknown"
        if 0 <= prediction_idx < len(le.classes_):
             status_label = le.classes_[prediction_idx] # e.g. "Present" or "Unoccupied"
        
        # Map to user-friendly terms
        is_free = False
        if "Unoccupied" in status_label or "Free" in status_label or status_label == "0":
             is_free = True
        elif status_label == 0: # If raw int
             is_free = True

        return jsonify({
            "is_free": is_free,
            "predicted_label": str(status_label),
            "input_time": timestamp_str
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
