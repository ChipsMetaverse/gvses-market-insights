import asyncio
import os
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()

async def search_for_openai_tools():
    """Use Anthropic's web search tool to find information about OpenAI's new agent tools"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found")
        return
    
    client = AsyncAnthropic(api_key=api_key)
    
    try:
        print("Using Anthropic's web search tool to find information about OpenAI's new agent tools...")
        
        response = await client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
            }],
            messages=[{
                "role": "user",
                "content": """Search for information about OpenAI's new tools for building agents announced in March 2025. 
                I need details about:
                1. The Responses API - what it does and how it works
                2. Web search capabilities for agents
                3. File search features
                4. Computer use functionality
                5. The new Agents SDK
                
                Please search for and summarize the key features and capabilities of these new tools."""
            }]
        )
        
        print("\n=== Search Results ===")
        if response.content:
            for content in response.content:
                if hasattr(content, 'text'):
                    print(content.text)
                else:
                    print(f"Content: {content}")
        
        # Check if tool use is required
        if response.stop_reason == 'tool_use':
            print("\nTool use requested - the model wants to perform a web search")
            # The API would handle the search internally
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(search_for_openai_tools())
