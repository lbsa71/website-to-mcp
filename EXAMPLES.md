# Example Queries for Website RAG MCP Service

This file contains example queries you can use to test the MCP service.

## Using MCP Python Client

### Basic Query

```python
from mcp import Client
import asyncio

async def basic_search():
    async with Client("website-rag") as client:
        result = await client.call_tool(
            "semantic_search",
            arguments={"query": "How do I get started?"}
        )
        
        print(f"Found {result['count']} results:")
        for i, item in enumerate(result['results'], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   URL: {item['source_url']}")
            print(f"   Score: {item['score']:.3f}")
            print(f"   Text: {item['text'][:200]}...")

asyncio.run(basic_search())
```

### Query with Custom top_k

```python
from mcp import Client
import asyncio

async def custom_topk_search():
    async with Client("website-rag") as client:
        result = await client.call_tool(
            "semantic_search",
            arguments={
                "query": "What are the best practices?",
                "top_k": 10
            }
        )
        
        print(f"Found {result['count']} results")
        return result

asyncio.run(custom_topk_search())
```

### Code-Related Query

```python
from mcp import Client
import asyncio

async def code_search():
    async with Client("website-rag") as client:
        result = await client.call_tool(
            "semantic_search",
            arguments={"query": "Show me an example of a function"}
        )
        
        for item in result['results']:
            print(f"\n{item['title']}")
            print(f"{item['text']}\n")

asyncio.run(code_search())
```

### List Available Tools

```python
from mcp import Client
import asyncio

async def list_tools():
    async with Client("website-rag") as client:
        tools = await client.list_tools()
        
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
            print(f"    Parameters: {tool.inputSchema}")

asyncio.run(list_tools())
```

### Access Resources

```python
from mcp import Client
import asyncio
import json

async def get_metadata():
    async with Client("website-rag") as client:
        # List all resources
        resources = await client.list_resources()
        print("Available resources:")
        for resource in resources:
            print(f"  - {resource.uri}: {resource.description}")
        
        # Read metadata
        metadata = await client.read_resource("website://docs/metadata")
        print("\nMetadata:")
        print(json.dumps(json.loads(metadata), indent=2))
        
        # Read stats
        stats = await client.read_resource("website://docs/stats")
        print("\nStats:")
        print(json.dumps(json.loads(stats), indent=2))

asyncio.run(get_metadata())
```

## Using MCP with JSON-RPC 2.0 (Direct stdio)

For testing or custom integrations, you can interact directly with the JSON-RPC protocol:

### Initialize Connection

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | python -m app.mcp_server
```

### List Tools

```bash
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python -m app.mcp_server
```

### Call Tool

```bash
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "semantic_search", "arguments": {"query": "How do I get started?", "top_k": 5}}}' | python -m app.mcp_server
```

## Example Queries by Domain

### Documentation Site (General)
- "How do I get started?"
- "What are the installation steps?"
- "How do I configure the application?"
- "What are the system requirements?"
- "Show me examples"

### API Documentation
- "How do I authenticate?"
- "What endpoints are available?"
- "Show me an example API request"
- "What are the rate limits?"
- "How do I handle errors?"

### Programming Documentation
- "How do I create a function?"
- "What are the best practices?"
- "Show me code examples"
- "How do I handle async operations?"
- "What libraries should I use?"

### Framework Documentation
- "How do I create a component?"
- "What is the project structure?"
- "How do I add routing?"
- "What are the lifecycle hooks?"
- "How do I manage state?"

## Tips for Better Queries

1. **Be specific**: Instead of "functions", try "how to create async functions in Python"
2. **Use natural language**: The system understands conversational queries
3. **Ask for examples**: Include "example" or "show me" for code snippets
4. **Adjust top_k**: Use higher values (10-20) for broader searches
5. **Check scores**: Results with score > 0.7 are typically very relevant

## Testing Different Scenarios

### Test semantic understanding

```python
from mcp import Client
import asyncio

async def test_semantic_understanding():
    async with Client("website-rag") as client:
        # These should return similar results
        result1 = await client.call_tool(
            "semantic_search",
            arguments={"query": "How do I start?"}
        )
        
        result2 = await client.call_tool(
            "semantic_search",
            arguments={"query": "What are the first steps?"}
        )
        
        print("Query 1 results:", len(result1['results']))
        print("Query 2 results:", len(result2['results']))

asyncio.run(test_semantic_understanding())
```

### Test code search

```python
from mcp import Client
import asyncio

async def test_code_search():
    async with Client("website-rag") as client:
        result = await client.call_tool(
            "semantic_search",
            arguments={"query": "function declaration example", "top_k": 5}
        )
        
        for item in result['results']:
            if 'code' in item.get('type', '').lower() or '```' in item['text']:
                print(f"Found code example: {item['title']}")
                print(item['text'][:300])

asyncio.run(test_code_search())
```

### Test context retrieval

```python
from mcp import Client
import asyncio

async def test_context_retrieval():
    async with Client("website-rag") as client:
        result = await client.call_tool(
            "semantic_search",
            arguments={"query": "step by step tutorial", "top_k": 10}
        )
        
        # Combine results to build comprehensive context
        context = "\n\n".join([
            f"{item['title']}: {item['text']}"
            for item in result['results'][:3]
        ])
        
        print("Combined context:")
        print(context)

asyncio.run(test_context_retrieval())
```
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "error handling and debugging", "top_k": 8}'
```
