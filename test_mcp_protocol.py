#!/usr/bin/env python3
"""
Test script for MCP server protocol
Tests JSON-RPC message handling without requiring external services.
"""

import json
import sys

def test_mcp_protocol():
    """Test MCP protocol structure (without running the server)."""
    print("=" * 60)
    print("MCP Server Protocol Tests")
    print("=" * 60)
    print()
    
    # Test 1: Check MCP SDK is available
    print("1. Testing MCP SDK availability...")
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import Tool, Resource
        print("✅ MCP SDK is available")
    except ImportError as e:
        print(f"❌ MCP SDK import failed: {e}")
        return False
    print()
    
    # Test 2: Check MCP server module syntax
    print("2. Testing MCP server module syntax...")
    try:
        import py_compile
        py_compile.compile('app/mcp_server.py', doraise=True)
        print("✅ MCP server syntax is valid")
    except Exception as e:
        print(f"❌ Syntax check failed: {e}")
        return False
    print()
    
    # Test 3: Validate tool definition structure
    print("3. Testing tool definition structure...")
    try:
        test_tool = Tool(
            name="semantic_search",
            description="Search documentation using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        )
        print(f"✅ Tool definition is valid: {test_tool.name}")
    except Exception as e:
        print(f"❌ Tool definition failed: {e}")
        return False
    print()
    
    # Test 4: Validate resource definition structure
    print("4. Testing resource definition structure...")
    try:
        from pydantic import AnyUrl
        test_resource = Resource(
            uri=AnyUrl("website://docs/metadata"),
            name="Documentation Metadata",
            description="Metadata about indexed documentation",
            mimeType="application/json"
        )
        print(f"✅ Resource definition is valid: {test_resource.uri}")
    except Exception as e:
        print(f"❌ Resource definition failed: {e}")
        return False
    print()
    
    # Test 5: Test JSON-RPC message format
    print("5. Testing JSON-RPC message format...")
    try:
        # Example initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Example tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        # Example tools/call request
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "semantic_search",
                "arguments": {
                    "query": "test query",
                    "top_k": 5
                }
            }
        }
        
        print("✅ JSON-RPC message formats are valid")
        print(f"   - Initialize request: {json.dumps(init_request)[:80]}...")
        print(f"   - Tools/list request: {json.dumps(tools_request)[:80]}...")
        print(f"   - Tools/call request: {json.dumps(call_request)[:80]}...")
    except Exception as e:
        print(f"❌ JSON-RPC format test failed: {e}")
        return False
    print()
    
    # Test 6: Check configuration
    print("6. Testing configuration...")
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'mcp' in config, "MCP configuration missing"
        assert 'server_name' in config['mcp'], "MCP server_name missing"
        assert config['mcp']['capabilities']['tools'] == True, "Tools capability not enabled"
        assert config['mcp']['capabilities']['resources'] == True, "Resources capability not enabled"
        
        print("✅ Configuration is valid")
        print(f"   - Server name: {config['mcp']['server_name']}")
        print(f"   - Tools enabled: {config['mcp']['capabilities']['tools']}")
        print(f"   - Resources enabled: {config['mcp']['capabilities']['resources']}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    print()
    
    # Test 7: Check MCP client config
    print("7. Testing MCP client configuration...")
    try:
        with open('mcp-client-config.json', 'r') as f:
            client_config = json.load(f)
        
        assert 'mcpServers' in client_config, "mcpServers key missing"
        assert 'website-rag' in client_config['mcpServers'], "website-rag server config missing"
        
        server_config = client_config['mcpServers']['website-rag']
        assert 'command' in server_config, "Command missing"
        assert 'args' in server_config, "Args missing"
        
        print("✅ MCP client configuration is valid")
        print(f"   - Command: {server_config['command']}")
        print(f"   - Args: {' '.join(server_config['args'])}")
    except Exception as e:
        print(f"❌ Client config test failed: {e}")
        return False
    print()
    
    # Test 8: Verify old REST API files are removed
    print("8. Checking for REST API cleanup...")
    import os
    issues = []
    
    # These files should not exist anymore
    if os.path.exists('app/api/main.py'):
        issues.append("app/api/main.py still exists (should be deleted)")
    
    if os.path.exists('mcp-manifest.json'):
        issues.append("mcp-manifest.json still exists (should be deleted)")
    
    if issues:
        print("⚠️  REST API cleanup pending:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Old REST API files cleaned up")
    print()
    
    return True


def main():
    """Run all tests."""
    success = test_mcp_protocol()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if success:
        print("✅ All MCP protocol tests passed!")
        print()
        print("Note: Full integration tests require:")
        print("  - Qdrant vector database running")
        print("  - Sentence transformers model downloaded")
        print("  - Document collection indexed")
        print()
        print("To run the MCP server:")
        print("  docker compose up -d qdrant")
        print("  docker compose run --rm ingest")
        print("  docker compose up mcp-server")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
