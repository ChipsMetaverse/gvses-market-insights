import asyncio
import os
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()

async def read_article_with_computer_use():
    """Use Computer Use API to read the OpenAI article"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment")
        return
    
    print(f"Using API key: {api_key[:10]}...")
    
    client = AsyncAnthropic(api_key=api_key)
    
    try:
        print("Sending request to Computer Use API...")
        
        response = await client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[{
                "type": "computer_20241022",
                "display_width_px": 1920,
                "display_height_px": 1080,
            }],
            messages=[{
                "role": "user",
                "content": "Take a screenshot of the current screen."
            }]
        )
        
        print("\n=== Response ===")
        if response.content:
            for content in response.content:
                if hasattr(content, 'text'):
                    print(content.text)
                elif hasattr(content, 'type'):
                    print(f"Content type: {content.type}")
        
        # Check if we need to handle tool use
        if response.stop_reason == 'tool_use':
            print("\nThe model wants to use computer tools.")
            # In production, we'd need to actually execute the computer use commands
            # and send the results back to the API
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(read_article_with_computer_use())
