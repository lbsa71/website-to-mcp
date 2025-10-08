"""
Semantic Chunking Module
Splits extracted content into meaningful chunks for embedding.
"""

from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticChunker:
    """Chunks content into meaningful pieces for embedding."""
    
    def __init__(self, min_chunk_size: int = 200, 
                 max_chunk_size: int = 500,
                 overlap: int = 50):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
    def chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks of approximately chunk_size words."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - self.overlap):
            chunk_words = words[i:i + chunk_size]
            if len(chunk_words) >= self.min_chunk_size or i == 0:
                chunks.append(' '.join(chunk_words))
                
        return chunks
        
    def create_chunks(self, content_data: List[Dict]) -> List[Dict]:
        """
        Create semantic chunks from crawled content.
        Each chunk preserves context (headers, url, title).
        """
        all_chunks = []
        
        for page in content_data:
            url = page['url']
            title = page['title']
            
            for section in page['sections']:
                # Build context from headers
                headers = section.get('headers', [])
                header_context = ' > '.join(headers) if headers else title
                
                # Combine paragraphs
                paragraphs = section.get('paragraphs', [])
                if paragraphs:
                    combined_text = ' '.join(paragraphs)
                    
                    # Chunk if too long
                    if len(combined_text.split()) > self.max_chunk_size:
                        text_chunks = self.chunk_text(combined_text, self.max_chunk_size)
                    else:
                        text_chunks = [combined_text]
                    
                    for chunk_text in text_chunks:
                        all_chunks.append({
                            'text': chunk_text,
                            'source_url': url,
                            'title': header_context,
                            'type': 'text'
                        })
                
                # Add code snippets as separate chunks
                code_snippets = section.get('code_snippets', [])
                for code in code_snippets:
                    # Chunk very long code
                    if len(code.split('\n')) > 50:
                        # Split by lines for code
                        lines = code.split('\n')
                        for i in range(0, len(lines), 40):
                            code_chunk = '\n'.join(lines[i:i+50])
                            all_chunks.append({
                                'text': code_chunk,
                                'source_url': url,
                                'title': f"{header_context} (code)",
                                'type': 'code'
                            })
                    else:
                        all_chunks.append({
                            'text': code,
                            'source_url': url,
                            'title': f"{header_context} (code)",
                            'type': 'code'
                        })
        
        logger.info(f"Created {len(all_chunks)} chunks from content")
        return all_chunks


if __name__ == "__main__":
    # Test the chunker
    test_data = [{
        'url': 'https://example.com/page1',
        'title': 'Test Page',
        'sections': [{
            'headers': ['Introduction', 'Getting Started'],
            'paragraphs': ['This is a test paragraph. ' * 100],
            'code_snippets': ['print("hello world")']
        }]
    }]
    
    chunker = SemanticChunker()
    chunks = chunker.create_chunks(test_data)
    print(f"Created {len(chunks)} chunks")
    if chunks:
        print(f"First chunk: {chunks[0]['text'][:100]}...")
