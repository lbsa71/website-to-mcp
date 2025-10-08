# Example Queries for Website RAG MCP Service

This file contains example queries you can use to test the service.

## Using curl

### Basic Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I get started?"}'
```

### Query with Custom top_k
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best practices?", "top_k": 10}'
```

### Code-Related Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me an example of a function"}'
```

## Using Python

```python
import requests

def query_rag_service(query: str, top_k: int = 5):
    """Query the RAG service."""
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "top_k": top_k}
    )
    return response.json()

# Example usage
results = query_rag_service("How do I initialize a project?")
print(f"Found {results['count']} results:")
for i, result in enumerate(results['results'], 1):
    print(f"\n{i}. {result['title']}")
    print(f"   URL: {result['source_url']}")
    print(f"   Score: {result['score']:.3f}")
    print(f"   Text: {result['text'][:200]}...")
```

## Using JavaScript/Node.js

```javascript
async function queryRAGService(query, topK = 5) {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, top_k: topK })
    });
    return await response.json();
}

// Example usage
queryRAGService('How do I create a function?')
    .then(results => {
        console.log(`Found ${results.count} results:`);
        results.results.forEach((result, i) => {
            console.log(`\n${i + 1}. ${result.title}`);
            console.log(`   Score: ${result.score.toFixed(3)}`);
            console.log(`   Text: ${result.text.substring(0, 200)}...`);
        });
    });
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
```bash
# These should return similar results
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I start?"}'

curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the first steps?"}'
```

### Test code search
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "function declaration example"}'
```

### Test context retrieval
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "error handling and debugging", "top_k": 8}'
```
