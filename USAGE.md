# Usage Guide - Website RAG MCP Service

This guide provides detailed instructions for using the Website RAG MCP Service.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Service](#running-the-service)
4. [Querying the API](#querying-the-api)
5. [Integration Examples](#integration-examples)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- Internet connection

### Quick Install

```bash
git clone https://github.com/lbsa71/website-to-mcp.git
cd website-to-mcp
```

## Configuration

### Basic Configuration

Edit `config.yaml` to customize the service:

```yaml
website:
  url: "https://your-docs-site.com"
  max_pages: 100
```

### Advanced Configuration

#### Chunking Strategy

Control how content is split:

```yaml
chunking:
  min_chunk_size: 200    # Minimum words per chunk
  max_chunk_size: 500    # Maximum words per chunk
  overlap: 50            # Overlapping words between chunks
```

**Tips:**
- Smaller chunks (200-300): Better for specific queries
- Larger chunks (400-500): Better for context-rich queries
- Increase overlap for better context continuity

#### Embedding Model

Choose the embedding model:

```yaml
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"  # or "cuda" for GPU
```

**Model Comparison:**

| Model | Dimension | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose (recommended) |
| all-mpnet-base-v2 | 768 | Slow | Excellent | High accuracy needed |
| paraphrase-MiniLM-L3-v2 | 384 | Very Fast | Moderate | Speed critical |

**Important:** If you change the model, update `vector_store.vector_size` to match the model's dimension.

#### Crawler Settings

Control crawling behavior:

```yaml
crawler:
  timeout: 30                    # Request timeout in seconds
  max_retries: 3                 # Retry failed requests
  delay_between_requests: 1      # Delay in seconds (be respectful!)
```

**Best Practices:**
- Increase delay for busy servers
- Reduce max_pages for testing
- Set timeout higher for slow sites

## Running the Service

### Method 1: Quick Start (Recommended)

```bash
./quickstart.sh
```

This script:
1. Starts Qdrant and API services
2. Runs the ingestion pipeline
3. Shows you example queries

### Method 2: Manual Steps

#### Step 1: Start Services

```bash
docker compose up -d
```

This starts:
- Qdrant vector database (port 6333)
- FastAPI server (port 8000)

#### Step 2: Run Ingestion

```bash
docker compose run --rm ingest
```

**What happens during ingestion:**
1. Crawls the configured website
2. Extracts semantic content
3. Creates text chunks
4. Generates embeddings
5. Stores in Qdrant

**Duration:** Depends on website size
- 10 pages: ~2-5 minutes
- 50 pages: ~10-20 minutes
- 100 pages: ~20-40 minutes

#### Step 3: Verify Service

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "documents_indexed": 1234
}
```

### Method 3: Development Mode

For local development without Docker:

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Qdrant separately
docker run -p 6333:6333 qdrant/qdrant

# Update config
# Set vector_store.host to "localhost"

# Run ingestion
python app/ingest.py

# Start API
uvicorn app.api.main:app --reload
```

## Querying the API

### Using curl

#### Basic Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I get started?"}'
```

#### Custom Number of Results

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "installation steps", "top_k": 10}'
```

#### Pretty Print Response

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "API documentation"}' | python -m json.tool
```

### Using Python

```python
import requests

def search_docs(query: str, top_k: int = 5):
    """Search documentation."""
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "top_k": top_k}
    )
    return response.json()

# Search
results = search_docs("How do I configure authentication?")

# Process results
for i, result in enumerate(results['results'], 1):
    print(f"{i}. {result['title']}")
    print(f"   URL: {result['source_url']}")
    print(f"   Score: {result['score']:.3f}")
    print(f"   Preview: {result['text'][:150]}...")
    print()
```

### Using JavaScript

```javascript
async function searchDocs(query, topK = 5) {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK })
    });
    
    const data = await response.json();
    return data.results;
}

// Example usage
const results = await searchDocs('How to deploy?');
results.forEach((result, i) => {
    console.log(`${i+1}. ${result.title} (${result.score.toFixed(3)})`);
    console.log(`   ${result.text.substring(0, 100)}...`);
});
```

## Integration Examples

### LLM Integration (RAG Pattern)

```python
import requests
import openai

def get_context(query: str) -> str:
    """Get relevant documentation context."""
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "top_k": 3}
    )
    results = response.json()['results']
    
    # Combine results into context
    context_parts = []
    for r in results:
        context_parts.append(f"From {r['title']}:\n{r['text']}")
    
    return "\n\n".join(context_parts)

