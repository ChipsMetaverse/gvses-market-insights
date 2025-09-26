#!/usr/bin/env python3
"""
Test script to diagnose OpenAI embeddings API access issues.
Tests all available embedding models and checks permissions.
"""

import os
import asyncio
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Available embedding models according to the allowed models list
EMBEDDING_MODELS = [
    "text-embedding-3-large",       # Preferred high-quality model
    "text-embedding-3-small"        # Lower-cost fallback
]

def test_sync_embeddings():
    """Test synchronous embeddings API access."""
    print("\n" + "="*60)
    print("TESTING SYNCHRONOUS EMBEDDINGS API")
    print("="*60)
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    test_text = "The quick brown fox jumps over the lazy dog"
    
    for model in EMBEDDING_MODELS:
        print(f"\nTesting model: {model}")
        print("-" * 40)
        
        try:
            response = client.embeddings.create(
                model=model,
                input=test_text,
                encoding_format="float"
            )
            
            # Check response structure
            embedding = response.data[0].embedding
            dimensions = len(embedding)
            
            print(f"✅ SUCCESS!")
            print(f"   Model: {response.model}")
            print(f"   Dimensions: {dimensions}")
            print(f"   Usage: {response.usage.total_tokens} tokens")
            print(f"   First 5 values: {embedding[:5]}")
            
        except Exception as e:
            print(f"❌ FAILED!")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            
            # Try to extract more details from the error
            if hasattr(e, 'response'):
                print(f"   Response status: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"   Response body: {getattr(e.response, 'text', 'N/A')}")

async def test_async_embeddings():
    """Test asynchronous embeddings API access."""
    print("\n" + "="*60)
    print("TESTING ASYNCHRONOUS EMBEDDINGS API")
    print("="*60)
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    test_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Trading patterns can indicate market sentiment"
    ]
    
    for model in EMBEDDING_MODELS:
        print(f"\nTesting model: {model}")
        print("-" * 40)
        
        try:
            # Test single embedding
            response = await client.embeddings.create(
                model=model,
                input=test_texts[0]
            )
            
            embedding = response.data[0].embedding
            print(f"✅ Single embedding SUCCESS!")
            print(f"   Dimensions: {len(embedding)}")
            
            # Test batch embeddings
            batch_response = await client.embeddings.create(
                model=model,
                input=test_texts
            )
            
            print(f"✅ Batch embedding SUCCESS!")
            print(f"   Batch size: {len(batch_response.data)}")
            print(f"   Total tokens: {batch_response.usage.total_tokens}")
            
        except Exception as e:
            print(f"❌ FAILED!")
            print(f"   Error: {str(e)}")

def check_api_key():
    """Check if API key is configured."""
    print("\n" + "="*60)
    print("API KEY CONFIGURATION")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ API key found")
        print(f"   Key starts with: {api_key[:15]}...")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print("❌ API key not found in environment variables")
        print("   Please set OPENAI_API_KEY in your .env file")
    
    return api_key is not None

def test_with_project_id():
    """Test if we need to specify organization or project ID."""
    print("\n" + "="*60)
    print("TESTING WITH ORGANIZATION/PROJECT SETTINGS")
    print("="*60)
    
    # Check for organization ID in environment
    org_id = os.getenv("OPENAI_ORG_ID")
    project_id = os.getenv("OPENAI_PROJECT_ID")
    
    print(f"Organization ID: {org_id or 'Not set'}")
    print(f"Project ID: {project_id or 'Not set'}")
    
    # Try with organization if available
    client_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
    if org_id:
        client_kwargs["organization"] = org_id
    
    client = OpenAI(**client_kwargs)
    
    # Test with the most basic model
    model = "text-embedding-ada-002"
    print(f"\nTesting {model} with organization settings...")
    
    try:
        response = client.embeddings.create(
            model=model,
            input="test"
        )
        print(f"✅ SUCCESS with current settings")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# OPENAI EMBEDDINGS API ACCESS DIAGNOSTIC")
    print("#"*60)
    
    # Check API key
    if not check_api_key():
        print("\n⚠️  Cannot proceed without API key")
        return
    
    # Test with organization/project settings
    test_with_project_id()
    
    # Test synchronous API
    test_sync_embeddings()
    
    # Test asynchronous API
    await test_async_embeddings()
    
    print("\n" + "#"*60)
    print("# DIAGNOSTIC COMPLETE")
    print("#"*60)

if __name__ == "__main__":
    asyncio.run(main())
