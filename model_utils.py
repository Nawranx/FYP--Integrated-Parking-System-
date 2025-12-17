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

def train_and_save_model(csv_path="on-street-parking-bay-sensors (1).csv"):
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()
    
    # Basic preprocessing matching the notebook
    df["slot_id"] = df["kerbsideid"]
    
    # Filter top 37 slots like in notebook to keep it consistent
    unique_slot_ids = df['slot_id'].unique()
    if len(unique_slot_ids) > 37:
        selected_slot_ids = unique_slot_ids[:37]
        df = df[df['slot_id'].isin(selected_slot_ids)]
    
    df["time"] = pd.to_datetime(df["lastupdated"], errors="coerce")
    df = df.dropna(subset=["time"])
    
    # Time features
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["weekday"] = df["time"].dt.weekday
    
    # Target encoding
    le = LabelEncoder()
    df["status_encoded"] = le.fit_transform(df["status_description"])
    
    feature_cols = ["hour", "day", "weekday"]
    X = df[feature_cols]
    y = df["status_encoded"]
    
    print(f"Training model on {len(df)} records...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softmax",
        num_class=len(unique_slot_ids) if len(unique_slot_ids) < 2 else len(le.classes_), # Logic fix for binary/multi class
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
        
    print(f"Model saved to {MODEL_FILE}")
    print(f"Encoder saved to {ENCODER_FILE}")

def load_model():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
        return None, None
    
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
    with open(ENCODER_FILE, "rb") as f:
        le = pickle.load(f)
    return model, le

if __name__ == "__main__":
    # If run directly, retrain
    train_and_save_model()
