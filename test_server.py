#!/usr/bin/env python3
"""
Test script for Claude Voice MCP Server
"""

import asyncio
import json
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_server():
    """Test the MCP server functionality."""
    print("🧪 Testing Claude Voice MCP Server")
    print("=" * 40)
    
    # Check environment
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Loaded .env file")
    else:
        print("⚠️  No .env file found - using environment variables")
    
    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Please set it in backend/.env or as an environment variable")
        return
    print("✅ Anthropic API key found")
    
    # Check Supabase (optional)
    supabase_url = os.environ.get("SUPABASE_URL")
    if supabase_url:
        print("✅ Supabase configured")
    else:
        print("ℹ️  Supabase not configured (optional)")
    
    # Test Claude service
    print("\n📡 Testing Claude API connection...")
    try:
        from mcp_server import ClaudeService
        
        claude = ClaudeService()
        response = await claude.ask("Hello! Can you hear me? Please respond with a brief greeting.")
        
        print("✅ Claude API working!")
        print(f"   Response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return
    
    # Test MCP servers
    mcp_servers_json = os.environ.get("MCP_SERVERS", "[]")
    try:
        mcp_servers = json.loads(mcp_servers_json)
        if mcp_servers:
            print(f"\n📡 Found {len(mcp_servers)} MCP server(s):")
            for server in mcp_servers:
                print(f"   - {server.get('name', 'unnamed')}: {server.get('url', 'no url')}")
        else:
            print("\nℹ️  No MCP servers configured")
    except:
        print("\n⚠️  Invalid MCP_SERVERS configuration")
    
    print("\n✨ All tests completed!")
    print("\nYou can now start the server with:")
    print("  cd backend && uvicorn mcp_server:app --reload")

if __name__ == "__main__":
    # Check for required packages
    try:
        import httpx
        import fastapi
        import pydantic
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Run: pip install -r backend/requirements.txt")
        sys.exit(1)
    
    # Run tests
    asyncio.run(test_server())
