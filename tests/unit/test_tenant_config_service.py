import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from tenant_config_service.main import app, get_db
from shared_kernel.domain.models import Base
from auth.jwt_validator import get_current_token_data
from shared_kernel.domain.schemas import TokenData

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tenant_config.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_token_data():
    return TokenData(
        user_id="123e4567-e89b-12d3-a456-426614174000",
        organization_id="123e4567-e89b-12d3-a456-426614174001",
        role="admin"
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_token_data] = override_get_current_token_data

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_organization():
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Test Org",
            "industry_type": "Healthcare",
            "admin_email": "admin@test.com",
            "admin_password": "securepassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Org"
    assert "id" in data

def test_create_department():
    response = client.post(
        "/api/v1/departments",
        json={
            "name": "Sales",
            "escalation_number": "+1234567890"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sales"
    assert data["organization_id"] == "123e4567-e89b-12d3-a456-426614174001"

def test_update_voice_config():
    response = client.put(
        "/api/v1/voice-config",
        json={
            "voice_id": "alloy",
            "greeting_text": "Hello!",
            "language": "en"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["voice_id"] == "alloy"

def test_create_business_rule():
    response = client.post(
        "/api/v1/business-rules",
        json={
            "rule_type": "escalation",
            "condition": {"intent": "billing"},
            "action": {"transfer_to": "billing_dept"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rule_type"] == "escalation"
