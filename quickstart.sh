#!/bin/bash
# Quick start script for Website RAG MCP Service

set -e

echo "================================================"
echo "Website RAG MCP Service - Quick Start"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found. Make sure you're in the project root directory."
    exit 1
fi

echo "Step 1: Starting Qdrant and API services..."
docker compose up -d

echo ""
echo "Step 2: Waiting for services to be ready (30 seconds)..."
sleep 30

echo ""
echo "Step 3: Running ingestion pipeline..."
echo "This will crawl the website and populate the vector database."
echo "This may take several minutes depending on the website size."
echo ""

docker compose run --rm ingest

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "The service is now running at http://localhost:8000"
echo ""
echo "Try these commands:"
echo ""
echo "1. Check health:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. Get stats:"
echo "   curl http://localhost:8000/stats"
echo ""
echo "3. Query the API:"
echo "   curl -X POST http://localhost:8000/query \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"your question\", \"top_k\": 5}'"
echo ""
echo "4. View logs:"
echo "   docker compose logs -f api"
echo ""
echo "5. Stop services:"
echo "   docker compose down"
echo ""
