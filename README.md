# DriveInSight: Integrated Smart Parking System 🚗💨

**DriveInSight** is an AI-powered end-to-end parking solution designed to minimize search time, reduce urban congestion, and provide drivers with a seamless "last-mile" navigation experience.

---

## 🌟 Key Features

### 1. Slot Availability Prediction (XGBoost)
Predicts future parking occupancy using historical time-series data. Drivers can search for their destination (e.g., "Plaza Mall") and a specific time to see predicted availability with high confidence scores.

### 2. Real-Time Vision Detection (YOLOv8)
A computer vision module that monitors parking facilities via live video feeds. It identifies available slots instantly and synchronizes the status to the cloud.

### 3. Smart Suggestion & Precision Navigation
A premium Flutter mobile app that suggests the best parking zone based on distance and live occupancy. It provides pinpoint GPS navigation directly to a **specific parking slot** using unique coordinates.

### 4. Admin Monitoring Portal (Streamlit)
A dedicated dashboard for facility managers to monitor live occupancy metrics, total capacity, and slot-level status in real-time.

---

## 🏗️ System Architecture

- **Mobile App**: Flutter (Premium Dark UI, Glassmorphism)
- **Backend API**: Flask (Python)
- **Computer Vision**: YOLOv8, OpenCV
- **Predictive Model**: XGBoost Regressor
- **Cloud/Database**: Firebase Realtime Database & Google Cloud Firestore
- **Admin Portal**: Streamlit

---

## 📂 Project Structure

### Backend & AI
- `api.py`: Core Flask API handling predictions and data sync.
- `detector.py` & `main.py`: YOLOv8 detection engine and multi-process launcher.
- `parking_model.pkl`: Trained XGBoost occupancy prediction model.
- `best.pt`: Trained YOLOv8 weights for vehicle detection.

### Frontend
- `parking_app/`: The full Flutter source code.
- `dashboard.py`: Streamlit-based Admin Monitoring portal.

### Configuration
- `parking_config.json`: Master configuration containing slot GPS coordinates and zone metadata.
- `polygons1.json` / `polygons2.json`: Coordinate data for detection zones.

---

## 🛠️ Setup & Installation

### Python Backend
1. Create a virtual environment: `python -m venv .venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with Firebase credentials.
4. Run the API: `python api.py`
5. Run the Detector: `python main.py`

### Flutter App
1. Navigate to the app directory: `cd parking_app`
2. Install packages: `flutter pub get`
3. Run the app: `flutter run`

---

## 🎯 Project Objectives
1. **Predictive Planning**: Help drivers plan their arrival and minimize search time via slot availability prediction.
2. **Precision Guidance**: Identify free slots instantly and guide drivers directly to them inside the facility.
3. **Unified Connectivity**: Provide a user-friendly mobile application that integrates prediction, detection, and navigation in one place.

---

**Developed for Final Year Project (FYP)**  
*DriveInSight: Stop Searching. Start Parking.* 🏁🚗💨
