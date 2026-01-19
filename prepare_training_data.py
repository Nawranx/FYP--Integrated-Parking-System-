
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Configuration
input_file = r'c:\Users\Nawran\Music\parking_lot-area 1 create polygons\On-street_Car_Parking_Sensor_Data_-_2020__Jan_-_May_.csv'
output_file = r'c:\Users\Nawran\Music\parking_lot-area 1 create polygons\processed_training_data.csv'
chunk_size = 500000

#Find top 60 BayIds 
from collections import Counter
bay_record_counts = Counter()

print("Scanning for top 60 BayIds...")
reader = pd.read_csv(input_file, chunksize=chunk_size, usecols=['BayId'], engine='c', low_memory=False)
for chunk in reader:
    bay_record_counts.update(chunk['BayId'].dropna().tolist())

# Sort and pick top 60
top_60_raw = [int(bay_id) for bay_id, _ in bay_record_counts.most_common(60)]

# Mapping Definition
# Area 1: Top 1-23 -> Model ID 1-23
# Area 2: Top 24-60 -> Model ID 24-60
bay_to_model_id = {bay_id: i+1 for i, bay_id in enumerate(top_60_raw)}
target_bays = set(top_60_raw)

print(f"Targeting {len(target_bays)} slots.")

# Extract historical records for the slots
print("Extracting records for target slots...")
all_sessions = []
date_format = '%m/%d/%Y %I:%M:%S %p'

reader = pd.read_csv(input_file, chunksize=chunk_size, usecols=['BayId', 'ArrivalTime', 'DepartureTime'], engine='c', low_memory=False)
for chunk in reader:
    # Filter for target bays
    mask = chunk['BayId'].isin(target_bays)
    filtered = chunk[mask].copy()
    
    # Convert to datetime
    filtered['Arrival'] = pd.to_datetime(filtered['ArrivalTime'], format=date_format, errors='coerce')
    filtered['Departure'] = pd.to_datetime(filtered['DepartureTime'], format=date_format, errors='coerce')
    
    # Drop invalid rows
    valid = filtered.dropna(subset=['Arrival', 'Departure'])
    all_sessions.append(valid[['BayId', 'Arrival', 'Departure']])
    
df_sessions = pd.concat(all_sessions)
print(f"Extracted {len(df_sessions):,} session records.")

# Generate Snapshots (0/1 Status)
# Time range for dataset
start_time = datetime(2020, 1, 1, 0, 0, 0)
end_time = datetime(2020, 5, 26, 23, 30, 0)
time_index = pd.date_range(start=start_time, end=end_time, freq='30min')

print(f"Generating snapshots for {len(time_index):,} time points...")

final_data = []

for i, bay_id in enumerate(top_60_raw):
    model_id = i + 1
    print(f"Processing Slot {model_id} (BayId {bay_id})...")
    
    # Get all sessions for this bay
    bay_data = df_sessions[df_sessions['BayId'] == bay_id]

    
    # Convert everything to numpy 
    bay_data = bay_data.sort_values('Arrival')
    arrivals = bay_data['Arrival'].values
    departures = bay_data['Departure'].values
    t_points = time_index.values
    
    statuses = []
    for t in t_points:

        # find intervals where arrival <= t
        idx = np.searchsorted(arrivals, t, side='right') - 1
        if idx >= 0 and t < departures[idx]:
            statuses.append(1) 
        else:
            statuses.append(0) 
            
   
    slot_df = pd.DataFrame({
        'hour': time_index.hour,
        'day': time_index.day,
        'weekday': time_index.weekday, 
        'slot_id_encoded': model_id - 1,
        'status_encoded': statuses
    })
    final_data.append(slot_df)

# Save
df_final = pd.concat(final_data)


status_map = {1: "Present", 0: "Unoccupied"}
df_final['status_description'] = df_final['status_encoded'].map(status_map)

# Save to CSV
df_final.to_csv(output_file, index=False)
print(f"Saved {len(df_final):,} snapshots to {output_file}")
