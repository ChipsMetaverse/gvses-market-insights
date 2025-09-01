"""
openai_agent.py - OpenAI function calling with GPT-4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses OpenAI v1 API for function calling with real market data tools.
Configured with G'sves persona for consistent market analysis.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from . import tools

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# G'sves system prompt - matching your ElevenLabs agent personality
SYSTEM_PROMPT = """You are G'sves, a distinguished senior market analyst with over 30 years of experience 
in global financial markets. You have a refined British demeanor, combining expertise with approachability.

Your expertise spans:
- Technical analysis and chart patterns
- Fundamental analysis and valuation
- Market psychology and sentiment
- Risk management strategies
- Options and derivatives

Communication style:
- Professional yet conversational
- Use precise numbers (e.g., "one hundred eleven thousand" not "about 111k")
- Reference specific data timestamps
- Provide confidence levels (high/medium/low) based on data availability

CRITICAL RULES:
1. ALWAYS use tools to fetch real-time data - never guess or use training data
2. Bitcoin should be around $100,000+ (2025 market) if mentioned
3. Include current price when discussing any symbol
4. Format responses for voice: clear numbers, no URLs
5. Use bullet points for clarity when listing multiple items

Response structure:
- Start with the most important data point (usually current price)
- Follow with supporting analysis
- End with actionable insights or recommendations"""

async def call_openai_agent(
    user_query: str, 
    model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Execute OpenAI agent with function calling for market analysis.
    
    Args:
        user_query: Natural language question from user
        model: OpenAI model to use (gpt-4o, gpt-4, gpt-3.5-turbo)
        temperature: Response creativity (0-1)
    
    Returns:
        Final answer incorporating real market data
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    # Available tools for function calling
    available_tools = [
        {
            "type": "function",
            "function": schema
        } for schema in tools.FUNCTION_SCHEMAS
    ]
    
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            # Call OpenAI with function calling
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=available_tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message.model_dump())
            
            # Check if the assistant wants to call functions
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the function
                    function_to_call = getattr(tools, function_name, None)
                    if function_to_call:
                        try:
                            result = await function_to_call(**function_args)
                            # Add function result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result)
                            })
                        except Exception as e:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": str(e)})
                            })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": f"Function {function_name} not found"})
                        })
            else:
                # No more function calls, return the response
                return assistant_message.content or "I couldn't generate a response."
                
        except Exception as e:
            return f"Error processing your request: {str(e)}"
    
    return "I've gathered the data but need more time to formulate a complete response."

async def main():
    """Interactive CLI for testing the agent."""
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        answer = await call_openai_agent(query)
        print(answer)
    else:
        # Interactive mode
        print("G'sves Market Insights (OpenAI Mode)")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ["exit", "quit"]:
                    print("Cheerio! Happy trading!")
                    break
                if query:
                    print("G'sves: ", end="", flush=True)
                    answer = await call_openai_agent(query)
                    print(answer + "\n")
            except KeyboardInterrupt:
                print("\nCheerio!")
                break
            except Exception as e:
                print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())