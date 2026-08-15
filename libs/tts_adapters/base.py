from abc import ABC, abstractmethod

class BaseTTSAdapter(ABC):
    """Base interface for Text-to-Speech adapters."""
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesizes text to audio.
        
        Args:
            text (str): The text to synthesize.
            
        Returns:
            bytes: The synthesized audio data (typically in WAV or mu-law format depending on the telephony provider requirements).
        """
        pass
