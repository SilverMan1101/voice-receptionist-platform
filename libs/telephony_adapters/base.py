from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTelephonyAdapter(ABC):
    """Base interface for Telephony adapters."""
    
    @abstractmethod
    def validate_webhook_signature(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """
        Validates the webhook signature from the telephony provider.
        """
        pass
        
    @abstractmethod
    def generate_connect_response(self, stream_url: str) -> str:
        """
        Generates the provider-specific response to connect the call to a media stream (e.g. TwiML).
        """
        pass
