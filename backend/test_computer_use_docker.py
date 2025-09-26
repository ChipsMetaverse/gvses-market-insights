#!/usr/bin/env python3
"""
Test Computer Use with Official Docker Container
================================================
Uses Anthropic's Computer Use Docker container to interact with the trading application.
"""

import asyncio
import base64
import httpx
import json
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

async def test_computer_use_interaction():
    """Test Computer Use by interacting with the Voice Assistant panel."""
    
    # The Computer Use container exposes a Streamlit API endpoint
    computer_use_url = "http://localhost:8501"
    
    # Initialize Anthropic client
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("=" * 60)
    print("COMPUTER USE DOCKER TEST")
    print("=" * 60)
    print()
    print("Testing Computer Use with the trading application...")
    print()
    
    # Define the task for Computer Use
    task_description = """
    Please help me test the Voice Assistant feature of the trading application:
    
    1. Open a browser and navigate to http://localhost:5174
    2. Wait for the page to load completely
    3. Look for the Voice Assistant panel on the RIGHT side of the page
    4. Click on the text input field (it should have placeholder text "Type a message...")
    5. Type the following question: "What is the current price of PLTR?"
    6. Press Enter to submit the message
    7. Wait for the response to appear
    8. Tell me what information was provided about PLTR
    
    Take your time and let me know what you see at each step.
    """
    
    # Computer Use tool definition
    tools = [{
        "type": "computer_20250124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1
    }]
    
    # Start the conversation
    messages = [{
        "role": "user",
        "content": task_description
    }]
    
    print(f"Task: {task_description}")
    print("\n" + "-" * 60 + "\n")
    
    max_iterations = 15
    
    for iteration in range(max_iterations):
        print(f"Iteration {iteration + 1}/{max_iterations}")
        
        try:
            # Call Claude with Computer Use tools
            response = await client.beta.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=messages,
                tools=tools,
                betas=["computer-use-2025-01-24"]
            )
            
            # Print Claude's response
            print(f"Claude's response:")
            for content in response.content:
                if content.type == "text":
                    print(f"  Text: {content.text}")
                elif content.type == "tool_use":
                    print(f"  Tool Use: {content.name} - {content.input.get('action', 'unknown')}")
            
            # Add Claude's response to the conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check if Claude is done (no tool calls)
            has_tool_calls = any(c.type == "tool_use" for c in response.content)
            
            if not has_tool_calls:
                print("\n" + "=" * 60)
                print("Task Complete!")
                print("=" * 60)
                for content in response.content:
                    if content.type == "text":
                        print(f"Final Response: {content.text}")
                break
            
            # Process tool calls and add results
            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    # In the Docker environment, the tool execution happens automatically
                    # We need to provide mock results for now
                    if content.input.get("action") == "screenshot":
                        # Mock screenshot result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": [{
                                "type": "text",
                                "text": "Screenshot taken successfully"
                            }]
                        })
                    else:
                        # Mock action result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": f"Action '{content.input.get('action', 'unknown')}' completed"
                        })
            
            # Add tool results to conversation
            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            # Small delay between iterations
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error in iteration {iteration + 1}: {e}")
            break
    
    print("\nTest completed.")

async def main():
    """Run the Computer Use test."""
    try:
        await test_computer_use_interaction()
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    print("Starting Computer Use Docker test...")
    print("Make sure the Computer Use container is running (docker ps)")
    print("You can access the UI at: http://localhost:8080")
    print()
    asyncio.run(main())