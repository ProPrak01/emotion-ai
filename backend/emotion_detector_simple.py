"""
Simplified emotion detector for deployment
Uses OpenCV for face detection and returns mock emotions
This avoids heavy dependencies like TensorFlow and FER
"""

import cv2
import numpy as np
import time
import random
from typing import Dict, List, Optional
from collections import deque

class EmotionDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.emotion_history = deque(maxlen=5)
        self.last_detection_time = 0
        self.detection_interval = 0.067  # ~15 FPS
        
    def detect_emotions(self, frame: np.ndarray) -> Dict:
        """
        Detect faces and return mock emotions for demo
        In production, this would use a real emotion detection model
        """
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_detection_time < self.detection_interval:
            return self._get_last_result()
            
        self.last_detection_time = current_time
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return self._create_empty_result()
            
            # For demo: generate realistic emotion scores based on face position
            # In a real app, this would use a trained model
            face_x, face_y, face_w, face_h = faces[0]
            
            # Create emotion scores based on face position (demo logic)
            emotions = self._generate_demo_emotions(face_x, face_y, face_w, face_h, frame.shape)
            
            # Add to history
            self.emotion_history.append(emotions)
            
            # Apply smoothing
            smoothed_emotions = self._smooth_emotions()
            
            # Get dominant emotion
            dominant_emotion = max(smoothed_emotions.items(), key=lambda x: x[1])[0]
            
            return {
                'success': True,
                'emotions': smoothed_emotions,
                'dominant_emotion': dominant_emotion,
                'confidence': smoothed_emotions[dominant_emotion],
                'num_faces': len(faces),
                'faces': [{'box': face.tolist()} for face in faces],
                'timestamp': current_time,
                'processing_time': time.time() - current_time
            }
            
        except Exception as e:
            return self._create_empty_result(error=str(e))
    
    def _generate_demo_emotions(self, x, y, w, h, shape):
        """Generate realistic-looking emotion scores for demo"""
        # Base emotions
        emotions = {
            'angry': 0.05,
            'disgust': 0.05,
            'fear': 0.05,
            'happy': 0.15,
            'sad': 0.10,
            'surprise': 0.10,
            'neutral': 0.50
        }
        
        # Modify based on face position (simulating different expressions)
        center_x = x + w/2
        center_y = y + h/2
        
        # If face is in upper part, more likely surprised
        if center_y < shape[0] * 0.4:
            emotions['surprise'] += 0.3
            emotions['neutral'] -= 0.3
        
        # If face is tilted (wider than tall), more likely happy
        if w > h * 1.2:
            emotions['happy'] += 0.4
            emotions['neutral'] -= 0.4
        
        # Add some randomness
        for emotion in emotions:
            emotions[emotion] += random.uniform(-0.1, 0.1)
            emotions[emotion] = max(0, min(1, emotions[emotion]))
        
        # Normalize
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v/total for k, v in emotions.items()}
        
        return emotions
    
    def _smooth_emotions(self) -> Dict[str, float]:
        """Apply temporal smoothing"""
        if not self.emotion_history:
            return self._get_default_emotions()
        
        smoothed = {emotion: 0.0 for emotion in self._get_default_emotions()}
        
        for emotions in self.emotion_history:
            for emotion, score in emotions.items():
                smoothed[emotion] += score
        
        # Average
        num_frames = len(self.emotion_history)
        for emotion in smoothed:
            smoothed[emotion] /= num_frames
        
        return smoothed
    
    def _create_empty_result(self, error: Optional[str] = None) -> Dict:
        """Create empty result when no faces detected"""
        return {
            'success': False,
            'emotions': self._get_default_emotions(),
            'dominant_emotion': 'neutral',
            'confidence': 0.0,
            'num_faces': 0,
            'faces': [],
            'timestamp': time.time(),
            'error': error
        }
    
    def _get_default_emotions(self) -> Dict[str, float]:
        """Get default emotion scores"""
        return {
            'angry': 0.0,
            'disgust': 0.0,
            'fear': 0.0,
            'happy': 0.0,
            'sad': 0.0,
            'surprise': 0.0,
            'neutral': 1.0
        }
    
    def _get_last_result(self) -> Dict:
        """Get the last detection result"""
        if self.emotion_history:
            smoothed = self._smooth_emotions()
            dominant = max(smoothed.items(), key=lambda x: x[1])[0]
            return {
                'success': True,
                'emotions': smoothed,
                'dominant_emotion': dominant,
                'confidence': smoothed[dominant],
                'cached': True,
                'timestamp': time.time()
            }
        return self._create_empty_result()
    
    def reset(self):
        """Reset emotion history"""
        self.emotion_history.clear()
        self.last_detection_time = 0
    
    def get_emotion_stats(self) -> Dict:
        """Get statistics"""
        return {
            'history_length': len(self.emotion_history),
            'current_emotions': self._smooth_emotions() if self.emotion_history else self._get_default_emotions()
        }