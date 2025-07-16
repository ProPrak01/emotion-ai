import pytest
import numpy as np
import cv2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion_detector import EmotionDetector

class TestEmotionDetector:
    @pytest.fixture
    def detector(self):
        return EmotionDetector()
    
    @pytest.fixture
    def test_frame(self):
        # Create a test frame (640x480 RGB)
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_initialization(self, detector):
        assert detector is not None
        assert detector.detector is not None
        assert len(detector.emotion_history) == 0
    
    def test_detect_emotions_with_frame(self, detector, test_frame):
        result = detector.detect_emotions(test_frame)
        
        assert 'success' in result
        assert 'emotions' in result
        assert 'dominant_emotion' in result
        assert 'confidence' in result
        assert 'timestamp' in result
        
        # Check emotion scores
        emotions = result['emotions']
        assert len(emotions) == 7
        assert all(0 <= score <= 1 for score in emotions.values())
        assert abs(sum(emotions.values()) - 1.0) < 0.01  # Should sum to ~1
    
    def test_empty_frame_handling(self, detector):
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_emotions(empty_frame)
        
        assert result is not None
        assert 'success' in result
    
    def test_emotion_smoothing(self, detector, test_frame):
        # Run detection multiple times
        for _ in range(10):
            detector.detect_emotions(test_frame)
        
        assert len(detector.emotion_history) <= detector.emotion_history.maxlen
        
        # Check smoothing
        smoothed = detector._smooth_emotions()
        assert len(smoothed) == 7
        assert all(isinstance(score, float) for score in smoothed.values())
    
    def test_rate_limiting(self, detector, test_frame):
        import time
        
        # First detection should work
        result1 = detector.detect_emotions(test_frame)
        assert not result1.get('cached', False)
        
        # Immediate second detection should be cached
        result2 = detector.detect_emotions(test_frame)
        assert result2.get('cached', False)
        
        # Wait for rate limit to pass
        time.sleep(detector.detection_interval + 0.1)
        result3 = detector.detect_emotions(test_frame)
        assert not result3.get('cached', False)
    
    def test_reset(self, detector, test_frame):
        # Add some history
        for _ in range(5):
            detector.detect_emotions(test_frame)
        
        assert len(detector.emotion_history) > 0
        
        # Reset
        detector.reset()
        assert len(detector.emotion_history) == 0
        assert detector.last_detection_time == 0
    
    def test_get_emotion_stats(self, detector, test_frame):
        # Initial stats
        stats = detector.get_emotion_stats()
        assert stats['history_length'] == 0
        
        # After detection
        detector.detect_emotions(test_frame)
        stats = detector.get_emotion_stats()
        assert stats['history_length'] > 0
        assert 'current_emotions' in stats
        assert 'detection_fps' in stats
    
    @pytest.mark.parametrize("num_faces", [0, 1, 3, 10])
    def test_multi_face_handling(self, detector, num_faces):
        # Mock faces result
        faces = []
        for i in range(num_faces):
            faces.append({
                'box': [i*50, i*50, 100, 100],
                'emotions': {
                    'angry': 0.1,
                    'disgust': 0.1,
                    'fear': 0.1,
                    'happy': 0.4,
                    'sad': 0.1,
                    'surprise': 0.1,
                    'neutral': 0.1
                }
            })
        
        result = detector._process_faces(faces)
        assert 'emotions' in result
        assert 'faces' in result
        assert len(result['faces']) == min(num_faces, detector.face_cascade)  # Limited by max_faces

if __name__ == "__main__":
    pytest.main([__file__, "-v"])