import cv2
import threading
import time
from queue import Queue

class CameraManager:
    def __init__(self, sources):
        self.sources = sources
        self.captures = []
        self.frame_queues = {}
        self.stop_signal = threading.Event()
        
        for idx, source in enumerate(self.sources):
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                self.captures.append(cap)
                self.frame_queues[idx] = Queue(maxsize=2) # Keep buffer small for low latency
            else:
                print(f"Error opening video source {source}")

        # Start capture threads
        self.threads = []
        for idx, cap in enumerate(self.captures):
            t = threading.Thread(target=self._capture_loop, args=(idx, cap))
            t.daemon = True
            t.start()
            self.threads.append(t)

    def _capture_loop(self, cam_id, cap):
        while not self.stop_signal.is_set():
            ret, frame = cap.read()
            if not ret:
                # Handle stream end or disconnection (reconnect logic could go here)
                time.sleep(0.1)
                continue
            
            # Put frame in queue (overwrite if full)
            if self.frame_queues[cam_id].full():
                try:
                    self.frame_queues[cam_id].get_nowait()
                except:
                    pass
            self.frame_queues[cam_id].put(frame)

    def get_frame(self, cam_id):
        if cam_id in self.frame_queues and not self.frame_queues[cam_id].empty():
            return self.frame_queues[cam_id].get()
        return None

    def release(self):
        self.stop_signal.set()
        for cap in self.captures:
            cap.release()
