import asyncio
import base64
from anthropic import AsyncAnthropic
import os
from typing import Dict, Any

async def read_openai_article():
    """Use Computer Use to navigate to and read the OpenAI article"""
    
    # Initialize the client
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    try:
        print("Starting Computer Use to read OpenAI article...")
        
        # Take a screenshot first to see current state
        initial_screenshot = {
            "type": "computer_20241022",
            "action": "screenshot"
        }
        
        # Navigate to the URL
        navigate_action = {
            "type": "computer_20241022",
            "action": "screenshot"  # Start with screenshot to see current state
        }
        
        # Create the request
        response = await client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            tools=[{
                "type": "computer_20241022",
                "display_width_px": 1920,
                "display_height_px": 1080,
            }],
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Please help me read the OpenAI article at: https://openai.com/index/new-tools-for-building-agents/

1. First, take a screenshot to see the current state
2. Open a web browser if not already open
3. Navigate to the URL
4. Scroll through the article and extract the key information about:
   - The new Responses API
   - Web search capabilities
   - File search features
   - Computer use functionality
   - The Agents SDK
   - Any code examples or technical details

Please summarize the main points of the article."""
                    }
                ]
            }],
            system="You are helping to read and extract information from a web article about OpenAI's new tools for building agents."
        )
        
        # Print the response
        print("\n=== Computer Use Response ===")
        print(response.content[0].text if response.content else "No response")
        
        # If there are tool calls in the response, we might need to handle them
        if hasattr(response, 'stop_reason') and response.stop_reason == 'tool_use':
            print("\nTool use requested by the model")
            # In a real implementation, we'd handle the tool calls here
            
    except Exception as e:
        print(f"Error using Computer Use: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(read_openai_article())
