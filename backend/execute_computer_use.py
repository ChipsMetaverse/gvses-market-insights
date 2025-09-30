#!/usr/bin/env python3
"""
Execute Computer Use Agent commands via the Anthropic API
This script sends commands to the Computer Use Docker container
"""

import os
import json
import requests
from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam
from typing import Dict, Any
import base64
import time

class ComputerUseExecutor:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.computer_use_url = "http://localhost:8080"
        
    def take_screenshot(self) -> str:
        """Take a screenshot of the current desktop state."""
        try:
            # Get screenshot from the VNC viewer
            response = requests.get("http://localhost:6080/api/screenshot", timeout=5)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode('utf-8')
        except:
            pass
        return None
    
    def send_computer_use_command(self, instruction: str) -> Dict[str, Any]:
        """Send a command to Computer Use to execute."""
        
        print(f"📤 Sending command to Computer Use...")
        print(f"   Instruction: {instruction[:100]}...")
        
        try:
            # Computer Use uses the Beta Computer Use API
            response = self.client.beta.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": instruction
                    }
                ],
                betas=["computer-use-2024-10-22"],
                tools=[
                    {
                        "type": "computer_20241022",
                        "display_width_px": 1024,
                        "display_height_px": 768,
                        "display_number": 0
                    }
                ]
            )
            
            print("✅ Command sent successfully")
            return {"success": True, "response": response}
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return {"success": False, "error": str(e)}
    
    def test_trading_app(self):
        """Test the trading application using Computer Use."""
        
        print("=" * 70)
        print("🤖 COMPUTER USE - TRADING APP TEST")
        print("=" * 70)
        
        # Define the test sequence
        test_instruction = """
        You are testing a trading application. Please perform these actions:
        
        1. Take a screenshot to see the current desktop
        2. Open Firefox browser if not already open
        3. Navigate to http://host.docker.internal:5174
        4. Wait for the trading dashboard to load
        5. Look for the TSLA chart in the center
        6. Find the Voice Assistant panel on the right side
        7. Click on the message input field
        8. Type "Show me patterns for TSLA"
        9. Press Enter to submit
        10. Take a screenshot of the results
        11. Report what you observed
        
        Please execute these steps one by one and report your findings.
        """
        
        print("\n📋 Test Instruction:")
        print(test_instruction)
        
        print("\n🚀 Executing test via Computer Use...")
        result = self.send_computer_use_command(test_instruction)
        
        if result["success"]:
            print("\n📊 Results:")
            print(result.get("response", "No response received"))
        else:
            print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
        
        return result

def main():
    """Main execution function."""
    
    # Check if API key is set
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY not set in environment")
        print("   Please set: export ANTHROPIC_API_KEY=your_key")
        return
    
    # Check if Computer Use is accessible
    try:
        response = requests.get("http://localhost:8080", timeout=3)
        if response.status_code != 200:
            print("⚠️ Computer Use interface returned unexpected status")
    except:
        print("❌ Cannot connect to Computer Use at http://localhost:8080")
        print("   Please ensure the Docker container is running")
        return
    
    print("✅ Computer Use is accessible")
    
    # Create executor and run test
    executor = ComputerUseExecutor()
    
    print("\n" + "=" * 70)
    print("🎯 SIMPLIFIED TEST APPROACH")
    print("=" * 70)
    print("\nSince Computer Use Docker has its own interface,")
    print("the easiest way to test is:")
    print("\n1. Open http://localhost:8080 in your browser")
    print("2. In the LEFT chat panel, paste this command:\n")
    
    command = """Please test the trading application:
1. Open Firefox
2. Go to http://host.docker.internal:5174
3. Click on the message input on the right side
4. Type "Show me TSLA patterns"
5. Press Enter
6. Tell me what you see"""
    
    print(command)
    
    print("\n3. Watch the RIGHT panel as Computer Use:")
    print("   • Opens Firefox")
    print("   • Navigates to the app")
    print("   • Clicks and types")
    print("   • Reports results")
    
    print("\n" + "=" * 70)
    print("💡 The Computer Use Docker interface is the best way")
    print("   to interact with it visually and see results.")
    print("=" * 70)

if __name__ == "__main__":
    main()