"""
Lightweight version of the app for free tier deployments
Optimized for Render.com free tier (512MB RAM limit)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
import json
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
from contextlib import asynccontextmanager

# Use minimal imports for memory efficiency
from emotion_detector import EmotionDetector
from config import settings

# Configure minimal logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global instances
emotion_detector = None
active_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global emotion_detector
    logger.info("Starting Emotion Music Generator (Lite)...")
    emotion_detector = EmotionDetector()
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Emotion Music Generator Lite",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable docs to save memory
    redoc_url=None
)

# Configure CORS
allowed_origins = os.getenv("FRONTEND_URL", "").split(",") if os.getenv("FRONTEND_URL") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.max_connections = 10  # Limit connections

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Max connections reached")
            return False
        
        await websocket.accept()
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Emotion Music Generator API (Lite)", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Simplified WebSocket endpoint"""
    connected = await manager.connect(websocket)
    if not connected:
        return
    
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'frame':
                # Decode base64 image
                try:
                    image_data = base64.b64decode(message['data'].split(',')[1])
                    nparr = np.frombuffer(image_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # Detect emotions
                        result = emotion_detector.detect_emotions(frame)
                        
                        # Send minimal response
                        await websocket.send_json({
                            'type': 'emotion_result',
                            'data': {
                                'success': result['success'],
                                'dominant_emotion': result.get('dominant_emotion', 'neutral'),
                                'confidence': result.get('confidence', 0),
                                'emotions': result.get('emotions', {})
                            }
                        })
                except Exception as e:
                    logger.error(f"Frame processing error: {e}")
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Minimal API endpoints
@app.post("/api/emotion")
async def detect_emotion(file: UploadFile = File(...)):
    """Detect emotion from uploaded image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        result = emotion_detector.detect_emotions(frame)
        return {
            'success': result['success'],
            'dominant_emotion': result.get('dominant_emotion', 'neutral'),
            'confidence': result.get('confidence', 0)
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)