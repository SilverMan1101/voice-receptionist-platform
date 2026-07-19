from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
import shutil

from services.shared_kernel.domain.models import KnowledgeDocument
from services.shared_kernel.domain.schemas import KnowledgeDocumentResponse
from services.shared_kernel.core.database import get_db
from services.knowledge_service.core.qdrant_client import QdrantStore
from services.knowledge_service.core.ingestion import IngestionPipeline

router = APIRouter()
qdrant_store = QdrantStore()

def get_ingestion_pipeline(db: Session = Depends(get_db)):
    return IngestionPipeline(qdrant_store=qdrant_store, db=db)

@router.post("/{org_id}/knowledge", response_model=KnowledgeDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge(
    org_id: UUID, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    # Save file temporarily
    upload_dir = f"/tmp/uploads/{org_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Determine source type from extension
    ext = os.path.splitext(file.filename)[1].lstrip('.').lower()
    source_type = ext if ext else "txt"
    
    # Create DB record
    db_doc = KnowledgeDocument(
        organization_id=org_id,
        source_type=source_type,
        filename_or_url=file.filename,
        status="pending"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Trigger background indexing
    background_tasks.add_task(pipeline.process_document, org_id, db_doc.id, file_path, source_type)
    
    return db_doc

@router.get("/{org_id}/knowledge", response_model=List[KnowledgeDocumentResponse])
def get_knowledge_documents(org_id: UUID, db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.organization_id == org_id).all()
    return docs

@router.delete("/{org_id}/knowledge/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(org_id: UUID, doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.organization_id == org_id, KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from Qdrant
    qdrant_store.delete_document(str(org_id), str(doc_id))
    
    # Delete from Postgres (cascade will handle chunks)
    db.delete(doc)
    db.commit()
    return None
