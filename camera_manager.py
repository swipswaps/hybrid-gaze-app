# Resilient V4L2 Camera Manager with Automatic Reconnection Logic
# Reference: OpenCV VideoCapture Documentation (https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)

import cv2
import time
import logging
logger = logging.getLogger(__name__)

class ResilientCameraManager:
    def __init__(self, camera_id: int, max_retries: int = 5):
        self.camera_id = camera_id
        self.max_retries = max_retries
        self.cap = None
        self._initialize_device()

    def _initialize_device(self):
        attempts = 0
        while attempts < self.max_retries:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            if self.cap.isOpened():
                logger.info(f"Camera /dev/video{self.camera_id} initialized")
                return
            attempts += 1
            time.sleep(1.0)
        raise ConnectionError(f"[HARDWARE_FAILURE]: Unable to acquire device /dev/video{self.camera_id}")

    def read_frame(self):
        if not self.cap or not self.cap.isOpened():
            try:
                self._initialize_device()
            except ConnectionError:
                return None
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Attempt recovery
            self.cap.release()
            try:
                self._initialize_device()
                ret, frame = self.cap.read()
                if not ret:
                    return None
            except ConnectionError:
                return None
        return frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
