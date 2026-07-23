import os
from uuid import UUID
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

class QdrantAdapter:
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "knowledge"):
        # We can configure this via env vars later
        qdrant_host = os.getenv("QDRANT_HOST", host)
        self.client = QdrantClient(host=qdrant_host, port=port)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # 1536 for text-embedding-3-small
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(size=1536, distance=qmodels.Distance.COSINE),
            )
            # Create a payload index on organization_id for fast filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="organization_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )

    def upsert_chunks(self, organization_id: UUID, document_id: UUID, chunks: List[Dict[str, Any]], vectors: List[List[float]]):
        """
        chunks: List of dicts containing 'text' and 'metadata'.
        """
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = str(UUID(int=(organization_id.int ^ document_id.int ^ i)))
            payload = {
                "organization_id": str(organization_id),
                "document_id": str(document_id),
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            }
            points.append(
                qmodels.PointStruct(id=point_id, vector=vector, payload=payload)
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, organization_id: UUID, query_vector: List[float], limit: int = 5, threshold: float = 0.7) -> List[Tuple[float, Dict[str, Any], bool]]:
        """
        Returns list of (score, payload, is_confident)
        """
        filter_org = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="organization_id",
                    match=qmodels.MatchValue(value=str(organization_id)),
                )
            ]
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=filter_org,
            limit=limit,
        )

        ret = []
        for r in results.points:
            is_confident = r.score >= threshold
            ret.append((r.score, r.payload, is_confident))
            
        return ret
