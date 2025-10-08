# System Diagram - Website RAG MCP Service

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DOCKER ENVIRONMENT                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    INGESTION PIPELINE                         │  │
│  │                    (Run Once / On-Demand)                     │  │
│  │                                                                │  │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐     │  │
│  │  │  Web    │──▶│ Chunk   │──▶│ Embed   │──▶│ Store   │     │  │
│  │  │Crawler  │   │  Text   │   │  Text   │   │ Vectors │     │  │
│  │  └─────────┘   └─────────┘   └─────────┘   └────┬────┘     │  │
│  │                                                   │           │  │
│  └───────────────────────────────────────────────────┼──────────┘  │
│                                                       │              │
│                                            ┌──────────▼─────────┐   │
│                                            │                    │   │
│                                            │   Qdrant Vector    │   │
│                                            │     Database       │   │
│                                            │                    │   │
│                                            │  • 384-dim vectors │   │
│                                            │  • Cosine search   │   │
│                                            │  • Persistent      │   │
│                                            │                    │   │
│                                            └──────────┬─────────┘   │
│                                                       │              │
│  ┌────────────────────────────────────────────────────┼─────────┐  │
│  │                  QUERY SERVICE                     │         │  │
│  │                  (Always Running)                  │         │  │
│  │                                                     │         │  │
│  │  ┌────────────────────────────────────────────┐   │         │  │
│  │  │          FastAPI Server                    │   │         │  │
│  │  │                                             │   │         │  │
│  │  │  POST /query                                │   │         │  │
│  │  │  ┌──────────────────────────────────┐     │   │         │  │
│  │  │  │ 1. Receive query text            │     │   │         │  │
│  │  │  │ 2. Generate embedding            │     │   │         │  │
│  │  │  │ 3. Search vectors ───────────────┼─────┼───┘         │  │
│  │  │  │ 4. Return top-k results          │     │             │  │
│  │  │  └──────────────────────────────────┘     │             │  │
│  │  │                                             │             │  │
│  │  │  GET /health  - Health check               │             │  │
│  │  │  GET /stats   - Statistics                 │             │  │
│  │  │  GET /        - Service info               │             │  │
│  │  │                                             │             │  │
│  │  └────────────────────────────────────────────┘             │  │
│  │                         ▲                                    │  │
│  └─────────────────────────┼────────────────────────────────────┘  │
│                             │                                       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   HTTP Requests    │
                    │   (Port 8000)      │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
         │  curl   │    │ Python  │    │   LLM   │
         │ Client  │    │  App    │    │   RAG   │
         └─────────┘    └─────────┘    └─────────┘
```

## Data Flow - Ingestion

```
External Website
      │
      │ HTTP GET
      ▼
┌──────────────┐
│ WebsiteCrawler│
│              │
│ • Follow links
│ • Extract HTML
│ • Parse content
└──────┬───────┘
       │
       │ Raw HTML + Metadata
       ▼
┌──────────────┐
│Content Extract│
│              │
│ • Headers
│ • Paragraphs
│ • Code blocks
└──────┬───────┘
       │
       │ Structured Content
       ▼
┌──────────────┐
│   Chunker    │
│              │
│ • Split text
│ • Add context
│ • Optimize size
└──────┬───────┘
       │
       │ Text Chunks (200-500 words)
       ▼
┌──────────────┐
│   Embedder   │
│              │
│ • sentence-transformers
│ • Batch process
│ • 384-dim vectors
└──────┬───────┘
       │
       │ Vector Embeddings
       ▼
┌──────────────┐
│ Vector Store │
│   (Qdrant)   │
│              │
│ • Index
│ • Persist
└──────────────┘
```

## Data Flow - Query

```
User Query
      │
      │ POST /query
      ▼
┌──────────────┐
│  FastAPI     │
│  Endpoint    │
└──────┬───────┘
       │
       │ Query Text
       ▼
┌──────────────┐
│  Embedder    │
│              │
│ • Same model
│ • 384-dim
└──────┬───────┘
       │
       │ Query Vector
       ▼
┌──────────────┐
│ Vector Store │
│   (Qdrant)   │
│              │
│ • Cosine similarity
│ • top-k search
└──────┬───────┘
       │
       │ Similar Vectors + Metadata
       ▼
┌──────────────┐
│   Format     │
│   Response   │
│              │
│ • text
│ • source_url
│ • title
│ • score
└──────┬───────┘
       │
       │ JSON Response
       ▼
    Client
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                         config.yaml                          │
│                                                               │
│  Central configuration loaded by all components              │
│  • Website URL & crawl settings                              │
│  • Chunk sizes & overlap                                     │
│  • Embedding model & device                                  │
│  • Vector store connection                                   │
│  • API settings                                              │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │  Crawler  │   │  Ingestion│   │    API    │
        │  Module   │   │  Pipeline │   │  Server   │
        └───────────┘   └───────────┘   └───────────┘
