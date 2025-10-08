# Architecture Documentation

## System Overview

The Website RAG MCP Service is a complete pipeline for converting documentation websites into a searchable knowledge base using vector embeddings and semantic search.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Environment                        │
│                                                                   │
│  ┌────────────────┐          ┌─────────────────────────────┐   │
│  │                │          │      Qdrant Vector DB        │   │
│  │  Ingestion     │          │                              │   │
│  │  Pipeline      │──────────▶  - Collection Management     │   │
│  │  (One-time)    │  Store   │  - Vector Storage            │   │
│  │                │  Vectors │  - Similarity Search         │   │
│  └────────────────┘          │  - Persistent Storage        │   │
│         │                     └─────────────┬───────────────┘   │
│         │                                   │                   │
│         │                     ┌─────────────▼───────────────┐   │
│         │                     │       FastAPI Server        │   │
│         │                     │                              │   │
│         │                     │  - Query Endpoint (/query)  │   │
│         │                     │  - Health Check (/health)   │◀──┼─── HTTP Requests
│         │                     │  - Stats (/stats)           │   │
│         │                     │  - Embedding Service        │   │
│         │                     └─────────────────────────────┘   │
│         │                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼
    ┌──────────────────────┐
    │  External Website    │
    │  (Documentation)     │
    └──────────────────────┘
```

## Data Flow

### Ingestion Phase (One-time)

```
1. Web Crawling
   └─▶ Input: Website URL
   └─▶ Output: Raw HTML pages
   └─▶ Component: WebsiteCrawler

2. Content Extraction
   └─▶ Input: Raw HTML
   └─▶ Output: Structured content (headers, paragraphs, code)
   └─▶ Component: WebsiteCrawler.extract_content()

3. Semantic Chunking
   └─▶ Input: Structured content
   └─▶ Output: Text chunks with metadata
   └─▶ Component: SemanticChunker

4. Embedding Generation
   └─▶ Input: Text chunks
   └─▶ Output: Vector embeddings (384-dimensional)
   └─▶ Component: EmbeddingService (sentence-transformers)

5. Vector Storage
   └─▶ Input: Embeddings + metadata
   └─▶ Output: Indexed vectors in Qdrant
   └─▶ Component: VectorStore
```

### Query Phase (Real-time)

```
1. User Query
   └─▶ HTTP POST to /query
   └─▶ Payload: {"query": "...", "top_k": 5}

2. Query Embedding
   └─▶ Input: Query text
   └─▶ Output: Query vector (384-dimensional)
   └─▶ Component: EmbeddingService

3. Vector Search
   └─▶ Input: Query vector
   └─▶ Output: Top-K similar vectors
   └─▶ Component: VectorStore (Qdrant)
   └─▶ Algorithm: Cosine similarity

4. Result Formatting
   └─▶ Input: Matched vectors + metadata
   └─▶ Output: JSON response with text, URLs, scores
   └─▶ Component: FastAPI endpoint

5. Response
   └─▶ JSON array of relevant chunks
   └─▶ Each with: text, source_url, title, score
```

## Module Details

### 1. WebsiteCrawler (`app/crawler/web_crawler.py`)

**Purpose**: Crawl documentation websites and extract semantic content

**Key Features**:
- Follows internal links (configurable)
- Respects rate limits with delays
- Filters out non-content (nav, footer, ads)
- Extracts headers, paragraphs, code snippets
- Preserves document structure

**Configuration**:
```yaml
website:
  url: "https://..."
  max_pages: 100
  follow_external_links: false

crawler:
  timeout: 30
  delay_between_requests: 1
```

**Output Format**:
```python
{
  'url': 'https://...',
  'title': 'Page Title',
  'sections': [
    {
      'headers': ['H1', 'H2'],
      'paragraphs': ['text...'],
      'code_snippets': ['code...']
    }
  ]
}
```

### 2. SemanticChunker (`app/chunker/semantic_chunker.py`)

**Purpose**: Split content into optimal chunks for embedding

**Key Features**:
- Configurable chunk sizes (200-500 words)
- Overlap between chunks for context
- Preserves headers as context
- Separate handling for code vs text
- Metadata preservation (URL, title)

**Configuration**:
```yaml
chunking:
  min_chunk_size: 200
  max_chunk_size: 500
  overlap: 50
```

**Output Format**:
```python
{
  'text': 'chunk content...',
  'source_url': 'https://...',
  'title': 'Section > Subsection',
  'type': 'text' | 'code'
}
```

### 3. EmbeddingService (`app/embedder/embedding_service.py`)

**Purpose**: Generate vector embeddings for text

**Key Features**:
- Uses sentence-transformers (local, no API costs)
- Batch processing for efficiency
- GPU support (optional)
- Consistent 384-dimensional vectors

**Configuration**:
```yaml
embedding:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"  # or "cuda"
```

**Model Options**:
- `all-MiniLM-L6-v2`: Fast, good quality (384 dim)
- `all-mpnet-base-v2`: Better quality, slower (768 dim)
- `paraphrase-MiniLM-L3-v2`: Fastest (384 dim)

### 4. VectorStore (`app/embedder/vector_store.py`)

**Purpose**: Manage vector storage and retrieval in Qdrant

**Key Features**:
- Automatic collection creation
- Batch upload (100 vectors at a time)
- Cosine similarity search
- Metadata storage (text, URL, title)
- Persistent storage

**Configuration**:
```yaml
vector_store:
  host: "qdrant"
  port: 6333
  collection_name: "website_docs"
  vector_size: 384
