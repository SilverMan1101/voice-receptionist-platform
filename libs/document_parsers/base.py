from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class ParsedDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]

class DocumentParserAdapter(ABC):
    @abstractmethod
    def parse(self, file_path: str, source_type: str) -> List[ParsedDocument]:
        """
        Parses a document into text content and metadata.
        Returns a list of ParsedDocument objects (e.g., one per page/chunk natively found in the doc).
        """
        pass
