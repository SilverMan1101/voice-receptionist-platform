import sys
import os
import uuid
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from libs.embedding_adapters.openai_adapter import OpenAIEmbeddingAdapter
from libs.document_parsers.langchain_adapter import LangChainDocumentParser
from services.shared_kernel.domain.models import KnowledgeDocument, KnowledgeChunk
from services.knowledge_service.core.qdrant_client import QdrantStore

class IngestionPipeline:
    def __init__(self, qdrant_store: QdrantStore, db: Session):
        self.qdrant_store = qdrant_store
        self.db = db
        # TODO: Allow per-tenant adapter selection in the future
        self.parser = LangChainDocumentParser()
        self.embedder = OpenAIEmbeddingAdapter()

    def process_document(self, org_id: uuid.UUID, doc_id: uuid.UUID, file_path: str, source_type: str):
        """
        End-to-end pipeline: Parse -> Embed -> Upsert to Qdrant -> Update DB
        """
        db_doc = self.db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == doc_id, 
            KnowledgeDocument.organization_id == org_id
        ).first()
        
        if not db_doc:
            raise ValueError(f"Document {doc_id} not found for org {org_id}")

        db_doc.status = "indexing"
        self.db.commit()

        try:
            # 1. Parse
            parsed_docs = self.parser.parse(file_path, source_type)
            texts = [doc.content for doc in parsed_docs if doc.content.strip()]

            if not texts:
                raise ValueError("No text content found in document")

            # 2. Embed
            # Note: For large documents, we should chunk the `texts` array before embedding
            # to avoid rate limits, but for MVP we assume moderate file sizes or handle inside embed_batch.
            embeddings = self.embedder.embed_batch(texts)

            # 3. Upsert to Qdrant
            vector_ids = self.qdrant_store.upsert_chunks(
                org_id=str(org_id),
                doc_id=str(doc_id),
                chunks=texts,
                embeddings=embeddings
            )

            # 4. Save chunk metadata to Postgres
            for idx, (text, vec_id) in enumerate(zip(texts, vector_ids)):
                chunk_record = KnowledgeChunk(
                    document_id=doc_id,
                    content=text,
                    vector_ref=vec_id,
                    chunk_index=idx
                )
                self.db.add(chunk_record)

            db_doc.status = "indexed"
            db_doc.last_indexed_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            db_doc.status = "failed"
            self.db.commit()
            raise e