```

**Search Algorithm**:
- Distance metric: Cosine similarity
- Returns top-K most similar vectors
- Includes similarity score (0-1)

### 5. FastAPI Server (`app/api/main.py`)

**Purpose**: Expose REST API for querying

**Endpoints**:

#### POST `/query`
Search for relevant content

Request:
```json
{
  "query": "your question",
  "top_k": 5  // optional
}
```

Response:
```json
{
  "results": [
    {
      "text": "...",
      "source_url": "...",
      "title": "...",
      "score": 0.85
    }
  ],
  "query": "your question",
  "count": 5
}
```

#### GET `/health`
Service health check

Response:
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "documents_indexed": 1234
}
```

#### GET `/stats`
Service statistics

Response:
```json
{
  "documents_indexed": 1234,
  "embedding_model": "...",
  "embedding_dimension": 384,
  "collection_name": "..."
}
```

## Docker Architecture

### Services

1. **qdrant**: Vector database
   - Image: `qdrant/qdrant:latest`
   - Ports: 6333 (HTTP), 6334 (gRPC)
   - Volume: Persistent storage
   - Always running

2. **ingest**: Ingestion pipeline
   - Build: Local Dockerfile
   - Profile: `ingest` (manual trigger)
   - Runs once then exits
   - Depends on: qdrant

3. **api**: REST API server
   - Build: Local Dockerfile
   - Port: 8000
   - Depends on: qdrant
   - Always running

### Volumes

- `qdrant_storage`: Persists vector database
  - Location: `/qdrant/storage` in container
  - Survives container restarts

### Networks

- `rag-network`: Bridge network
  - Allows inter-service communication
  - Services reference each other by name

## Configuration Management

All configuration is centralized in `config.yaml`:

```yaml
website:         # What to crawl
chunking:        # How to split content
embedding:       # Which model to use
vector_store:    # Where to store vectors
api:             # API settings
crawler:         # Crawling behavior
```

Loaded by all components:
- Environment variable: `CONFIG_PATH`
- Default: `/app/config.yaml`
- Mounted as volume in Docker

## Scaling Considerations

### Vertical Scaling
- **CPU**: More cores → faster embedding generation
- **RAM**: More memory → larger batch sizes
- **GPU**: CUDA support → 10-100x faster embeddings

### Horizontal Scaling
- Multiple API instances behind load balancer
- Shared Qdrant instance
- Read replicas for Qdrant (enterprise)

### Performance Tuning
- Adjust `chunking.max_chunk_size` for granularity
- Increase embedding batch size for throughput
- Use faster embedding models for lower latency
- Increase `api.top_k` for broader search

## Security Considerations

- No authentication implemented (add reverse proxy with auth)
- Rate limiting not implemented (add in production)
- CORS not configured (configure for cross-origin)
- Runs on localhost by default

## Monitoring and Debugging

### Logs
```bash
docker compose logs -f api      # API logs
docker compose logs -f qdrant   # Qdrant logs
docker compose logs ingest      # Ingestion logs
```

### Metrics
- `/health`: Service status
- `/stats`: Document count
- Qdrant dashboard: http://localhost:6333/dashboard

### Common Issues

1. **No results returned**
   - Check ingestion completed: `/stats`
   - Verify embeddings stored in Qdrant
   - Try broader queries

2. **Out of memory**
   - Reduce `website.max_pages`
   - Decrease batch size in embedding
   - Use smaller embedding model

3. **Slow ingestion**
   - Increase `crawler.delay_between_requests`
   - Use GPU for embeddings
   - Reduce `chunking.max_chunk_size`

## MCP Integration

The service implements the Model Context Protocol (MCP) for LLM integration.

### Manifest
`mcp-manifest.json` describes:
- Service capabilities
- Endpoint specifications
- Data formats
- Configuration

### Usage in LLM Applications
```python
# 1. Query for relevant context
context = query_rag_service(user_question)

# 2. Build prompt
prompt = f"Context: {context}\n\nQuestion: {user_question}"

# 3. Send to LLM
response = llm.generate(prompt)
```

## Deployment Patterns

### Development
```bash
docker compose up -d
docker compose run --rm ingest
```

### Production
- Use reverse proxy (nginx, Traefik)
- Add authentication (JWT, API keys)
- Enable HTTPS
- Set up monitoring (Prometheus, Grafana)
- Configure backups for Qdrant volume
- Use environment-specific configs

### CI/CD
```bash
# Build
docker compose build

# Test
docker compose up -d
docker compose run --rm ingest
./test.sh

# Deploy
docker compose push
# Deploy to production environment
```
