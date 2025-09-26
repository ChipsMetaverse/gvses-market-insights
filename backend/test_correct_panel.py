#!/usr/bin/env python3
"""
Test Computer Use with CORRECT panel location.
The text input is in the RIGHT panel (Voice Assistant), not the left panel.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from services.seasoned_trader_verifier import SeasonedTraderVerifier

async def test_correct_input_location():
    """Test with correct input location - RIGHT panel."""
    print("Testing with CORRECT input location...")
    
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    # CORRECTED scenario - input is in RIGHT panel
    scenario = {
        "name": "Test Correct Input Location",
        "description": "Find input in Voice Assistant panel (RIGHT side)",
        "steps": [
            {
                "action": "Look for the Voice Assistant panel on the RIGHT side of the screen",
                "expected": "Should see 'VOICE ASSISTANT' heading in right panel"
            },
            {
                "action": "Find the text input field at the bottom of the Voice Assistant panel with placeholder 'Type a message...'",
                "expected": "Input field should be visible and clickable"
            },
            {
                "action": "Click on the text input field in the Voice Assistant panel",
                "expected": "Input field should be focused"
            },
            {
                "action": "Type 'Good morning' in the input field",
                "expected": "Text should appear in the input"
            },
            {
                "action": "Press Enter to send the message",
                "expected": "Message should be sent and appear in conversation"
            }
        ]
    }
    
    print("\n📍 CORRECT LOCATION:")
    print("- Panel: RIGHT side (Voice Assistant)")
    print("- Class: voice-text-input")
    print("- Placeholder: 'Type a message...'")
    print("\nStarting test...")
    
    result = await verifier.run_scenario(scenario)
    
    print(f"\nResult: {result['status']}")
    
    if result['status'] == 'completed':
        print("✅ Found and used the correct input field!")
    else:
        print("❌ Still having issues - check if app is running")
    
    return result

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     CORRECT INPUT LOCATION TEST                         ║
    ║     Input is in RIGHT panel (Voice Assistant)           ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    asyncio.run(test_correct_input_location())