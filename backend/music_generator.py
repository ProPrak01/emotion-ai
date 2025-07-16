import os
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import threading
import time
from typing import Dict, Optional, List
import logging
from config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

logger = logging.getLogger(__name__)

class MusicGenerator:
    def __init__(self):
        self.current_emotion = "neutral"
        self.target_emotion = "neutral"
        self.current_params = settings.emotion_music_params["neutral"].copy()
        self.is_playing = False
        self.music_tracks = {}
        self.ambient_track = None
        self.current_track = None
        self.fade_thread = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.volume = 0.6
        self.style = settings.default_music_style
        self.transition_lock = threading.Lock()
        
        # Load music tracks
        self._load_music_tracks()
        
    def _load_music_tracks(self):
        """Load pre-composed music tracks for each emotion"""
        music_dir = os.path.join(os.path.dirname(__file__), settings.music_assets_dir)
        
        # Create placeholder tracks if music files don't exist
        if not os.path.exists(music_dir):
            logger.info("Music directory not found, creating placeholder tracks")
            self._create_placeholder_tracks()
            return
            
        # Load tracks for each emotion
        for emotion in settings.emotion_music_params.keys():
            emotion_dir = os.path.join(music_dir, emotion)
            if os.path.exists(emotion_dir):
                tracks = []
                for file in os.listdir(emotion_dir):
                    if file.endswith(('.mp3', '.wav', '.ogg')):
                        track_path = os.path.join(emotion_dir, file)
                        tracks.append(AudioSegment.from_file(track_path))
                self.music_tracks[emotion] = tracks
            else:
                # Create placeholder if emotion directory doesn't exist
                self.music_tracks[emotion] = [self._create_placeholder_audio(emotion)]
        
        # Load ambient track
        ambient_path = os.path.join(music_dir, "ambient.wav")
        if os.path.exists(ambient_path):
            self.ambient_track = AudioSegment.from_file(ambient_path)
        else:
            self.ambient_track = self._create_ambient_track()
    
    def _create_placeholder_tracks(self):
        """Create placeholder audio tracks for each emotion"""
        for emotion in settings.emotion_music_params.keys():
            self.music_tracks[emotion] = [self._create_placeholder_audio(emotion)]
        self.ambient_track = self._create_ambient_track()
        
    def _create_placeholder_audio(self, emotion: str) -> AudioSegment:
        """Create a placeholder audio segment for an emotion"""
        # Generate a simple sine wave with parameters based on emotion
        params = settings.emotion_music_params[emotion]
        duration_ms = 10000  # 10 seconds
        sample_rate = 44100
        
        # Base frequency modified by emotion
        base_freq = 440  # A4
        freq_multiplier = {
            "happy": 1.5,
            "sad": 0.7,
            "angry": 1.2,
            "surprise": 1.3,
            "neutral": 1.0,
            "fear": 0.9,
            "disgust": 0.8
        }.get(emotion, 1.0)
        
        frequency = base_freq * freq_multiplier
        
        # Generate sine wave
        t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000))
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Add harmonics for richness
        wave += 0.3 * np.sin(4 * np.pi * frequency * t)
        wave += 0.2 * np.sin(6 * np.pi * frequency * t)
        
        # Apply envelope
        envelope = np.exp(-t / (duration_ms / 1000 * 0.8))
        wave = wave * envelope * params['volume']
        
        # Convert to audio segment
        audio_data = (wave * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        
        return audio_segment
    
    def _create_ambient_track(self) -> AudioSegment:
        """Create an ambient background track"""
        duration_ms = 30000  # 30 seconds
        sample_rate = 44100
        
        # Create low-frequency ambient sound
        t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000))
        wave = 0.1 * np.sin(2 * np.pi * 80 * t)  # Low bass
        wave += 0.05 * np.sin(2 * np.pi * 120 * t)  # Mid bass
        
        # Add some noise for texture
        wave += 0.02 * np.random.normal(0, 1, len(t))
        
        # Convert to audio segment
        audio_data = (wave * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        
        return audio_segment
    
    async def update_emotion(self, emotion: str, confidence: float):
        """Update the target emotion and trigger music transition"""
        if emotion not in settings.emotion_music_params:
            logger.warning(f"Unknown emotion: {emotion}")
            return
            
        self.target_emotion = emotion
        
        # Start transition in background
        await self._transition_to_emotion(emotion, confidence)
    
    async def _transition_to_emotion(self, emotion: str, confidence: float):
        """Smoothly transition to new emotion music"""
        with self.transition_lock:
            if self.current_emotion == emotion:
                # Just update parameters if same emotion
                self._update_music_params(emotion, confidence)
                return
            
            logger.info(f"Transitioning from {self.current_emotion} to {emotion}")
            
            # Get target parameters
            target_params = settings.emotion_music_params[emotion].copy()
            target_params['volume'] *= confidence  # Scale by confidence
            
            # Crossfade to new track
            old_track = self.current_track
            new_track = self._get_track_for_emotion(emotion)
            
            if old_track and new_track:
                # Fade out old, fade in new
                fade_duration_ms = int(settings.music_fade_duration * 1000)
                
                # Start new track at low volume
                new_track = new_track - 20  # Reduce volume by 20dB
                
                # TODO: Implement actual playback system
                # This would integrate with a proper audio backend
                
            self.current_emotion = emotion
            self.current_track = new_track
            self.current_params = target_params
    
    def _get_track_for_emotion(self, emotion: str) -> Optional[AudioSegment]:
        """Get a music track for the given emotion"""
        if emotion in self.music_tracks and self.music_tracks[emotion]:
            # Randomly select a track for variety
            import random
            return random.choice(self.music_tracks[emotion])
        return None
    
    def _update_music_params(self, emotion: str, confidence: float):
        """Update music parameters without changing track"""
        params = settings.emotion_music_params[emotion].copy()
        
        # Interpolate parameters based on confidence
        for key in ['tempo', 'volume', 'reverb', 'brightness']:
            if key in params:
                current = self.current_params.get(key, 1.0)
                target = params[key]
                # Smooth interpolation
                self.current_params[key] = current + (target - current) * 0.3
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_style(self, style: str):
        """Change music style preset"""
        self.style = style
        # Reload tracks for new style if available
        self._load_music_tracks()
    
    def get_current_state(self) -> Dict:
        """Get current music state"""
        return {
            'current_emotion': self.current_emotion,
            'target_emotion': self.target_emotion,
            'is_playing': self.is_playing,
            'volume': self.volume,
            'style': self.style,
            'params': self.current_params,
            'available_styles': ['ambient', 'electronic', 'classical']
        }
    
    def start_playback(self):
        """Start music playback"""
        self.is_playing = True
        # TODO: Implement actual audio playback loop
        logger.info("Music playback started")
    
    def stop_playback(self):
        """Stop music playback"""
        self.is_playing = False
        logger.info("Music playback stopped")
    
    def reset(self):
        """Reset to neutral state"""
        self.current_emotion = "neutral"
        self.target_emotion = "neutral"
        self.current_params = settings.emotion_music_params["neutral"].copy()
        if self.fade_thread and self.fade_thread.is_alive():
            self.fade_thread.join(timeout=1.0)