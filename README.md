# Website RAG MCP Service

A turnkey Dockerized service that crawls documentation websites, extracts semantic content, stores vector embeddings, and exposes an MCP (Model Context Protocol) server for retrieval-augmented generation (RAG). Perfect for integrating documentation search with MCP-compatible LLM clients like Claude Desktop.

## 🚀 Features

- **Website Ingestion**: Crawls documentation sites and extracts semantic content (headers, paragraphs, code snippets)
- **Smart Chunking**: Splits content into meaningful chunks while preserving context
- **Vector Embeddings**: Uses sentence-transformers for local, cost-free embeddings
- **Semantic Search**: Powered by Qdrant vector database for fast similarity search
- **MCP Protocol**: Full Model Context Protocol implementation with JSON-RPC 2.0 over stdio
- **MCP Tools**: Semantic search exposed as MCP tool for LLM agents
- **MCP Resources**: Documentation metadata accessible as MCP resources
- **Fully Dockerized**: One command to spin up the entire service

## 📚 Documentation

This project includes comprehensive documentation to help you get started and customize the service:

- **[README.md](README.md)** - Main documentation with quick start guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture and component design
- **[USAGE.md](USAGE.md)** - Comprehensive usage guide with examples
- **[EXAMPLES.md](EXAMPLES.md)** - Code examples and query patterns
- **[DIAGRAM.md](DIAGRAM.md)** - Visual system diagrams and data flow
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development and contribution guidelines
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview and deliverables

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
# Start Qdrant vector database and MCP server
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

### 5. Use with MCP Client

The server uses the Model Context Protocol and communicates via stdio. Configure your MCP client using the provided configuration:

**For Claude Desktop**, add to your config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "website-rag": {
      "command": "docker",
      "args": ["compose", "run", "--rm", "mcp-server"],
      "env": {
        "CONFIG_PATH": "/app/config.yaml"
      }
    }
  }
}
```

**For other MCP clients**, use the configuration in `mcp-client-config.json`.

The server provides:
- **Tool**: `semantic_search` - Search documentation using semantic similarity
- **Resources**: 
  - `website://docs/metadata` - Documentation metadata
  - `website://docs/stats` - Collection statistics

Example using MCP client:

```python
# Using an MCP client library
from mcp import Client

async with Client("website-rag") as client:
    # List available tools
    tools = await client.list_tools()
    
    # Call semantic_search tool
    result = await client.call_tool(
        "semantic_search",
        arguments={"query": "How do I create a function?", "top_k": 5}
    )
    
    print(result)
```
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

# MCP server settings
mcp:
  server_name: "website-rag-mcp"
  capabilities:
    tools: true               # Enable tool support
    resources: true           # Enable resource support
    prompts: false            # Prompts not implemented

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

## 🔌 MCP Integration

This service implements the Model Context Protocol, allowing it to be used as a tool provider for MCP-compatible clients.

### Available MCP Tools

#### `semantic_search`

Search documentation using semantic similarity.

**Parameters:**
- `query` (string, required): The search query text
- `top_k` (integer, optional): Number of results to return (default: 5, max: 20)

**Returns:**
```json
{
  "query": "your search query",
  "results": [
    {
      "text": "Content chunk...",
      "source_url": "https://...",
      "title": "Section title",
      "score": 0.85
    }
  ],
  "count": 5
}
```

### Available MCP Resources

#### `website://docs/metadata`

Get metadata about the indexed documentation.

**Returns:** JSON containing total chunks, website URL, last update time, embedding model info, etc.

#### `website://docs/stats`

Get statistics about the documentation collection.

**Returns:** JSON containing documents indexed, embedding model details, and vector store configuration.
    
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
│ MCP Server  │ Expose tools/resources via JSON-RPC 2.0
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
- Check document count using MCP resources
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
| MCP Server | MCP Python SDK |
| Protocol | JSON-RPC 2.0 over stdio |
| Orchestration | Docker Compose |

## 🔗 Related Projects

- [Qdrant](https://qdrant.tech/) - Vector database
- [sentence-transformers](https://www.sbert.net/) - Embedding models
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - MCP server implementation
