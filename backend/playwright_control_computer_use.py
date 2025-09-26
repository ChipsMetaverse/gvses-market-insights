#!/usr/bin/env python3
"""
Playwright Control for Computer Use
====================================
Uses Playwright to control the Computer Use interface and monitor its interactions
with the trading application.
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import time

async def control_computer_use():
    """Control Computer Use via Playwright to test the trading app."""
    
    print("=" * 60)
    print("PLAYWRIGHT COMPUTER USE CONTROLLER")
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
            await asyncio.sleep(3)
            
            # The Computer Use interface has a text input area for sending messages
            # Look for the Streamlit chat input
            # Wait longer for the page to fully load
            print("2. Waiting for interface to fully load...")
            await asyncio.sleep(5)
            
            print("3. Finding chat input area...")
            
            # The Computer Use interface combines Streamlit chat with desktop view
            # Try to find the chat input with various approaches
            chat_input = None
            
            # First, look for any text input or textarea elements
            try:
                # Try to find the chat input by looking for any textarea
                textareas = await page.query_selector_all('textarea')
                if textareas:
                    chat_input = textareas[0]  # Use the first textarea found
                    print(f"   Found {len(textareas)} textarea(s), using the first one")
                else:
                    # Try input fields
                    inputs = await page.query_selector_all('input[type="text"]')
                    if inputs:
                        chat_input = inputs[0]
                        print(f"   Found {len(inputs)} text input(s), using the first one")
            except Exception as e:
                print(f"   Could not find standard inputs: {e}")
            
            # If still no input found, try iframe approach (desktop view might be in iframe)
            if not chat_input:
                print("   Looking for embedded frames...")
                iframes = await page.query_selector_all('iframe')
                print(f"   Found {len(iframes)} iframe(s)")
            
            # Prepare the test command for Computer Use
            test_command = """Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load completely
4. Look for the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (it has placeholder text "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit the message
8. Wait for the response to appear
9. Report what information was provided about PLTR

Take your time and describe what you see at each step."""
            
            print("4. Sending test command to Computer Use...")
            print("   Command: Test Voice Assistant with PLTR query")
            
            if chat_input:
                # Type the command into the chat
                await chat_input.fill(test_command)
                
                # Submit the message (usually Enter key or a send button)
                await page.keyboard.press("Enter")
            else:
                # Fallback: try typing directly
                await page.keyboard.type(test_command)
                await page.keyboard.press("Enter")
            
            print("5. Command sent! Monitoring Computer Use actions...")
            print("   Computer Use will now:")
            print("   - Open Firefox in the virtual desktop")
            print("   - Navigate to the trading application")
            print("   - Interact with the Voice Assistant")
            print()
            
            # Monitor for responses and actions
            start_time = time.time()
            max_duration = 120  # 2 minutes max
            
            print("6. Monitoring activity (2 minutes max)...")
            print("-" * 40)
            
            while time.time() - start_time < max_duration:
                # Check for new messages in the chat
                messages = await page.query_selector_all('[data-testid="stChatMessage"]')
                
                # Also check the desktop view area for visual changes
                desktop_frame = await page.query_selector('iframe')
                
                # Log current status
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0:  # Log every 10 seconds
                    print(f"   [{elapsed}s] Monitoring... ({len(messages)} messages in chat)")
                
                # Small delay to not overwhelm
                await asyncio.sleep(2)
                
                # Check if Computer Use has completed the task
                # Look for completion indicators in the chat
                last_message_text = ""
                if messages and len(messages) > 0:
                    try:
                        last_message = messages[-1]
                        last_message_text = await last_message.inner_text()
                        
                        if any(phrase in last_message_text.lower() for phrase in [
                            "task complete", "successfully", "pltr", "price", 
                            "trading", "voice assistant"
                        ]):
                            print(f"\n   [ACTIVITY] New message detected:")
                            print(f"   {last_message_text[:200]}...")
                            
                            if "complete" in last_message_text.lower():
                                print("\n✅ Task appears to be complete!")
                                break
                    except:
                        pass
            
            print("-" * 40)
            print()
            
            # Take a screenshot of the final state
            print("7. Taking screenshot of final state...")
            screenshot_path = "computer_use_playwright_result.png"
            await page.screenshot(path=screenshot_path)
            print(f"   Screenshot saved to: {screenshot_path}")
            
            # Extract final messages for summary
            print("\n8. Extracting Computer Use responses...")
            all_messages = await page.query_selector_all('[data-testid="stChatMessage"]')
            
            if all_messages:
                print("\nComputer Use Activity Log:")
                print("=" * 40)
                for i, msg in enumerate(all_messages[-5:], 1):  # Last 5 messages
                    try:
                        text = await msg.inner_text()
                        # Clean up and truncate for display
                        text = text.strip()[:300]
                        print(f"\nMessage {i}:")
                        print(text)
                    except:
                        pass
                print("=" * 40)
            
            print("\n✅ Monitoring complete!")
            print("\nSummary:")
            print("- Computer Use interface controlled via Playwright")
            print("- Test command sent to interact with trading app")
            print("- Actions monitored for 2 minutes")
            print("- Screenshot captured of final state")
            
            # Keep browser open for manual inspection
            print("\n⏸️  Keeping browser open for 30 seconds for inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()
            print("\n🏁 Browser closed. Test complete.")

async def main():
    """Run the Computer Use controller."""
    await control_computer_use()

if __name__ == "__main__":
    print("Starting Playwright control of Computer Use...")
    print("Make sure Docker container is running: docker ps | grep computer-use")
    print()
    asyncio.run(main())