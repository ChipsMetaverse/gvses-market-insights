#!/usr/bin/env python3
"""
Opens Computer Use and provides test instructions
"""

import webbrowser
import time

def open_computer_use_test():
    """Open Computer Use and provide instructions."""
    
    print("=" * 70)
    print("🤖 OPENING COMPUTER USE AGENT FOR TESTING")
    print("=" * 70)
    
    # Open Computer Use in browser
    print("\n🌐 Opening Computer Use in your browser...")
    webbrowser.open("http://localhost:8080")
    
    time.sleep(2)
    
    print("\n✅ Computer Use should now be open in your browser!")
    print("\n" + "=" * 70)
    print("📋 COPY THIS TEST COMMAND:")
    print("=" * 70)
    
    test_command = """Please test the trading application:

1. Open Firefox browser
2. Go to http://host.docker.internal:5174
3. Find the Voice Assistant panel on the right
4. Click the message input field
5. Type: "Show me TSLA patterns"
6. Press Enter and tell me what you see"""
    
    print("\n" + test_command)
    
    print("\n" + "=" * 70)
    print("🎯 INSTRUCTIONS:")
    print("=" * 70)
    print("\n1. Look at your browser - Computer Use should be open")
    print("2. Find the chat input box on the LEFT side")
    print("3. PASTE the command above into the chat")
    print("4. Press ENTER to send it")
    print("5. WATCH the right panel - you'll see:")
    print("   • Firefox opening")
    print("   • Automatic navigation")
    print("   • Mouse clicking elements")
    print("   • Keyboard typing")
    print("\n⏱️  This will take about 30-45 seconds to complete")
    
    print("\n" + "=" * 70)
    print("💡 WHAT'S HAPPENING:")
    print("=" * 70)
    print("\n• Computer Use is an AI agent that can control a browser")
    print("• It will open Firefox in a virtual desktop")
    print("• It will navigate to your trading app")
    print("• It will interact with the Voice Assistant")
    print("• It will report back what it finds")
    
    print("\n🔗 If the browser didn't open, go to: http://localhost:8080")
    print("\n✨ The test is starting now - go paste the command!")

if __name__ == "__main__":
    open_computer_use_test()