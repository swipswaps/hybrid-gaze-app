# FastAPI Augmented Backend with Kalman Filter, Calibration, Structured Logging and Prometheus Metrics
# Reference: FastAPI Concurrency and Async Endpoints (https://fastapi.tiangolo.com/async/)
# Reference: Kalman, R. E. (1960). "A New Approach to Linear Filtering and Prediction Problems." Journal of Basic Engineering, 82(1), 35–45. DOI: 10.1115/1.3662552.

import cv2
import numpy as np
import subprocess
import os
import io
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import mediapipe as mp
from PIL import Image

# Local modules
from camera_manager import ResilientCameraManager
from kalman_gaze import GazeKalmanTracker
from config import settings
from logging_config import setup_structured_logging
from metrics import setup_metrics_endpoint

# Initialize structured logging
setup_structured_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hybrid Eye Tracker & Media Processing Backend", version="2.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics endpoint
setup_metrics_endpoint(app)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Camera managers with resilience
cameras = {
    0: ResilientCameraManager(settings.PRIMARY_CAMERA_ID),
    1: ResilientCameraManager(settings.SECONDARY_CAMERA_ID)
}

# Storage directory for processed media
STORAGE_DIR = settings.STORAGE_DIR
os.makedirs(STORAGE_DIR, exist_ok=True)

# Kalman filter instance for gaze smoothing
kalman = GazeKalmanTracker()

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI backend service started successfully", extra={"service": "backend", "status": "running"})

@app.get("/health")
def health_check():
    active = [k for k, v in cameras.items() if v.cap and v.cap.isOpened()]
    logger.debug("Health check", extra={"active_cameras": active})
    return {"status": "healthy", "active_cameras": active}

@app.post("/api/images/process")
async def process_image_frame(file: UploadFile = File(...)):
    """Optimize and store captured frame with Pillow."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image.thumbnail((settings.FRAME_WIDTH, settings.FRAME_HEIGHT))
        output_path = os.path.join(STORAGE_DIR, f"processed_{file.filename}")
        image.save(output_path, "JPEG", quality=85)
        logger.info("Image processed", extra={"filename": file.filename, "path": output_path})
        return {"filename": file.filename, "status": "optimized_and_stored", "path": output_path}
    except Exception as e:
        logger.error("Image processing failed", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/media/transcode")
async def transcode_video_segment(input_filename: str, output_format: str = "mp4"):
    """FFmpeg subprocess wrapper for transcoding."""
    input_path = os.path.join(STORAGE_DIR, input_filename)
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Input media file not found")
    output_filename = f"transcoded_{os.path.splitext(input_filename)[0]}.{output_format}"
    output_path = os.path.join(STORAGE_DIR, output_filename)
    cmd = ["ffmpeg", "-y", "-i", input_path, "-vcodec", "libx264", "-crf", "28", output_path]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        logger.error("FFmpeg transcoding failed", extra={"stderr": process.stderr.decode()})
        raise HTTPException(status_code=500, detail=f"FFmpeg encoding failed: {process.stderr.decode()}")
    logger.info("Transcoding succeeded", extra={"output": output_filename})
    return {"output_file": output_filename, "status": "transcoded_successfully"}

@app.websocket("/ws/track/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: int):
    await websocket.accept()
    if camera_id not in cameras:
        await websocket.close(code=4004)
        return
    cam = cameras[camera_id]
    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                await websocket.send_json({"error": "Failed to capture frame from hardware device"})
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            payload = {"landmarks": [], "status": "no_face_detected"}
            if results.multi_face_landmarks:
                payload["status"] = "tracked"
                face_landmarks = results.multi_face_landmarks[0]
                # Periocular landmarks (indices from MediaPipe Face Mesh topology)
                left_eye_indices = [33, 133, 160, 159, 158, 144, 153, 154, 155, 133]
                h, w, _ = frame.shape
                extracted_points = []
                for idx in left_eye_indices:
                    lm = face_landmarks.landmark[idx]
                    x, y = int(lm.x * w), int(lm.y * h)
                    # Apply Kalman smoothing
                    smoothed_x, smoothed_y = kalman.filter_point(x, y)
                    extracted_points.append({"x": int(smoothed_x), "y": int(smoothed_y)})
                payload["landmarks"] = extracted_points
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("WebSocket error", exc_info=True)
        await websocket.send_json({"error": str(e)})
