from .base import EmbeddingAdapter
from typing import List
import os
import dotenv

dotenv.load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIEmbeddingAdapter(EmbeddingAdapter):
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        if OpenAI is None:
            raise ImportError("Please install openai package to use OpenAIEmbeddingAdapter")
            
        self.model = model
        # Uses OPENAI_API_KEY from environment if api_key is None
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Mapping common models to their dimensions
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }

    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [data.embedding for data in response.data]

    @property
    def dimension(self) -> int:
        return self._dimensions.get(self.model, 1536)
