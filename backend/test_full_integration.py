#!/usr/bin/env python3
"""Test the full integration with ideal formatter and bounded insights."""

import asyncio
import json
from services.agent_orchestrator import get_orchestrator

async def test_full_integration():
    orchestrator = get_orchestrator()
    
    print("Testing Full Integration with Ideal Format + Bounded Insights")
    print("=" * 70)
    
    # Test with a simple stock query
    response = await orchestrator.process_query("analyze AAPL stock with detailed insights")
    
    # Extract the formatted text
    formatted_text = response.get('text', '')
    
    # Print the response
    print("\n[FULL RESPONSE]")
    print("-" * 70)
    print(formatted_text[:2500])  # First 2500 chars
    if len(formatted_text) > 2500:
        print("\n... [content continues] ...\n")
    print("-" * 70)
    
    # Check for key sections
    sections = [
        "## Here's your real-time",
        "Market Snapshot & Context",
        "Key Headlines",
        "Technical Overview & Forecasts",
        "Broader Trends & Forecasts",
        "Summary Table",
        "Strategic Insights",
        "AI Analysis",  # New bounded insight section
        "Would you like me to dive deeper",
        "Disclaimer"
    ]
    
    print("\n[SECTION VERIFICATION]")
    print("-" * 70)
    for section in sections:
        present = "✅" if section in formatted_text else "❌"
        print(f"  {present} {section}")
    
    # Check metadata
    print("\n[METADATA]")
    print("-" * 70)
    print(f"  Tools used: {response.get('tools_used', [])}")
    print(f"  Data sources: {[d.get('data_source') for d in response.get('data', {}).values() if isinstance(d, dict) and 'data_source' in d]}")
    print(f"  Response length: {len(formatted_text)} characters")
    print(f"  Timestamp: {response.get('timestamp', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_full_integration())