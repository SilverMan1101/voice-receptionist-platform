import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from dotenv import load_dotenv

from embedding_adapters.base import GeminiEmbeddingAdapter

load_dotenv()
embedder = GeminiEmbeddingAdapter()
vector = embedder.embed_text("hello")
print(len(vector))
