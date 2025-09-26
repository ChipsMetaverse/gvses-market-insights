#!/usr/bin/env python3
"""
Simple test to see what panels Computer Use can identify.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.computer_use_verifier import ComputerUseVerifier

async def test_find_panels():
    """Simple test to identify visible panels."""
    print("Testing panel identification...")
    
    verifier = ComputerUseVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 300
    
    # Very simple scenario
    scenario = {
        "name": "Identify Panels",
        "description": "Find and identify all visible panels",
        "steps": [
            {
                "action": "Take a screenshot and identify all visible panels. Look for: 1) Left panel with CHART ANALYSIS, 2) Center chart area, 3) Right panel with VOICE ASSISTANT",
                "expected": "Should identify three main panels"
            },
            {
                "action": "Locate the text input field. It should be in the Voice Assistant panel on the right side, at the bottom of that panel",
                "expected": "Should find input with placeholder 'Type a message...'"
            },
            {
                "action": "Click on that text input field",
                "expected": "Input should be focused"
            }
        ]
    }
    
    print("\n🔍 Looking for:")
    print("- Left: CHART ANALYSIS panel")
    print("- Center: Trading chart")
    print("- Right: VOICE ASSISTANT panel with text input")
    
    result = await verifier.run_scenario(scenario)
    
    print(f"\nResult: {result['status']}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_find_panels())