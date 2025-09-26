#!/usr/bin/env python3
"""Test if the Responses API actually works."""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_responses_api():
    """Test if client.responses.create() works."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("=" * 60)
    print("Testing Responses API (client.responses.create)")
    print("=" * 60)
    
    # Confirm client.responses exists
    print("\n✅ client.responses exists:", hasattr(client, 'responses'))
    print("✅ client.responses.create exists:", hasattr(client.responses, 'create'))
    
    # Try the simplest possible request
    print("\nAttempting to call client.responses.create()...")
    print("-" * 40)
    
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input="Tell me a joke about Python programming"
        )
        
        print("✅ SUCCESS! Responses API is working!")
        
        # Check for output_text property
        if hasattr(response, 'output_text'):
            print(f"\n✅ output_text property exists")
            print(f"   Response: {response.output_text}")
        else:
            print("\n⚠️  No output_text property")
            print(f"   Response attributes: {[a for a in dir(response) if not a.startswith('_')][:10]}")
        
        # Check output array
        if hasattr(response, 'output'):
            print(f"\n📊 Output array has {len(response.output)} items")
            for i, item in enumerate(response.output):
                item_type = getattr(item, 'type', 'unknown')
                print(f"   Item {i}: type={item_type}")
                if item_type == 'message':
                    content = getattr(item, 'content', None)
                    if content:
                        print(f"   Message content preview: {str(content)[:100]}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"\nError type: {type(e).__name__}")
        
        # If it's a 404, the API endpoint might not be available
        if "404" in str(e):
            print("\n⚠️  The Responses API endpoint doesn't exist on the server")
            print("   This suggests the API is not yet publicly available")
        elif "not found" in str(e).lower():
            print("\n⚠️  The model or endpoint is not available")
        else:
            print("\n⚠️  Unknown error - the API may be in preview/beta")

if __name__ == "__main__":
    test_responses_api()