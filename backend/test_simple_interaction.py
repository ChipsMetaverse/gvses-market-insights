#!/usr/bin/env python3
"""
Minimal test - just click in the right area and type.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.computer_use_verifier import ComputerUseVerifier

async def test_simple():
    """Minimal test - click and type."""
    verifier = ComputerUseVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    scenario = {
        "name": "Simple Click and Type",
        "description": "Click in right panel and type",
        "steps": [
            {
                "action": "Click somewhere in the bottom-right area of the screen where you see a text input field",
                "expected": "Click should work"
            },
            {
                "action": "Type 'Hello'",
                "expected": "Text should appear"
            }
        ]
    }
    
    print("Running minimal interaction test...")
    result = await verifier.run_scenario(scenario)
    print(f"Result: {result['status']}")
    
    # Show what actions were taken
    if result.get('steps'):
        print("\nActions taken:")
        for step in result['steps']:
            if step.get('type') == 'action':
                action = step.get('action', {})
                print(f"  - {action}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_simple())