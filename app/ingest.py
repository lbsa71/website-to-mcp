"""
Ingestion Script
Crawls website, chunks content, generates embeddings, and stores in vector DB.
"""

import yaml
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.web_crawler import WebsiteCrawler
from chunker.semantic_chunker import SemanticChunker
from embedder.embedding_service import EmbeddingService
from embedder.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion pipeline."""
    # Load configuration
    config_path = os.environ.get('CONFIG_PATH', '/app/config.yaml')
    logger.info(f"Loading configuration from {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Step 1: Crawl website
    logger.info("=" * 60)
    logger.info("STEP 1: Crawling website")
    logger.info("=" * 60)
    
    crawler = WebsiteCrawler(
        base_url=config['website']['url'],
        max_pages=config['website']['max_pages'],
        follow_external=config['website']['follow_external_links'],
        timeout=config['crawler']['timeout'],
        delay=config['crawler']['delay_between_requests']
    )
    
    content_data = crawler.crawl()
    logger.info(f"Crawled {len(content_data)} pages")
    
    if not content_data:
        logger.error("No content extracted. Exiting.")
        return
    
    # Step 2: Chunk content
    logger.info("=" * 60)
    logger.info("STEP 2: Chunking content")
    logger.info("=" * 60)
    
    chunker = SemanticChunker(
        min_chunk_size=config['chunking']['min_chunk_size'],
        max_chunk_size=config['chunking']['max_chunk_size'],
        overlap=config['chunking']['overlap']
    )
    
    chunks = chunker.create_chunks(content_data)
    logger.info(f"Created {len(chunks)} chunks")
    
    if not chunks:
        logger.error("No chunks created. Exiting.")
        return
    
    # Step 3: Generate embeddings
    logger.info("=" * 60)
    logger.info("STEP 3: Generating embeddings")
    logger.info("=" * 60)
    
    embedder = EmbeddingService(
        model_name=config['embedding']['model'],
        device=config['embedding']['device']
    )
    
    # Extract texts from chunks
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.embed_batch(texts)
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    # Step 4: Store in vector database
    logger.info("=" * 60)
    logger.info("STEP 4: Storing in vector database")
    logger.info("=" * 60)
    
    vector_store = VectorStore(
        host=config['vector_store']['host'],
        port=config['vector_store']['port'],
        collection_name=config['vector_store']['collection_name'],
        vector_size=config['vector_store']['vector_size']
    )
    
    vector_store.connect()
    vector_store.ensure_collection()
    vector_store.store_embeddings(chunks, embeddings)
    
    final_count = vector_store.count()
    logger.info(f"Ingestion complete! Total vectors in store: {final_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
