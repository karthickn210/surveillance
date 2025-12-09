from ultralytics import YOLO
import cv2
import numpy as np
from reid_utils import ReIDExtractor, compare_embeddings
import math

class MLEngine:
    def __init__(self, model_path="yolov8n.pt"):
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        print("Loading ReID model...")
        self.reid_extractor = ReIDExtractor()
        
        # Target Embedding (The person we want to track)
        self.target_embedding = None
        self.target_threshold = 0.6 # Similarity threshold
        
        # Harassment Config
        self.harassment_threshold_dist = 50 # pixels (logic needs refinement based on depth)
        
    def update_target(self, image_path):
        """Updates the target embedding from an uploaded image."""
        img = cv2.imread(image_path)
        if img is not None:
            self.target_embedding = self.reid_extractor.extract(img)
            print("Target updated successfully.")
            return True
        return False

    def process_frame(self, frame):
        """
        Runs detection, tracking, and harassment checks on a single frame.
        Returns: annotated_frame, metadata
        """
        # Track persons (0) and Knives (43)
        # Lower confidence to 0.15 to catch smaller/occluded weapons
        results = self.model.track(frame, persist=True, verbose=False, classes=[0, 43], conf=0.15, iou=0.5) 
        
        detections = []
        alerts = []
        pixel_locations = []

        if results[0].boxes:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0]) # Get confidence
                track_id = int(box.id[0]) if box.id is not None else -1
                
                # Debug logging
                # print(f"DEBUG: Detected Class {cls} with Conf {conf:.2f}")

                # Weapon Detection (Class 43 = Knife)
                if cls == 43:
                    alert_msg = f"WEAPON DETECTED! (Knife) Conf: {conf:.2f}"
                    print(f"!!! {alert_msg} !!!") # Print to console for user to see
                    alerts.append(alert_msg)
                    
                    # More prominent visual alert
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    
                    # Background for text for better readability
                    label = "WEAPON: KNIFE"
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    cv2.rectangle(frame, (x1, y1 - 25), (x1 + w, y1), (0, 0, 255), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    continue # Skip person logic for weapons

                # Person Logic
                if cls == 0:
                    # Extract Person Crop for ReID
                    person_crop = frame[y1:y2, x1:x2]
                    
                    is_target = False
                    similarity = 0.0
                    
                    # Check for Target Match
                    if self.target_embedding is not None and person_crop.size > 0:
                        curr_embedding = self.reid_extractor.extract(person_crop)
                        similarity = compare_embeddings(self.target_embedding, curr_embedding)
                        if similarity > self.target_threshold:
                            is_target = True
                            alerts.append(f"Target Detected! ID: {track_id} (Sim: {similarity:.2f})")

                    # Store center point for simple harassment logic
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                    pixel_locations.append({'id': track_id, 'x': center_x, 'y': center_y})

                    # Draw Visuals
                    color = (0, 0, 255) if is_target else (0, 255, 0)
                    label = f"ID: {track_id} {'TARGET' if is_target else ''}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Simple Harassment/Proximity Logic
        # Check if any two people are very close (could imply fighting/harassment)
        for i in range(len(pixel_locations)):
            for j in range(i + 1, len(pixel_locations)):
                p1 = pixel_locations[i]
                p2 = pixel_locations[j]
                dist = math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])
                if dist < self.harassment_threshold_dist:
                    alerts.append(f"Proximity Alert: ID {p1['id']} and {p2['id']} (Dist: {dist:.1f})")
                    cv2.putText(frame, "PROXIMITY ALERT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        return frame, alerts
