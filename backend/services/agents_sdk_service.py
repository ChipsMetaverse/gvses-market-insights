"""
Agents SDK Service
==================
Integration service for OpenAI Agents SDK workflow logic.
Translates the Agent Builder workflow into Python implementation.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentQuery(BaseModel):
    """Input query model matching the frontend format"""
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class AgentResponse(BaseModel):
    """Response model matching existing agent orchestrator format"""
    text: str
    tools_used: List[str] = []
    data: Dict[str, Any] = {}
    timestamp: str
    model: str = "agents-sdk"
    cached: bool = False
    session_id: Optional[str] = None
    chart_commands: Optional[List[str]] = []

class IntentClassificationResult(BaseModel):
    """Intent classification result from Agent Builder workflow"""
    intent: str
    confidence: float
    reasoning: str

class AgentsSDKService:
    """
    Service that implements the Agent Builder workflow logic using OpenAI Agents SDK patterns.
    Replicates the conditional logic, intent classification, and tool routing.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.mcp_server_url = "https://gvses-mcp-sse-server.fly.dev/sse"
        self.model = "gpt-4o"  # Use GPT-4 for intelligence layer
        
        # Initialize HTTP client for MCP tool calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Available MCP tools from the Agent Builder configuration
        self.available_tools = [
            "get_stock_quote", "get_stock_history", "get_stock_news",
            "get_market_overview", "get_market_movers", "search_symbol",
            "get_cnbc_movers", "get_market_sentiment", "change_chart_symbol",
            "set_chart_timeframe", "toggle_chart_indicator", "capture_chart_snapshot"
        ]
        
        logger.info(f"🤖 Agents SDK Service initialized with {len(self.available_tools)} available tools")

    async def run_workflow(self, agent_query: AgentQuery) -> AgentResponse:
        """
        Main workflow execution following Agent Builder logic:
        1. Intent Classification
        2. Conditional Routing (Educational vs Market Data vs Chart Commands)
        3. Tool Execution
        4. Response Generation
        """
        try:
            logger.info(f"🚀 [AGENTS SDK] Starting workflow for query: {agent_query.query[:100]}...")
            
            # Check for "Good morning" greeting first (as per idealagent.md)
            if self._is_good_morning_greeting(agent_query.query):
                logger.info(f"☀️ [AGENTS SDK] Good morning greeting detected - generating market brief")
                response = await self._generate_market_brief(agent_query)
            else:
                # Step 1: Intent Classification
                intent_result = await self._classify_intent(agent_query.query, agent_query.conversation_history)
                logger.info(f"🎯 [AGENTS SDK] Classified intent: {intent_result.intent} (confidence: {intent_result.confidence})")
                
                # Step 2: Conditional Routing based on intent
                if intent_result.intent == "educational":
                    response = await self._handle_educational_query(agent_query, intent_result)
                elif intent_result.intent in ["market_data", "chart_command"]:
                    response = await self._handle_market_data_query(agent_query, intent_result)
                else:
                    # Default fallback
                    response = await self._handle_general_query(agent_query, intent_result)
            
            # Step 3: Add metadata
            response.timestamp = datetime.now().isoformat()
            response.session_id = agent_query.session_id
            response.data["intent"] = intent_result.intent
            response.data["confidence"] = intent_result.confidence
            response.data["reasoning"] = intent_result.reasoning
            
            logger.info(f"✅ [AGENTS SDK] Workflow completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ [AGENTS SDK] Workflow failed: {str(e)}")
            # Return fallback response
            return AgentResponse(
                text=f"I apologize, but I encountered an error processing your request. Please try again.",
                tools_used=[],
                data={"error": str(e), "fallback": True},
                timestamp=datetime.now().isoformat(),
                session_id=agent_query.session_id
            )

    async def _classify_intent(self, query: str, conversation_history: List[Dict[str, str]]) -> IntentClassificationResult:
        """
        Intent Classification step from Agent Builder workflow.
        Classifies user query into educational, market_data, chart_command, or general.
        """
        
        # Build conversation context
        context_messages = []
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            context_messages.append(f"{msg['role']}: {msg['content']}")
        
        context = "\n".join(context_messages) if context_messages else "No previous context"
        
        # Intent classification prompt (based on Agent Builder configuration)
        system_prompt = """You are an intent classifier for a voice-enabled trading assistant. 

Classify the user's query into one of these intents:
- "educational": General trading/finance education, explanations, learning questions
- "market_data": Requests for stock prices, market data, news, analysis  
- "chart_command": Commands to modify charts (change symbol, timeframe, indicators)
- "general": Other queries that don't fit the above categories

Consider the conversation context and respond with JSON containing:
- intent: one of the four categories above
- confidence: float between 0.0 and 1.0
- reasoning: brief explanation of classification

Examples:
- "What is a moving average?" → educational
- "Show me Tesla's stock price" → market_data  
- "Switch the chart to 4-hour timeframe" → chart_command
- "How are you doing today?" → general"""

        try:
            # Use OpenAI API directly for intent classification
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Conversation context:\n{context}\n\nCurrent query: {query}"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }
            
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = json.loads(result["choices"][0]["message"]["content"])
                
                return IntentClassificationResult(
                    intent=content.get("intent", "general"),
                    confidence=content.get("confidence", 0.5),
                    reasoning=content.get("reasoning", "Intent classification completed")
                )
            else:
                logger.error(f"Intent classification API error: {response.status_code}")
                # Fallback intent classification
                return IntentClassificationResult(
                    intent="general",
                    confidence=0.3,
                    reasoning="API error, using fallback classification"
                )
                
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return IntentClassificationResult(
                intent="general", 
                confidence=0.2,
                reasoning=f"Classification error: {str(e)}"
            )

    async def _handle_educational_query(self, agent_query: AgentQuery, intent_result: IntentClassificationResult) -> AgentResponse:
        """Handle educational queries - explanations, learning content"""
        
        system_prompt = """You are GVSES AI, a professional trading and market analysis assistant. 
        
The user has asked an educational question about trading, finance, or markets. Provide a clear, accurate, and helpful educational response. Focus on:
- Clear explanations of concepts
- Practical examples when relevant  
- Professional trading terminology
- Risk awareness and responsible trading

Be conversational but authoritative. Keep responses concise but comprehensive."""

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            # Build conversation context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in agent_query.conversation_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current query
            messages.append({"role": "user", "content": agent_query.query})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result["choices"][0]["message"]["content"]
                
                return AgentResponse(
                    text=response_text,
                    tools_used=["educational_response"],
                    data={"category": "educational", "approach": "direct_explanation"},
                    timestamp=datetime.now().isoformat()
                )
            else:
                logger.error(f"Educational query API error: {response.status_code}")
                return AgentResponse(
                    text="I'd be happy to help explain that concept. Could you please rephrase your question?",
                    tools_used=[],
                    data={"error": "api_error", "fallback": True},
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Educational query processing failed: {str(e)}")
            return AgentResponse(
                text="I apologize, but I'm having trouble processing your educational question right now. Please try again.",
                tools_used=[],
                data={"error": str(e), "fallback": True},
                timestamp=datetime.now().isoformat()
            )

    async def _handle_market_data_query(self, agent_query: AgentQuery, intent_result: IntentClassificationResult) -> AgentResponse:
        """Handle market data queries - stock prices, news, analysis, chart commands"""
        
        # This is where we would call MCP tools
        # For now, implementing a simplified version that calls the existing MCP endpoint
        
        try:
            logger.info(f"🔍 [AGENTS SDK] Processing market data query: '{agent_query.query}'")
            logger.info(f"📊 [AGENTS SDK] Intent confidence: {intent_result.confidence}")
            
            # Parse query for potential chart commands
            chart_commands = self._extract_chart_commands(agent_query.query)
            logger.info(f"📈 [AGENTS SDK] Extracted chart commands: {chart_commands}")
            
            # Call existing MCP endpoint for market data
            logger.info(f"🌐 [AGENTS SDK] Calling MCP orchestrator for market data...")
            mcp_response = await self._call_existing_mcp_orchestrator(agent_query)
            logger.info(f"📤 [AGENTS SDK] MCP response received: {type(mcp_response)} with keys: {list(mcp_response.keys()) if isinstance(mcp_response, dict) else 'not dict'}")
            
            # Log response details
            response_text = mcp_response.get("text", "I retrieved the market data you requested.")
            tools_used = mcp_response.get("tools_used", ["market_data_fetch"])
            response_data = mcp_response.get("data", {})
            
            logger.info(f"💬 [AGENTS SDK] Response text length: {len(response_text)}")
            logger.info(f"🔧 [AGENTS SDK] Tools used: {tools_used}")
            logger.info(f"📋 [AGENTS SDK] Response data keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'not dict'}")
            
            final_response = AgentResponse(
                text=response_text,
                tools_used=tools_used,
                data=response_data,
                chart_commands=chart_commands,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"✅ [AGENTS SDK] Market data response prepared successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"Market data query processing failed: {str(e)}")
            return AgentResponse(
                text="I apologize, but I'm having trouble retrieving that market data right now. Please try again.",
                tools_used=[],
                data={"error": str(e), "fallback": True},
                timestamp=datetime.now().isoformat()
            )

    async def _handle_general_query(self, agent_query: AgentQuery, intent_result: IntentClassificationResult) -> AgentResponse:
        """Handle general queries that don't fit other categories"""
        
        system_prompt = """You are GVSES AI, a professional trading assistant. The user has asked a general question that doesn't directly relate to market data or trading education. Respond helpfully while staying focused on your role as a trading assistant. If the query is completely off-topic, politely redirect the conversation back to trading and markets."""

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": agent_query.query}
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 300
            }
            
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result["choices"][0]["message"]["content"]
                
                return AgentResponse(
                    text=response_text,
                    tools_used=["general_response"],
                    data={"category": "general", "approach": "conversational"},
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AgentResponse(
                    text="I'm here to help with trading and market questions. How can I assist you with your investments today?",
                    tools_used=[],
                    data={"fallback": True},
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"General query processing failed: {str(e)}")
            return AgentResponse(
                text="I'm here to help with trading and market analysis. What would you like to know?",
                tools_used=[],
                data={"error": str(e), "fallback": True},
                timestamp=datetime.now().isoformat()
            )

    def _extract_chart_commands(self, query: str) -> List[str]:
        """Extract chart commands from query text (simplified implementation)"""
        commands = []
        query_lower = query.lower()
        
        # Simple pattern matching for chart commands
        if any(phrase in query_lower for phrase in ["show", "display", "load", "switch to"]):
            # Look for symbol patterns
            import re
            symbol_pattern = r'\b[A-Z]{1,5}\b'
            matches = re.findall(symbol_pattern, query.upper())
            if matches:
                commands.append(f"LOAD:{matches[0]}")
        
        if any(phrase in query_lower for phrase in ["timeframe", "time frame", "1h", "4h", "1d", "1w"]):
            if "1h" in query_lower or "hour" in query_lower:
                commands.append("TIMEFRAME:1h")
            elif "4h" in query_lower:
                commands.append("TIMEFRAME:4h") 
            elif "1d" in query_lower or "day" in query_lower:
                commands.append("TIMEFRAME:1D")
            elif "1w" in query_lower or "week" in query_lower:
                commands.append("TIMEFRAME:1W")
        
        return commands

    async def _call_existing_mcp_orchestrator(self, agent_query: AgentQuery) -> Dict[str, Any]:
        """Execute MCP tools directly using Agent SDK patterns instead of delegating to regular orchestrator"""
        
        try:
            logger.info(f"🛠️ [AGENTS SDK] Executing MCP tools directly for query: {agent_query.query}")
            
            # Parse the query to determine which MCP tools to call
            symbol = self._extract_symbol_from_query(agent_query.query)
            logger.info(f"📊 [AGENTS SDK] Extracted symbol: {symbol}")
            
            if symbol:
                # Call MCP tool directly for stock quote
                stock_data = await self._call_mcp_tool_directly("get_stock_quote", {"symbol": symbol})
                logger.info(f"💰 [AGENTS SDK] Stock data retrieved: {type(stock_data)}")
                
                # Also fetch historical data for BTD calculations
                historical_data = await self._call_mcp_tool_directly("get_stock_history", {"symbol": symbol})
                logger.info(f"📈 [AGENTS SDK] Historical data retrieved for BTD calculations")
                
                if not historical_data:
                    logger.warning(f"⚠️ [AGENTS SDK] No historical data returned for {symbol}")
                    historical_data = {}
                
                # Calculate BTD levels
                btd_levels = await self._calculate_btd_levels(symbol, stock_data, historical_data)
                logger.info(f"🎯 [AGENTS SDK] BTD levels calculated: {btd_levels}")
                
                if stock_data and stock_data.get("symbol"):
                    # Generate AI response using the stock data and BTD levels
                    ai_response = await self._generate_ai_response_with_btd(agent_query.query, stock_data, btd_levels, symbol)
                    
                    return {
                        "text": ai_response,
                        "tools_used": ["get_stock_quote", "get_stock_history", "btd_calculation", "ai_analysis"],
                        "data": {
                            "symbol": symbol,
                            "price": stock_data.get("price", 0),
                            "change": stock_data.get("change_abs", 0),
                            "change_percent": stock_data.get("change_pct", 0),
                            "btd_levels": btd_levels,
                            "stock_data": stock_data,
                            "mcp_direct": True
                        }
                    }
                else:
                    logger.warning(f"⚠️ [AGENTS SDK] No valid stock data returned for {symbol}")
            
            # Fallback: generate general response
            logger.info(f"🔄 [AGENTS SDK] Using fallback response generation")
            fallback_text = f"I processed your query about {symbol if symbol else 'the market'}. The market data system is available for analysis."
            
            return {
                "text": fallback_text,
                "tools_used": ["agent_sdk_analysis"],
                "data": {"fallback": True, "query": agent_query.query, "symbol": symbol}
            }
                
        except Exception as e:
            logger.error(f"❌ [AGENTS SDK] MCP tool execution failed: {str(e)}")
            return {
                "text": f"I encountered an issue processing your market query. Please try again.",
                "tools_used": ["error_handler"],
                "data": {"error": str(e), "fallback": True}
            }

    def _extract_symbol_from_query(self, query: str) -> str:
        """Extract stock symbol from user query with improved context awareness"""
        query_upper = query.upper()
        
        # Check if query is about market scanning or general queries - no symbol needed
        scan_keywords = ["SCAN", "MARKET", "OPPORTUNITIES", "TRADING PLAN", "WHICH STOCKS", "BEST STOCKS", "TOP STOCKS", "GOOD MORNING"]
        if any(keyword in query_upper for keyword in scan_keywords):
            # Unless there's an explicit symbol mentioned after these keywords
            import re
            # Look for patterns like "scan AAPL" or "market for TSLA"
            specific_symbol_pattern = re.search(r'(?:FOR|OF|ABOUT|SHOW ME|SHOW|GET|PULL UP)\s+([A-Z]{1,5})\b', query_upper)
            if not specific_symbol_pattern:
                return None
        
        # Common company name to symbol mapping (check these first)
        company_mappings = {
            "APPLE": "AAPL",
            "TESLA": "TSLA", 
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "NVIDIA": "NVDA",
            "META": "META",
            "FACEBOOK": "META",
            "AMAZON": "AMZN",
            "PALANTIR": "PLTR",
            "BERKSHIRE": "BRK.B"
        }
        
        for company, symbol in company_mappings.items():
            if company in query_upper:
                return symbol
        
        # Check for explicit ticker symbols mentioned
        # Look for patterns like "AAPL", "ticker AAPL", "$AAPL", etc.
        import re
        
        # Pattern 1: $ followed by symbol (e.g., $AAPL)
        dollar_pattern = re.search(r'\$([A-Z]{1,5})\b', query_upper)
        if dollar_pattern:
            return dollar_pattern.group(1)
        
        # Pattern 2: Known stock indices
        if any(pattern in query_upper for pattern in ["SPY", "S&P", "SPX", "S&P 500"]):
            return "SPY"
        if "QQQ" in query_upper or "NASDAQ" in query_upper:
            return "QQQ"
        if "DIA" in query_upper or "DOW" in query_upper:
            return "DIA"
        
        # Pattern 3: Look for standalone uppercase words that are likely symbols
        # but only if they appear in certain contexts
        symbol_contexts = [
            r'(?:BTD|BUY LOW|SELL HIGH|LEVELS?|PRICES?)\s+(?:FOR|OF)\s+([A-Z]{1,5})\b',  # BTD/Buy Low/Sell High for AAPL (prioritize this)
            r'\b([A-Z]{1,5})\s+(?:STOCK|PRICE|QUOTE|CHART)',  # AAPL stock, TSLA price
            r'(?:STOCK|PRICE|QUOTE|CHART)\s+(?:FOR|OF)\s+([A-Z]{1,5})\b',  # price of AAPL
            r'(?:SHOW ME|SHOW|GET|PULL UP|DISPLAY|WHAT IS)\s+([A-Z]{1,5})(?:\s+WITH|\s+INCLUDING|$)',  # show AAPL or show AAPL with...
            r'\b([A-Z]{1,5})\s+(?:IS|TRADING|AT|UP|DOWN)',  # AAPL is trading
            r'(?:BUY|SELL|LONG|SHORT)\s+([A-Z]{1,5})\b',  # buy AAPL
        ]
        
        for pattern in symbol_contexts:
            match = re.search(pattern, query_upper)
            if match:
                potential_symbol = match.group(1)
                # Exclude common words that might match but aren't symbols
                exclude_words = {"THE", "FOR", "AND", "BUT", "CAN", "WILL", "SHOW", "GET", "WHAT", 
                               "WHERE", "WHEN", "WHO", "HOW", "WHICH", "SCAN", "NEAR", "LOAD", 
                               "GOOD", "BEST", "TOP", "ALL", "ANY", "SOME", "MORE", "LESS", "BTD",
                               "HIGH", "LOW", "BUY", "SELL", "WITH", "INCLUDING"}
                if potential_symbol not in exclude_words:
                    return potential_symbol
        
        # Pattern 4: If query is just a ticker symbol by itself (e.g., "AAPL" or "aapl")
        query_stripped = query.strip()
        if len(query_stripped) <= 5 and query_stripped.upper().isalpha():
            # But exclude common words
            if query_stripped.upper() not in {"HELLO", "HI", "HEY", "HELP", "TEST", "SCAN", "NEAR", "SHOW"}:
                return query_stripped.upper()
        
        return None
    
    async def _call_mcp_tool_directly(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool directly using the existing market service"""
        try:
            logger.info(f"🔧 [AGENTS SDK] Calling MCP tool: {tool_name} with params: {params}")
            
            if tool_name == "get_stock_quote" and params.get("symbol"):
                symbol = params["symbol"]
                
                # Use the existing market service API endpoint
                api_url = os.getenv("API_URL", "http://localhost:8000")
                response = await self.http_client.get(
                    f"{api_url}/api/stock-price?symbol={symbol}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ [AGENTS SDK] MCP stock quote success for {symbol}: ${data.get('price', 'N/A')}")
                    return data
                else:
                    logger.error(f"❌ [AGENTS SDK] MCP stock quote failed: {response.status_code}")
                    return None
            
            elif tool_name == "get_stock_history" and params.get("symbol"):
                symbol = params["symbol"]
                
                # Use the existing market service API endpoint for historical data
                api_url = os.getenv("API_URL", "http://localhost:8000")
                response = await self.http_client.get(
                    f"{api_url}/api/stock-history?symbol={symbol}&days=200",  # Get 200 days for moving averages
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ [AGENTS SDK] Historical data retrieved for {symbol}")
                    return data
                else:
                    logger.error(f"❌ [AGENTS SDK] Historical data fetch failed: {response.status_code}")
                    return None
            
            logger.warning(f"⚠️ [AGENTS SDK] Unsupported MCP tool: {tool_name}")
            return None
            
        except Exception as e:
            logger.error(f"💥 [AGENTS SDK] MCP tool call failed: {str(e)}")
            return None
    
    async def _generate_ai_response_with_data(self, query: str, stock_data: Dict[str, Any], symbol: str) -> str:
        """Generate AI response incorporating stock data"""
        try:
            price = stock_data.get("price", 0)
            change = stock_data.get("change_abs", 0)
            change_percent = stock_data.get("change_pct", 0)
            prev_close = stock_data.get("prev_close", 0)
            is_open = stock_data.get("is_open", False)
            
            # Handle case where price is 0 (market closed or data unavailable)
            if price == 0 and prev_close > 0:
                # Market is closed, use previous close
                price_info = f"Previous close: ${prev_close:.2f}"
                market_status = "Market is currently closed."
            elif price == 0:
                # No data available
                price_info = "Price data unavailable at this time."
                market_status = "Please try again during market hours."
            else:
                # Live price available
                price_info = f"Current price: ${price:.2f}"
                if change != 0:
                    price_info += f", {change:+.2f} ({change_percent:+.2f}%)"
                market_status = "Market is open." if is_open else "After-hours trading."
            
            # Create context for AI response
            system_prompt = """You are GVSES AI, a professional trading assistant. 
            
            The user asked about a stock and you have retrieved market data. 
            Provide a concise, informative response that includes:
            - Price information (current or previous close)
            - Market status if relevant
            - Keep it conversational for voice interface
            
            Be professional but conversational. Keep response under 100 words."""
            
            user_message = f"""Query: "{query}"

Stock Data for {symbol}:
- {price_info}
- Status: {market_status}

Please provide a professional trading assistant response."""

            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result["choices"][0]["message"]["content"]
                logger.info(f"🤖 [AGENTS SDK] AI response generated successfully")
                return ai_text
            else:
                logger.error(f"❌ [AGENTS SDK] AI response generation failed: {response.status_code}")
                # Fallback response
                return f"{symbol} is currently trading at ${price}, with a change of ${change} ({change_percent}%) in today's session."
                
        except Exception as e:
            logger.error(f"💥 [AGENTS SDK] AI response generation error: {str(e)}")
            # Simple fallback
            return f"I found that {symbol} is currently at ${stock_data.get('price', 'N/A')}."

    async def _calculate_btd_levels(self, symbol: str, stock_data: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate Buy The Dip (BTD), Buy Low, and Sell High levels based on technical analysis
        Following the idealagent.md specifications:
        - BTD: 200-day MA + 61.8% Fibonacci retracement + historical support
        - Buy Low: 50-day MA + 50% retracement + consolidation zone  
        - Sell High: Recent highs + RSI >70 + resistance
        """
        try:
            current_price = stock_data.get("price", 0)
            if current_price == 0:
                current_price = stock_data.get("prev_close", 0)
            
            # Default levels if we can't calculate
            btd_levels = {
                "btd": current_price * 0.90,  # 10% below
                "buy_low": current_price * 0.95,  # 5% below
                "sell_high": current_price * 1.05  # 5% above
            }
            
            # Try to calculate from historical data if available
            if historical_data and "candles" in historical_data:
                candles = historical_data["candles"]
                
                if len(candles) >= 200:
                    # Calculate moving averages
                    closes = [c.get("close", 0) for c in candles[-200:]]
                    
                    # 200-day MA for BTD
                    ma_200 = sum(closes) / len(closes)
                    
                    # 50-day MA for Buy Low
                    ma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else ma_200
                    
                    # Find recent high and low for Fibonacci levels
                    recent_high = max(closes[-100:]) if len(closes) >= 100 else max(closes)
                    recent_low = min(closes[-100:]) if len(closes) >= 100 else min(closes)
                    
                    # Calculate Fibonacci retracements
                    fib_range = recent_high - recent_low
                    fib_618 = recent_high - (fib_range * 0.618)  # 61.8% retracement for BTD
                    fib_50 = recent_high - (fib_range * 0.50)   # 50% retracement for Buy Low
                    
                    # Calculate RSI for Sell High (simplified 14-day RSI)
                    if len(closes) >= 15:
                        gains = []
                        losses = []
                        for i in range(len(closes) - 14, len(closes)):
                            change = closes[i] - closes[i-1]
                            if change > 0:
                                gains.append(change)
                                losses.append(0)
                            else:
                                gains.append(0)
                                losses.append(abs(change))
                        
                        avg_gain = sum(gains) / 14
                        avg_loss = sum(losses) / 14
                        rs = avg_gain / avg_loss if avg_loss > 0 else 100
                        rsi = 100 - (100 / (1 + rs))
                    else:
                        rsi = 50  # Neutral RSI if not enough data
                    
                    # Calculate BTD levels based on technical confluence
                    btd_levels["btd"] = min(ma_200, fib_618) * 0.98  # Slight discount for strong support
                    btd_levels["buy_low"] = min(ma_50, fib_50) 
                    
                    # Sell High based on recent highs and RSI
                    if rsi > 70:
                        btd_levels["sell_high"] = recent_high * 0.98  # Near recent high but slightly below
                    else:
                        btd_levels["sell_high"] = recent_high * 1.02  # Above recent high if not overbought
                    
                    # Ensure levels make sense relative to current price
                    if btd_levels["btd"] > current_price:
                        btd_levels["btd"] = current_price * 0.90
                    if btd_levels["buy_low"] > current_price:
                        btd_levels["buy_low"] = current_price * 0.95
                    if btd_levels["sell_high"] < current_price:
                        btd_levels["sell_high"] = current_price * 1.05
                        
            logger.info(f"📊 [AGENTS SDK] BTD Levels - BTD: ${btd_levels['btd']:.2f}, Buy Low: ${btd_levels['buy_low']:.2f}, Sell High: ${btd_levels['sell_high']:.2f}")
            return btd_levels
            
        except Exception as e:
            logger.error(f"Error calculating BTD levels: {str(e)}")
            # Return default levels on error
            return {
                "btd": current_price * 0.90,
                "buy_low": current_price * 0.95, 
                "sell_high": current_price * 1.05
            }
    
    async def _generate_ai_response_with_btd(self, query: str, stock_data: Dict[str, Any], btd_levels: Dict[str, float], symbol: str) -> str:
        """Generate AI response that includes specific BTD level prices"""
        try:
            price = stock_data.get("price", 0)
            change = stock_data.get("change_abs", 0)
            change_percent = stock_data.get("change_pct", 0)
            prev_close = stock_data.get("prev_close", 0)
            is_open = stock_data.get("is_open", False)
            
            # Handle case where price is 0 (market closed or data unavailable)
            if price == 0 and prev_close > 0:
                price = prev_close
                price_status = "previous close"
            elif price == 0:
                price_status = "unavailable"
            else:
                price_status = "current"
            
            # Check if query mentions BTD, levels, or trading plan
            query_upper = query.upper()
            wants_btd = any(term in query_upper for term in ["BTD", "BUY THE DIP", "BUY LOW", "SELL HIGH", "LEVELS", "TRADING"])
            
            logger.info(f"🔍 [AGENTS SDK] Query analysis - wants_btd: {wants_btd}, query: {query[:100]}")
            
            if wants_btd:
                # Format response with BTD levels as specified in idealagent.md
                response = f"""## {symbol} - Trading Levels

**Current Price:** ${price:.2f} {f'({change:+.2f}, {change_percent:+.2f}%)' if change != 0 else ''}

**Trading Levels:**
- **Buy The Dip (BTD):** ${btd_levels['btd']:.2f}
  - Most aggressive entry for loading maximum shares
  - Position size: 5-8% of portfolio
  
- **Buy Low:** ${btd_levels['buy_low']:.2f}
  - Medium-term swing trade entry
  - Position size: 3-5% of portfolio
  
- **Sell High:** ${btd_levels['sell_high']:.2f}
  - Exit/profit-taking zone
  - Scale out systematically

**Risk Management:**
- Stop Loss: ${btd_levels['btd'] * 0.95:.2f} (5% below BTD)
- Risk/Reward: 1:{((btd_levels['sell_high'] - btd_levels['buy_low']) / (btd_levels['buy_low'] - btd_levels['btd'] * 0.95)):.1f}

The market is {'open' if is_open else 'closed'}. These levels are based on technical analysis including moving averages and Fibonacci retracements."""
            else:
                # Simple response for basic price queries
                response = f"{symbol} is currently trading at ${price:.2f}"
                if change != 0:
                    response += f", {'up' if change > 0 else 'down'} by {abs(change_percent):.2f}% with a {'gain' if change > 0 else 'loss'} of ${abs(change):.2f}"
                response += f". The market is {'open' if is_open else 'closed'} right now"
                if not is_open:
                    response += ", so these numbers can change"
                response += ". If you need more details or have any other questions, feel free to ask!"
            
            return response
                
        except Exception as e:
            logger.error(f"💥 [AGENTS SDK] AI BTD response generation error: {str(e)}")
            # Simple fallback
            return f"{symbol} is currently at ${stock_data.get('price', 'N/A')}. I can help you analyze trading levels if you'd like."
    
    def _is_good_morning_greeting(self, query: str) -> bool:
        """Check if the query is a 'Good morning' greeting that should trigger market brief"""
        query_lower = query.lower().strip()
        greetings = ["good morning", "gm", "morning", "buenos dias", "bonjour"]
        return any(greeting in query_lower for greeting in greetings)
    
    async def _generate_market_brief(self, agent_query: AgentQuery) -> AgentResponse:
        """Generate daily market brief as specified in idealagent.md"""
        try:
            # Fetch market movers data
            api_url = os.getenv("API_URL", "http://localhost:8000")
            
            # Get market overview
            overview_response = await self.http_client.get(
                f"{api_url}/api/market-overview",
                timeout=10.0
            )
            
            # Get market movers  
            movers_response = await self.http_client.get(
                f"{api_url}/api/market-movers?type=gainers",
                timeout=10.0
            )
            
            losers_response = await self.http_client.get(
                f"{api_url}/api/market-movers?type=losers",
                timeout=10.0
            )
            
            # Build market brief response
            brief = f"""## Market Overview

**Date & Time:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

**Market Status:** {'Open' if datetime.now().hour >= 9 and datetime.now().hour < 16 else 'Pre-market'}

**Major Indices:**
- S&P 500: Check current levels
- Nasdaq: Monitor tech performance  
- Dow Jones: Track blue chips

## Top Movers

**Biggest Gainers:**"""
            
            if movers_response.status_code == 200:
                gainers = movers_response.json()
                for i, stock in enumerate(gainers[:3], 1):
                    symbol = stock.get("symbol", "N/A")
                    change_pct = stock.get("change_pct", 0)
                    brief += f"\n{i}. {symbol} (+{abs(change_pct):.1f}%)"
            else:
                brief += "\n- Market data temporarily unavailable"
            
            brief += "\n\n**Biggest Losers:**"
            
            if losers_response.status_code == 200:
                losers = losers_response.json()
                for i, stock in enumerate(losers[:3], 1):
                    symbol = stock.get("symbol", "N/A")
                    change_pct = stock.get("change_pct", 0)
                    brief += f"\n{i}. {symbol} (-{abs(change_pct):.1f}%)"
            else:
                brief += "\n- Market data temporarily unavailable"
            
            brief += """

## High-Conviction Trades

Focus on stocks with:
- Strong news catalysts
- Technical alignment with BTD or Buy Low levels
- Elevated volume and momentum
- Clear risk/reward setups (minimum 2:1)

## Risk Management Reminder

- Max portfolio heat: <10%
- Risk per trade: 1-2%
- Stop losses: Always below support
- Diversification: Multiple sectors

Good morning! Ready to analyze any specific stocks or opportunities you're watching today."""
            
            return AgentResponse(
                text=brief,
                tools_used=["market_overview", "market_movers", "market_brief"],
                data={"type": "market_brief", "triggered_by": "good_morning"},
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating market brief: {str(e)}")
            return AgentResponse(
                text="Good morning! How can I assist you with your trading or market-related queries today?",
                tools_used=["greeting"],
                data={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

# Global service instance
agents_sdk_service = AgentsSDKService()