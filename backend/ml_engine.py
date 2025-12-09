import os
import time
from ultralytics import YOLO
import cv2
import numpy as np
from reid_utils import ReIDExtractor, compare_embeddings
import math

class MLEngine:
    def __init__(self, model_path="yolov8n.pt"):
        # Check for custom weapons model
        custom_model_path = "weapons.pt"
        if os.path.exists(custom_model_path):
            print(f"Loading Custom Weapon Model: {custom_model_path}...")
            try:
                self.model = YOLO(custom_model_path)
                self.using_custom_model = True
            except Exception as e:
                print(f"Error loading custom model: {e}")
                print(f"Falling back to Standard YOLO Model: {model_path}...")
                self.model = YOLO(model_path)
                self.using_custom_model = False
        else:
            print(f"Loading Standard YOLO Model: {model_path}...")
            self.model = YOLO(model_path)
            self.using_custom_model = False
            
        print("Loading ReID model...")
        self.reid_extractor = ReIDExtractor()
        
        # Target Embedding
        self.target_embedding = None
        self.target_threshold = 0.6 
        
        # Harassment Config
        self.harassment_threshold_dist = 50 
        
        # Dynamic Class Mapping
        self.weapon_classes = []
        self.person_class = -1
        
        # Map classes by name
        for id, name in self.model.names.items():
            name = name.lower()
            if 'person' in name:
                self.person_class = id
            elif any(x in name for x in ['knife', 'gun', 'pistol', 'weapon', 'firearm', 'rifle']):
                self.weapon_classes.append(id)
                
        print(f"Person Class ID: {self.person_class}")
        print(f"Weapon Class IDs: {self.weapon_classes}")
        
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
        # Track persons and weapons
        classes_to_track = [self.person_class] + self.weapon_classes
        # Filter out -1 if person not found (unlikely)
        classes_to_track = [c for c in classes_to_track if c != -1]
        
        results = self.model.track(frame, persist=True, verbose=False, classes=classes_to_track, conf=0.15, iou=0.5) 
        
        detections = []
        alerts = []
        pixel_locations = []

        if results[0].boxes:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                conf = float(box.conf[0]) 
                track_id = int(box.id[0]) if box.id is not None else -1
                
                # Weapon Detection
                if cls in self.weapon_classes:
                    weapon_name = self.model.names[cls]
                    alert_msg = f"WEAPON DETECTED! ({weapon_name}) Conf: {conf:.2f}"
                    print(f"!!! {alert_msg} !!!")
                    
                    # Create Alert Object
                    timestamp = time.time()
                    filename = f"alert_{timestamp}_{track_id}.jpg"
                    filepath = os.path.join("alerts", filename)
                    
                    try:
                        cv2.imwrite(filepath, frame)
                    except Exception as e:
                        print(f"Error saving alert image: {e}")

                    alerts.append({
                        "type": "weapon",
                        "subtype": weapon_name,
                        "message": alert_msg,
                        "image": f"/alerts/{filename}",
                        "confidence": conf,
                        "timestamp": timestamp
                    })
                    
                    # Visual Alert
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    label = f"WEAPON: {weapon_name.upper()}"
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    cv2.rectangle(frame, (x1, y1 - 25), (x1 + w, y1), (0, 0, 255), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    continue 

                # Person Logic
                if cls == self.person_class:
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
                            timestamp = time.time()
                            # Optional: Save target sightings too?
                            alerts.append({
                                "type": "target",
                                "message": f"Target Detected! ID: {track_id}",
                                "confidence": similarity,
                                "timestamp": timestamp
                            })

                    # Store center point for simple harassment logic
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                    pixel_locations.append({'id': track_id, 'x': center_x, 'y': center_y})

                    # Draw Visuals
                    color = (0, 0, 255) if is_target else (0, 255, 0)
                    label = f"ID: {track_id} {'TARGET' if is_target else ''}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Simple Harassment/Proximity Logic
        for i in range(len(pixel_locations)):
            for j in range(i + 1, len(pixel_locations)):
                p1 = pixel_locations[i]
                p2 = pixel_locations[j]
                dist = math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])
                if dist < self.harassment_threshold_dist:
                    alerts.append({
                         "type": "harassment", 
                         "message": f"Proximity Alert: ID {p1['id']} and {p2['id']}",
                         "timestamp": time.time()
                    })
                    cv2.putText(frame, "PROXIMITY ALERT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        return frame, alerts
