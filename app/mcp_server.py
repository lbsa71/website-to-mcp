"""
MCP Server for Website RAG Service
Implements proper Model Context Protocol with JSON-RPC 2.0 over stdio.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Optional

import yaml
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent
from pydantic import AnyUrl

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedder.embedding_service import EmbeddingService
from embedder.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
embedder: Optional[EmbeddingService] = None
vector_store: Optional[VectorStore] = None
config: Optional[dict] = None
last_crawl_time: Optional[str] = None

# Create MCP server
mcp = FastMCP(
    "website-rag-mcp",
    instructions="Semantic search over documentation websites using vector embeddings"
)


def initialize_services():
    """Initialize embedding service and vector store."""
    global embedder, vector_store, config, last_crawl_time
    
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
    
    # Set last crawl time (could be enhanced to read from metadata)
    last_crawl_time = datetime.now().isoformat()
    
    logger.info("MCP server initialized successfully!")


@mcp.tool()
async def semantic_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Search documentation using semantic similarity.
    
    Args:
        query: The search query text
        top_k: Number of results to return (default: 5, max: 20)
    
    Returns:
        Dictionary containing search results with text, URLs, titles, and scores
    """
    try:
        # Validate top_k
        top_k = min(max(1, top_k), 20)
        
        logger.info(f"Processing semantic search: {query[:50]}...")
        
        # Generate embedding for query
        query_embedding = embedder.embed_text(query)
        
        # Search vector store
        results = vector_store.search(query_embedding, top_k=top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in semantic_search: {str(e)}")
        raise


@mcp.resource("website://docs/metadata")
async def get_docs_metadata() -> str:
    """
    Get metadata about the indexed documentation.
    
    Returns information about the documentation collection including
    total chunks, website URL, and last update time.
    """
    try:
        metadata = {
            "total_chunks": vector_store.count(),
            "website_url": config['website']['url'],
            "last_updated": last_crawl_time,
            "embedding_model": config['embedding']['model'],
            "embedding_dimension": embedder.get_dimension(),
            "collection_name": config['vector_store']['collection_name']
        }
        return json.dumps(metadata, indent=2)
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        raise


@mcp.resource("website://docs/stats")
async def get_docs_stats() -> str:
    """
    Get statistics about the documentation collection.
    
    Returns the number of indexed document chunks and model information.
    """
    try:
        stats = {
            "documents_indexed": vector_store.count(),
            "embedding_model": config['embedding']['model'],
            "embedding_dimension": embedder.get_dimension(),
            "vector_store": {
                "host": config['vector_store']['host'],
                "collection": config['vector_store']['collection_name']
            }
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise


async def main():
    """Main entry point for the MCP server."""
    try:
        # Initialize services
        initialize_services()
        
        # Run MCP server with stdio transport
        logger.info("Starting MCP server with stdio transport...")
        await mcp.run_stdio_async()
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
