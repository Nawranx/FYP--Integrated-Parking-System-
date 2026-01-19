import json
from datetime import datetime
import pandas as pd
from model_utils import load_model_and_encoders
from firestore_client import save_prediction_to_firestore

def update_all_predictions():
    print("Loading config...")
    try:
        with open("parking_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config not found.")
        return

    print("Loading model...")
    model, le, slot_le = load_model_and_encoders()
    if not model:
        print("Model not loaded.")
        return

    timestamp_str = datetime.now().isoformat()
    dt = datetime.fromisoformat(timestamp_str)
    
    # Pre-calculate time features
    hour = dt.hour
    day = dt.day
    weekday = dt.weekday()

    for area_name, area_data in config.items():
        print(f"Processing {area_name}...")
        slots = area_data.get("slots", {})
        
        free_slots = []
        
        for slot_id in slots.keys():
            # Prepare input
            try:
                # Map local ID ("1", "2") to model ID ("1", "24")
                # Area 1: 1 -> "1", Area 2: 1 -> "24"
                model_slot_id = slot_id
                if area_name == "area2":
                    model_slot_id = str(int(slot_id) + 23)

                encoded_slot = slot_le.transform([model_slot_id])[0]
                
                input_df = pd.DataFrame([{
                    "hour": hour,
                    "day": day,
                    "weekday": weekday,
                    "slot_id_encoded": encoded_slot
                }])
                
                pred = model.predict(input_df)
                label = le.inverse_transform(pred)[0]
                
               
                if str(label).lower() in ["unoccupied", "free", "0"]:
                    free_slots.append(slot_id)
                    
            except ValueError:
                print(f"Slot {slot_id} not known to model.")
                continue
                
        # Save to Firestore
        print(f"Area {area_name}: {len(free_slots)} free slots found.")
        save_prediction_to_firestore(area_name, timestamp_str, free_slots)

if __name__ == "__main__":
    update_all_predictions()
