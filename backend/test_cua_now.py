#!/usr/bin/env python3
"""
Test Computer Use Agent - Direct API interaction
"""

import requests
import json
import time

def test_computer_use_api():
    """Test Computer Use via direct API calls."""
    
    print("=" * 70)
    print("🤖 TESTING COMPUTER USE AGENT")
    print("=" * 70)
    
    # Check if Computer Use is running
    print("\n1️⃣ Checking Computer Use status...")
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("   ✅ Computer Use interface is accessible")
        else:
            print(f"   ⚠️ Computer Use returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot connect to Computer Use: {e}")
        print("   Please ensure Docker container is running")
        return False
    
    # Check if trading app is accessible
    print("\n2️⃣ Checking trading app status...")
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("   ✅ Trading app is running")
        else:
            print(f"   ⚠️ Trading app returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Trading app not accessible: {e}")
        print("   Please run: cd frontend && npm run dev")
        return False
    
    # Check backend API
    print("\n3️⃣ Checking backend API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend API healthy")
            print(f"      Phase 5 ML: {data.get('ml_status', {}).get('phase5_enabled', False)}")
        else:
            print(f"   ⚠️ Backend API returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend API not accessible: {e}")
        print("   Please run: cd backend && uvicorn mcp_server:app --reload")
        return False
    
    # Test Computer Use readiness
    print("\n4️⃣ Testing Computer Use readiness...")
    
    # Check VNC desktop
    try:
        response = requests.get("http://localhost:6080/vnc.html", timeout=5)
        if response.status_code == 200:
            print("   ✅ VNC desktop viewer is accessible")
        else:
            print(f"   ⚠️ VNC viewer returned status {response.status_code}")
    except:
        print("   ⚠️ VNC viewer not accessible")
    
    print("\n" + "=" * 70)
    print("✅ COMPUTER USE IS READY!")
    print("=" * 70)
    
    print("\n📋 Test Instructions:")
    print("1. Open your browser to: http://localhost:8080")
    print("2. You'll see a split screen interface:")
    print("   - LEFT: Chat with Claude")
    print("   - RIGHT: Virtual desktop view")
    print("\n3. Copy and paste this test command in the chat:\n")
    
    test_command = """Test the trading application by doing the following:

1. Open Firefox browser
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading dashboard to load completely
4. Look for the TSLA chart in the center
5. Find the Voice Assistant panel on the right side
6. Click on the message input field (it says "Connect to send messages")
7. Type exactly: "What are the patterns for TSLA?"
8. Press Enter to submit
9. Wait 5 seconds for a response
10. Tell me what you see in the Voice Assistant panel

Also describe the current price and technical levels shown for TSLA."""
    
    print(test_command)
    
    print("\n4. Watch Computer Use work:")
    print("   • Firefox will open automatically")
    print("   • Mouse will move and click on elements")
    print("   • Keyboard will type the message")
    print("   • Results will be reported in the chat")
    
    print("\n🎯 Expected Results:")
    print("   • CUA successfully navigates to the app")
    print("   • CUA finds and clicks the message input")
    print("   • CUA types and submits a pattern request")
    print("   • CUA reports TSLA price and technical levels")
    print("   • CUA describes any patterns found (or lack thereof)")
    
    print("\n⏱️  Typical completion time: 30-60 seconds")
    
    return True

if __name__ == "__main__":
    if test_computer_use_api():
        print("\n🚀 Ready to test! Open http://localhost:8080 now")
        print("   Paste the command above and watch it work!")
    else:
        print("\n❌ Please fix the issues above before testing")