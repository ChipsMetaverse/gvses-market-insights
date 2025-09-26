#!/usr/bin/env python3

import asyncio
import json
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

async def test_responses_api():
    """Test direct Responses API to see structure"""
    
    # Load environment variables
    load_dotenv()
    
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    query = "Give me entry points for swing trades on AAPL tomorrow"
    
    # Convert messages to Responses API format
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"""Provide swing trade analysis for AAPL.
                
Include this JSON structure in your response:
```json
{{
  "swing_trade": {{
    "entry_points": [245.50, 244.00],
    "stop_loss": 242.00,
    "targets": [250.00, 255.00, 260.00],
    "risk_reward": 2.5,
    "support_levels": [240.00, 238.00],
    "resistance_levels": [252.00, 256.00]
  }}
}}
```

Question: {query}"""
                }
            ]
        }
    ]
    
    # Use same parameters as in agent_orchestrator
    response = await client.responses.create(
        model="gpt-5-mini",
        input=messages,
        tools=[],
        max_output_tokens=1500
    )
    
    print("Response type:", type(response))
    print("\nResponse attributes:", [attr for attr in dir(response) if not attr.startswith('_')])
    
    if hasattr(response, 'output'):
        print("\nOutput type:", type(response.output))
        print("Output length:", len(response.output) if hasattr(response.output, '__len__') else 'N/A')
        
        if isinstance(response.output, list):
            for i, item in enumerate(response.output):
                print(f"\n{'='*60}")
                print(f"Output[{i}] type: {type(item)}")
                print(f"Output[{i}] attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")
                
                # Try to get text from various attributes
                if hasattr(item, 'text'):
                    print(f"Output[{i}].text: {item.text[:200] if item.text else 'None'}")
                if hasattr(item, 'content'):
                    print(f"Output[{i}].content type: {type(item.content)}")
                    if isinstance(item.content, list):
                        print(f"Output[{i}].content length: {len(item.content)}")
                        for j, content_item in enumerate(item.content[:3]):  # First 3 items
                            print(f"  Content[{j}] type: {type(content_item)}")
                            if hasattr(content_item, 'text'):
                                print(f"  Content[{j}].text (first 100 chars): {content_item.text[:100]}")
                            if hasattr(content_item, 'type'):
                                print(f"  Content[{j}].type: {content_item.type}")
                    else:
                        print(f"Output[{i}].content: {str(item.content)[:200]}")
                if hasattr(item, 'type'):
                    print(f"Output[{i}].type: {item.type}")
                if hasattr(item, 'role'):
                    print(f"Output[{i}].role: {item.role}")
                    
                # Check if it's a reasoning item
                if 'reasoning' in str(type(item)).lower():
                    print(f"Output[{i}] is a reasoning item")
                    
                # Check if it's a text item
                if 'text' in str(type(item)).lower():
                    print(f"Output[{i}] is a text item")
                
                # Check for message item
                if 'message' in str(type(item)).lower():
                    print(f"Output[{i}] is a message item")
    
    print(f"\n{'='*60}")
    print("EXTRACTION TEST:")
    # Try the extraction logic from agent_orchestrator
    if hasattr(response, 'output') and isinstance(response.output, list):
        for output_item in response.output:
            # Skip reasoning items
            if hasattr(output_item, 'type') and output_item.type == 'reasoning':
                continue
            
            # Try to extract text
            if hasattr(output_item, 'role') and output_item.role == 'assistant':
                if hasattr(output_item, 'content') and isinstance(output_item.content, list):
                    for content_item in output_item.content:
                        if hasattr(content_item, 'type') and content_item.type == 'output_text':
                            if hasattr(content_item, 'text'):
                                print(f"✓ FOUND TEXT via content[].text: {content_item.text[:200]}...")
                                return

if __name__ == "__main__":
    asyncio.run(test_responses_api())
