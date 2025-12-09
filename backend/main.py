from fastapi import FastAPI, BackgroundTasks, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import asyncio
import os
import shutil
import ssl
import certifi
import time

# Fix SSL Certificate Errors on Mac
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

from fastapi.staticfiles import StaticFiles

from ml_engine import MLEngine
from camera_manager import CameraManager
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve alert images statically
os.makedirs("alerts", exist_ok=True)
app.mount("/alerts", StaticFiles(directory="alerts"), name="alerts")

# Global State
TARGET_IMAGE_PATH = "target_person.jpg"
ml_engine = MLEngine()
# Using 0 as default webcam, and a video file if available for testing 2nd stream
camera_manager = CameraManager(sources=[0]) 

# In-memory alert history (List of dicts)
alert_history = []

@app.get("/")
def read_root():
    return {"status": "Surveillance System Backend Running"}

@app.get("/api/alerts")
def get_alerts():
    # Return reverse list (newest first)
    return alert_history[::-1]

@app.post("/upload_target")
async def upload_target(file: UploadFile = File(...)):
    with open(TARGET_IMAGE_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    success = ml_engine.update_target(TARGET_IMAGE_PATH)
    if success:
        return {"message": "Target image uploaded and updated successfully"}
    return {"message": "Failed to update target"}

@app.websocket("/ws/stream/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await websocket.accept()
    try:
        while True:
            frame = camera_manager.get_frame(int(camera_id))
            if frame is not None:
                # Process Frame with ML Engine
                # ml_engine now returns structured alert dicts
                processed_frame, new_alerts = ml_engine.process_frame(frame)
                
                # Store new alerts
                if new_alerts:
                    for alert in new_alerts:
                        # Ensure alert has timestamp
                        if 'timestamp' not in alert:
                            alert['timestamp'] = time.time()
                        alert_history.append(alert)
                    
                    # Limit history size
                    if len(alert_history) > 100:
                         alert_history.pop(0)

                # Encode to JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame)
                await websocket.send_bytes(buffer.tobytes())
                
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
