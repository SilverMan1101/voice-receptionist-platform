from fastapi.testclient import TestClient
import sys
import os

# Add the conversation-engine directory directly to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services/conversation-engine')))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "conversation-engine"}
