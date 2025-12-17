# detector.py
import cv2
import json
import os
import numpy as np
from ultralytics import YOLO
import cvzone
import time

from firebase_client import update_parking_area

class ParkingAreaDetector:
    def __init__(self, area_name, video_source, polygon_file, model_path="best.pt"):
        self.area_name = area_name          # "area1" or "area2"
        self.video_source = video_source    # "vid1.mp4" or "vid2.mp4" or RTSP
        self.polygon_file = polygon_file
        self.model = YOLO(model_path)
        self.names = self.model.names
        self.cap = cv2.VideoCapture(video_source)
        self.frame_count = 0


        self.polygons = []
        self.polygon_points = []
        self.paused = False
        self.last_push_time = 0

        self._load_polygons()

        cv2.namedWindow(self.area_name)
        cv2.setMouseCallback(self.area_name, self._mouse_callback)

    def _load_polygons(self):
        if os.path.exists(self.polygon_file):
            try:
                with open(self.polygon_file, 'r') as f:
                    self.polygons = json.load(f)
            except:
                self.polygons = []

    def _save_polygons(self):
        with open(self.polygon_file, 'w') as f:
            json.dump(self.polygons, f)

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.polygon_points.append((x, y))
            if len(self.polygon_points) == 4:
                self.polygons.append(self.polygon_points.copy())
                self._save_polygons()
                self.polygon_points.clear()

    def run(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps and fps > 0 else 30
        delay *= 3 if self.area_name == "area2" else 20

        while True:
            if not self.paused:
                ret, frame = self.cap.read()
                self.frame_count += 1
                if self.frame_count % 3 != 0:
                    continue


                # if this is a file, loop it; if it's a camera, you may want to break instead
                if not ret:
                    # for simulation (video file)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                frame = cv2.resize(frame, (1020, 500))
                results = self.model.track(frame, persist=True)

                # draw polygons
                for poly in self.polygons:
                    pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

                occupied_slots = set()
                slot_status = {}

                if results and results[0].boxes.id is not None:
                    ids = results[0].boxes.id.cpu().numpy().astype(int)
                    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                    class_ids = results[0].boxes.cls.int().cpu().tolist()

                    for track_id, box, class_id in zip(ids, boxes, class_ids):
                        x1, y1, x2, y2 = box
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        # optional: only cars
                        # if self.names[class_id] != "car":
                        #     continue

                        for idx, poly in enumerate(self.polygons):
                            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
                            if cv2.pointPolygonTest(pts, (cx, cy), False) >= 0:
                                cv2.circle(frame, (cx, cy), 4, (255, 0, 255), -1)
                                cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                                occupied_slots.add(idx)
                                break

                total_zones = len(self.polygons)
                occupied_zones = len(occupied_slots)
                free_zones = total_zones - occupied_zones

                # Build slot_status and draw labels
                for idx, poly in enumerate(self.polygons):
                    slot_id = idx + 1
                    is_occupied = idx in occupied_slots
                    slot_status[slot_id] = "occupied" if is_occupied else "free"

                    pts = np.array(poly, np.int32)
                    cx = int(pts[:, 0].mean())
                    cy = int(pts[:, 1].mean())
                    color = (0, 0, 255) if is_occupied else (0, 255, 0)
                    label = f"S{slot_id}"
                    cv2.putText(frame, label, (cx - 10, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

                cvzone.putTextRect(frame, f'{self.area_name} FREE:{free_zones}', (30, 40), 2, 2)
                cvzone.putTextRect(frame, f'{self.area_name} OCC:{occupied_zones}', (30, 140), 2, 2)

                # push to Firebase every 2 seconds
                now = time.time()
                if now - self.last_push_time > 2:
                    update_parking_area(
                        area_name=self.area_name,
                        slot_status=slot_status,
                        total_slots=total_zones,
                        free_slots=free_zones,
                        occupied_slots=occupied_zones
                    )
                    self.last_push_time = now

                # draw in-progress polygon points
                for pt in self.polygon_points:
                    cv2.circle(frame, pt, 5, (0, 0, 255), -1)

            cv2.imshow(self.area_name, frame)
            key = cv2.waitKey(delay if not self.paused else 0) & 0xFF

            if key == 27:
                break
            elif key == 32:
                self.paused = not self.paused
            elif key == ord('r') and self.polygons:
                self.polygons.pop()
                self._save_polygons()

        self.cap.release()
        cv2.destroyWindow(self.area_name)
