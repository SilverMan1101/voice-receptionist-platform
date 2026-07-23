import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from knowledge_service.main import app, get_db, qdrant, embedder
from shared_kernel.domain.models import Base
from auth.jwt_validator import get_current_token_data
from shared_kernel.domain.schemas import TokenData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_knowledge.db"
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

def test_query_knowledge(monkeypatch):
    # Mock Qdrant and Embedder
    qdrant.search = MagicMock(return_value=[
        (0.85, {"text": "This is grounded info", "metadata": {}}, True),
        (0.60, {"text": "Less confident info", "metadata": {}}, False)
    ])
    embedder.embed_text = MagicMock(return_value=[0.1] * 1536)

    response = client.post(
        "/api/v1/knowledge/query",
        json={"query": "test query", "threshold": 0.7}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    
    res1 = data["results"][0]
    assert res1["score"] == 0.85
    assert res1["is_confident"] is True
    assert res1["text"] == "This is grounded info"

    res2 = data["results"][1]
    assert res2["score"] == 0.60
    assert res2["is_confident"] is False
    assert res2["text"] == "Less confident info"

    # Verify Qdrant was called with correct org
    qdrant.search.assert_called_once()
    kwargs = qdrant.search.call_args[1]
    assert str(kwargs["organization_id"]) == "123e4567-e89b-12d3-a456-426614174001"
