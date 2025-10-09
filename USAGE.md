# Usage Guide - Website RAG MCP Service

This guide provides detailed instructions for using the Website RAG MCP Service.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Service](#running-the-service)
4. [Using with MCP Clients](#using-with-mcp-clients)
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

# Start MCP server
python -m app.mcp_server
```

## Using with MCP Clients

The service implements the Model Context Protocol and communicates via stdio using JSON-RPC 2.0.

### Claude Desktop Integration

Add to your Claude Desktop configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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

Restart Claude Desktop. The server will appear in the MCP section with available tools.

### Using MCP Python Client

```python
from mcp import Client
import asyncio

async def search_documentation():
    # Connect to the MCP server
    async with Client("website-rag") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Call semantic_search tool
        result = await client.call_tool(
            "semantic_search",
            arguments={
                "query": "How do I configure authentication?",
                "top_k": 5
            }
        )
        
        # Process results
        for i, item in enumerate(result['results'], 1):
            print(f"{i}. {item['title']}")
            print(f"   URL: {item['source_url']}")
            print(f"   Score: {item['score']:.3f}")
            print(f"   Preview: {item['text'][:150]}...")
            print()

asyncio.run(search_documentation())
```

### Available MCP Tools

#### `semantic_search`

Search documentation using semantic similarity.

**Parameters:**
- `query` (string, required): Search query text
- `top_k` (integer, optional): Number of results (default: 5, max: 20)

**Example:**
```python
result = await client.call_tool(
    "semantic_search",
    arguments={"query": "installation steps", "top_k": 10}
)
```

### Available MCP Resources

#### `website://docs/metadata`

Get metadata about the indexed documentation.

```python
metadata = await client.read_resource("website://docs/metadata")
print(metadata)
```

#### `website://docs/stats`

Get collection statistics.

```python
stats = await client.read_resource("website://docs/stats")
print(stats)
```

### Testing MCP Protocol

The server communicates via JSON-RPC 2.0. Example messages:

**Initialize request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test-client", "version": "1.0.0"}
  }
}
```

**Tools/list request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Tools/call request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "semantic_search",
    "arguments": {"query": "test", "top_k": 5}
  }
}
```

## Integration Examples

### LLM Integration (RAG Pattern)

Using MCP with an LLM:

```python
from mcp import Client
import asyncio

async def answer_with_docs(question: str) -> str:
    """Answer question using documentation via MCP."""
    async with Client("website-rag") as client:
        # Get relevant context using semantic_search tool
        result = await client.call_tool(
            "semantic_search",
            arguments={"query": question, "top_k": 3}
        )
        
        # Combine results into context
        context_parts = []
        for r in result['results']:
            context_parts.append(f"From {r['title']}:\n{r['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Build prompt for LLM
        prompt = f"""Using the following documentation, answer the question.

Documentation:
{context}

Question: {question}

Answer:"""
        
        # Send to your LLM (OpenAI, Anthropic, etc.)
        # response = llm.complete(prompt)
        # return response

# Example usage
asyncio.run(answer_with_docs("How do I configure authentication?"))
```

### MCP Server in Custom Application

```python
import subprocess
import json

def query_mcp_server(query: str, top_k: int = 5):
    """Query MCP server via subprocess."""
    # Start MCP server process
    process = subprocess.Popen(
        ["python", "-m", "app.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize request
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "custom-app", "version": "1.0.0"}
        }
    }
    process.stdin.write(json.dumps(init_msg) + "\n")
    process.stdin.flush()
    
    # Send tools/call request
    call_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "semantic_search",
            "arguments": {"query": query, "top_k": top_k}
        }
    }
    process.stdin.write(json.dumps(call_msg) + "\n")
    process.stdin.flush()
    
    # Read response
    response = process.stdout.readline()
    return json.loads(response)
```

### Chatbot Integration

```python
from mcp import Client
import asyncio

class DocsChatbot:
    """Chatbot with documentation access via MCP."""
    
    def __init__(self, mcp_server: str = "website-rag"):
        self.mcp_server = mcp_server
        self.conversation_history = []
    
    async def search_docs(self, query: str, top_k: int = 3):
        """Search documentation using MCP."""
        async with Client(self.mcp_server) as client:
            result = await client.call_tool(
                "semantic_search",
                arguments={"query": query, "top_k": top_k}
            )
            return result['results']
    
    async def chat(self, user_message: str) -> str:
        """Process user message with doc context."""
        # Search for relevant docs
        docs = await self.search_docs(user_message)
        
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
response = asyncio.run(chatbot.chat("How do I get started?"))
print(response)
```

## Troubleshooting

### Service Won't Start

**Check Docker:**
```bash
docker --version
docker compose --version
```

**Check if Qdrant port is free:**
```bash
# Make sure port 6333 is free
netstat -tuln | grep 6333

# Or on Mac:
lsof -i :6333
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

**Check document count via MCP:**
```python
from mcp import Client
import asyncio

async def check_stats():
    async with Client("website-rag") as client:
        stats = await client.read_resource("website://docs/stats")
        print(stats)

asyncio.run(check_stats())
```

**Verify ingestion completed:**
```bash
docker compose logs ingest | grep "Ingestion complete"
```

**Try simpler queries with MCP client:**
```python
# Instead of very specific query, try broader ones
result = await client.call_tool(
    "semantic_search",
    arguments={"query": "getting started", "top_k": 10}
)
```

**Increase top_k parameter:**
```python
result = await client.call_tool(
    "semantic_search",
    arguments={"query": "your query", "top_k": 20}
)
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
