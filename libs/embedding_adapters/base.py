from typing import List
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class EmbeddingAdapter:
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class GeminiEmbeddingAdapter(EmbeddingAdapter):

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=os.environ["GEMINI_API_KEY"]
        )

    def embed_text(self, text: str):
        return self.embeddings.embed_query(text)

    def embed_texts(self, texts: List[str]):
        return self.embeddings.embed_documents(texts)

    









# class OpenAIEmbeddingAdapter(EmbeddingAdapter):
#     def __init__(self):
#         from langchain_openai import OpenAIEmbeddings
#         # Assumes OPENAI_API_KEY is in environment
#         self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#     def embed_text(self, text: str) -> List[float]:
#         return self.embeddings.embed_query(text)

#     def embed_texts(self, texts: List[str]) -> List[List[float]]:
#         return self.embeddings.embed_documents(texts)

