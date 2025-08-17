"""
Audio processing utilities for voice assistant.
"""

import io
import wave
import numpy as np
from typing import Optional, Tuple
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import base64
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio recording, transcription, and synthesis."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000
        self.channels = 1
    
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Convert audio bytes to text using speech recognition."""
        try:
            # Convert bytes to AudioData
            audio = sr.AudioData(audio_data, self.sample_rate, 2)
            
            # Use Google Speech Recognition (can be replaced with other services)
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            logger.warning("Speech not recognized")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            raise Exception(f"Speech recognition error: {e}")
    
    async def synthesize_speech(self, text: str, language: str = 'en') -> bytes:
        """Convert text to speech and return audio bytes."""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Read audio data
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(tmp_path)
            
            return audio_data
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise Exception(f"Text-to-speech error: {e}")
    
    def process_audio_stream(self, audio_chunk: bytes) -> Tuple[bool, Optional[bytes]]:
        """Process incoming audio stream chunk."""
        # This would implement voice activity detection
        # and audio buffering for real-time processing
        # Return (is_speech_complete, processed_audio)
        return False, None
    
    def convert_webm_to_wav(self, webm_data: bytes) -> bytes:
        """Convert WebM audio to WAV format."""
        # This would use ffmpeg or similar to convert formats
        # For now, return as-is (needs implementation)
        return webm_data
    
    def encode_audio_base64(self, audio_data: bytes) -> str:
        """Encode audio data to base64 string."""
        return base64.b64encode(audio_data).decode('utf-8')
    
    def decode_audio_base64(self, audio_base64: str) -> bytes:
        """Decode base64 string to audio data."""
        return base64.b64decode(audio_base64)


class VoiceActivityDetector:
    """Detects voice activity in audio streams."""
    
    def __init__(self, threshold: float = 0.01):
        self.threshold = threshold
        self.buffer = []
        self.is_speaking = False
        self.silence_count = 0
        self.max_silence = 20  # frames of silence before stopping
    
    def process_frame(self, audio_frame: bytes) -> Tuple[bool, bool]:
        """
        Process an audio frame for voice activity.
        Returns: (is_voice_active, is_speech_complete)
        """
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_frame, dtype=np.int16)
        
        # Calculate energy
        energy = np.sqrt(np.mean(audio_array ** 2))
        
        # Normalize energy
        normalized_energy = energy / 32768.0
        
        # Check if voice is active
        voice_active = normalized_energy > self.threshold
        
        speech_complete = False
        
        if voice_active:
            self.is_speaking = True
            self.silence_count = 0
            self.buffer.append(audio_frame)
        elif self.is_speaking:
            self.silence_count += 1
            self.buffer.append(audio_frame)
            
            if self.silence_count >= self.max_silence:
                # Speech is complete
                speech_complete = True
                self.is_speaking = False
                self.silence_count = 0
        
        return voice_active, speech_complete
    
    def get_speech_buffer(self) -> bytes:
        """Get the accumulated speech buffer."""
        if not self.buffer:
            return b''
        
        result = b''.join(self.buffer)
        self.buffer = []
        return result
    
    def reset(self):
        """Reset the detector state."""
        self.buffer = []
        self.is_speaking = False
        self.silence_count = 0
