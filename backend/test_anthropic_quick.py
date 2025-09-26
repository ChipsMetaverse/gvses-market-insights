#!/usr/bin/env python3
"""
Quick Anthropic Computer Use Test
==================================
Minimal test to verify Anthropic Computer Use is working.
"""

import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_anthropic():
    """Test basic Anthropic API connection."""
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("Testing Anthropic API connection...")
    
    try:
        # Simple test without Computer Use first
        response = await client.messages.create(
            model="claude-3-haiku-20240307",  # Using a simpler model first
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'Hello, Computer Use test working!'"
            }]
        )
        
        print(f"Basic API Response: {response.content[0].text}")
        
        # Now test with Computer Use tool
        print("\nTesting Computer Use tool definition...")
        response = await client.beta.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=100,
            tools=[{
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1024,
                "display_height_px": 768,
                "display_number": 1
            }],
            betas=["computer-use-2025-01-24"],
            messages=[{
                "role": "user",
                "content": "Can you see the computer tool? Just say yes or no."
            }]
        )
        
        print(f"Computer Use Response: {response.content[0].text if response.content else 'No response'}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_anthropic())
    if success:
        print("\n✅ Anthropic API and Computer Use are configured correctly!")
    else:
        print("\n❌ Failed to connect to Anthropic API")