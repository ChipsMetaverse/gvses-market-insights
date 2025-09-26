#!/usr/bin/env python3
"""
Playwright Test for Computer Use - With Backend Fix
====================================================
Tests Computer Use after fixing the host.docker.internal backend connection.
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import time

async def test_computer_use_fixed():
    """Test Computer Use with the fixed backend connection."""
    
    print("=" * 60)
    print("TESTING COMPUTER USE WITH FIXED BACKEND")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # Launch browser to control Computer Use interface
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("1. Opening Computer Use interface...")
            await page.goto("http://localhost:8080")
            await page.wait_for_load_state("networkidle")
            
            # Wait for the interface to fully load
            print("2. Waiting for interface to fully load...")
            await asyncio.sleep(5)
            
            print("3. Looking for chat input...")
            
            # Try to find any input element we can type in
            chat_input = None
            
            # Method 1: Try to find textarea elements
            textareas = await page.query_selector_all('textarea')
            if textareas:
                print(f"   Found {len(textareas)} textarea(s)")
                chat_input = textareas[0]
                await chat_input.click()
                print("   Clicked on first textarea")
            else:
                # Method 2: Try text inputs
                inputs = await page.query_selector_all('input[type="text"]')
                if inputs:
                    print(f"   Found {len(inputs)} text input(s)")
                    chat_input = inputs[0]
                    await chat_input.click()
                    print("   Clicked on first text input")
                else:
                    # Method 3: Just click and type
                    print("   No standard inputs found, trying direct keyboard input")
                    await page.click('body')
            
            # The test command with refresh first
            test_command = """Please help me test the Voice Assistant after the backend fix:

1. First, refresh the current Firefox page (press F5 or Ctrl+R) to get the latest frontend updates
2. Wait for the trading application to fully reload
3. Navigate to http://host.docker.internal:5174 if not already there
4. Look for the Voice Assistant panel on the RIGHT side
5. Click on the text input field (placeholder: "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit
8. Wait for the response
9. Report what response you received and whether the API connection is working

Take your time and describe what you see at each step, especially any errors."""
            
            print("4. Sending test command with refresh instruction...")
            print("   This will refresh the page to get the backend fix")
            
            if chat_input:
                # Clear any existing text and type the command
                await chat_input.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")
                await chat_input.type(test_command)
                print("   Command typed in chat input")
            else:
                # Fallback: just type
                await page.keyboard.type(test_command)
                print("   Command typed directly")
            
            # Submit the message
            await page.keyboard.press("Enter")
            print("   Command sent!")
            
            print("\n5. Monitoring Computer Use actions...")
            print("   Computer Use will now:")
            print("   - Refresh the page to get backend fix")
            print("   - Navigate to trading application")
            print("   - Test Voice Assistant with PLTR query")
            print("   - Report if backend connection is working")
            print()
            
            # Monitor for 3 minutes to give Computer Use time
            start_time = time.time()
            max_duration = 180  # 3 minutes
            last_message_count = 0
            
            print("6. Monitoring activity (3 minutes max)...")
            print("-" * 40)
            
            while time.time() - start_time < max_duration:
                # Check for new messages
                messages = await page.query_selector_all('[data-testid="stChatMessage"]')
                current_count = len(messages) if messages else 0
                
                # Log progress
                elapsed = int(time.time() - start_time)
                
                # Check if new messages appeared
                if current_count > last_message_count:
                    print(f"\n   [{elapsed}s] NEW ACTIVITY! {current_count} messages (was {last_message_count})")
                    
                    # Try to get the last message
                    if messages:
                        try:
                            last_msg = await messages[-1].inner_text()
                            print(f"   Latest: {last_msg[:150]}...")
                            
                            # Check for completion indicators
                            if any(phrase in last_msg.lower() for phrase in [
                                "pltr", "price", "successful", "working", "response", 
                                "market", "trading", "complete", "error", "failed"
                            ]):
                                print(f"\n   🎯 Relevant response detected!")
                                
                                if "complete" in last_msg.lower() or "successful" in last_msg.lower():
                                    print("\n✅ Task appears successful!")
                                    break
                        except:
                            pass
                    
                    last_message_count = current_count
                elif elapsed % 15 == 0:  # Log every 15 seconds
                    print(f"   [{elapsed}s] Still monitoring... ({current_count} messages)")
                
                await asyncio.sleep(3)
            
            print("-" * 40)
            
            # Take final screenshot
            print("\n7. Taking final screenshot...")
            screenshot_path = "computer_use_backend_test_result.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"   Screenshot saved to: {screenshot_path}")
            
            # Extract and display final messages
            print("\n8. Final Computer Use Activity:")
            print("=" * 40)
            
            final_messages = await page.query_selector_all('[data-testid="stChatMessage"]')
            if final_messages:
                # Show last 3 messages
                for i, msg in enumerate(final_messages[-3:], 1):
                    try:
                        text = await msg.inner_text()
                        print(f"\nMessage {i}:")
                        print(text[:500])  # Show more content
                        print("...")
                    except:
                        pass
            else:
                print("No messages found in chat")
            
            print("=" * 40)
            
            # Check desktop view for visual confirmation
            print("\n9. Checking desktop view...")
            desktop_frame = await page.query_selector('iframe')
            if desktop_frame:
                print("   Desktop view iframe found - Computer Use has visual access")
            else:
                print("   No desktop iframe found")
            
            print("\n✅ Test Complete!")
            print("\nSummary:")
            print("- Test command sent with refresh instruction")
            print("- Monitored for 3 minutes")
            print("- Screenshot captured")
            print("- Check screenshot to see if backend connection worked")
            
            # Keep open briefly for inspection
            print("\n⏸️  Keeping browser open for 15 seconds...")
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()
            print("\n🏁 Browser closed.")

async def main():
    """Run the test."""
    await test_computer_use_fixed()

if __name__ == "__main__":
    print("Starting Computer Use test with backend fix...")
    print("This will test if the Voice Assistant now works correctly")
    print()
    asyncio.run(main())