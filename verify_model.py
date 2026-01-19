import pandas as pd
import pickle
from datetime import datetime
from model_utils import load_model_and_encoders
import os

def test_model():
    print("Loading model...")
    # Ensure we are in the right directory or provide absolute paths if needed
    # Assuming running from the same dir as model_utils.py
    model, le, slot_le = load_model_and_encoders()
    
    if not model:
        print("Failed to load model/encoders. Make sure .pkl files exist.")
        return

    print("Model loaded successfully.")
    
    # Test case
    timestamp_str = datetime.now().isoformat()
    slot_id = "10280" 
    
    print(f"Testing prediction for Slot '{slot_id}' at {timestamp_str}")
    
    try:
        dt = datetime.fromisoformat(timestamp_str)
        
        # Check if slot_id is in the encoder
        if slot_id not in slot_le.classes_:
            print(f"Error: Slot ID '{slot_id}' not found in encoder classes: {slot_le.classes_}")
            return

        # Encode inputs
        encoded_slot = slot_le.transform([slot_id])[0]
        
        input_data = {
            "hour": [dt.hour],
            "day": [dt.day],
            "weekday": [dt.weekday()],
            "slot_id_encoded": [encoded_slot]
        }
        
        df = pd.DataFrame(input_data)
        print("Input DataFrame:")
        print(df)
        
        # Predict
        pred = model.predict(df)
        label = le.inverse_transform(pred)
        
        print(f"Raw Prediction: {pred[0]}")
        print(f"Decoded Label: {label[0]}")
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model()
