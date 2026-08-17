import sys
import os
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services')))
from knowledge_service.main import app as knowledge_app
from conversation_engine.main import app as engine_app
from shared_kernel.domain import models
from shared_kernel.core.database import SessionLocal, engine

# Setup test DB
models.Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def knowledge_client():
    with TestClient(knowledge_app) as client:
        yield client

@pytest.fixture(scope="module")
def engine_client():
    with TestClient(engine_app) as client:
        yield client

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_token_data(org_id: str):
    def mock_dependency():
        from shared_kernel.domain.schemas import TokenData
        return TokenData(organization_id=org_id, role="admin")
    return mock_dependency

def test_knowledge_api_isolation(knowledge_client, db_session):
    org_a = uuid4()
    org_b = uuid4()

    # Seed DB
    db_session.add(models.Organization(id=org_a, name="Org A"))
    db_session.add(models.Organization(id=org_b, name="Org B"))
    db_session.commit()

    doc_a = models.KnowledgeDocument(organization_id=org_a, source_type="pdf", filename_or_url="doc_a.pdf")
    doc_b = models.KnowledgeDocument(organization_id=org_b, source_type="pdf", filename_or_url="doc_b.pdf")
    db_session.add(doc_a)
    db_session.add(doc_b)
    db_session.commit()

    # Query as org_a
    from knowledge_service.main import get_current_token_data as k_get_current_token_data
    knowledge_app.dependency_overrides[k_get_current_token_data] = override_get_current_token_data(str(org_a))
    
    response = knowledge_client.get("/api/v1/knowledge")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["filename_or_url"] == "doc_a.pdf" for d in data)
    assert not any(d["filename_or_url"] == "doc_b.pdf" for d in data)

    # Cleanup overrides
    knowledge_app.dependency_overrides.clear()

def test_calls_api_isolation(engine_client, db_session):
    org_a = uuid4()
    org_b = uuid4()

    # Seed DB
    # (Orgs might already exist if tests run in same session, but it's safe to add since we use new UUIDs)
    db_session.add(models.Organization(id=org_a, name="Org A"))
    db_session.add(models.Organization(id=org_b, name="Org B"))
    db_session.commit()

    call_a = models.Call(organization_id=org_a, caller_number="+1234567890")
    call_b = models.Call(organization_id=org_b, caller_number="+0987654321")
    db_session.add(call_a)
    db_session.add(call_b)
    db_session.commit()

    # Query as org_b
    from libs.auth.jwt_validator import get_current_token_data
    engine_app.dependency_overrides[get_current_token_data] = override_get_current_token_data(str(org_b))
    
    response = engine_client.get("/api/v1/calls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["caller_number"] == "+0987654321" for c in data)
    assert not any(c["caller_number"] == "+1234567890" for c in data)

    # Cleanup overrides
    engine_app.dependency_overrides.clear()
