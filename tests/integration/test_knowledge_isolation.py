import pytest
import uuid
from services.knowledge_service.core.qdrant_client import QdrantStore

def test_qdrant_tenant_isolation():
    """
    Test to ensure that payload filtering in Qdrant successfully isolates tenant data.
    Verifies that querying with one organization ID does not return data from another organization.
    """
    store = QdrantStore(vector_size=2)
    
    org1_id = str(uuid.uuid4())
    org2_id = str(uuid.uuid4())
    
    doc1_id = str(uuid.uuid4())
    doc2_id = str(uuid.uuid4())
    
    try:
        # 1. Insert data for org 1
        store.upsert_chunks(
            org_id=org1_id,
            doc_id=doc1_id,
            chunks=["org1 chunk A", "org1 chunk B"],
            embeddings=[[0.1, 0.2], [0.3, 0.4]]
        )
        
        # 2. Insert data for org 2
        store.upsert_chunks(
            org_id=org2_id,
            doc_id=doc2_id,
            chunks=["org2 chunk A", "org2 chunk B"],
            embeddings=[[0.1, 0.21], [0.3, 0.41]] # Very similar vectors
        )
        
        # 3. Search as org 1 using a vector that matches both
        results_org1 = store.search(org_id=org1_id, query_embedding=[0.1, 0.2], limit=5)
        
        # Verify we only got org1's chunks
        assert len(results_org1) == 2
        for payload, score in results_org1:
            assert payload["organization_id"] == org1_id
            assert "org1" in payload["content"]
            
        # 4. Search as org 2
        results_org2 = store.search(org_id=org2_id, query_embedding=[0.1, 0.2], limit=5)
        
        assert len(results_org2) == 2
        for payload, score in results_org2:
            assert payload["organization_id"] == org2_id
            assert "org2" in payload["content"]
    finally:
        # 5. Cleanup
        store.delete_document(org_id=org1_id, doc_id=doc1_id)
        store.delete_document(org_id=org2_id, doc_id=doc2_id)
