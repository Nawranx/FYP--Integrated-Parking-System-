
import pandas as pd
from collections import Counter
from datetime import datetime

file_path = r'c:\Users\Nawran\Music\parking_lot-area 1 create polygons\On-street_Car_Parking_Sensor_Data_-_2020__Jan_-_May_.csv'
chunk_size = 500000

total_records = 0
bay_record_counts = Counter()
monthly_counts = Counter()
min_date = None
max_date = None

# Format: 04/28/2020 12:25:28 PM
date_format = '%m/%d/%Y %I:%M:%S %p'

try:
    print(f"Analyzing 2.3GB dataset {file_path}...")
    # Only load the columns we need to save memory and time
    reader = pd.read_csv(
        file_path, 
        chunksize=chunk_size, 
        usecols=['BayId', 'ArrivalTime'],
        engine='c',
        low_memory=False
    )
    
    for i, chunk in enumerate(reader):
        total_records += len(chunk)
        
        # 1. Bay Counts
        bay_record_counts.update(chunk['BayId'].dropna().tolist())
        
        # 2. Monthly Counts
        # Fast date parsing
        chunk['Arrival'] = pd.to_datetime(chunk['ArrivalTime'], format=date_format, errors='coerce')
        valid_dates = chunk['Arrival'].dropna()
        
        if not valid_dates.empty:
            c_min = valid_dates.min()
            c_max = valid_dates.max()
            if min_date is None or c_min < min_date: min_date = c_min
            if max_date is None or c_max > max_date: max_date = c_max
            
            months = valid_dates.dt.strftime('%B %Y').tolist()
            monthly_counts.update(months)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed {total_records:,} records...")

    print("\n--- Final Results ---")
    print(f"Total Records: {total_records:,}")
    print(f"Total Unique Slots (BayId): {len(bay_record_counts):,}")
    
    counts = list(bay_record_counts.values())
    if counts:
        print(f"Average records per slot: {sum(counts) / len(counts):.2f}")
        print(f"Min records for a slot: {min(counts)}")
        print(f"Max records for a slot: {max(counts)}")
    
    print(f"Date Range: {min_date} to {max_date}")
    print("\nRecords per Month:")
    for month, count in sorted(monthly_counts.items(), key=lambda x: datetime.strptime(x[0], '%B %Y')):
        print(f"{month}: {count:,}")
        
except Exception as e:
    print(f"Error: {e}")
