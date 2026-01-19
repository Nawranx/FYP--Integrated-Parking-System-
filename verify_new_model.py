
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import os

MODEL_FILE = "parking_model.pkl"
ENCODER_FILE = "label_encoder.pkl"
SLOT_ENCODER_FILE = "slot_encoder.pkl"

def verify():
    print("Loading model and encoders...")
    if not os.path.exists(MODEL_FILE):
        print("Error: Model file not found.")
        return
        
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_FILE, "rb") as f:
        le = pickle.load(f)
    with open(SLOT_ENCODER_FILE, "rb") as f:
        slot_le = pickle.load(f)
        
    print(f"Model loaded. Classes: {le.classes_}")
    
    # Test cases: Area 1 (ID 1-23), Area 2 (ID 34-70 mapped to Area 2 slots 1-37)
    # Actually, in api.py:
    # Area 1: model_slot_id = slot_id (e.g., "1")
    # Area 2: model_slot_id = str(int(slot_id) + 23) (e.g., Area 2 slot "1" -> "24")
    
    test_slots = ["1", "23", "24", "60"]
    test_time = "2026-01-20T14:30:00"
    dt = datetime.fromisoformat(test_time)
    
    print(f"\nVerifying predictions for {test_time}:")
    
    input_rows = []
    for sid in test_slots:
        try:
            encoded_slot = slot_le.transform([sid])[0]
            input_rows.append({
                "hour": dt.hour,
                "day": dt.day,
                "weekday": dt.weekday(),
                "slot_id_encoded": encoded_slot
            })
        except ValueError:
            print(f"Error: Slot {sid} not in encoder.")
            
    if input_rows:
        input_df = pd.DataFrame(input_rows)
        preds = model.predict(input_df)
        labels = le.inverse_transform(preds)
        
        for sid, label in zip(test_slots, labels):
            area = "Area 1" if int(sid) <= 23 else "Area 2"
            local_id = int(sid) if int(sid) <= 23 else int(sid) - 23
            print(f"[{area}] Slot {local_id} (Global {sid}): {label}")

if __name__ == "__main__":
    verify()
