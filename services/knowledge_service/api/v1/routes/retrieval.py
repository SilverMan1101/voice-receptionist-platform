from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from services.knowledge_service.core.qdrant_client import QdrantStore
from libs.embedding_adapters.openai_adapter import OpenAIEmbeddingAdapter

router = APIRouter()

qdrant_store = QdrantStore()
embedder = OpenAIEmbeddingAdapter()

class RetrievalQuery(BaseModel):
    query_text: str
    limit: int = 5
    confidence_threshold: float = 0.75 # Default threshold

class RetrievalResult(BaseModel):
    content: str
    document_id: str
    chunk_index: int
    confidence_score: float
    is_confident: bool
    metadata: Dict[str, Any]

class RetrievalResponse(BaseModel):
    results: List[RetrievalResult]

@router.post("/{org_id}/retrieval", response_model=RetrievalResponse)
def retrieve_knowledge(org_id: UUID, query: RetrievalQuery):
    try:
        # Embed the query
        query_embedding = embedder.embed_text(query.query_text)
        
        # Search Qdrant with payload filtering
        hits = qdrant_store.search(
            org_id=str(org_id),
            query_embedding=query_embedding,
            limit=query.limit
        )
        
        results = []
        for payload, score in hits:
            results.append(
                RetrievalResult(
                    content=payload.get("content", ""),
                    document_id=payload.get("document_id", ""),
                    chunk_index=payload.get("chunk_index", 0),
                    confidence_score=score,
                    is_confident=score >= query.confidence_threshold,
                    metadata=payload
                )
            )
            
        return RetrievalResponse(results=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
