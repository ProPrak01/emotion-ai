import cv2
import numpy as np
from fer import FER
from typing import Dict, List, Optional, Tuple
import logging
from collections import deque
import time
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        self.detector = FER(mtcnn=True)
        self.emotion_history = deque(maxlen=settings.emotion_smoothing_frames)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.last_detection_time = 0
        self.detection_interval = 1.0 / settings.detection_fps
        
    def detect_emotions(self, frame: np.ndarray) -> Dict:
        """
        Detect emotions from a video frame
        
        Args:
            frame: numpy array representing the image frame
            
        Returns:
            Dictionary with emotion data and metadata
        """
        current_time = time.time()
        
        # Rate limiting for performance
        if current_time - self.last_detection_time < self.detection_interval:
            return self._get_last_result()
            
        self.last_detection_time = current_time
        
        try:
            # Detect emotions
            result = self.detector.detect_emotions(frame)
            
            if not result:
                return self._create_empty_result()
            
            # Process multiple faces and get dominant emotion
            emotions_data = self._process_faces(result)
            
            # Add to history for smoothing
            self.emotion_history.append(emotions_data['emotions'])
            
            # Apply smoothing
            smoothed_emotions = self._smooth_emotions()
            
            # Get dominant emotion
            dominant_emotion = max(smoothed_emotions.items(), key=lambda x: x[1])[0]
            
            return {
                'success': True,
                'emotions': smoothed_emotions,
                'dominant_emotion': dominant_emotion,
                'confidence': smoothed_emotions[dominant_emotion],
                'num_faces': len(result),
                'faces': emotions_data['faces'],
                'timestamp': current_time,
                'processing_time': time.time() - current_time
            }
            
        except Exception as e:
            logger.error(f"Error detecting emotions: {e}")
            return self._create_empty_result(error=str(e))
    
    def _process_faces(self, faces: List[Dict]) -> Dict:
        """Process multiple faces and aggregate emotions"""
        all_emotions = {
            'angry': [],
            'disgust': [],
            'fear': [],
            'happy': [],
            'sad': [],
            'surprise': [],
            'neutral': []
        }
        
        face_data = []
        
        for face in faces[:settings.max_faces]:
            emotions = face['emotions']
            box = face['box']
            
            # Filter by confidence threshold
            for emotion, score in emotions.items():
                if score >= settings.confidence_threshold:
                    all_emotions[emotion].append(score)
            
            face_data.append({
                'box': box,
                'emotions': emotions
            })
        
        # Average emotions across all faces
        averaged_emotions = {}
        for emotion, scores in all_emotions.items():
            if scores:
                averaged_emotions[emotion] = np.mean(scores)
            else:
                averaged_emotions[emotion] = 0.0
        
        # Normalize scores
        total = sum(averaged_emotions.values())
        if total > 0:
            averaged_emotions = {k: v/total for k, v in averaged_emotions.items()}
        
        return {
            'emotions': averaged_emotions,
            'faces': face_data
        }
    
    def _smooth_emotions(self) -> Dict[str, float]:
        """Apply temporal smoothing to emotion scores"""
        if not self.emotion_history:
            return self._get_default_emotions()
        
        smoothed = {emotion: 0.0 for emotion in self._get_default_emotions()}
        
        for emotions in self.emotion_history:
            for emotion, score in emotions.items():
                smoothed[emotion] += score
        
        # Average over history
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
        """Get the last detection result for rate limiting"""
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
        """Get statistics about emotion detection"""
        if not self.emotion_history:
            return {'history_length': 0, 'emotions': self._get_default_emotions()}
        
        return {
            'history_length': len(self.emotion_history),
            'current_emotions': self._smooth_emotions(),
            'detection_fps': settings.detection_fps,
            'smoothing_frames': settings.emotion_smoothing_frames
        }