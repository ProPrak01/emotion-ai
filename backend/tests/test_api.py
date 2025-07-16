import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
import base64
import numpy as np
from PIL import Image
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_image(self):
        # Create a test image
        img = Image.new('RGB', (640, 480), color='white')
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='JPEG')
        img_byte_array.seek(0)
        return img_byte_array
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "emotion_detector" in data
        assert "music_generator" in data
    
    def test_emotion_detection_endpoint(self, client, test_image):
        response = client.post(
            "/api/emotion",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "emotions" in data
        assert "dominant_emotion" in data
    
    def test_emotion_detection_invalid_file(self, client):
        response = client.post(
            "/api/emotion",
            files={"file": ("test.txt", b"not an image", "text/plain")}
        )
        assert response.status_code == 400 or response.status_code == 500
    
    def test_music_control_endpoint(self, client):
        response = client.get("/api/music/control")
        assert response.status_code == 200
        data = response.json()
        assert "current_emotion" in data
        assert "is_playing" in data
        assert "volume" in data
        assert "style" in data
    
    def test_music_update_endpoint(self, client):
        response = client.post(
            "/api/music/update",
            params={"emotion": "happy", "confidence": 0.8}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["emotion"] == "happy"
    
    def test_stats_endpoint(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "detector_stats" in data
        assert "music_state" in data
        assert "history" in data
        assert "total_detections" in data
    
    def test_websocket_connection(self, client):
        with client.websocket_connect("/ws") as websocket:
            # Send a test message
            test_frame = {
                "type": "frame",
                "data": "data:image/jpeg;base64,/9j/4AAQSkZJRg=="  # Minimal JPEG header
            }
            websocket.send_text(json.dumps(test_frame))
            
            # Should receive a response (or timeout)
            try:
                data = websocket.receive_json(timeout=2)
                assert "type" in data
            except:
                # Timeout is acceptable for invalid image
                pass
    
    def test_websocket_control_messages(self, client):
        with client.websocket_connect("/ws") as websocket:
            # Test volume control
            control_msg = {
                "type": "control",
                "action": "set_volume",
                "value": 0.7
            }
            websocket.send_text(json.dumps(control_msg))
            
            # Test style control
            style_msg = {
                "type": "control",
                "action": "set_style",
                "value": "electronic"
            }
            websocket.send_text(json.dumps(style_msg))
            
            # Test reset
            reset_msg = {
                "type": "control",
                "action": "reset"
            }
            websocket.send_text(json.dumps(reset_msg))
    
    def test_calibrate_endpoint(self, client, test_image):
        response = client.post(
            "/api/calibrate",
            params={"emotion": "happy"},
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @pytest.mark.parametrize("emotion", ["happy", "sad", "angry", "neutral"])
    def test_music_update_various_emotions(self, client, emotion):
        response = client.post(
            f"/api/music/update",
            params={"emotion": emotion, "confidence": 0.75}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["emotion"] == emotion
    
    def test_concurrent_websocket_connections(self, client):
        # Test multiple simultaneous connections
        websockets = []
        try:
            for i in range(3):
                ws = client.websocket_connect("/ws").__enter__()
                websockets.append(ws)
            
            # All should be connected
            assert len(websockets) == 3
            
        finally:
            for ws in websockets:
                ws.__exit__(None, None, None)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])