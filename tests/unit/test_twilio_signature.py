import pytest
from twilio.request_validator import RequestValidator
from libs.telephony_adapters.twilio_adapter import TwilioAdapter

def test_twilio_signature_validation_success():
    auth_token = "12345"
    adapter = TwilioAdapter(auth_token=auth_token)
    
    url = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {
        "CallSid": "CA1234567890AWWW",
        "Caller": "+12349013030",
        "Digits": "1234",
        "From": "+12349013030",
        "To": "+18005551212"
    }
    
    # Generate a valid signature for the given params and token
    validator = RequestValidator(auth_token)
    signature = validator.compute_signature(url, params)
    
    # Adapter should validate it successfully
    is_valid = adapter.validate_webhook_signature(signature, url, params)
    assert is_valid is True

def test_twilio_signature_validation_failure():
    auth_token = "12345"
    adapter = TwilioAdapter(auth_token=auth_token)
    
    url = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {
        "CallSid": "CA1234567890AWWW",
    }
    
    # Invalid signature
    signature = "invalid_signature="
    
    is_valid = adapter.validate_webhook_signature(signature, url, params)
    assert is_valid is False

def test_twilio_signature_validation_no_token():
    # If no token is provided, it should fail closed based on our implementation
    adapter = TwilioAdapter(auth_token="")
    url = "https://mycompany.com/webhook"
    
    is_valid = adapter.validate_webhook_signature("anysig", url, {})
    assert is_valid is False
