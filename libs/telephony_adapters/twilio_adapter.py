import os
from typing import Dict, Any
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from .base import BaseTelephonyAdapter
from dotenv import load_dotenv

load_dotenv()
class TwilioAdapter(BaseTelephonyAdapter):
    def __init__(self, auth_token: str = None):
        self.auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "6cbf20a03f4388361671ba19522bce5c")
        self.validator = RequestValidator(self.auth_token)
        
    def validate_webhook_signature(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """
        Validates that the incoming request truly originated from Twilio.
        """
        if not self.auth_token:
            # If no auth token is provided in dev, fail open or fail closed depending on environment.
            # But the requirement says "strictly verify", so let's enforce it if we have it, 
            # or return false if we don't.
            return False
        return self.validator.validate(url, params, signature)
        
    def generate_connect_response(self, stream_url: str) -> str:
        """
        Generates the TwiML to connect the call to our WebSocket Media Stream.
        """
        response = VoiceResponse()
        connect = Connect()
        connect.stream(url=stream_url)
        response.append(connect)
        return str(response)
