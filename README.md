# Website RAG MCP Service

A turnkey Dockerized service that crawls documentation websites, extracts semantic content, stores vector embeddings, and exposes a REST API for retrieval-augmented generation (RAG). Perfect for LLM-powered documentation search and MCP data sources.

## 🚀 Features

- **Website Ingestion**: Crawls documentation sites and extracts semantic content (headers, paragraphs, code snippets)
- **Smart Chunking**: Splits content into meaningful chunks while preserving context
- **Vector Embeddings**: Uses sentence-transformers for local, cost-free embeddings
- **Semantic Search**: Powered by Qdrant vector database for fast similarity search
- **REST API**: FastAPI-based endpoint for querying relevant content
- **MCP Compatible**: Ready-to-use as an MCP data source for LLMs
- **Fully Dockerized**: One command to spin up the entire service

## 📋 Prerequisites

- Docker and Docker Compose
- At least 4GB RAM available for Docker
- Internet connection (for initial setup and crawling)

## 🏃 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/lbsa71/website-to-mcp.git
cd website-to-mcp
```

### 2. Configure the Website to Crawl

Edit `config.yaml` to set the website URL you want to index:

```yaml
website:
  url: "https://docs.sine.space/scripting/"  # Change this to your target URL
  max_pages: 100
  follow_external_links: false
```

### 3. Start the Services

```bash
# Start Qdrant vector database and API server
docker compose up -d

# Wait for services to be ready (about 30 seconds)
docker compose ps
```

### 4. Run the Ingestion Pipeline

This crawls the website, generates embeddings, and populates the vector database:

```bash
docker compose run --rm ingest
```

This may take several minutes depending on the size of the website. You'll see progress logs showing:
- Pages being crawled
- Chunks being created
- Embeddings being generated
- Data being stored in Qdrant

### 5. Query the API

Once ingestion is complete, you can query the API:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I create a function?", "top_k": 5}'
```

Example response:

```json
{
  "results": [
    {
      "text": "To create a function in Lua, use the function keyword...",
      "source_url": "https://docs.sine.space/scripting/functions",
      "title": "Functions > Creating Functions",
      "score": 0.87
    }
  ],
  "query": "How do I create a function?",
  "count": 5
}
```

## 🔧 Configuration

### Main Configuration File (`config.yaml`)

```yaml
# Website settings
website:
  url: "https://your-docs-site.com"
  max_pages: 100              # Maximum pages to crawl
  follow_external_links: false # Stay within the same domain

# Chunking settings
chunking:
  min_chunk_size: 200         # Minimum words per chunk
  max_chunk_size: 500         # Maximum words per chunk
  overlap: 50                 # Word overlap between chunks

# Embedding settings
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"               # Use "cuda" if GPU available

# Vector store settings
vector_store:
  host: "qdrant"
  port: 6333
  collection_name: "website_docs"
  vector_size: 384            # Must match embedding model dimension

# API settings
api:
  host: "0.0.0.0"
  port: 8000
  top_k: 5                    # Default number of results

# Crawler settings
crawler:
  timeout: 30
  max_retries: 3
  delay_between_requests: 1   # Seconds between requests
```

### Changing the Target Website

1. Edit `config.yaml` and update the `website.url` field
2. Optionally adjust `max_pages` based on site size
3. Re-run ingestion:
   ```bash
   docker compose run --rm ingest
   ```

### Using a Different Embedding Model

You can use any model from [sentence-transformers](https://www.sbert.net/docs/pretrained_models.html):

```yaml
embedding:
  model: "sentence-transformers/all-mpnet-base-v2"  # Better quality, slower
  # or
  model: "sentence-transformers/paraphrase-MiniLM-L3-v2"  # Faster, smaller
```

**Note**: If you change the model, update `vector_size` to match the model's dimension.

## 📡 API Endpoints

### POST `/query`

Search for semantically relevant content.

**Request:**
```json
{
  "query": "your search query",
  "top_k": 5  // optional
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Content chunk...",
      "source_url": "https://...",
      "title": "Section title",
      "score": 0.85
    }
  ],
  "query": "your search query",
  "count": 5
}
```

### GET `/health`

Check service health.

**Response:**
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "documents_indexed": 1234
}
```

### GET `/stats`

Get service statistics.

**Response:**
```json
{
  "documents_indexed": 1234,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "collection_name": "website_docs"
}
```

### GET `/`

Service information and available endpoints.

## 🔌 MCP Integration

The service is MCP-compatible and can be used as a data source for LLMs. See `mcp-manifest.json` for the complete manifest.

### Using as an MCP Data Source

1. Point your MCP client to `http://localhost:8000`
2. Use the `/query` endpoint for retrieval
3. The manifest at `mcp-manifest.json` describes the service capabilities

