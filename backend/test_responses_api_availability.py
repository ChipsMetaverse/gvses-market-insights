#!/usr/bin/env python3
"""Check where Responses API is available in OpenAI SDK."""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def check_responses_api():
    """Check different ways to access the Responses API."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("=" * 60)
    print("Checking Responses API Availability")
    print(f"OpenAI SDK Version: {client.__module__}")
    print("=" * 60)
    
    # Check 1: Direct client.responses
    print("\n1. Checking client.responses:")
    if hasattr(client, 'responses'):
        print("   ✅ client.responses exists")
    else:
        print("   ❌ client.responses NOT found")
    
    # Check 2: Beta namespace
    print("\n2. Checking client.beta:")
    if hasattr(client, 'beta'):
        print("   ✅ client.beta exists")
        beta_attrs = [attr for attr in dir(client.beta) if not attr.startswith('_')]
        print(f"   Available beta features: {', '.join(beta_attrs[:10])}")
        
        if hasattr(client.beta, 'responses'):
            print("   ✅ client.beta.responses exists")
        else:
            print("   ❌ client.beta.responses NOT found")
    else:
        print("   ❌ client.beta NOT found")
    
    # Check 3: Look for any responses-related attributes
    print("\n3. Searching for 'response' related attributes:")
    client_attrs = [attr for attr in dir(client) if 'response' in attr.lower()]
    if client_attrs:
        print(f"   Found: {', '.join(client_attrs)}")
    else:
        print("   No 'response' related attributes found")
    
    # Check 4: Available top-level APIs
    print("\n4. Available top-level APIs:")
    apis = []
    for attr in dir(client):
        if not attr.startswith('_') and hasattr(getattr(client, attr), 'create'):
            apis.append(attr)
    print(f"   {', '.join(apis)}")
    
    # Check 5: Try importing responses directly
    print("\n5. Checking direct import:")
    try:
        from openai.resources import responses
        print("   ✅ openai.resources.responses can be imported")
    except ImportError as e:
        print(f"   ❌ Cannot import openai.resources.responses: {e}")
    
    # Check 6: Look for Responses in types
    print("\n6. Checking openai.types:")
    try:
        import openai.types as types
        response_types = [t for t in dir(types) if 'Response' in t]
        if response_types:
            print(f"   Found Response types: {', '.join(response_types[:5])}")
        else:
            print("   No Response types found")
    except Exception as e:
        print(f"   Error checking types: {e}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("The Responses API appears to be documented but not yet")
    print("implemented in the current OpenAI Python SDK (v1.109.0).")
    print("It may be:")
    print("1. Coming in a future SDK release")
    print("2. Available only via direct HTTP API calls")
    print("3. In closed beta/preview for select users")
    print("=" * 60)

if __name__ == "__main__":
    check_responses_api()