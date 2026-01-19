import json

def generate_config():
    base_lat = 6.1235
    base_lng = 100.3654
    
    # Area 1: 23 slots
    area1_slots = {}
    for i in range(1, 24):
        slot_id = str(i)
        area1_slots[slot_id] = {
            "lat": base_lat + (i * 0.00001),
            "lng": base_lng + (i * 0.00001)
        }

    # Area 2: 37 slots (1-37)
    area2_slots = {}
    for i in range(1, 38):
        slot_id = str(i)
        area2_slots[slot_id] = {
            "lat": base_lat + (i * 0.00002) + 0.001, # Offset for area 2
            "lng": base_lng + (i * 0.00002) + 0.001
        }
        
    config = {
        "area1": {
            "name": "Area 1",
            "description": "23 slots",
            "location": {"lat": base_lat, "lng": base_lng},
            "slots": area1_slots
        },
        "area2": {
            "name": "Area 2", 
            "description": "37 slots",
            "location": {"lat": base_lat + 0.001, "lng": base_lng + 0.001},
            "slots": area2_slots
        }
    }
    
    with open("parking_config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("Generated parking_config.json")

if __name__ == "__main__":
    generate_config()
