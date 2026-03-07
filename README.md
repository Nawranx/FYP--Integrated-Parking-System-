# DriveInSight: Integrated System for Space Utilization Forecasting with Real-Time Parking Guidance 🚗💨

**DriveInSight** is an integrated smart parking system that combines machine learning-based availability prediction, real-time computer vision detection, and slot-level navigation into a single unified platform — helping drivers find parking faster while reducing congestion, fuel waste, and frustration.

# Overview
Most parking systems operate in silos: some show static availability signs, others offer basic reservations — but none bring prediction, live monitoring, and intelligent guidance together in one place. DriveInSight bridges that gap.
Built as a Final Year Project, the system is deployed as a Flutter mobile application backed by a Flask REST API, Firebase Realtime Database, and Firestore, with computer vision processing running on live CCTV feeds.

---

## 🌟 Key Features

### 1. Parking Availability Prediction
An XGBoost model trained on historical IN/OUT parking records forecasts slot availability at user-selected future times, with a confidence score and specific slot recommendations. Achieves 95.23% accuracy.

### 2. Real-Time Slot Detection
YOLOv8 processes live CCTV feeds to classify each parking slot as free or occupied, updating Firebase every ~2 seconds. Achieves mAP@50 of 97.9%, precision 97.4%, recall 94.0%.

### 3. Nearest-Slot Navigation
A rule-based guidance module integrated with GeoFire and Google Maps directs drivers to the nearest confirmed-free slot with turn-by-turn directions.

### 4. Smart Recommendation Engine
Ranks parking zones by proximity and live availability, with intelligent fallback when preferred zones are full.

### 5. Admin Dashboard
A Streamlit-based monitoring interface for parking operators to track real-time occupancy across all zones.

### 6. Cross-Platform Mobile App
Built with Flutter (Dart), featuring secure Firebase Auth, live slot visualisation, trip planning, and in-app navigation.

---

## 🏗️ System Architecture

- **Mobile App**: Flutter 
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
