#!/usr/bin/env python3
"""Test Responses API tool format"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test_responses_format():
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Check if responses API exists
    if not hasattr(client, 'responses'):
        print("❌ Responses API not available")
        return
    
    print("✅ Responses API available")
    
    # Test different tool formats
    
    # Format 1: Chat Completions style (what we currently have)
    tools_chat_style = [
        {
            "type": "function",
            "function": {
                "name": "get_stock_price",
                "description": "Get stock price",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"}
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]
    
    # Format 2: Simplified (just the function part)
    tools_simplified = [
        {
            "name": "get_stock_price",
            "description": "Get stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"]
            }
        }
    ]
    
    # Format 3: Even simpler
    tools_minimal = [
        {
            "name": "get_stock_price",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                }
            }
        }
    ]
    
    messages = [
        {"role": "system", "content": [{"type": "input_text", "text": "You are a helpful assistant."}]},
        {"role": "user", "content": [{"type": "input_text", "text": "What is the price of AAPL?"}]}
    ]
    
    # Try each format
    formats = [
        ("Chat Completions style", tools_chat_style),
        ("Simplified format", tools_simplified),
        ("Minimal format", tools_minimal)
    ]
    
    for format_name, tools in formats:
        print(f"\n Testing {format_name}...")
        try:
            response = await client.responses.create(
                model="gpt-4o",
                input=messages,
                tools=tools,
                temperature=0.7,
                max_output_tokens=1000
            )
            print(f"✅ {format_name} works!")
            print(f"   Response ID: {response.id}")
            break
        except Exception as e:
            error_msg = str(e)
            if "tools[0].name" in error_msg:
                print(f"❌ {format_name} failed: Missing tools[0].name")
            elif "tools[0].function" in error_msg:
                print(f"❌ {format_name} failed: Missing tools[0].function")
            else:
                print(f"❌ {format_name} failed: {error_msg[:100]}")

if __name__ == "__main__":
    asyncio.run(test_responses_format())