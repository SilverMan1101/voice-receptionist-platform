import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from services.tenant_config_service.main import app
from services.shared_kernel.core.database import get_db
from services.shared_kernel.domain.models import Base

# Setup in-memory SQLite for testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_organization():
    # Create Organization
    org_data = {
        "name": "Test Org",
        "industry": "Healthcare",
        "timezone": "UTC"
    }
    response = client.post("/api/v1/organizations/", json=org_data)
    assert response.status_code == 201
    created_org = response.json()
    assert created_org["name"] == "Test Org"
    assert "id" in created_org
    
    org_id = created_org["id"]
    
    # Get Organization
    response = client.get(f"/api/v1/organizations/{org_id}")
    assert response.status_code == 200
    assert response.json()["id"] == org_id

def test_create_and_get_department():
    # First create an organization
    org_response = client.post("/api/v1/organizations/", json={"name": "Test Org 2", "industry_type": "Tech", "timezone": "UTC"})
    org_id = org_response.json()["id"]
    
    # Create Department
    dept_data = {
        "name": "Sales",
        "escalation_number": "+1234567890"
    }
    response = client.post(f"/api/v1/organizations/{org_id}/departments", json=dept_data)
    assert response.status_code == 201
    created_dept = response.json()
    assert created_dept["name"] == "Sales"
    
    dept_id = created_dept["id"]
    
    # Get Departments list
    response = client.get(f"/api/v1/organizations/{org_id}/departments")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == dept_id

def test_create_voice_config():
    org_response = client.post("/api/v1/organizations/", json={"name": "Test Org 3", "industry_type": "Retail", "timezone": "UTC"})
    org_id = org_response.json()["id"]
    
    voice_data = {
        "voice_id": "test_voice",
        "language": "en-US",
        "tone": "professional"
    }
    response = client.post(f"/api/v1/organizations/{org_id}/voice-configs", json=voice_data)
    assert response.status_code == 201
    assert response.json()["voice_id"] == "test_voice"

def test_create_business_rule():
    org_response = client.post("/api/v1/organizations/", json={"name": "Test Org 4", "industry_type": "Finance", "timezone": "UTC"})
    org_id = org_response.json()["id"]
    
    rule_data = {
        "rule_type": "routing",
        "condition": {"type": "intent", "value": "sales"},
        "action": {"type": "transfer", "destination": "sales_agent"},
        "active": True
    }
    response = client.post(f"/api/v1/organizations/{org_id}/business-rules", json=rule_data)
    assert response.status_code == 201
    assert response.json()["rule_type"] == "routing"
