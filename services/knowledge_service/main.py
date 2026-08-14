import sys
import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from shared_kernel.core.database import get_db
from shared_kernel.domain import models, schemas
from auth.jwt_validator import get_current_token_data
from document_parsers.base import LangChainDocumentParser
# from embedding_adapters.base import OpenAIEmbeddingAdapter
from embedding_adapters.base import GeminiEmbeddingAdapter
from knowledge_service.infrastructure.qdrant_adapter import QdrantAdapter
app = FastAPI(title="Knowledge Service")


parser = None
embedder = None
qdrant = None
# Initialize adapters
# parser = LangChainDocumentParser()
# embedder = OpenAIEmbeddingAdapter()
# qdrant = QdrantAdapter()

@app.on_event("startup")
def startup_event():
    global parser, embedder, qdrant

    print("START: parser")
    parser = LangChainDocumentParser()

    print("START: embedder")
    embedder = GeminiEmbeddingAdapter()

    print("START: qdrant")
    qdrant = QdrantAdapter()

    print("DONE startup")


class QueryRequest(BaseModel):
    query: str
    limit: int = 5
    threshold: float = 0.5 # Default threshold

class QueryResponseChunk(BaseModel):
    score: float
    is_confident: bool
    text: str
    metadata: dict

class QueryResponse(BaseModel):
    results: List[QueryResponseChunk]

@app.post("/api/v1/knowledge/upload", response_model=schemas.KnowledgeDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    token_data: schemas.TokenData = Depends(get_current_token_data),
    db: Session = Depends(get_db)
):
    # Determine source type based on extension
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        source_type = "pdf"
    elif ext in ["txt", "md"]:
        source_type = "text"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Create DB entry
    db_doc = models.KnowledgeDocument(
        organization_id=token_data.organization_id,
        source_type=source_type,
        filename_or_url=filename,
        status="indexing"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    try:
        # Save uploaded file to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Parse
        chunks = parser.parse(tmp_path, source_type)
        
        # Embed
        texts = [c.text for c in chunks]
        if texts:
            vectors = embedder.embed_texts(texts)
            
            # Prepare payload for upsert
            payloads = [{"text": c.text, "metadata": c.metadata} for c in chunks]
            
            # Upsert to Qdrant
            qdrant.upsert_chunks(
                organization_id=token_data.organization_id,
                document_id=db_doc.id,
                chunks=payloads,
                vectors=vectors
            )

        # Cleanup tmp
        os.remove(tmp_path)

        # Mark as indexed
        db_doc.status = "indexed"
        from datetime import datetime
        db_doc.last_indexed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_doc)

    except Exception as e:
        db_doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

    return db_doc

@app.post("/api/v1/knowledge/query", response_model=QueryResponse)
def query_knowledge(
    req: QueryRequest,
    token_data: schemas.TokenData = Depends(get_current_token_data)
):
    # Embed query
    query_vector = embedder.embed_text(req.query)
    
    # Search Qdrant
    search_results = qdrant.search(
        organization_id=token_data.organization_id,
        query_vector=query_vector,
        limit=req.limit,
        threshold=req.threshold
    )

    # Format response
    results = []
    for score, payload, is_confident in search_results:
        results.append(QueryResponseChunk(
            score=score,
            is_confident=is_confident,
            text=payload.get("text", ""),
            metadata=payload.get("metadata", {})
        ))
    
    return QueryResponse(results=results)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "knowledge_service"}
