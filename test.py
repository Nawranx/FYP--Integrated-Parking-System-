from detector import ParkingAreaDetector

det = ParkingAreaDetector(
    area_name="area1",
    video_source="11.mp4",        # same file that works in your old script
    polygon_file="polygons1.json",
    model_path="best.pt"
)

det.run()
