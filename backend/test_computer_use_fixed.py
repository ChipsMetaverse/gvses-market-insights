#!/usr/bin/env python3
"""
Test Computer Use with the fixed implementation
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.computer_use_verifier import ComputerUseVerifier
from dotenv import load_dotenv

load_dotenv()

async def test_computer_use():
    """Test Computer Use with fixed implementation."""
    print("Testing Computer Use with fixed implementation...")
    
    verifier = ComputerUseVerifier()
    
    # Use localhost directly instead of tunnel
    verifier.tunnel_url = "http://localhost:5174"
    
    # Use headless=False to see the browser
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500  # Slow down actions for visibility
    
    # Simple test scenario
    scenario = {
        "name": "Quick Test - Find and Click Input",
        "description": "Test that Computer Use can find and interact with the query input",
        "steps": [
            {
                "action": "Find the query input field in the Market Insights panel and click on it",
                "expected": "Input field should be focused"
            },
            {
                "action": "Type 'What is PLTR?' in the input field",
                "expected": "Text should appear in the input"
            },
            {
                "action": "Press Enter to submit the query",
                "expected": "Query should be submitted and response should appear"
            }
        ]
    }
    
    result = await verifier.run_scenario(scenario)
    
    print("\n=== Test Results ===")
    print(f"Status: {result['status']}")
    print(f"Steps executed: {len(result.get('steps', []))}")
    print(f"Screenshots taken: {len(result.get('screenshots', []))}")
    print(f"Issues found: {len(result.get('issues', []))}")
    
    if result.get('steps'):
        print("\nSteps:")
        for i, step in enumerate(result['steps'], 1):
            action_desc = step.get('action', step.get('content', ''))
            if isinstance(action_desc, dict):
                action_desc = str(action_desc)
            elif not isinstance(action_desc, str):
                action_desc = str(action_desc)
            print(f"{i}. {step.get('type')}: {action_desc[:100] if action_desc else 'N/A'}")
    
    if result.get('issues'):
        print("\nIssues:")
        for issue in result['issues']:
            print(f"- {issue}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_computer_use())
    
    if result['status'] == 'completed':
        print("\n✅ Computer Use is working correctly!")
    else:
        print(f"\n❌ Computer Use failed: {result.get('error', 'Unknown error')}")