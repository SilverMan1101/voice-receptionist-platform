from abc import ABC, abstractmethod

class BaseSTTAdapter(ABC):
    """Base interface for Speech-to-Text adapters."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, mime_type: str = "audio/wav") -> str:
        """
        Transcribes the given audio data.
        
        Args:
            audio_data (bytes): The raw audio bytes.
            mime_type (str): The MIME type of the audio data.
            
        Returns:
            str: The transcribed text.
        """
        pass
