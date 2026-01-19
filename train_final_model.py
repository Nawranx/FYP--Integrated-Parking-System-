
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Configuration
input_file = r'c:\Users\Nawran\Music\parking_lot-area 1 create polygons\processed_training_data.csv'
model_file = "parking_model.pkl"
label_encoder_file = "label_encoder.pkl"
slot_encoder_file = "slot_encoder.pkl"

def train():
    print(f"Loading processed data from {input_file}...")
    df = pd.read_csv(input_file)
    
    
    X = df[['hour', 'day', 'weekday', 'slot_id_encoded']]
    y_raw = df['status_description']
    
    # Status Label Encoder
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    print(f"Classes: {le.classes_}") 
    
    slot_le = LabelEncoder()
    slot_le.classes_ = np.array([str(i) for i in range(1, 61)])
    
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    count_0 = np.sum(y_train == 0)
    count_1 = np.sum(y_train == 1)
    scale = count_0 / count_1
    print(f"Class Balance - Present: {count_0}, Unoccupied: {count_1}, Scale: {scale:.2f}")

    print(f"Training on {len(X_train):,} samples...")
    
    # XGBoost Model
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        scale_pos_weight=scale, # to improve recall of free slots
        random_state=42,
        eval_metric="logloss"
    )
    
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save Artifacts
    print("\nSaving model and encoders...")
    with open(model_file, "wb") as f:
        pickle.dump(model, f)
    with open(label_encoder_file, "wb") as f:
        pickle.dump(le, f)
    with open(slot_encoder_file, "wb") as f:
        pickle.dump(slot_le, f)
        
    print("Done! Artifacts updated.")

if __name__ == "__main__":
    train()
