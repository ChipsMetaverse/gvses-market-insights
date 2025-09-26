#!/usr/bin/env python3
import os
import asyncio
from openai import AsyncOpenAI

async def test_embedding():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key exists: {bool(api_key)}")
    if api_key:
        print(f"API Key prefix: {api_key[:20]}...")
        print(f"API Key length: {len(api_key)}")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        print("\n✓ OpenAI client created")
        
        print("\nTesting embedding...")
        response = await client.embeddings.create(
            model="text-embedding-3-large",
            input="What is RSI?"
        )
        
        print(f"✓ Embedding successful!")
        print(f"  Vector length: {len(response.data[0].embedding)}")
        print(f"  First 5 values: {response.data[0].embedding[:5]}")
        
    except Exception as e:
        print(f"\n✗ Embedding failed!")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_embedding())
