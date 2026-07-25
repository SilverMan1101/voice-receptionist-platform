from typing import List, Optional
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    text: str
    metadata: dict

class DocumentParserAdapter:
    def parse(self, file_path: str, source_type: str) -> List[DocumentChunk]:
        """Parses a document and returns a list of chunks."""
        raise NotImplementedError

class LangChainDocumentParser(DocumentParserAdapter):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )

    def parse(self, file_path: str, source_type: str) -> List[DocumentChunk]:
        # Very simplified loader selection based on extension
        from langchain_community.document_loaders import PyPDFLoader, TextLoader

        if source_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif source_type == "text":
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        docs = loader.load()
        chunks = self.text_splitter.split_documents(docs)
        
        return [DocumentChunk(text=chunk.page_content, metadata=chunk.metadata) for chunk in chunks]
