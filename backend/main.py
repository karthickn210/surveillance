
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import asyncio
import os
import shutil
import ssl
import certifi

# Fix SSL Certificate Errors on Mac
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

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

# Global State
TARGET_IMAGE_PATH = "target_person.jpg"
ml_engine = MLEngine()
# Using 0 as default webcam, and a video file if available for testing 2nd stream
camera_manager = CameraManager(sources=[0]) 

@app.get("/")
def read_root():
    return {"status": "Surveillance System Backend Running"}

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
                processed_frame, alerts = ml_engine.process_frame(frame)
                
                # Encode to JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame)
                await websocket.send_bytes(buffer.tobytes())
                
                # Send alerts if any (This assumes client can handle mixed messages or separate socket)
                # For simplicity in this demo, we overlay alerts on the image, 
                # but we could also send a separate text frame.
                if alerts:
                    # In a real app, send JSON with metadata. 
                    # Here we rely on the visual overlay for speed.
                    pass 
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
