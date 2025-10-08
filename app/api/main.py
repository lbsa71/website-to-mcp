"""
FastAPI Server for Website RAG MCP Service
Exposes REST endpoints for querying the vector store.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import yaml
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedder.embedding_service import EmbeddingService
from embedder.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website RAG MCP Service",
    description="Semantic search over documentation websites",
    version="1.0.0"
)

# Global instances
embedder = None
vector_store = None
config = None


class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    top_k: Optional[int] = None


class QueryResult(BaseModel):
    """Single query result."""
    text: str
    source_url: str
    title: str
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Query response model."""
    results: List[QueryResult]
    query: str
    count: int


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global embedder, vector_store, config
    
    # Load configuration
    config_path = os.environ.get('CONFIG_PATH', '/app/config.yaml')
    logger.info(f"Loading configuration from {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize embedding service
    logger.info("Initializing embedding service...")
    embedder = EmbeddingService(
        model_name=config['embedding']['model'],
        device=config['embedding']['device']
    )
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    vector_store = VectorStore(
        host=config['vector_store']['host'],
        port=config['vector_store']['port'],
        collection_name=config['vector_store']['collection_name'],
        vector_size=config['vector_store']['vector_size']
    )
    vector_store.connect()
    vector_store.ensure_collection()
    
    logger.info("API server ready!")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Website RAG MCP Service",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST - Search for relevant content",
            "/health": "GET - Health check",
            "/stats": "GET - Service statistics"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        count = vector_store.count()
        return {
            "status": "healthy",
            "vector_store": "connected",
            "documents_indexed": count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/stats")
async def stats():
    """Get service statistics."""
    try:
        count = vector_store.count()
        return {
            "documents_indexed": count,
            "embedding_model": config['embedding']['model'],
            "embedding_dimension": embedder.get_dimension(),
            "collection_name": config['vector_store']['collection_name']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the vector store for semantically similar content.
    
    Returns top-k most relevant text chunks based on semantic similarity.
    """
    try:
        # Get top_k from request or config
        top_k = request.top_k if request.top_k else config['api']['top_k']
        
        # Generate embedding for query
        logger.info(f"Processing query: {request.query[:50]}...")
        query_embedding = embedder.embed_text(request.query)
        
        # Search vector store
        results = vector_store.search(query_embedding, top_k=top_k)
        
        # Format response
        return QueryResponse(
            results=[QueryResult(**r) for r in results],
            query=request.query,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
