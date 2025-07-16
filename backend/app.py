from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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

from emotion_detector import EmotionDetector
from music_generator import MusicGenerator
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global instances
emotion_detector = None
music_generator = None
active_connections: List[WebSocket] = []
emotion_history = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global emotion_detector, music_generator
    logger.info("Starting Emotion Music Generator...")
    emotion_detector = EmotionDetector()
    music_generator = MusicGenerator()
    music_generator.start_playback()
    yield
    # Shutdown
    logger.info("Shutting down Emotion Music Generator...")
    music_generator.stop_playback()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
import re

def is_allowed_origin(origin: str) -> bool:
    if not origin:
        return False
    
    # Check exact matches
    if origin in settings.allowed_origins:
        return True
    
    # Check wildcard patterns
    for allowed in settings.allowed_origins:
        if "*" in allowed:
            pattern = allowed.replace(".", r"\.").replace("*", ".*")
            if re.match(pattern, origin):
                return True
    
    return False

# Get allowed origins, expanding wildcards for production
allowed_origins = []
for origin in settings.allowed_origins:
    if "*" not in origin:
        allowed_origins.append(origin)
    else:
        # For production, add specific domains
        if "vercel.app" in origin:
            allowed_origins.extend([
                "https://emotion-music.vercel.app",
                "https://emotion-music-generator.vercel.app"
            ])
        if "netlify.app" in origin:
            allowed_origins.extend([
                "https://emotion-music.netlify.app",
                "https://emotion-music-generator.netlify.app"
            ])

# In production, also allow the deployed frontend URL from environment
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Emotion Music Generator API", "version": "1.0.0"}

@app.post("/api/emotion")
async def detect_emotion(file: UploadFile = File(...)):
    """
    Detect emotion from uploaded image
    """
    try:
        # Read image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect emotions
        result = emotion_detector.detect_emotions(frame)
        
        if result['success']:
            # Update music based on emotion
            await music_generator.update_emotion(
                result['dominant_emotion'],
                result['confidence']
            )
            
            # Store in history
            emotion_history.append({
                'timestamp': datetime.now().isoformat(),
                'emotion': result['dominant_emotion'],
                'confidence': result['confidence'],
                'all_emotions': result['emotions']
            })
            
            # Limit history size
            if len(emotion_history) > 100:
                emotion_history.pop(0)
            
            # Broadcast to connected clients
            await manager.broadcast({
                'type': 'emotion_update',
                'data': result
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in emotion detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time emotion detection
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive frame data
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'frame':
                # Decode base64 image
                image_data = base64.b64decode(message['data'].split(',')[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect emotions
                    result = emotion_detector.detect_emotions(frame)
                    
                    if result['success']:
                        # Update music
                        await music_generator.update_emotion(
                            result['dominant_emotion'],
                            result['confidence']
                        )
                        
                        # Send results back
                        await websocket.send_json({
                            'type': 'emotion_result',
                            'data': result
                        })
                        
                        # Broadcast music state
                        await manager.broadcast({
                            'type': 'music_update',
                            'data': music_generator.get_current_state()
                        })
            
            elif message['type'] == 'control':
                # Handle music control messages
                if message['action'] == 'set_volume':
                    music_generator.set_volume(message['value'])
                elif message['action'] == 'set_style':
                    music_generator.set_style(message['value'])
                elif message['action'] == 'reset':
                    emotion_detector.reset()
                    music_generator.reset()
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/music/control")
async def get_music_state():
    """Get current music state"""
    return music_generator.get_current_state()

@app.post("/api/music/update")
async def update_music(emotion: str, confidence: float = 1.0):
    """Manually update music emotion"""
    try:
        await music_generator.update_emotion(emotion, confidence)
        return {"status": "success", "emotion": emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get emotion detection statistics"""
    return {
        "detector_stats": emotion_detector.get_emotion_stats(),
        "music_state": music_generator.get_current_state(),
        "history": emotion_history[-20:],  # Last 20 entries
        "total_detections": len(emotion_history)
    }

@app.post("/api/calibrate")
async def calibrate_emotion(emotion: str, file: UploadFile = File(...)):
    """Calibrate emotion detection for user"""
    # TODO: Implement user-specific calibration
    return {"status": "success", "message": "Calibration feature coming soon"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "emotion_detector": emotion_detector is not None,
        "music_generator": music_generator is not None,
        "active_connections": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )