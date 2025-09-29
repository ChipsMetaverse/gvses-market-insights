#!/usr/bin/env python3
"""
Quick test of chart command extraction
"""

import asyncio
import aiohttp
import json


async def test_quick():
    """Quick test of command extraction."""
    
    print("Testing chart command extraction...")
    
    query = "Show support at 440 and resistance at 460 on TSLA"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/api/agent/orchestrate",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"\nQuery: {query}")
                    print(f"Response text preview: {data.get('text', '')[:200]}...")
                    
                    chart_commands = data.get("chart_commands", [])
                    if chart_commands:
                        print(f"\n✅ SUCCESS! Generated {len(chart_commands)} chart commands:")
                        for cmd in chart_commands:
                            print(f"   • {cmd}")
                    else:
                        print(f"\n❌ No chart commands generated")
                    
                    return chart_commands
                else:
                    print(f"HTTP {response.status}: {await response.text()}")
                    return []
        except asyncio.TimeoutError:
            print("Request timed out after 30 seconds")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []


if __name__ == "__main__":
    commands = asyncio.run(test_quick())
    exit(0 if commands else 1)