def answer_with_docs(question: str) -> str:
    """Answer question using documentation."""
    # Get relevant context
    context = get_context(question)
    
    # Build prompt
    prompt = f"""Using the following documentation, answer the question.

Documentation:
{context}

Question: {question}

Answer:"""
    
    # Query LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Use it
answer = answer_with_docs("How do I configure authentication?")
print(answer)
```

### Chatbot Integration

```python
class DocsChatbot:
    """Chatbot with documentation access."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.conversation_history = []
    
    def search_docs(self, query: str, top_k: int = 3):
        """Search documentation."""
        response = requests.post(
            f"{self.api_url}/query",
            json={"query": query, "top_k": top_k}
        )
        return response.json()['results']
    
    def chat(self, user_message: str) -> str:
        """Process user message with doc context."""
        # Search for relevant docs
        docs = self.search_docs(user_message)
        
        # Build context
        if docs:
            context = "Relevant documentation:\n"
            for doc in docs[:2]:  # Use top 2 results
                context += f"- {doc['title']}: {doc['text'][:200]}...\n"
        else:
            context = "No relevant documentation found.\n"
        
        # Add to conversation
        self.conversation_history.append({
            'user': user_message,
            'context': context
        })
        
        # Generate response (simplified)
        response = f"Based on the documentation:\n{context}"
        return response

# Usage
chatbot = DocsChatbot()
response = chatbot.chat("How do I get started?")
print(response)
```

### API Gateway Integration

Add to your API gateway config (e.g., Kong, Traefik):

```yaml
# Kong example
services:
  - name: docs-search
    url: http://localhost:8000
    routes:
      - name: docs-query
        paths:
          - /api/docs/search
        methods:
          - POST
```

## Troubleshooting

### Service Won't Start

**Check Docker:**
```bash
docker --version
docker compose --version
```

**Check ports:**
```bash
# Make sure ports 6333 and 8000 are free
netstat -tuln | grep -E '6333|8000'

# Or on Mac:
lsof -i :6333
lsof -i :8000
```

**View logs:**
```bash
docker compose logs -f
```

### Ingestion Fails

**Check website accessibility:**
```bash
curl -I https://your-target-website.com
```

**Reduce max_pages for testing:**
```yaml
website:
  max_pages: 5  # Start small
```

**Check ingestion logs:**
```bash
docker compose logs ingest
```

### No Results from Queries

**Check document count:**
```bash
curl http://localhost:8000/stats
```

**Verify ingestion completed:**
```bash
docker compose logs ingest | grep "Ingestion complete"
```

**Try simpler queries:**
```bash
# Instead of very specific query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "specific technical term"}'

# Try broader query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "getting started"}'
```

**Increase top_k:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your query", "top_k": 20}'
```

### Out of Memory

**Reduce ingestion batch size:**

Edit `app/embedder/embedding_service.py`:
```python
# Change batch_size from 32 to 16
embeddings = self.model.encode(texts, batch_size=16)
```

**Increase Docker memory:**
```bash
# Docker Desktop: Settings > Resources > Memory
# Linux: Edit /etc/docker/daemon.json
```

**Process in batches:**
```yaml
# First run
website:
  max_pages: 50

# Second run (update URL or use different config)
website:
  max_pages: 50
```

### Slow Performance

**Use GPU for embeddings:**
```yaml
embedding:
  device: "cuda"  # If GPU available
```

**Use faster model:**
```yaml
embedding:
  model: "sentence-transformers/paraphrase-MiniLM-L3-v2"
  # Don't forget to update vector_size!
```

**Reduce chunk size:**
```yaml
chunking:
  max_chunk_size: 300  # Smaller = faster
```

## Maintenance

### Update Indexed Content

When source website changes:

```bash
# Stop services
docker compose down

# Optional: Clear old data
docker volume rm website-to-mcp_qdrant_storage

# Restart and re-index
docker compose up -d
docker compose run --rm ingest
```

### View Service Status

```bash
docker compose ps
```

### Stop Services

```bash
docker compose down
```

### Stop and Remove All Data

```bash
docker compose down -v
```

## Performance Tips

1. **Optimize chunk size** for your use case
2. **Use GPU** if available (10-100x faster)
3. **Increase crawler delay** if getting rate limited
4. **Index incrementally** for large sites
5. **Use caching** in your application layer

## Security Recommendations

For production deployment:

1. Add authentication (API keys, JWT)
2. Use HTTPS (reverse proxy with SSL)
3. Implement rate limiting
4. Set up CORS policies
5. Run behind firewall
6. Monitor access logs
7. Keep dependencies updated

See `CONTRIBUTING.md` for development guidelines.
