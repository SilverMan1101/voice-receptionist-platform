from abc import ABC, abstractmethod
from typing import List

class EmbeddingAdapter(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single text string into a vector.
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a batch of text strings into a list of vectors.
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Returns the dimension of the embedding vectors produced by this adapter.
        """
        pass
