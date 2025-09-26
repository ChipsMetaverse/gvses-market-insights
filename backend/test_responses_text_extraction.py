#!/usr/bin/env python3
"""Simple test to verify Responses API text extraction fix."""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_responses_api_text_extraction():
    """Test that output_text property is working correctly."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("Testing Responses API text extraction fix...")
    print("-" * 50)
    
    # Test with a simple query using gpt-4o-mini (faster and cheaper)
    try:
        response = client.beta.responses.create(
            model="gpt-4o-mini",
            input="Tell me a one-sentence joke about programming",
            max_tokens=100
        )
        
        # Check if output_text property exists and works
        if hasattr(response, 'output_text'):
            text = response.output_text
            print(f"✅ SUCCESS: output_text property exists")
            print(f"   Text length: {len(text) if text else 0} chars")
            print(f"   Text preview: {text[:200] if text else 'None'}")
        else:
            print("❌ FAIL: output_text property not found")
            print(f"   Response attributes: {dir(response)[:10]}")
            
        # Also check the output array for comparison
        if hasattr(response, 'output'):
            print(f"\n📊 Output array has {len(response.output)} items")
            for i, item in enumerate(response.output):
                print(f"   Item {i}: type={getattr(item, 'type', 'unknown')}")
                
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
        # Try with regular chat completions as fallback
        print("\nTrying Chat Completions API as comparison...")
        try:
            chat_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Tell me a one-sentence joke about programming"}],
                max_tokens=100
            )
            text = chat_response.choices[0].message.content
            print(f"✅ Chat Completions works: {len(text)} chars")
        except Exception as e2:
            print(f"❌ Chat Completions also failed: {str(e2)}")

if __name__ == "__main__":
    test_responses_api_text_extraction()