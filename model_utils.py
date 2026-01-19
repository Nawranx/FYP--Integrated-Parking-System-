import pandas as pd
import numpy as np
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

MODEL_FILE = "parking_model.pkl"
ENCODER_FILE = "label_encoder.pkl"
SLOT_ENCODER_FILE = "slot_encoder.pkl"

def train_and_save_model(csv_path="on-street-parking-bay-sensors (1).csv"):
    print("Loading dataset...")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()
    
    # Basic preprocessing
    df["slot_id"] = df["kerbsideid"].astype(str) # Ensure string
    
    # Filter if needed (keeping logic from before)
    # Filter if needed (keeping logic from before)
    # NEW: Map top 60 slots to IDs 1-60
    unique_slot_ids = df['slot_id'].value_counts().index
    if len(unique_slot_ids) > 60:
        top_60_slots = unique_slot_ids[:60]
    else:
        top_60_slots = unique_slot_ids
    
    # Create mapping: Old ID -> New ID ("1", "2", ... "60")
    slot_mapping = {old_id: str(i+1) for i, old_id in enumerate(top_60_slots)}
    
    print(f"Mapping {len(slot_mapping)} slots to simplified IDs 1-60...")
    
    # Filter dataset to only these slots
    df = df[df['slot_id'].isin(top_60_slots)].copy()
    
    # Apply mapping
    df["mapped_slot_id"] = df["slot_id"].map(slot_mapping)
    
    df["time"] = pd.to_datetime(df["lastupdated"], errors="coerce")
    df = df.dropna(subset=["time"])
    
    # Time features
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["weekday"] = df["time"].dt.weekday
    
    # Target encoding
    le = LabelEncoder()
    df["status_encoded"] = le.fit_transform(df["status_description"])
    
    # NEW: Slot ID encoding using the MAPPED ID
    slot_le = LabelEncoder()
    df["slot_id_encoded"] = slot_le.fit_transform(df["mapped_slot_id"])
    
    feature_cols = ["hour", "day", "weekday", "slot_id_encoded"]
    X = df[feature_cols]
    y = df["status_encoded"]
    
    print(f"Training model on {len(df)} records with features {feature_cols}...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softmax",
        num_class=len(le.classes_), 
        random_state=42,
        eval_metric="mlogloss"
    )
    
    model.fit(X, y)
    print("Model trained.")
    
    # Save artifacts
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    with open(ENCODER_FILE, "wb") as f:
        pickle.dump(le, f)
    with open(SLOT_ENCODER_FILE, "wb") as f:
        pickle.dump(slot_le, f)
        
    print(f"Model saved to {MODEL_FILE}")
    print(f"Encoders saved to {ENCODER_FILE}, {SLOT_ENCODER_FILE}")

def load_model_and_encoders():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE) or not os.path.exists(SLOT_ENCODER_FILE):
        return None, None, None
    
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_FILE, "rb") as f:
        le = pickle.load(f)
    with open(SLOT_ENCODER_FILE, "rb") as f:
        slot_le = pickle.load(f)
    return model, le, slot_le

if __name__ == "__main__":
    train_and_save_model()
