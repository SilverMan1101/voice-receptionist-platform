# import sys
# import os
# import pytest
# from uuid import uuid4

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services')))
# from knowledge_service.infrastructure.qdrant_adapter import QdrantAdapter

# @pytest.fixture
# def qdrant():
#     collection = f"test_tenant_isolation_{uuid4().hex}"
#     adapter = QdrantAdapter(collection_name=collection)
#     yield adapter
#     try:
#         adapter.client.delete_collection(adapter.collection_name)
#     except Exception:
#         pass

# def test_tenant_isolation(qdrant):
#     org_a = uuid4()
#     org_b = uuid4()
#     doc_a = uuid4()
#     doc_b = uuid4()

#     # Generate identical embeddings for both organizations
#     vector = [0.1] * 1536
#     chunks_a = [{"text": "Org A Secret", "metadata": {}}]
#     chunks_b = [{"text": "Org B Secret", "metadata": {}}]
    
#     try:
#         # Upsert for A
#         qdrant.upsert_chunks(
#             organization_id=org_a,
#             document_id=doc_a,
#             chunks=chunks_a,
#             vectors=[vector]
#         )

#         # Upsert for B
#         qdrant.upsert_chunks(
#             organization_id=org_b,
#             document_id=doc_b,
#             chunks=chunks_b,
#             vectors=[vector]
#         )

#         # Allow time for Qdrant to index (if needed, Qdrant is fast but let's be safe)
#         import time
#         time.sleep(1)

#         # Query as Org A
#         res_a = qdrant.search(organization_id=org_a, query_vector=vector, limit=10, threshold=0.0)
#         assert len(res_a) == 1
#         assert res_a[0][1]["text"] == "Org A Secret"

#         # Query as Org B
#         res_b = qdrant.search(organization_id=org_b, query_vector=vector, limit=10, threshold=0.0)
#         assert len(res_b) == 1
#         assert res_b[0][1]["text"] == "Org B Secret"

#     except Exception as e:
#         pytest.fail(f"Test failed: {e}")






































import os
import sys
from uuid import uuid4

import pytest

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../services")
    )
)

from knowledge_service.infrastructure.qdrant_adapter import QdrantAdapter


@pytest.fixture
def qdrant():
    collection = f"test_tenant_isolation_{uuid4().hex}"
    adapter = QdrantAdapter(collection_name=collection)

    yield adapter

    # Always clean up the temporary collection
    try:
        adapter.client.delete_collection(adapter.collection_name)
    except Exception:
        pass


def test_tenant_isolation(qdrant):
    """Ensure searches are isolated by organization_id."""

    org_a = uuid4()
    org_b = uuid4()

    doc_a = uuid4()
    doc_b = uuid4()

    # Use identical embeddings so this test cannot accidentally pass
    # because the vectors are naturally far apart.
    vector = [0.1] * 3072

    qdrant.upsert_chunks(
        organization_id=org_a,
        document_id=doc_a,
        chunks=[
            {
                "text": "Org A Secret",
                "metadata": {},
            }
        ],
        vectors=[vector],
    )

    qdrant.upsert_chunks(
        organization_id=org_b,
        document_id=doc_b,
        chunks=[
            {
                "text": "Org B Secret",
                "metadata": {},
            }
        ],
        vectors=[vector],
    )

    # Query as Organization A
    results_a = qdrant.search(
        organization_id=org_a,
        query_vector=vector,
        limit=10,
        threshold=0.0,
    )
    # print("results_a =", results_a)
    # print("first =", results_a[0])
    # print("len tuple =", len(results_a[0]))

    # texts_a = [chunk["text"] for _, chunk in results_a]
    # texts_a = [item[1]["text"] for item in results_a]
    # texts_a = [item[2]["text"] for item in results_a]
    texts_a = [item[1]["text"] for item in results_a]



    # Must return A's own data...
    assert "Org A Secret" in texts_a

    # ...and must never leak B's data.
    assert "Org B Secret" not in texts_a

    # Query as Organization B
    results_b = qdrant.search(
        organization_id=org_b,
        query_vector=vector,
        limit=10,
        threshold=0.0,
    )

    # texts_b = [chunk["text"] for _, chunk in results_b]
    texts_b = [item[1]["text"] for item in results_b]

    # Must return B's own data...
    assert "Org B Secret" in texts_b

    # ...and must never leak A's data.
    assert "Org A Secret" not in texts_b

    # Since each tenant only has one document, there should be exactly one hit.
    assert results_a[0][1]["organization_id"] == str(org_a)
    assert results_b[0][1]["organization_id"] == str(org_b)
    assert len(results_a) == 1
    assert len(results_b) == 1
