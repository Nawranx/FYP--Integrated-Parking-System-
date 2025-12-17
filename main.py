
from detector import ParkingAreaDetector
from multiprocessing import Process

def run_area1():
    area1_detector = ParkingAreaDetector(
        area_name="area1",
        video_source="11.mp4",          # or RTSP URL / camera index
        polygon_file="polygons1.json"
    )
    area1_detector.run()

def run_area2():
    area2_detector = ParkingAreaDetector(
        area_name="area2",
        video_source="vid1.mp4",
        polygon_file="polygons2.json"
    )
    area2_detector.run()

if __name__ == "__main__":
    p1 = Process(target=run_area1)
    p2 = Process(target=run_area2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()