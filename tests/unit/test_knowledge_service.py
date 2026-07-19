import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
import json

from services.knowledge_service.main import app
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

@pytest.fixture
def mock_qdrant(mocker):
    # Mock the QdrantStore instance in the routers
    mock = mocker.patch("services.knowledge_service.api.v1.routes.knowledge.qdrant_store")
    mocker.patch("services.knowledge_service.api.v1.routes.retrieval.qdrant_store", mock)
    return mock

@pytest.fixture
def mock_embedder(mocker):
    # Mock the embedding adapter
    mock = mocker.patch("services.knowledge_service.api.v1.routes.retrieval.embedder")
    mock.embed_text.return_value = [0.1] * 1536
    return mock

@pytest.fixture
def mock_background_tasks(mocker):
    # Disable actual background processing during tests
    return mocker.patch("fastapi.BackgroundTasks.add_task")

def test_upload_knowledge(mock_qdrant, mock_background_tasks):
    org_id = str(uuid.uuid4())
    
    # Create a dummy file
    files = {'file': ('test.txt', b'This is test content', 'text/plain')}
    
    response = client.post(f"/api/v1/{org_id}/knowledge", files=files)
    assert response.status_code == 201
    
    data = response.json()
    assert data["organization_id"] == org_id
    assert data["filename_or_url"] == "test.txt"
    assert data["status"] == "pending"
    
    # Ensure background task was triggered
    mock_background_tasks.assert_called_once()

def test_get_knowledge_documents():
    org_id = str(uuid.uuid4())
    
    # Add a document directly to DB for retrieval
    db = TestingSessionLocal()
    from services.shared_kernel.domain.models import KnowledgeDocument
    doc = KnowledgeDocument(
        organization_id=uuid.UUID(org_id),
        source_type="txt",
        filename_or_url="test2.txt",
        status="processed"
    )
    db.add(doc)
    db.commit()
    db.close()
    
    response = client.get(f"/api/v1/{org_id}/knowledge")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename_or_url"] == "test2.txt"

def test_delete_knowledge(mock_qdrant):
    org_id = str(uuid.uuid4())
    
    # Add a document directly to DB
    db = TestingSessionLocal()
    from services.shared_kernel.domain.models import KnowledgeDocument
    doc = KnowledgeDocument(
        organization_id=uuid.UUID(org_id),
        source_type="txt",
        filename_or_url="test3.txt",
        status="processed"
    )
    db.add(doc)
    db.commit()
    doc_id = str(doc.id)
    db.close()
    
    # Delete the document
    response = client.delete(f"/api/v1/{org_id}/knowledge/{doc_id}")
    assert response.status_code == 204
    
    # Ensure Qdrant deletion was called
    mock_qdrant.delete_document.assert_called_once_with(org_id, doc_id)
    
    # Ensure it's deleted from DB
    response = client.get(f"/api/v1/{org_id}/knowledge")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_retrieve_knowledge(mock_qdrant, mock_embedder):
    org_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    
    # Mock qdrant search response
    mock_qdrant.search.return_value = [
        ({"content": "Relevant content", "document_id": doc_id, "chunk_index": 0}, 0.85)
    ]
    
    query_data = {
        "query_text": "Find relevant info",
        "limit": 5,
        "confidence_threshold": 0.8
    }
    
    response = client.post(f"/api/v1/{org_id}/retrieval", json=query_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    
    result = data["results"][0]
    assert result["content"] == "Relevant content"
    assert result["confidence_score"] == 0.85
    assert result["is_confident"] is True  # 0.85 >= 0.8
    
    # Verify qdrant was called with correct org_id
    mock_qdrant.search.assert_called_once()
    assert mock_qdrant.search.call_args[1]["org_id"] == org_id
