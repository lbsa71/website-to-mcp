"""
Embedding Service Module
Generates embeddings for text chunks using sentence-transformers.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates embeddings for text chunks."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 device: str = "cpu"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
        
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
        
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_tensor=False
        )
        return [emb.tolist() for emb in embeddings]
        
    def get_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.dimension


if __name__ == "__main__":
    # Test the embedding service
    embedder = EmbeddingService()
    test_text = "This is a test sentence for embedding."
    embedding = embedder.embed_text(test_text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