```

## Docker Services

```
┌─────────────────────────────────────────────────────────────┐
│                     docker-compose.yml                       │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │  qdrant   │   │  ingest   │   │    api    │
        │           │   │           │   │           │
        │ Image:    │   │ Build:    │   │ Build:    │
        │ qdrant/   │   │ Dockerfile│   │ Dockerfile│
        │ qdrant    │   │           │   │           │
        │           │   │ Profile:  │   │ Port:     │
        │ Port:     │   │ ingest    │   │ 8000      │
        │ 6333      │   │           │   │           │
        │           │   │ Command:  │   │ Command:  │
        │ Volume:   │   │ python    │   │ uvicorn   │
        │ qdrant_   │   │ app/      │   │ app.api.  │
        │ storage   │   │ ingest.py │   │ main:app  │
        └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ┌─────────▼────────┐
                    │  rag-network     │
                    │  (bridge)        │
                    └──────────────────┘
```

## Request/Response Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ POST http://localhost:8000/query
       │ {
       │   "query": "How do I authenticate?",
       │   "top_k": 5
       │ }
       ▼
┌──────────────────────────────────────────┐
│           FastAPI Server                 │
│                                          │
│  1. Parse request                        │
│  2. Validate input                       │
│  3. Generate query embedding             │
│     └─▶ sentence-transformers            │
│  4. Search Qdrant                        │
│     └─▶ Cosine similarity                │
│  5. Retrieve top-k results               │
│  6. Format response                      │
└──────┬───────────────────────────────────┘
       │
       │ {
       │   "results": [
       │     {
       │       "text": "To authenticate, use...",
       │       "source_url": "https://...",
       │       "title": "Authentication > Getting Started",
       │       "score": 0.87
       │     },
       │     ...
       │   ],
       │   "query": "How do I authenticate?",
       │   "count": 5
       │ }
       ▼
┌──────────────┐
│   Client     │
└──────────────┘
```

## File Organization

```
website-to-mcp/
│
├── Core Application
│   └── app/
│       ├── crawler/      - Web crawling & extraction
│       ├── chunker/      - Semantic chunking
│       ├── embedder/     - Embeddings & vector store
│       ├── api/          - REST API server
│       └── ingest.py     - Ingestion orchestration
│
├── Infrastructure
│   ├── Dockerfile        - Container definition
│   ├── docker-compose.yml - Service orchestration
│   ├── config.yaml       - Central configuration
│   └── requirements.txt  - Python dependencies
│
├── Documentation
│   ├── README.md         - Main documentation
│   ├── ARCHITECTURE.md   - System architecture
│   ├── USAGE.md          - Usage guide
│   ├── EXAMPLES.md       - Code examples
│   ├── CONTRIBUTING.md   - Development guide
│   ├── PROJECT_SUMMARY.md - Project overview
│   └── DIAGRAM.md        - This file
│
├── MCP Integration
│   └── mcp-manifest.json - MCP service manifest
│
└── Utilities
    ├── quickstart.sh     - Quick setup script
    ├── test.sh           - Testing script
    └── validate.py       - Validation script
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                                                               │
│  FastAPI + Uvicorn (REST API)                                │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic                           │
│                                                               │
│  • WebsiteCrawler (BeautifulSoup, requests)                 │
│  • SemanticChunker (Custom Python)                          │
│  • EmbeddingService (sentence-transformers)                 │
│  • VectorStore (qdrant-client)                              │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│                                                               │
│  Qdrant Vector Database                                      │
│  • Cosine similarity search                                  │
│  • Persistent storage                                        │
│  • 384-dimensional vectors                                   │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure                           │
│                                                               │
│  Docker + Docker Compose                                     │
│  • Container orchestration                                   │
│  • Network isolation                                         │
│  • Volume persistence                                        │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Flow

```
1. Clone Repository
   └─▶ git clone https://github.com/lbsa71/website-to-mcp.git

2. Configure
   └─▶ Edit config.yaml (set website URL)

3. Build & Start Services
   └─▶ docker compose up -d
       ├─▶ Pull/Build images
       ├─▶ Create network
       ├─▶ Create volumes
       ├─▶ Start Qdrant
       └─▶ Start API server

4. Ingest Content
   └─▶ docker compose run --rm ingest
       ├─▶ Crawl website
       ├─▶ Extract content
       ├─▶ Create chunks
       ├─▶ Generate embeddings
       └─▶ Store in Qdrant

5. Service Ready
   └─▶ API available at http://localhost:8000
       ├─▶ /query - Semantic search
       ├─▶ /health - Health check
       └─▶ /stats - Statistics
```

## Scaling Strategy

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
    │  API    │       │  API    │       │  API    │
    │Instance1│       │Instance2│       │Instance3│
    └────┬────┘       └────┬────┘       └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Qdrant     │
                    │   Cluster    │
                    └──────────────┘
```
