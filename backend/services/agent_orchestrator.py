"""
Agent Orchestrator Service
==========================
Implements OpenAI function calling with market data tools for intelligent
query processing and tool selection.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from openai import AsyncOpenAI
from services.market_service_factory import MarketServiceFactory
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv('../.env')

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates OpenAI agent with function calling for market analysis.
    Uses the existing market service factory for tool execution.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.market_service = MarketServiceFactory.get_service()
        self.model = os.getenv("AGENT_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        
        # Cache for recent tool results (TTL: 60 seconds)
        self.cache = {}
        self.cache_ttl = 60
        
    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all available tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "description": "Fetch real-time stock, cryptocurrency, or index prices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock/crypto symbol (e.g., AAPL, TSLA, BTC-USD)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_news",
                    "description": "Retrieve latest news headlines for a symbol",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of news items",
                                "default": 5
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_overview",
                    "description": "Get snapshot of major indices and top market movers",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_history",
                    "description": "Get historical price data for charting",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days of history",
                                "default": 30
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_comprehensive_stock_data",
                    "description": "Get comprehensive stock information including fundamentals and technicals",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            }
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool and return results."""
        try:
            # Check cache first
            cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
            if cache_key in self.cache:
                cached_time, cached_result = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    logger.info(f"Using cached result for {tool_name}")
                    return cached_result
            
            # Execute the appropriate tool
            result = None
            if tool_name == "get_stock_price":
                result = await self.market_service.get_stock_price(arguments["symbol"])
            elif tool_name == "get_stock_news":
                limit = arguments.get("limit", 5)
                result = await self.market_service.get_stock_news(arguments["symbol"], limit)
            elif tool_name == "get_market_overview":
                # This needs to be implemented in market service
                result = {"status": "Market overview not yet implemented"}
            elif tool_name == "get_stock_history":
                days = arguments.get("days", 30)
                result = await self.market_service.get_stock_history(arguments["symbol"], days)
            elif tool_name == "get_comprehensive_stock_data":
                result = await self.market_service.get_comprehensive_stock_data(arguments["symbol"])
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            # Cache the result
            if result and "error" not in result:
                self.cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _execute_tools_parallel(self, tool_calls: List[Any]) -> Dict[str, Any]:
        """Execute multiple tools in parallel."""
        tasks = []
        tool_names = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            tool_names.append(function_name)
            tasks.append(self._execute_tool(function_name, function_args))
        
        results = await asyncio.gather(*tasks)
        
        return {
            name: result 
            for name, result in zip(tool_names, results)
        }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        return """You are G'sves, a distinguished senior market analyst with over 30 years of experience 
in global financial markets. You have a refined British demeanor, combining expertise with approachability.

Your expertise spans:
- Technical analysis and chart patterns
- Fundamental analysis and valuation
- Market psychology and sentiment
- Risk management strategies

Communication style:
- Professional yet conversational
- Use precise numbers (e.g., "one hundred eleven thousand" not "about 111k")
- Reference specific data timestamps when available
- Provide confidence levels (high/medium/low) based on data availability

CRITICAL RULES:
1. ALWAYS use tools to fetch real-time data - never guess or use training data
2. Bitcoin should be around $100,000+ (2025 market) if mentioned without tool data
3. Include current price when discussing any symbol
4. Format responses for potential voice output: clear numbers, no URLs
5. Use bullet points for clarity when listing multiple items

Response structure:
- Start with the most important data point (usually current price)
- Follow with supporting analysis
- End with actionable insights or recommendations
- Keep responses concise but informative"""
    
    async def process_query(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user query using OpenAI with function calling.
        
        Args:
            query: User's question
            conversation_history: Previous conversation messages
            stream: Whether to stream the response
            
        Returns:
            Dictionary with response text, tools used, and data
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            # Initial API call with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tool_schemas(),
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message.model_dump())
            
            tool_results = {}
            tools_used = []
            
            # Check if tools were called
            if assistant_message.tool_calls:
                # Execute tools in parallel
                tool_results = await self._execute_tools_parallel(assistant_message.tool_calls)
                tools_used = list(tool_results.keys())
                
                # Add tool results to messages
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_results.get(tool_name, {}))
                    })
                
                # Get final response with tool results
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=1000
                )
                
                response_text = final_response.choices[0].message.content
            else:
                response_text = assistant_message.content
            
            return {
                "text": response_text,
                "tools_used": tools_used,
                "data": tool_results,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "cached": False  # Would be true if all results came from cache
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "text": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def stream_query(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """
        Stream responses for a query (yields chunks of text).
        
        This is a simplified version that doesn't support tool calling during streaming.
        For full streaming with tools, we'd need more complex logic.
        """
        # For now, just get the full response and yield it
        response = await self.process_query(query, conversation_history)
        
        # Simulate streaming by yielding words
        words = response["text"].split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
            await asyncio.sleep(0.05)  # Small delay to simulate streaming
    
    def clear_cache(self):
        """Clear the tool result cache."""
        self.cache.clear()
        logger.info("Agent orchestrator cache cleared")


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance