import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Page config must be first
st.set_page_config(
    page_title="Parking Availability",
    page_icon="🚗",
    layout="wide"
)

# --- Firebase Initialization ---
# We use a singleton pattern with st.cache_resource to initialize only once
@st.cache_resource
def init_firebase():
    # Check if app is already initialized to avoid errors
    if not firebase_admin._apps:
        # Use the absolute path or relative path to your JSON key
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
        })
    return True

try:
    init_firebase()
except Exception as e:
    st.error(f"Failed to connect to Firebase: {e}")
    st.stop()


# --- UI Layout ---

st.title("🚗 Real-time Parking Availability ")
st.markdown("Monitor parking slots in real-time.")

# Container for auto-refreshing content
placeholder = st.empty()

def fetch_data():
    ref = db.reference("parking")
    return ref.get()

def display_area(area_name, data):
    if not data:
        st.warning(f"No data for {area_name}")
        return

    # Extract metrics
    free = data.get("free_slots", 0)
    total = data.get("total_slots", 0)
    occupied = data.get("occupied_slots", 0)
    slots_data = data.get("slots", {})

    # Create a nice card/header
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.metric(label=f"{area_name} Free", value=f"{free}/{total}", delta=f"{occupied} occupied", delta_color="inverse")
    
    with col2:
        # Create a grid for slots
        # Just simple boxes
        st.markdown(f"**{area_name} Slots Status:**")
        
        # Robustly handle non-dict data types (e.g. list from Firebase or None)
        if not isinstance(slots_data, dict):
            if isinstance(slots_data, list):
                # Convert list to dict, skipping None values
                cleaned_slots = {}
                for i, val in enumerate(slots_data):
                    if val is not None:
                        cleaned_slots[str(i)] = val
                slots_data = cleaned_slots
            else:
                # Fallback for None or other types
                slots_data = {}

        # Sort keys to ensure order 1, 2, 3...
        sorted_keys = sorted(slots_data.keys(), key=lambda x: int(x))
        
        cols = st.columns(10) # 10 slots per row max
        for i, key in enumerate(sorted_keys):
            status = slots_data[key].get("status", "unknown")
            is_free = status == "free"
            color = "green" if is_free else "red"
            icon = "✅" if is_free else "🚗"
            
            with cols[i % 10]:
                st.markdown(
                    f"""
                    <div style="
                        background-color: {'#d4edda' if is_free else '#f8d7da'};
                        border: 1px solid {'#c3e6cb' if is_free else '#f5c6cb'};
                        color: {'#155724' if is_free else '#721c24'};
                        padding: 10px;
                        border-radius: 5px;
                        text-align: center;
                        margin-bottom: 5px;
                    ">
                        <strong>S{key}</strong><br>{icon}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    st.markdown("---")


# --- Main Loop ---

# Use @st.fragment to update only this part of the page without full reload (blinking)
@st.fragment(run_every=2)
def auto_refresh_loop():
    data = fetch_data()
    if data:
        for area_name, area_data in data.items():
            display_area(area_name, area_data)
    else:
        st.info("Waiting for data...")

# Main execution
st.subheader("Live Status")
auto_refresh_loop()

