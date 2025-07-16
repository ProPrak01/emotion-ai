from pydantic_settings import BaseSettings
from typing import List, Dict
import os

class Settings(BaseSettings):
    app_name: str = "Emotion Music Generator"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Emotion detection settings
    emotion_detection_model: str = "fer"
    confidence_threshold: float = 0.5
    emotion_smoothing_frames: int = 5
    max_faces: int = 5
    detection_fps: int = 15
    
    # Music settings
    music_fade_duration: float = 2.0  # seconds
    music_volume_range: tuple = (0.3, 1.0)
    tempo_range: tuple = (0.7, 1.3)
    default_music_style: str = "ambient"
    
    # Emotion mappings
    emotion_colors: Dict[str, str] = {
        "happy": "#FFD700",
        "sad": "#4169E1", 
        "angry": "#DC143C",
        "surprise": "#9370DB",
        "neutral": "#808080",
        "fear": "#FF6347",
        "disgust": "#32CD32"
    }
    
    emotion_music_params: Dict[str, Dict] = {
        "happy": {
            "tempo": 1.2,
            "volume": 0.8,
            "reverb": 0.2,
            "brightness": 0.8
        },
        "sad": {
            "tempo": 0.8,
            "volume": 0.5,
            "reverb": 0.6,
            "brightness": 0.3
        },
        "angry": {
            "tempo": 1.3,
            "volume": 0.9,
            "reverb": 0.1,
            "brightness": 0.9
        },
        "surprise": {
            "tempo": 1.1,
            "volume": 0.7,
            "reverb": 0.3,
            "brightness": 0.7
        },
        "neutral": {
            "tempo": 1.0,
            "volume": 0.6,
            "reverb": 0.3,
            "brightness": 0.5
        },
        "fear": {
            "tempo": 1.1,
            "volume": 0.6,
            "reverb": 0.5,
            "brightness": 0.4
        },
        "disgust": {
            "tempo": 0.9,
            "volume": 0.5,
            "reverb": 0.4,
            "brightness": 0.4
        }
    }
    
    # Performance settings
    max_memory_mb: int = 500
    max_cpu_percent: int = 40
    frame_timeout_ms: int = 50
    music_transition_latency_ms: int = 100
    
    # Paths
    models_dir: str = "models"
    music_assets_dir: str = "../frontend/assets/music"
    log_file: str = "emotion_music.log"
    
    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://*.netlify.app"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()