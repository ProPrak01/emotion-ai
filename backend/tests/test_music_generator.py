import pytest
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_generator import MusicGenerator
from config import settings

class TestMusicGenerator:
    @pytest.fixture
    def music_gen(self):
        return MusicGenerator()
    
    def test_initialization(self, music_gen):
        assert music_gen is not None
        assert music_gen.current_emotion == "neutral"
        assert music_gen.target_emotion == "neutral"
        assert music_gen.volume == 0.6
        assert music_gen.style == settings.default_music_style
    
    def test_load_music_tracks(self, music_gen):
        # Should have tracks for each emotion
        expected_emotions = list(settings.emotion_music_params.keys())
        assert all(emotion in music_gen.music_tracks for emotion in expected_emotions)
        
        # Each emotion should have at least one track
        for emotion, tracks in music_gen.music_tracks.items():
            assert len(tracks) >= 1
    
    @pytest.mark.asyncio
    async def test_update_emotion(self, music_gen):
        # Test emotion update
        await music_gen.update_emotion("happy", 0.8)
        assert music_gen.target_emotion == "happy"
        
        # Test with invalid emotion
        await music_gen.update_emotion("invalid_emotion", 0.5)
        # Should not crash, target emotion should remain
        assert music_gen.target_emotion == "happy"
    
    def test_volume_control(self, music_gen):
        # Test volume limits
        music_gen.set_volume(0.5)
        assert music_gen.volume == 0.5
        
        music_gen.set_volume(1.5)  # Over limit
        assert music_gen.volume == 1.0
        
        music_gen.set_volume(-0.5)  # Under limit
        assert music_gen.volume == 0.0
    
    def test_style_change(self, music_gen):
        original_style = music_gen.style
        
        music_gen.set_style("electronic")
        assert music_gen.style == "electronic"
        
        music_gen.set_style("classical")
        assert music_gen.style == "classical"
    
    def test_get_current_state(self, music_gen):
        state = music_gen.get_current_state()
        
        assert 'current_emotion' in state
        assert 'target_emotion' in state
        assert 'is_playing' in state
        assert 'volume' in state
        assert 'style' in state
        assert 'params' in state
        assert 'available_styles' in state
        
        assert state['current_emotion'] == "neutral"
        assert isinstance(state['params'], dict)
    
    def test_playback_control(self, music_gen):
        # Test start
        music_gen.start_playback()
        assert music_gen.is_playing == True
        
        # Test stop
        music_gen.stop_playback()
        assert music_gen.is_playing == False
    
    def test_reset(self, music_gen):
        # Change state
        music_gen.current_emotion = "happy"
        music_gen.target_emotion = "sad"
        music_gen.current_params = {"tempo": 1.5}
        
        # Reset
        music_gen.reset()
        
        assert music_gen.current_emotion == "neutral"
        assert music_gen.target_emotion == "neutral"
        assert music_gen.current_params == settings.emotion_music_params["neutral"]
    
    def test_placeholder_audio_creation(self, music_gen):
        # Test placeholder audio generation
        for emotion in settings.emotion_music_params.keys():
            audio = music_gen._create_placeholder_audio(emotion)
            assert audio is not None
            assert audio.duration_seconds > 0
            assert audio.frame_rate == 44100
    
    def test_ambient_track_creation(self, music_gen):
        ambient = music_gen._create_ambient_track()
        assert ambient is not None
        assert ambient.duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_emotion_transition_params(self, music_gen):
        # Test parameter updates during transition
        initial_params = music_gen.current_params.copy()
        
        await music_gen.update_emotion("happy", 0.9)
        
        # Parameters should change
        assert music_gen.current_params != initial_params
        
        # Check specific param ranges
        assert 0 <= music_gen.current_params['volume'] <= 1
        assert 0 <= music_gen.current_params['tempo'] <= 2
        assert 0 <= music_gen.current_params['reverb'] <= 1
        assert 0 <= music_gen.current_params['brightness'] <= 1
    
    def test_thread_safety(self, music_gen):
        # Test transition lock
        assert music_gen.transition_lock is not None
        
        # Acquire lock
        with music_gen.transition_lock:
            # Lock should be held
            assert music_gen.transition_lock.locked()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])