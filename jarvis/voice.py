"""
ULTRON VOICE — Text-to-Speech engine.

Uses edge-tts for natural-sounding voice synthesis.
Falls back to pyttsx3 for offline operation.
"""

import asyncio
import os
import io
import time
import threading
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "jarvis" / "voice_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default voice — deep, clear, authoritative
DEFAULT_VOICE = "en-US-GuyNeural"
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "-5Hz"


async def speak_edge_tts(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Generate speech audio using edge-tts. Returns WAV bytes."""
    import edge_tts

    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=DEFAULT_RATE,
        pitch=DEFAULT_PITCH,
    )

    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])

    return bytes(audio_data)


def speak_pyttsx3(text: str):
    """Fallback: speak using system TTS."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Try to find a male voice
        for v in voices:
            if 'male' in v.name.lower() or 'david' in v.name.lower() or 'mark' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        engine.setProperty('rate', 175)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[VOICE] pyttsx3 error: {e}")


class VoiceEngine:
    """Voice synthesis engine for Ultron."""

    def __init__(self):
        self.voice = DEFAULT_VOICE
        self.enabled = True
        self._speaking = False
        self._queue = []
        self._lock = threading.Lock()

    async def speak(self, text: str) -> bytes:
        """Generate speech and return audio bytes (MP3 format from edge-tts)."""
        if not self.enabled or not text:
            return b''

        self._speaking = True
        try:
            audio = await speak_edge_tts(text, self.voice)
            return audio
        except Exception as e:
            print(f"[VOICE] edge-tts failed: {e}, falling back to pyttsx3")
            # Fallback to local TTS
            speak_pyttsx3(text)
            return b''
        finally:
            self._speaking = False

    @property
    def is_speaking(self):
        return self._speaking
