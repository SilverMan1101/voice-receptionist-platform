import os
from .base import BaseSTTAdapter
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
class GeminiSTTAdapter(BaseSTTAdapter):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    async def transcribe(self, audio_data: bytes, mime_type: str = "audio/wav") -> str:
        """
        Transcribe audio using Gemini's multimodal capabilities.
        Note: The input audio must be in a supported format. Twilio streams mu-law by default,
        so it may need to be wrapped in a wav container or decoded.
        """
        prompt = "Transcribe the following audio exactly as spoken, without any additional commentary."
        
        # Gemini API expects the part to specify the mime_type
        audio_part = types.Part.from_bytes(data=audio_data, mime_type=mime_type)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[audio_part, prompt]
        )
        
        return response.text.strip() if response.text else ""
