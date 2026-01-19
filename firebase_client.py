import firebase_admin
from firebase_admin import credentials, db
import time
import os
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
    })


def update_parking_area(area_name: str, slot_status: dict,
                        total_slots: int, free_slots: int, occupied_slots: int):
    """
    Writes the parking status of one area into Realtime Database.
    area_name: "area1" or "area2"
    slot_status: {1: "free", 2: "occupied", ...}
    """
    ref = db.reference(f"parking/{area_name}")
    slots_payload = {
        str(slot_id): {"status": status}
        for slot_id, status in slot_status.items()
    }

    data = {
        "area_name": area_name,
        "total_slots": total_slots,
        "free_slots": free_slots,
        "occupied_slots": occupied_slots,
        "slots": slots_payload,
        "updated_at": int(time.time())  # unix timestamp
    }
    ref.set(data)

def get_parking_data(area_name: str = None):
    """
    Reads parking data. If area_name provided, returns that area.
    Otherwise returns all.
    """
    ref = db.reference("parking")
    if area_name:
        return ref.child(area_name).get()
    return ref.get()
