#!/usr/bin/env python3
"""Quick test of trader Computer Use setup."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.seasoned_trader_verifier import SeasonedTraderVerifier

async def quick_test():
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    # Simple trader scenario
    scenario = {
        "name": "Quick Trader Test",
        "description": "Test G'sves trader persona",
        "steps": [
            {"action": "Type 'Good morning' in the query input", "expected": "Market brief response"},
            {"action": "Ask 'What are the LTB levels for NVDA?'", "expected": "Technical levels shown"}
        ]
    }
    
    print("Testing G'sves trader persona...")
    result = await verifier.run_scenario(scenario)
    print(f"Result: {result['status']}")
    
    if result['status'] == 'completed':
        print("✅ Trader persona working!")
    
    return result

if __name__ == "__main__":
    asyncio.run(quick_test())