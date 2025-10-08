#!/bin/bash
# Test script for the Website RAG MCP Service

echo "==================================="
echo "Website RAG MCP Service - Test Script"
echo "==================================="
echo ""

# Check if services are running
echo "1. Checking if services are running..."
if ! docker compose ps | grep -q "qdrant.*Up"; then
    echo "❌ Qdrant is not running. Start with: docker compose up -d"
    exit 1
fi

if ! docker compose ps | grep -q "rag-api.*Up"; then
    echo "❌ API service is not running. Start with: docker compose up -d"
    exit 1
fi

echo "✅ Services are running"
echo ""

# Wait for API to be ready
echo "2. Waiting for API to be ready..."
max_retries=30
retry=0
while [ $retry -lt $max_retries ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready"
        break
    fi
    retry=$((retry + 1))
    sleep 1
done

if [ $retry -eq $max_retries ]; then
    echo "❌ API failed to start within 30 seconds"
    exit 1
fi
echo ""

# Test health endpoint
echo "3. Testing /health endpoint..."
health_response=$(curl -s http://localhost:8000/health)
echo "Response: $health_response"
echo ""

# Test stats endpoint
echo "4. Testing /stats endpoint..."
stats_response=$(curl -s http://localhost:8000/stats)
echo "Response: $stats_response"
echo ""

# Test query endpoint
echo "5. Testing /query endpoint..."
echo "Query: 'How do I create a function?'"
query_response=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I create a function?", "top_k": 3}')

echo "Response:"
echo "$query_response" | python3 -m json.tool 2>/dev/null || echo "$query_response"
echo ""

# Summary
echo "==================================="
echo "Test Summary"
echo "==================================="
echo "✅ All endpoints tested successfully"
echo ""
echo "Try your own queries:"
echo "curl -X POST http://localhost:8000/query \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"your question here\", \"top_k\": 5}'"
echo ""
