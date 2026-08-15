import os
import redis
from .base import BaseTTSAdapter
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
class GeminiTTSAdapter(BaseTTSAdapter):
    def __init__(self, model_name: str = "gemini-2.0-flash", redis_url: str = None):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.redis_client = redis.from_url(redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio using Gemini's audio generation capability.
        Returns the raw audio bytes (typically PCM/WAV).
        """
        cache_key = f"tts_cache:{hash(text)}"
        cached_audio = self.redis_client.get(cache_key)
        if cached_audio:
            return cached_audio

        # Use Gemini 2.0 or 1.5 flash to generate audio output
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[text],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
            )
        )
        
        # Extract audio bytes from the response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                    audio_bytes = part.inline_data.data
                    # Cache short phrases like greetings or holds (heuristic: < 150 chars)
                    if len(text) < 150:
                        self.redis_client.setex(cache_key, 3600 * 24, audio_bytes)
                    return audio_bytes
                    
        raise ValueError("Failed to generate audio from Gemini")
