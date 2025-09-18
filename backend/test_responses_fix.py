#!/usr/bin/env python3
"""Fix Responses API tool format"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test_responses_fix():
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    if not hasattr(client, 'responses'):
        print("❌ Responses API not available")
        return
    
    print("✅ Responses API available")
    
    # Try a hybrid format - keep type but flatten function
    tools_hybrid = [
        {
            "type": "function",
            "name": "get_stock_price",
            "description": "Get stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"}
                },
                "required": ["symbol"]
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": [{"type": "input_text", "text": "You are a helpful assistant."}]},
        {"role": "user", "content": [{"type": "input_text", "text": "What is the price of AAPL?"}]}
    ]
    
    print("\nTesting hybrid format (type + flattened function)...")
    try:
        response = await client.responses.create(
            model="gpt-4o",
            input=messages,
            tools=tools_hybrid,
            temperature=0.7,
            max_output_tokens=1000
        )
        print("✅ Hybrid format works!")
        print(f"   Response ID: {response.id}")
        
        # Check if there's a required_action
        if hasattr(response, 'required_action'):
            print(f"   Required action: {response.required_action}")
        
        # Check response content
        if hasattr(response, 'output'):
            print(f"   Output: {response.output[:100]}...")
            
        return response
        
    except Exception as e:
        print(f"❌ Hybrid format failed: {e}")
        
        # Try without tools at all to see if basic Responses API works
        print("\nTesting without tools...")
        try:
            response = await client.responses.create(
                model="gpt-4o",
                input=messages,
                temperature=0.7,
                max_output_tokens=1000
            )
            print("✅ Responses API works without tools!")
            print(f"   Response ID: {response.id}")
            
            if hasattr(response, 'output'):
                output = response.output
                if isinstance(output, list) and len(output) > 0:
                    content = output[0]
                    if isinstance(content, dict) and 'content' in content:
                        text = content['content']
                        if isinstance(text, list) and len(text) > 0:
                            actual_text = text[0].get('text', '')
                            print(f"   Output: {actual_text[:100]}...")
                
            return response
            
        except Exception as e2:
            print(f"❌ Without tools also failed: {e2}")
            return None

if __name__ == "__main__":
    asyncio.run(test_responses_fix())