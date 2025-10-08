#!/usr/bin/env python3
"""
Validation script for Website RAG MCP Service
Tests the core logic without external dependencies.
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    try:
        from crawler import web_crawler
        from chunker import semantic_chunker
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_crawler_logic():
    """Test web crawler logic."""
    print("\nTesting web crawler logic...")
    from crawler.web_crawler import WebsiteCrawler
    
    try:
        crawler = WebsiteCrawler("https://example.com", max_pages=5)
        
        # Test URL validation
        assert crawler.is_valid_url("https://example.com/page1") == True
        assert crawler.is_valid_url("https://example.com/image.jpg") == False
        assert crawler.is_valid_url("ftp://example.com") == False
        
        print("✅ Web crawler logic tests passed")
        return True
    except Exception as e:
        print(f"❌ Web crawler test error: {e}")
        return False

def test_chunker_logic():
    """Test chunking logic."""
    print("\nTesting chunker logic...")
    from chunker.semantic_chunker import SemanticChunker
    
    try:
        chunker = SemanticChunker(min_chunk_size=200, max_chunk_size=500)
        
        # Test with sample data
        sample_data = [{
            'url': 'https://example.com/test',
            'title': 'Test Page',
            'sections': [{
                'headers': ['Introduction'],
                'paragraphs': ['This is a test paragraph.'],
                'code_snippets': []
            }]
        }]
        
        chunks = chunker.create_chunks(sample_data)
        assert len(chunks) > 0
        assert 'text' in chunks[0]
        assert 'source_url' in chunks[0]
        assert 'title' in chunks[0]
        
        print(f"✅ Chunker logic tests passed (created {len(chunks)} chunks)")
        return True
    except Exception as e:
        print(f"❌ Chunker test error: {e}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'website' in config
        assert 'chunking' in config
        assert 'embedding' in config
        assert 'vector_store' in config
        assert 'api' in config
        
        print("✅ Configuration loading tests passed")
        return True
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def test_mcp_manifest():
    """Test MCP manifest is valid."""
    print("\nTesting MCP manifest...")
    try:
        import json
        with open('mcp-manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'manifest_version' in manifest
        assert 'service' in manifest
        assert 'endpoints' in manifest
        assert 'query' in manifest['endpoints']
        
        print("✅ MCP manifest is valid")
        return True
    except Exception as e:
        print(f"❌ Manifest test error: {e}")
        return False

def test_docker_compose():
    """Test docker-compose.yml is valid."""
    print("\nTesting docker-compose.yml...")
    try:
        import yaml
        with open('docker-compose.yml', 'r') as f:
            compose = yaml.safe_load(f)
        
        assert 'services' in compose
        assert 'qdrant' in compose['services']
        assert 'api' in compose['services']
        assert 'ingest' in compose['services']
        
        print("✅ docker-compose.yml is valid")
        return True
    except Exception as e:
        print(f"❌ Docker compose test error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Website RAG MCP Service - Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_crawler_logic,
        test_chunker_logic,
        test_config_loading,
        test_mcp_manifest,
        test_docker_compose,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All validation tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