Example integration with an LLM:

```python
import requests

def get_relevant_context(query: str) -> str:
    """Fetch relevant documentation for a query."""
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "top_k": 3}
    )
    results = response.json()["results"]
    
    # Combine results into context
    context = "\n\n".join([
        f"Source: {r['title']}\n{r['text']}"
        for r in results
    ])
    return context

# Use in LLM prompt
user_query = "How do I initialize a project?"
context = get_relevant_context(user_query)
prompt = f"Context:\n{context}\n\nQuestion: {user_query}\nAnswer:"
```

## 🏗️ Architecture

```
┌─────────────┐
│   Website   │
└──────┬──────┘
       │ Crawl
       ▼
┌─────────────┐
│   Crawler   │ Extract semantic content
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Chunker   │ Split into meaningful chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embedder   │ Generate vector embeddings
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Qdrant    │ Store vectors
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ Expose REST endpoint
└─────────────┘
```

## 🛠️ Development

### Running Locally (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Start Qdrant (using Docker)
docker run -p 6333:6333 qdrant/qdrant

# Update config to use localhost
# In config.yaml: vector_store.host: "localhost"

# Run ingestion
python app/ingest.py

# Start API server
uvicorn app.api.main:app --reload
```

### Project Structure

```
website-to-mcp/
├── app/
│   ├── api/
│   │   └── main.py           # FastAPI application
│   ├── crawler/
│   │   └── web_crawler.py    # Website crawling logic
│   ├── chunker/
│   │   └── semantic_chunker.py  # Text chunking
│   ├── embedder/
│   │   ├── embedding_service.py # Embedding generation
│   │   └── vector_store.py   # Qdrant integration
│   └── ingest.py             # Ingestion pipeline
├── config.yaml               # Configuration file
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Container definition
├── mcp-manifest.json         # MCP service manifest
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔄 Re-indexing / Updating Content

To refresh the indexed content when the source website updates:

```bash
# Stop the services
docker compose down

# Clear the vector database (optional, to start fresh)
docker volume rm website-to-mcp_qdrant_storage

# Start services and re-ingest
docker compose up -d
docker compose run --rm ingest
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check service logs
docker compose logs qdrant
docker compose logs api

# Ensure ports 6333 and 8000 are available
netstat -tuln | grep -E '6333|8000'
```

### Ingestion fails

- Check that the website URL is accessible
- Increase `crawler.timeout` in config.yaml
- Reduce `website.max_pages` for large sites
- Check logs: `docker compose logs ingest`

### Query returns no results

- Ensure ingestion completed successfully
- Check document count: `curl http://localhost:8000/stats`
- Try different queries or increase `top_k`

### Out of memory errors

- Reduce `website.max_pages`
- Process in batches by running ingestion multiple times with different URL filters
- Increase Docker memory limit

## 📊 Performance Tips

- **GPU Acceleration**: Set `embedding.device: "cuda"` if you have a GPU
- **Faster Models**: Use smaller embedding models for speed
- **Batch Size**: Adjust batch sizes in embedding_service.py for your hardware
- **Chunking**: Smaller chunks = more granular search, larger chunks = more context

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📚 Tech Stack

| Component | Technology |
|-----------|-----------|
| Web Crawler | Python + BeautifulSoup |
| Chunking | Custom Python logic |
| Embeddings | sentence-transformers (local) |
| Vector Store | Qdrant |
| API Server | FastAPI |
| Orchestration | Docker Compose |

## 🔗 Related Projects

- [Qdrant](https://qdrant.tech/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Embedding models
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
