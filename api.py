from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import json
import firebase_admin
from firebase_admin import credentials, firestore, db as realtime_db
import firebase_client
import firestore_client
from model_utils import load_model_and_encoders
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase App once
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
    })

db = firestore.client()

app = Flask(__name__)

# Load model and encoders
print("Loading model and encoders...")
model, le, slot_le = load_model_and_encoders()
if model:
    print("Model loaded successfully.")
else:
    print("Model not found! Run model_utils.py first.")

# Load config
try:
    with open("parking_config.json", "r") as f:
        PARKING_CONFIG = json.load(f)
except Exception as e:
    print(f"Error loading parking_config.json: {e}")
    PARKING_CONFIG = {}

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "running", 
        "endpoints": ["/predict", "/areas", "/parking", "/health"]
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "parking-api"}), 200

@app.route("/areas", methods=["GET"])
def get_areas():
    # Helper to return static config (coordinates etc)
    # Filter out API keys if present
    response = {k:v for k,v in PARKING_CONFIG.items() if "_api_key" not in k and "_url" not in k}
    return jsonify(response)

@app.route('/parking', methods=['GET'])
def get_parking_status():
    area_name = request.args.get('area')
    print(f"DEBUG: Fetching real-time status for area: {area_name}")
    try:
        data = firebase_client.get_parking_data(area_name)
        
        if data is None:
            print(f"DEBUG: Area '{area_name}' not found in Firebase.")
            return jsonify({"error": f"Area '{area_name}' not found"}), 404

        # FIX: Firebase sometimes converts maps with numeric keys ("1", "2") into lists.
        # Flutter expects a Map, so we convert it back if necessary.
        if data and 'slots' in data and isinstance(data['slots'], list):
            slots_list = data['slots']
            slots_dict = {}
            for i, slot_val in enumerate(slots_list):
                if slot_val is not None:
                    slots_dict[str(i)] = slot_val
            data['slots'] = slots_dict

        print(f"DEBUG: Data sent to App: {data}")
        return jsonify(data), 200
    except Exception as e:
        print(f"DEBUG: Error fetching real-time status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["GET", "POST"])
def predict():
    """
    Returns a LIST of free slot IDs for the predicted time.
    Query Params (GET) or Body (POST):
    - area_name: str (e.g., 'area1')
    - timestamp: str (ISO format)
    """
    if not model or not slot_le:
        return jsonify({"error": "Model not loaded"}), 500

    if request.method == 'POST':
        data = request.json
        area_name = data.get("area_name")
        timestamp_str = data.get("timestamp")
    else:
        area_name = request.args.get("area_name")
        timestamp_str = request.args.get("timestamp")

    if not area_name or not timestamp_str:
        return jsonify({"error": "Missing area_name or timestamp"}), 400
    
    # Get all slots for this area from config
    area_config = PARKING_CONFIG.get(area_name)
    if not area_config:
        return jsonify({"error": f"Area {area_name} not found in config"}), 404
        
    slots_dict = area_config.get("slots", {})
    
    try:
        # 1. Check Firestore Cache First
        cached_result = firestore_client.get_prediction_from_firestore(area_name, timestamp_str)
        if cached_result:
            print(f"Returning cached prediction from Firestore for {area_name} at {timestamp_str}")
            return jsonify({
                "free_slots": cached_result.get("free_slots", []),
                "total_checked": len(slots_dict), # Appoximation from config
                "input_time": timestamp_str,
                "source": "cache"
            })

        dt = datetime.fromisoformat(timestamp_str)
        hour = dt.hour
        day = dt.day
        weekday = dt.weekday()

        # Prepare batch input: one row per slot
        input_rows = []
        valid_slots = []
        
        for slot_id_str in slots_dict.keys():
            try:
                 # Map local ID ("1", "2") to model ID ("1", "24")
                 # Area 1: 1 -> "1", Area 2: 1 -> "24"
                 model_slot_id = slot_id_str
                 if area_name == "area2":
                     model_slot_id = str(int(slot_id_str) + 23)

                 encoded_slot = slot_le.transform([model_slot_id])[0]
                 input_rows.append({
                     "hour": hour,
                     "day": day,
                     "weekday": weekday,
                     "slot_id_encoded": encoded_slot
                 })
                 valid_slots.append(slot_id_str)
            except ValueError:
                # Slot ID not known to model
                continue
        
        if not input_rows:
             return jsonify({"free_slots": [], "message": "No known slots for this area in model"})
             
        input_df = pd.DataFrame(input_rows)
        
        # Predict batch
        predictions = model.predict(input_df)
        predicted_labels = le.inverse_transform(predictions)
        
        free_slots = []
        for slot_id, label in zip(valid_slots, predicted_labels):
            # Check if label implies free (Assuming 'Unoccupied' or similar)
            if str(label).lower() in ["unoccupied", "free", "0"]:
                free_slots.append(slot_id)
        
        # 2. Save Prediction to Firestore for future use
        try:
            firestore_client.save_prediction_to_firestore(area_name, timestamp_str, free_slots)
        except Exception as fe:
            print(f"Warning: Failed to save to Firestore: {fe}")

        return jsonify({
            "free_slots": free_slots,
            "total_checked": len(valid_slots),
            "input_time": timestamp_str,
            "source": "model"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
