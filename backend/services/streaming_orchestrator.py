"""
Streaming Agent Orchestrator
============================
Implements TRUE streaming with OpenAI's new response format.
Progressive tool execution and immediate content streaming.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
from openai import AsyncOpenAI
from services.market_service_factory import MarketServiceFactory
from response_formatter import MarketResponseFormatter

logger = logging.getLogger(__name__)

class StreamingOrchestrator:
    """
    Enhanced orchestrator with true streaming capabilities.
    Implements OpenAI's new response format best practices.
    """
    
    def __init__(self, client: AsyncOpenAI, market_service):
        self.client = client
        self.market_service = market_service
        self.model = "gpt-4o"
        self.temperature = 0.7
    
    async def stream_with_tools(
        self,
        messages: List[Dict],
        tools: List[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response with progressive tool execution.
        
        This implementation:
        1. Starts streaming content immediately
        2. Executes tools in parallel as detected
        3. Interleaves content and tool results
        4. Provides real-time updates to frontend
        """
        
        # Create the streaming response
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=self.temperature,
            stream=True,
            max_tokens=4000
        )
        
        # Track state
        accumulated_content = []
        tool_calls = {}
        current_tool_id = None
        tool_execution_tasks = []
        
        # Process stream chunks
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue
            
            # 1. Stream content immediately as it arrives
            if delta.content:
                accumulated_content.append(delta.content)
                yield {
                    "type": "content",
                    "text": delta.content,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # 2. Handle tool calls progressively
            if delta.tool_calls:
                for tool_call_delta in delta.tool_calls:
                    # New tool call starting
                    if tool_call_delta.id:
                        current_tool_id = tool_call_delta.id
                        tool_calls[current_tool_id] = {
                            "id": tool_call_delta.id,
                            "name": "",
                            "arguments": "",
                            "started": False
                        }
                    
                    # Accumulate tool name
                    if current_tool_id and tool_call_delta.function:
                        if tool_call_delta.function.name:
                            tool_calls[current_tool_id]["name"] = tool_call_delta.function.name
                        
                        # Accumulate arguments
                        if tool_call_delta.function.arguments:
                            tool_calls[current_tool_id]["arguments"] += tool_call_delta.function.arguments
                            
                            # Try to parse and execute as soon as we have complete arguments
                            try:
                                args = json.loads(tool_calls[current_tool_id]["arguments"])
                                tool_name = tool_calls[current_tool_id]["name"]
                                
                                if tool_name and not tool_calls[current_tool_id]["started"]:
                                    tool_calls[current_tool_id]["started"] = True
                                    
                                    # Start tool execution immediately
                                    yield {
                                        "type": "tool_start",
                                        "tool": tool_name,
                                        "arguments": args
                                    }
                                    
                                    # Execute tool in background
                                    task = asyncio.create_task(
                                        self._execute_tool_async(tool_name, args)
                                    )
                                    tool_execution_tasks.append((tool_name, task))
                                    
                            except json.JSONDecodeError:
                                # Arguments not complete yet
                                pass
        
        # 3. Stream tool results as they complete (non-blocking)
        if tool_execution_tasks:
            # Process completed tools as they finish
            for tool_name, task in tool_execution_tasks:
                try:
                    result = await task
                    yield {
                        "type": "tool_complete",
                        "tool": tool_name,
                        "result": result,
                        "success": True
                    }
                except Exception as e:
                    logger.error(f"Tool {tool_name} failed: {e}")
                    yield {
                        "type": "tool_complete",
                        "tool": tool_name,
                        "error": str(e),
                        "success": False
                    }
        
        # 4. Send completion signal
        yield {
            "type": "stream_complete",
            "content_length": len("".join(accumulated_content)),
            "tools_executed": len(tool_execution_tasks)
        }
    
    async def _execute_tool_async(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Execute a tool asynchronously with timeout.
        """
        timeout_map = {
            "get_stock_price": 2.0,
            "get_stock_history": 3.0,
            "get_stock_news": 4.0,
            "get_comprehensive_stock_data": 5.0,
            "get_market_overview": 3.0
        }
        
        timeout = timeout_map.get(tool_name, 5.0)
        
        try:
            # Map tool names to market service methods
            method_map = {
                "get_stock_price": lambda args: self.market_service.get_stock_price(args["symbol"]),
                "get_stock_history": lambda args: self.market_service.get_stock_history(
                    args["symbol"], args.get("days", 30)
                ),
                "get_stock_news": lambda args: self.market_service.get_stock_news(
                    args["symbol"], args.get("limit", 5)
                ),
                "get_comprehensive_stock_data": lambda args: self.market_service.get_comprehensive_stock_data(
                    args["symbol"]
                ),
                "get_market_overview": lambda args: self.market_service.get_market_overview()
            }
            
            if tool_name in method_map:
                result = await asyncio.wait_for(
                    method_map[tool_name](arguments),
                    timeout=timeout
                )
                return result
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except asyncio.TimeoutError:
            logger.warning(f"Tool {tool_name} timed out after {timeout}s")
            return {"error": f"Tool timed out after {timeout}s"}
        except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}")
            return {"error": str(e)}
    
    async def process_query_streaming(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a query with full streaming support.
        """
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        messages.append({"role": "user", "content": query})
        
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_price",
                    "description": "Get real-time stock price",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock ticker symbol"}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_news",
                    "description": "Get latest news for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "limit": {"type": "integer", "default": 5}
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_comprehensive_stock_data",
                    "description": "Get comprehensive stock analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"}
                        },
                        "required": ["symbol"]
                    }
                }
            }
        ]
        
        # Stream with tools
        async for chunk in self.stream_with_tools(messages, tools):
            yield chunk