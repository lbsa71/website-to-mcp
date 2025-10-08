"""
Vector Store Module
Handles storage and retrieval of embeddings using Qdrant.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using Qdrant."""
    
    def __init__(self, host: str = "localhost", port: int = 6333,
                 collection_name: str = "website_docs",
                 vector_size: int = 384):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = None
        
    def connect(self):
        """Connect to Qdrant server."""
        logger.info(f"Connecting to Qdrant at {self.host}:{self.port}")
        self.client = QdrantClient(host=self.host, port=self.port)
        
    def ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
        else:
            logger.info(f"Collection {self.collection_name} already exists")
            
    def store_embeddings(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Store chunks and their embeddings in the vector database."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
            
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'text': chunk['text'],
                    'source_url': chunk['source_url'],
                    'title': chunk['title'],
                    'type': chunk.get('type', 'text')
                }
            )
            points.append(point)
            
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            logger.info(f"Uploaded batch {i // batch_size + 1} ({len(batch)} points)")
            
        logger.info(f"Stored {len(points)} embeddings in {self.collection_name}")
        
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar chunks using query embedding."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [
            {
                'text': hit.payload['text'],
                'source_url': hit.payload['source_url'],
                'title': hit.payload['title'],
                'score': hit.score
            }
            for hit in results
        ]
        
    def count(self) -> int:
        """Get the number of vectors in the collection."""
        collection_info = self.client.get_collection(self.collection_name)
        return collection_info.points_count
        
    def delete_collection(self):
        """Delete the collection."""
        logger.info(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)


if __name__ == "__main__":
    # Test the vector store
    store = VectorStore()
    store.connect()
    store.ensure_collection()
    print(f"Collection ready. Current count: {store.count()}")
