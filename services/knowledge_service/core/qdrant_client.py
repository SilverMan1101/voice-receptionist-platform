import os
import uuid
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "knowledge_base")

class QdrantStore:
    def __init__(self, vector_size: int = 1536):
        self.client = QdrantClient(url=QDRANT_URL)
        self.collection_name = QDRANT_COLLECTION
        self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size: int):
        try:
            self.client.get_collection(self.collection_name)
        except UnexpectedResponse:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            # Create a payload index on organization_id for efficient filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="organization_id",
                field_schema="keyword"
            )

    def upsert_chunks(self, org_id: str, doc_id: str, chunks: List[str], embeddings: List[List[float]]) -> List[str]:
        """
        Upserts embedded chunks to Qdrant, associating them with the organization and document.
        Returns the list of vector IDs generated.
        """
        points = []
        vector_ids = []
        
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            vector_ids.append(point_id)
            
            payload = {
                "organization_id": org_id,
                "document_id": doc_id,
                "chunk_index": idx,
                "content": chunk_text
            }
            
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return vector_ids

    def search(self, org_id: str, query_embedding: List[float], limit: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches for relevant chunks using payload filtering by organization_id.
        Returns a list of tuples containing (payload, score).
        """
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=org_id)
                    )
                ]
            ),
            limit=limit,
            with_payload=True
        )
        
        return [(hit.payload, hit.score) for hit in search_result.points]

    def delete_document(self, org_id: str, doc_id: str):
        """
        Deletes all chunks associated with a specific document within an organization.
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="organization_id", match=MatchValue(value=org_id)),
                    FieldCondition(key="document_id", match=MatchValue(value=doc_id))
                ]
            )
        )
