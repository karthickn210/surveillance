# Surveillance AI System

An advanced surveillance system powered by **FastAPI (Python)** and **React**. Features robust human detection, specific person re-identification (tracking), harassment detection, and weapon (knife) tracking with real-time dashboard alerts.

## 🌟 Features

- **Multi-Camera Support**: Real-time monitoring of up to 4 RTSP streams.
- **Weapon Detection**:
  - Automatically detects knives (using YOLOv8).
  - Triggers visual RED alerts on the live feed.
  - **Saves snapshot** of the threat to the server.
  - **Clickable Dashboard Alerts**: View high-res evidence of any detected threat.
- **Person Tracking (Re-ID)**:
  - Upload a photo of a target person.
  - System tracks them across cameras with specific bounding boxes.
- **Harassment/Action Detection**:
  - Proximity-based alerts for potential altercations.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, YOLOv8 (Ultralytics), OpenCV, PyTorch.
- **Frontend**: React, Vite, Tailwind CSS v4.
- **Communication**: WebSockets (Streaming), REST API (Alerts/Uploads).

## 🚀 Quick Start

The easiest way to run the system is using the helper script:

```bash
./start.sh
```

This will:
1.  Launch the FastAPI Backend (Port 8000).
2.  Launch the React Frontend (Port 5173).

## 📂 Manual Installation

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## ⚠️ Notes for Testing
- **Weapon Detection**: Hold up a knife (or image of one) to the webcam. It should save a snapshot to `backend/alerts/` and show up in the "Live Alerts" panel on the right. Click the alert to view the image.
- **Performance**: Running YOLO tracking + ReID on CPU can be slow. A GPU is recommended for multiple streams.
