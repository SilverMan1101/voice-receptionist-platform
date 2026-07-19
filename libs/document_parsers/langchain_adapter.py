from .base import DocumentParserAdapter, ParsedDocument
from typing import List

try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        UnstructuredWordDocumentLoader,
        CSVLoader,
        UnstructuredMarkdownLoader,
        WebBaseLoader,
    )
except ImportError:
    PyPDFLoader = None

class LangChainDocumentParser(DocumentParserAdapter):
    def __init__(self):
        if PyPDFLoader is None:
            raise ImportError("Please install langchain-community and required unstructured packages to use LangChainDocumentParser")

    def parse(self, file_path: str, source_type: str) -> List[ParsedDocument]:
        loader = self._get_loader(file_path, source_type)
        if not loader:
            raise ValueError(f"Unsupported source type: {source_type}")
            
        docs = loader.load()
        
        parsed_docs = []
        for doc in docs:
            parsed_docs.append(
                ParsedDocument(
                    content=doc.page_content,
                    metadata=doc.metadata
                )
            )
            
        return parsed_docs

    def _get_loader(self, file_path: str, source_type: str):
        source_type = source_type.lower()
        if source_type == "pdf":
            return PyPDFLoader(file_path)
        elif source_type in ["txt", "text"]:
            return TextLoader(file_path)
        elif source_type == "docx":
            return UnstructuredWordDocumentLoader(file_path)
        elif source_type == "csv":
            return CSVLoader(file_path)
        elif source_type == "md":
            return UnstructuredMarkdownLoader(file_path)
        elif source_type == "url":
            return WebBaseLoader(file_path)
        return None
