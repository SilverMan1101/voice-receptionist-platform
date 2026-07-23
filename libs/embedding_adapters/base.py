from typing import List
import os

class EmbeddingAdapter:
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class OpenAIEmbeddingAdapter(EmbeddingAdapter):
    def __init__(self):
        from langchain_openai import OpenAIEmbeddings
        # Assumes OPENAI_API_KEY is in environment
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def embed_text(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)
