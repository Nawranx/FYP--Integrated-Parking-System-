import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Use the same credentials as your realtime database
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_prediction_to_firestore(area_name, timestamp_str, free_slots):
    """Stores the prediction result in a 'predictions' collection."""
    # Create a unique ID based on area and time (e.g., 'area1_2023-11-01T22:00:00')
    doc_id = f"{area_name}_{timestamp_str}"
    doc_ref = db.collection("predictions").document(doc_id)
    
    doc_ref.set({
        "area_name": area_name,
        "prediction_time": timestamp_str,
        "free_slots": free_slots,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    print(f"Prediction saved to Firestore for {doc_id}")

def get_prediction_from_firestore(area_name, timestamp_str):
    """Retrieves a previously stored prediction."""
    doc_id = f"{area_name}_{timestamp_str}"
    doc_ref = db.collection("predictions").document(doc_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return None