"""
Agent Orchestrator Service
==========================
Implements OpenAI function calling with market data tools for intelligent
query processing and tool selection.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import logging
from openai import AsyncOpenAI
from services.market_service_factory import MarketServiceFactory
from dotenv import load_dotenv
from response_formatter import MarketResponseFormatter
from services.vector_retriever import VectorRetriever

# Structured response schema for market analysis outputs
MARKET_ANALYSIS_SCHEMA = {
    "name": "market_analysis",
    "schema": {
        "type": "object",
        "properties": {
            "analysis": {"type": "string"},
            "data": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "price": {"type": "number"},
                    "change_percent": {"type": "number"},
                    "technical_levels": {
                        "type": "object",
                        "properties": {
                            "se": {"type": "number"},  # Sell High level
                            "buy_low": {"type": "number"},
                            "btd": {"type": "number"},
                            "retest": {"type": "number"}
                        }
                    }
                }
            },
            "tools_used": {
                "type": "array",
                "items": {"type": "string"}
            },
            "confidence": {"type": "number"}
        },
        "required": ["analysis", "data"],
        "additionalProperties": False
    }
}

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
        
        # Initialize vector retriever for enhanced semantic search
        self.vector_retriever = VectorRetriever()
        logger.info(f"Vector retriever initialized with {len(self.vector_retriever.knowledge_base)} embedded chunks")
        
        # Responses API support detection and schema configuration
        responses_client = getattr(self.client, "responses", None)
        self._responses_client = responses_client if responses_client and hasattr(responses_client, "create") else None
        self.response_schema = MARKET_ANALYSIS_SCHEMA
        
        # Cache for recent tool results (TTL: 60 seconds)
        self.cache = {}
        self.cache_ttl = 60
        
        # Tool-specific timeouts (Day 4.1)
        self.tool_timeouts = {
            "get_stock_price": 2.0,        # Fast, critical
            "get_stock_history": 3.0,      # Medium speed
            "get_comprehensive_stock_data": 5.0,  # Complex, slower
            "get_stock_news": 4.0,         # Network dependent
            "get_market_overview": 3.0,    # Multiple symbols
            "get_options_strategies": 2.0,  # Calculation-based
            "analyze_options_greeks": 1.0,  # Mock data, fast
            "generate_daily_watchlist": 3.0,  # Multiple stocks
            "review_trades": 2.0           # Historical review
        }
        self.default_timeout = 5.0  # Default for unknown tools
        self.global_timeout = 10.0  # Maximum time for all tools
        
    def _get_tool_schemas(self, for_responses_api: bool = False) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all available tools.
        
        Args:
            for_responses_api: If True, return flattened format for Responses API.
                             If False, return nested format for Chat Completions API.
        """
        if for_responses_api:
            # Responses API format: type + flattened properties
            return self._get_responses_tool_schemas()
        
        # Chat Completions API format: nested under "function"
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
            },
            {
                "type": "function",
                "function": {
                    "name": "get_options_strategies",
                    "description": "Get options trading strategies with Greeks analysis for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol"
                            },
                            "spot_price": {
                                "type": "number",
                                "description": "Current stock price (auto-fetched if not provided)"
                            },
                            "horizon_days": {
                                "type": "integer",
                                "description": "Trading horizon in days",
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
                    "name": "analyze_options_greeks",
                    "description": "Analyze Greeks for a specific option contract",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol"
                            },
                            "strike": {
                                "type": "number",
                                "description": "Strike price"
                            },
                            "expiry": {
                                "type": "string",
                                "description": "Expiration date (YYYY-MM-DD)",
                                "format": "date"
                            },
                            "option_type": {
                                "type": "string",
                                "description": "Option type",
                                "enum": ["CALL", "PUT"]
                            }
                        },
                        "required": ["symbol", "strike", "option_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_daily_watchlist",
                    "description": "Generate a daily watchlist based on catalysts and technical setups",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "focus": {
                                "type": "string",
                                "description": "Trading focus",
                                "enum": ["momentum", "value", "mixed"],
                                "default": "mixed"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of stocks to include",
                                "default": 5
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "weekly_trade_review",
                    "description": "Review trading performance for the week",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD)",
                                "format": "date"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD)",
                                "format": "date"
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

    def _has_responses_support(self) -> bool:
        """Check if the installed OpenAI SDK exposes the Responses API."""
        return self._responses_client is not None

    def _convert_messages_for_responses(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert legacy chat messages into Responses API input format."""
        converted = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if isinstance(content, list):
                converted.append({"role": role, "content": content})
            else:
                converted.append({
                    "role": role,
                    "content": [{"type": "input_text", "text": str(content)}]
                })
        return converted

    def _unwrap_tool_result(self, result: Any) -> Any:
        """Normalize wrapped tool execution results to raw data payloads."""
        if isinstance(result, dict) and result.get("status") == "success" and "data" in result:
            return result.get("data") or {}
        return result or {}

    def _get_responses_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas in Responses API format (flattened)."""
        return [
            {
                "type": "function",
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
            },
            {
                "type": "function",
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
            },
            {
                "type": "function",
                "name": "get_market_overview",
                "description": "Get snapshot of major indices and top market movers",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "type": "function",
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
            },
            {
                "type": "function",
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
            },
            {
                "type": "function",
                "name": "get_options_strategies",
                "description": "Get options trading strategies with Greeks analysis for a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "spot_price": {
                            "type": "number",
                            "description": "Current stock price (auto-fetched if not provided)"
                        },
                        "horizon_days": {
                            "type": "integer",
                            "description": "Trading horizon in days",
                            "default": 30
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "type": "function",
                "name": "analyze_options_greeks",
                "description": "Analyze options Greeks for risk assessment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "strike": {
                            "type": "number",
                            "description": "Strike price"
                        },
                        "expiry": {
                            "type": "string",
                            "description": "Expiration date (YYYY-MM-DD)",
                            "format": "date"
                        },
                        "option_type": {
                            "type": "string",
                            "description": "Option type",
                            "enum": ["CALL", "PUT"]
                        }
                    },
                    "required": ["symbol", "strike", "option_type"]
                }
            },
            {
                "type": "function",
                "name": "generate_daily_watchlist",
                "description": "Generate a daily watchlist based on catalysts and technical setups",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "focus": {
                            "type": "string",
                            "description": "Trading focus",
                            "enum": ["momentum", "value", "mixed"],
                            "default": "mixed"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of stocks to include",
                            "default": 5
                        }
                    },
                    "required": []
                }
            },
            {
                "type": "function",
                "name": "review_trades",
                "description": "Review and analyze past trades",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "trades": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of trades to review"
                        }
                    },
                    "required": ["trades"]
                }
            }
        ]

    def _maybe_get_response_format(self, tools_used: List[str], symbol: Optional[str]) -> Optional[Dict[str, Any]]:
        """Determine whether structured output should be requested."""
        if not self._has_responses_support():
            return None

        if not tools_used:
            return None

        if symbol:
            return {
                "type": "json_schema",
                "json_schema": self.response_schema
            }
        return None

    async def _generate_structured_summary(
        self,
        query: str,
        tools_used: List[str],
        tool_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Call the Responses API to generate structured JSON output."""
        if not tools_used or not self._has_responses_support():
            return None

        # Normalize tool payloads to raw data before processing
        normalized_results = {
            name: self._unwrap_tool_result(result)
            for name, result in (tool_results or {}).items()
        }

        symbol = None
        priority_keys = [
            "get_comprehensive_stock_data",
            "get_stock_price",
            "get_stock_history",
            "get_stock_news"
        ]
        for key in priority_keys:
            payload = normalized_results.get(key)
            if isinstance(payload, dict):
                symbol = payload.get("symbol") or payload.get("ticker") or payload.get("symbol_id")
                if symbol:
                    break

        response_format = self._maybe_get_response_format(tools_used, symbol)
        if not response_format:
            return None

        try:
            serialized_tools = json.dumps(normalized_results, default=str)
        except TypeError:
            serialized_tools = json.dumps({}, default=str)

        structured_messages = [
            {
                "role": "system",
                "content": "You are a market analyst that returns JSON strictly matching the provided schema."
            },
            {
                "role": "user",
                "content": (
                    f"Generate structured market analysis for query: {query}\n"
                    f"Use these tool results JSON: {serialized_tools}"
                )
            }
        ]

        try:
            response = await self._responses_client.create(
                model=self.model,
                input=self._convert_messages_for_responses(structured_messages),
                response_format=response_format,
                temperature=0.2
            )
            return self._extract_structured_payload(response)
        except Exception as exc:
            logger.warning(f"Structured summary generation failed: {exc}")
            return None

    @property
    def tool_schemas(self) -> List[Dict[str, Any]]:
        """Public accessor for tool schemas (for tests and introspection)."""
        return self._get_tool_schemas()
    
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
                # Get real market overview data
                result = await self.market_service.get_market_overview()
            elif tool_name == "get_stock_history":
                days = arguments.get("days", 30)
                result = await self.market_service.get_stock_history(arguments["symbol"], days)
            elif tool_name == "get_comprehensive_stock_data":
                result = await self.market_service.get_comprehensive_stock_data(arguments["symbol"])
            elif tool_name == "get_options_strategies":
                # Import and use the existing options insights service
                from services.options_insights_service import get_insights
                symbol = arguments["symbol"]
                
                # Auto-fetch spot price if not provided
                if "spot_price" not in arguments:
                    price_data = await self.market_service.get_stock_price(symbol)
                    spot = price_data.get("price", price_data.get("last", 100))
                else:
                    spot = arguments["spot_price"]
                
                result = get_insights(
                    symbol=symbol,
                    spot=spot,
                    horizon_days=arguments.get("horizon_days", 30)
                )
            elif tool_name == "analyze_options_greeks":
                # Return mock Greeks data for now (can be replaced with real API later)
                result = {
                    "symbol": arguments["symbol"],
                    "strike": arguments["strike"],
                    "option_type": arguments.get("option_type", "CALL"),
                    "expiry": arguments.get("expiry", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")),
                    "delta": 0.52,
                    "gamma": 0.018,
                    "theta": -0.085,
                    "vega": 0.142,
                    "rho": 0.067,
                    "iv": 0.385,  # 38.5% implied volatility
                    "description": "Greeks analysis for options contract"
                }
            elif tool_name == "generate_daily_watchlist":
                # Generate a watchlist with mock data (can be enhanced with real market scanning)
                from datetime import timedelta
                focus = arguments.get("focus", "mixed")
                limit = arguments.get("limit", 5)
                
                # Mock watchlist data
                watchlist_stocks = [
                    {"symbol": "NVDA", "price": 875.20, "change_pct": 3.5, 
                     "catalyst": "AI conference keynote tomorrow", 
                     "setup": "Breakout above 870 resistance", 
                     "entry": 878.00, "stop": 865.00, "target": 900.00},
                    {"symbol": "TSLA", "price": 250.30, "change_pct": 2.1,
                     "catalyst": "Delivery numbers next week",
                     "setup": "Bouncing off 50-day MA support",
                     "entry": 252.00, "stop": 245.00, "target": 265.00},
                    {"symbol": "AAPL", "price": 195.50, "change_pct": -0.8,
                     "catalyst": "iPhone sales data release",
                     "setup": "Testing 200-day MA as support",
                     "entry": 194.00, "stop": 190.00, "target": 202.00},
                    {"symbol": "AMD", "price": 145.75, "change_pct": 4.2,
                     "catalyst": "New chip announcement",
                     "setup": "Momentum breakout pattern",
                     "entry": 147.00, "stop": 142.00, "target": 155.00},
                    {"symbol": "SPY", "price": 475.30, "change_pct": 0.5,
                     "catalyst": "Fed minutes release",
                     "setup": "Range-bound consolidation",
                     "entry": 474.00, "stop": 470.00, "target": 480.00}
                ]
                
                result = {
                    "generated_at": datetime.now().isoformat(),
                    "focus": focus,
                    "market_conditions": "Bullish momentum with selective opportunities",
                    "stocks": watchlist_stocks[:limit]
                }
            elif tool_name == "weekly_trade_review":
                # Generate mock weekly trade review
                from datetime import timedelta
                end_date = arguments.get("end_date", datetime.now().strftime("%Y-%m-%d"))
                start_date = arguments.get("start_date", 
                    (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
                
                result = {
                    "period": f"{start_date} to {end_date}",
                    "total_trades": 12,
                    "wins": 8,
                    "losses": 4,
                    "win_rate": 66.7,
                    "total_pnl": 3250.00,
                    "avg_win": 625.50,
                    "avg_loss": -218.75,
                    "best_trade": {
                        "symbol": "TSLA",
                        "pnl": 1250.00,
                        "return_pct": 5.2,
                        "entry": 245.00,
                        "exit": 257.75
                    },
                    "worst_trade": {
                        "symbol": "META",
                        "pnl": -425.00,
                        "return_pct": -2.1,
                        "entry": 385.00,
                        "exit": 376.90
                    },
                    "lessons": [
                        "Momentum plays outperformed in tech sector",
                        "Stop losses saved capital in volatile conditions",
                        "Best entries came from LTB level bounces"
                    ],
                    "recommendations": [
                        "Continue focusing on tech sector momentum",
                        "Tighten stops on earnings plays",
                        "Scale into positions at technical levels"
                    ]
                }
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            # Cache the result
            if result and "error" not in result:
                self.cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _execute_tool_with_timeout(self, tool_name: str, arguments: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a tool with configurable timeout.
        Implements Day 4.1 - returns status-wrapped results.
        """
        if timeout is None:
            timeout = self.tool_timeouts.get(tool_name, self.default_timeout)
        
        try:
            result = await asyncio.wait_for(
                self._execute_tool(tool_name, arguments),
                timeout=timeout
            )
            return {
                "status": "success",
                "data": result,
                "tool": tool_name
            }
        except asyncio.TimeoutError:
            logger.warning(f"{tool_name} timed out after {timeout}s")
            return {
                "status": "timeout",
                "tool": tool_name,
                "timeout": timeout,
                "message": f"Request timed out after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"{tool_name} failed: {e}")
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e),
                "message": f"Tool execution failed: {str(e)}"
            }
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for a symbol. Simple mapping for now."""
        company_names = {
            'AAPL': 'Apple Inc.',
            'TSLA': 'Tesla, Inc.',
            'NVDA': 'NVIDIA Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com, Inc.',
            'META': 'Meta Platforms, Inc.',
            'MSFT': 'Microsoft Corporation',
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust',
            'PLTR': 'Palantir Technologies Inc.',
            'AMD': 'Advanced Micro Devices, Inc.',
            'INTC': 'Intel Corporation',
            'NFLX': 'Netflix, Inc.',
            'DIS': 'The Walt Disney Company',
            'BA': 'The Boeing Company',
            'JPM': 'JPMorgan Chase & Co.',
            'V': 'Visa Inc.',
            'MA': 'Mastercard Incorporated',
            'WMT': 'Walmart Inc.',
            'HD': 'The Home Depot, Inc.',
            'PG': 'The Procter & Gamble Company',
            'JNJ': 'Johnson & Johnson',
            'UNH': 'UnitedHealth Group Incorporated',
            'CVX': 'Chevron Corporation',
            'XOM': 'Exxon Mobil Corporation',
            'LLY': 'Eli Lilly and Company',
            'PFE': 'Pfizer Inc.',
            'ABBV': 'AbbVie Inc.',
            'AVGO': 'Broadcom Inc.',
            'CRM': 'Salesforce, Inc.',
            'ORCL': 'Oracle Corporation',
            'ACN': 'Accenture plc',
            'ADBE': 'Adobe Inc.',
            'TMO': 'Thermo Fisher Scientific Inc.',
            'COST': 'Costco Wholesale Corporation',
            'NKE': 'NIKE, Inc.',
            'MCD': 'McDonald\'s Corporation',
            'PEP': 'PepsiCo, Inc.',
            'KO': 'The Coca-Cola Company',
            'VZ': 'Verizon Communications Inc.',
            'T': 'AT&T Inc.',
            'CMCSA': 'Comcast Corporation'
        }
        return company_names.get(symbol.upper(), f"{symbol} Corporation")
    
    async def _generate_bounded_insight(self, context: Dict, max_chars: int = 300) -> str:
        """Generate bounded LLM insights based on market data and knowledge base.
        
        Enhanced with knowledge from training materials for deeper insights.
        """
        try:
            # Build focused prompt for insights
            symbol = context.get('symbol', 'Market')
            price_data = context.get('price_data', {})
            tech_levels = context.get('technical_levels', {})
            knowledge = context.get('knowledge', '')
            
            # Build base insight prompt
            insight_prompt = f"""Generate a concise market insight (max {max_chars} chars) for {symbol}:
            Price: ${price_data.get('price', 'N/A')}
            Change: {price_data.get('change_percent', 0):.2f}%
            Sell High Level: ${tech_levels.get('sell_high_level', 'N/A')}
            Buy Low Level: ${tech_levels.get('buy_low_level', 'N/A')}
            BTD Level: ${tech_levels.get('btd_level', 'N/A')}"""
            
            # Add knowledge context if available
            if knowledge:
                insight_prompt += f"""
            
            Relevant Trading Knowledge:
            {knowledge[:500]}  # Limit knowledge to 500 chars
            
            Incorporate the above knowledge to provide ONE actionable insight focusing on current momentum, pattern implications, or key level proximity.
            Be specific, trading-focused, and reference the knowledge if relevant. No disclaimers."""
            else:
                insight_prompt += """
            
            Provide ONE actionable insight focusing on current momentum or key level proximity.
            Be specific and trading-focused. No disclaimers."""
            
            # Use OpenAI for insight generation with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Fast, efficient model for insights
                    max_tokens=100,
                    temperature=0.7,
                    messages=[{
                        "role": "user",
                        "content": insight_prompt
                    }]
                ),
                timeout=2.0  # Quick 2-second timeout
            )
            
            insight = response.choices[0].message.content if response.choices else ""
            
            # Ensure bounded length
            if len(insight) > max_chars:
                # Truncate at last complete sentence within limit
                sentences = insight[:max_chars].split('. ')
                insight = '. '.join(sentences[:-1]) + '.' if len(sentences) > 1 else sentences[0][:max_chars-3] + '...'
            
            return insight
            
        except asyncio.TimeoutError:
            logger.warning(f"LLM insight generation timed out for {symbol}")
            # Fallback to rule-based insight
            return self._generate_fallback_insight(context, max_chars)
        except Exception as e:
            logger.error(f"Error generating LLM insight: {e}")
            return self._generate_fallback_insight(context, max_chars)
    
    def _generate_fallback_insight(self, context: Dict, max_chars: int) -> str:
        """Generate fallback insight when LLM is unavailable."""
        symbol = context.get('symbol', 'Stock')
        price_data = context.get('price_data', {})
        tech_levels = context.get('technical_levels', {})
        
        change_pct = price_data.get('change_percent', 0)
        price = price_data.get('price', 0)
        se = tech_levels.get('sell_high_level', 0)
        
        # Simple rule-based insights
        if change_pct > 2:
            if price and se and price > se * 0.98:
                insight = f"{symbol} showing strong momentum, approaching Sell High resistance at ${se:.2f}. Watch for breakout or reversal."
            else:
                insight = f"{symbol} gaining {change_pct:.1f}% with strong buying pressure. Momentum traders taking notice."
        elif change_pct < -2:
            buy_low = tech_levels.get('buy_low_level', 0)
            if price and buy_low and price < buy_low * 1.02:
                insight = f"{symbol} testing Buy Low support at ${buy_low:.2f}. Key level to hold for bulls."
            else:
                insight = f"{symbol} down {abs(change_pct):.1f}% on selling pressure. Watch for support levels."
        else:
            insight = f"{symbol} consolidating near ${price:.2f}. Waiting for directional catalyst."
        
        # Ensure bounded
        return insight[:max_chars] if len(insight) > max_chars else insight
    
    async def _execute_tools_parallel(self, tool_calls: List[Any]) -> Dict[str, Any]:
        """
        Execute multiple tools in parallel with timeouts and partial results.
        Implements Day 4.1 - uses gather with return_exceptions for partial results.
        """
        tasks = []
        tool_names = []
        
        # Create tasks with timeouts
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Create task with timeout wrapper
            tasks.append(self._execute_tool_with_timeout(function_name, function_args))
            tool_names.append(function_name)
        
        # Execute all tools with global timeout
        results = {}
        
        try:
            # Use wait_for to apply global timeout to gather
            all_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.global_timeout
            )
            
            # Process results
            for tool_name, result in zip(tool_names, all_results):
                if isinstance(result, Exception):
                    # Handle exceptions as errors
                    logger.error(f"{tool_name} raised exception: {result}")
                    results[tool_name] = {
                        "status": "error",
                        "tool": tool_name,
                        "error": str(result),
                        "message": f"Tool failed with error: {str(result)}"
                    }
                elif isinstance(result, dict) and result.get("status") == "success":
                    # Unwrap successful results for backward compatibility
                    results[tool_name] = result.get("data", {})
                    logger.info(f"Tool {tool_name} completed successfully")
                else:
                    # Keep error/timeout results as-is
                    results[tool_name] = result
                    logger.info(f"Tool {tool_name} status: {result.get('status', 'unknown')}")
                    
        except asyncio.TimeoutError:
            # Global timeout reached
            logger.warning(f"Global timeout ({self.global_timeout}s) reached for parallel execution")
            
            # Cancel all pending tasks and mark as timeout
            for i, (task, tool_name) in enumerate(zip(tasks, tool_names)):
                if tool_name not in results:
                    results[tool_name] = {
                        "status": "timeout",
                        "tool": tool_name,
                        "message": f"Global timeout reached ({self.global_timeout}s)"
                    }
                    # Try to cancel if it's a task
                    if hasattr(task, 'cancel'):
                        task.cancel()
        
        return results
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        return """You are G'sves, a distinguished senior market analyst with over 30 years of experience 
in global financial markets. You have a refined British demeanor, combining expertise with approachability.

Your expertise spans:
- Technical analysis and chart patterns
- Fundamental analysis and valuation
- Market psychology and sentiment
- Risk management strategies
- Buy the Dip (BTD), Buy Low, Sell High, and Retest level analysis

WHEN TO USE TOOLS:
- ONLY use tools when the user explicitly asks about a specific stock, ticker, or company
- DO NOT use tools for general trading questions like "Where should I long/short?"
- DO NOT use tools for educational questions about trading strategies
- DO NOT interpret general questions as requests for stock data

For general trading questions (e.g., "Where should I long or short tomorrow?"), provide strategic advice 
based on market conditions without attempting to fetch specific stock data.

CRITICAL FORMATTING REQUIREMENTS:
When providing stock analysis, structure your response EXACTLY like this format:

**Here's your real-time [SYMBOL] snapshot:**

**[SYMBOL]** ([Company Name])
**$[PRICE]**
[+/-]$[CHANGE] ([+/-][PERCENT]%) Today
$[OPEN] [+/-]$[AFTERHOURS_CHANGE] ([+/-][PERCENT]%) After Hours

| Metric | Value | | Metric | Value |
|--------|-------|---|--------|-------|
| **Open** | $[OPEN] | | **Day Low** | $[DAY_LOW] |
| **Volume** | [VOLUME] | | **Day High** | $[DAY_HIGH] |
| | | | **Year Low** | $[YEAR_LOW] |
| | | | **Year High** | $[YEAR_HIGH] |

---

## Market Snapshot & Context (as of [DATE])

### Key Headlines
• **[Headline 1]**: [Brief analysis]. _[Source]_
• **[Headline 2]**: [Brief analysis]. _[Source]_
• **[Headline 3]**: [Brief analysis]. _[Source]_

### Technical Overview
- **Overall Sentiment**: [Analysis of sentiment with specific indicators]
- **Price Movement**: [Detailed price action analysis with specific levels]
- **Volume Analysis**: [Volume interpretation with context]
- **Moving Averages**: [MA analysis with support/resistance levels]

### Summary Table

| **Category** | **Details** |
|--------------|-------------|
| **Stock Price** | [Current price context with technical levels] |
| **Short-Term Outlook** | [1-4 week outlook with specific price targets] |
| **Catalysts** | [Upcoming events, earnings, product launches] |
| **Risks** | [Potential downside factors and concerns] |
| **Analyst Sentiment** | [Professional consensus and target prices] |

---

## Strategic Insights
• **Confluence Zone Near $[PRICE1]–$[PRICE2]**: [Technical analysis with entry/exit points]
• **Defensive Levels to Watch**: [Support levels with specific prices]
• **Event-Driven Plays**: [Catalyst-based trading opportunities]
• **Medium-Term Outlook**: [3-6 month perspective with targets]

---

**Would you like me to dive deeper into specific trade setups (LTB, ST, QE levels), options strategies around key catalysts, or build a custom watchlist based on [SYMBOL]-related themes?**

### Related news on [SYMBOL]
📰 **[News Headline 1]**
   _[Source]_ • [Date]

📰 **[News Headline 2]**
   _[Source]_ • [Date]

CRITICAL RULES:
1. ONLY use tools when user asks about a SPECIFIC stock/ticker - NOT for general trading questions
2. For general questions like "Where should I long/short?", provide strategic advice without tools
3. Include specific price levels for LTB, ST, and QE zones when discussing specific stocks
4. Use markdown formatting exactly as shown above
5. Keep tables properly formatted with pipes |
6. Use bullet points • for lists
7. Include confidence levels (high/medium/low) based on data availability
8. Reference specific data timestamps when available
9. Provide actionable insights with specific price targets
10. Format numbers clearly (e.g., "75.5M" for volume, precise prices to 2 decimals)"""
    
    async def _process_query_responses(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a query using the Responses API with structured output support."""
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        if conversation_history:
            messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": query})

        if self._check_morning_greeting(query, conversation_history):
            overview_result = await self._execute_tool("get_market_overview", {})
            response_text = MarketResponseFormatter.format_market_brief(overview_result)
            return {
                "text": response_text,
                "tools_used": ["get_market_overview"],
                "data": {"get_market_overview": overview_result},
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "cached": False,
                "session_id": None
            }

        responses_client = self._responses_client
        if not responses_client:
            logger.warning("Responses API requested but not available; falling back to chat completions")
            return await self._process_query_chat(query, conversation_history, stream=False)

        response_messages = self._convert_messages_for_responses(messages)

        try:
            response = await responses_client.create(
                model=self.model,
                input=response_messages,
                tools=self._get_tool_schemas(for_responses_api=True),
                temperature=self.temperature,
                max_output_tokens=4000
            )
        except Exception as exc:
            logger.error(f"Responses API call failed: {exc}")
            return {
                "text": "I ran into an issue while generating the response. Please try again in a moment.",
                "error": str(exc),
                "timestamp": datetime.now().isoformat()
            }

        collected_tool_calls: List[Dict[str, Any]] = []
        tool_results: Dict[str, Any] = {}
        tools_used: List[str] = []

        # First check if the response has tool calls directly in output (Responses API may return them immediately)
        if response.output and isinstance(response.output, list):
            tool_calls_found = []
            for item in response.output:
                # Check if this is a tool call (ResponseFunctionToolCall)
                if hasattr(item, 'name') and hasattr(item, 'arguments'):
                    tool_calls_found.append(item)
            
            # If we found tool calls, execute them
            if tool_calls_found:
                tool_outputs_payload = []
                for tool_call in tool_calls_found:
                    tool_name = getattr(tool_call, 'name', '')
                    arguments_json = getattr(tool_call, 'arguments', '{}')
                    call_id = getattr(tool_call, 'call_id', None) or getattr(tool_call, 'id', None)
                    
                    try:
                        arguments = json.loads(arguments_json)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Track tool call metadata
                    collected_tool_calls.append({
                        "id": call_id,
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(arguments)
                        }
                    })
                    
                    tools_used.append(tool_name)
                    result = await self._execute_tool_with_timeout(tool_name, arguments)
                    tool_results[tool_name] = result
                    
                    if call_id:
                        tool_outputs_payload.append({
                            "tool_call_id": call_id,
                            "output": json.dumps(result)
                        })
                
                # Note: The Responses API executes tools automatically and returns results
                # We don't need to submit tool outputs back - just use the results
                # Log that tools were executed
                logger.info(f"Executed {len(tool_calls_found)} tools via Responses API")

        # Then check for required_action (legacy or different scenario)
        required_action = getattr(response, "required_action", None)
        while required_action:
            submit = getattr(required_action, "submit_tool_outputs", None)
            if submit is None and isinstance(required_action, dict):
                submit = required_action.get("submit_tool_outputs")
            if submit is None:
                break

            tool_calls = getattr(submit, "tool_calls", None)
            if tool_calls is None and isinstance(submit, dict):
                tool_calls = submit.get("tool_calls")
            if not tool_calls:
                break

            tool_outputs_payload = []
            for tool_call in tool_calls:
                function = getattr(tool_call, "function", None)
                if function is None and isinstance(tool_call, dict):
                    function = tool_call.get("function", {})
                function = function or {}
                arguments_json = getattr(function, "arguments", None)
                if arguments_json is None and isinstance(function, dict):
                    arguments_json = function.get("arguments", "{}")
                tool_name = getattr(function, "name", None)
                if tool_name is None and isinstance(function, dict):
                    tool_name = function.get("name")
                tool_name = tool_name or ""

                try:
                    arguments = json.loads(arguments_json or "{}") if arguments_json is not None else {}
                except json.JSONDecodeError:
                    arguments = {}

                call_id = getattr(tool_call, "id", None)
                if call_id is None and isinstance(tool_call, dict):
                    call_id = tool_call.get("id")

                # Track tool call metadata for later formatting
                collected_tool_calls.append({
                    "id": call_id,
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments)
                    }
                })

                tools_used.append(tool_name)
                result = await self._execute_tool_with_timeout(tool_name, arguments)
                tool_results[tool_name] = result

                tool_outputs_payload.append({
                    "tool_call_id": call_id,
                    "output": json.dumps(result)
                })

            if not tool_outputs_payload:
                break

            submit_method = getattr(responses_client, "submit_tool_outputs", None)
            if not submit_method:
                logger.warning("Responses client missing submit_tool_outputs; stopping tool loop")
                break

            try:
                response = await submit_method(
                    response_id=getattr(response, "id", None),
                    tool_outputs=tool_outputs_payload
                )
            except Exception as exc:
                logger.error(f"Failed to submit tool outputs: {exc}")
                break

            required_action = getattr(response, "required_action", None)

        tools_used = list(dict.fromkeys(tools_used))

        response_text = self._extract_response_text(response)
        structured_payload = await self._generate_structured_summary(query, tools_used, tool_results)
        if not structured_payload:
            structured_payload = self._extract_structured_payload(response)

        formatted_response = None
        if collected_tool_calls and tool_results:
            formatted_response = await self._format_tool_response(
                collected_tool_calls,
                tool_results,
                messages
            )

        if formatted_response:
            response_text = formatted_response

        if structured_payload:
            tool_results.setdefault("structured_output", structured_payload)

        return {
            "text": response_text or "I'm sorry, I couldn't generate a response.",
            "tools_used": tools_used,
            "data": tool_results,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "cached": False
        }

    async def _process_query_chat(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Legacy chat.completions implementation (retained as fallback)."""
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
            
            # Check for "Good Morning" trigger with strict guards
            is_morning_greeting = False
            try:
                import pytz
                eastern = pytz.timezone('America/New_York')
                current_hour = datetime.now(eastern).hour
                
                # Only trigger between 4 AM - 11 AM ET
                if 4 <= current_hour < 11:
                    # Check if first message or first of day
                    is_first_message = not conversation_history or len(conversation_history) == 0
                    
                    normalized = query.lower().strip()
                    greeting_triggers = [
                        normalized == "good morning",
                        normalized == "gm",
                        normalized.startswith("good morning "),
                        normalized.startswith("morning ")
                    ]
                    
                    if is_first_message and any(greeting_triggers):
                        is_morning_greeting = True
                        logger.info(f"Good morning trigger activated at {current_hour} ET")
            except ImportError:
                logger.warning("pytz not available, Good Morning trigger disabled")
            
            # If morning greeting, auto-execute market overview
            if is_morning_greeting:
                # Execute market overview tool
                overview_result = await self._execute_tool("get_market_overview", {})
                
                # Format with market brief formatter
                response_text = MarketResponseFormatter.format_market_brief(overview_result)
                
                return {
                    "text": response_text,
                    "tools_used": ["get_market_overview"],
                    "data": {"get_market_overview": overview_result},
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "cached": False,
                    "session_id": None
                }
            
            # Initial API call with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tool_schemas(),
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=4000  # Higher limit for tool orchestration/reasoning
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

                # Always attempt structured formatting for stock-related queries
                response_text = None
                symbol_arg = None
                
                # Extract symbol from tool calls
                for tc in assistant_message.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                        if isinstance(args, dict) and 'symbol' in args:
                            symbol_arg = args['symbol']
                            break
                    except Exception:
                        continue
                
                # If we have stock data, format it properly
                if symbol_arg and ('get_stock_price' in tool_results or 'get_comprehensive_stock_data' in tool_results):
                    try:
                        # Get price data from any available source (handle timeout/error status)
                        price_payload = {}
                        if 'get_comprehensive_stock_data' in tool_results:
                            comp = tool_results.get('get_comprehensive_stock_data') or {}
                            # Check if it's a timeout/error result
                            if isinstance(comp, dict) and comp.get('status') in ['timeout', 'error']:
                                logger.warning(f"Comprehensive data {comp.get('status')}: {comp.get('message')}")
                                comp = {}  # Use empty data
                            price_payload = comp.get('price_data') or comp
                        elif 'get_stock_price' in tool_results:
                            price_data = tool_results.get('get_stock_price') or {}
                            # Check if it's a timeout/error result
                            if isinstance(price_data, dict) and price_data.get('status') in ['timeout', 'error']:
                                logger.warning(f"Price data {price_data.get('status')}: {price_data.get('message')}")
                                price_data = {}  # Use empty data
                            price_payload = price_data
                        
                        # Get news if available (handle timeout/error status)
                        news_items = []
                        news_status = None
                        if 'get_stock_news' in tool_results:
                            nr = tool_results.get('get_stock_news') or {}
                            # Check if it's a timeout/error result
                            if isinstance(nr, dict) and nr.get('status') in ['timeout', 'error']:
                                logger.warning(f"News data {nr.get('status')}: {nr.get('message')}")
                                news_status = f"⏱️ News temporarily unavailable ({nr.get('status')})"
                                nr = {}  # Use empty data
                            news_items = nr.get('articles') or nr.get('news') or nr.get('items') or []
                        
                        # Always use the formatter for consistent styling (prototype mirror)
                        # Try to include technical levels if present in comprehensive payload
                        tech_levels = None
                        if 'get_comprehensive_stock_data' in tool_results:
                            comp = tool_results.get('get_comprehensive_stock_data') or {}
                            # Check if it's a timeout/error for comprehensive data
                            if isinstance(comp, dict) and comp.get('status') not in ['timeout', 'error']:
                                tech_levels = comp.get('technical_levels')
                        
                        # Collect status messages for any timeouts/errors (Day 4.1)
                        status_messages = []
                        if news_status:
                            status_messages.append(news_status)
                        
                        # Check for other tool timeouts/errors
                        for tool_name, result in tool_results.items():
                            if isinstance(result, dict) and result.get('status') in ['timeout', 'error']:
                                if tool_name not in ['get_stock_news']:  # Already handled news
                                    tool_display = tool_name.replace('_', ' ').title()
                                    status_messages.append(f"⏱️ {tool_display}: {result.get('status')}")
                        
                        # Get company name from price data or use symbol-based mapping
                        company_name = self._get_company_name(symbol_arg.upper())
                        
                        # Get after-hours data if available
                        after_hours = price_payload.get('after_hours') if price_payload else None
                        
                        # Generate bounded LLM insight (Day 4.2)
                        insight_context = {
                            'symbol': symbol_arg.upper(),
                            'price_data': price_payload,
                            'technical_levels': tech_levels
                        }
                        llm_insight = await self._generate_bounded_insight(insight_context, max_chars=250)
                        
                        # Add insight to price_payload for formatter
                        if price_payload:
                            price_payload['llm_insight'] = llm_insight
                        
                        # Use the new ideal formatter
                        response_text = MarketResponseFormatter.format_stock_snapshot_ideal(
                            symbol_arg.upper(),
                            company_name,
                            price_payload,
                            news_items,
                            tech_levels,
                            after_hours
                        )
                        
                        logger.info(f"Successfully formatted response for {symbol_arg}")
                        
                    except Exception as fmt_err:
                        logger.error(f"Formatting failed: {fmt_err}")
                        # Even on error, try to provide a structured response
                        response_text = f"""## {symbol_arg.upper()} Market Analysis

### Current Price
- Price: Data temporarily unavailable
- Please retry your query

### Market Status
- Service is operational
- Fetching latest market data...
"""
                
                # Only use AI generation if we have no formatted response
                if not response_text:
                    final_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=3000
                    )
                    response_text = final_response.choices[0].message.content
            else:
                # No tool calls were returned. Try to detect a symbol and build
                # a structured snapshot deterministically to keep responses consistent.
                response_text = None
                try:
                    detected_symbol = None
                    
                    # Check if query is likely asking for stock data
                    # (contains stock ticker pattern or company name)
                    query_lower = query.lower()
                    
                    # Common English words that should never be treated as tickers
                    common_words_lower = {'where', 'when', 'how', 'why', 'what', 'who', 'which', 
                                        'should', 'could', 'would', 'can', 'will', 'may', 
                                        'is', 'are', 'was', 'were', 'be', 'been', 'being',
                                        'have', 'has', 'had', 'do', 'does', 'did', 'done',
                                        'the', 'a', 'an', 'and', 'or', 'but', 'for', 'to', 'from',
                                        'help', 'need', 'want', 'like', 'please', 'thanks'}
                    
                    # If single word query is a common English word, it's not a stock query
                    if len(query.split()) == 1 and query_lower in common_words_lower:
                        is_stock_query = False
                    else:
                        is_stock_query = any([
                            # Check for explicit stock-related keywords with potential tickers
                            'snapshot' in query_lower,
                            'price' in query_lower and len(query.split()) <= 5,
                            'stock' in query_lower and len(query.split()) <= 5,
                            'quote' in query_lower,
                            # Single word queries are often tickers (unless common word)
                            len(query.split()) == 1
                        ])
                    
                    if is_stock_query:
                        # 1) Try semantic search via market service (company names or tickers)
                        # But skip if it's just a common word
                        try:
                            if query_lower not in common_words_lower:
                                results = await self.market_service.search_assets(query, 1)
                                if results and isinstance(results, list) and len(results) > 0:
                                    detected_symbol = results[0].get('symbol')
                        except Exception as _:
                            pass

                        # 2) Regex fallback for obvious uppercase tokens in ORIGINAL query
                        # (not uppercased version to avoid false positives)
                        if not detected_symbol:
                            import re
                            m = re.search(r"\b[A-Z]{1,5}\b", query)
                            if m:
                                potential_symbol = m.group(0)
                                # Skip common English words that might appear in uppercase
                                common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'TO', 'FROM', 
                                              'WHERE', 'WHEN', 'HOW', 'WHY', 'WHAT', 'WHO', 'WHICH'}
                                if potential_symbol not in common_words:
                                    detected_symbol = potential_symbol

                    if detected_symbol:
                        # Fetch data directly and format
                        comp = await self.market_service.get_comprehensive_stock_data(detected_symbol)
                        price_payload = comp.get('price_data') or comp
                        news_result = await self.market_service.get_stock_news(detected_symbol, 5)
                        news_items = news_result.get('articles') or news_result.get('news') or news_result.get('items') or []
                        tech_levels = comp.get('technical_levels')
                        company_name = self._get_company_name(detected_symbol)
                        after_hours = {}  # No after-hours data in fallback
                        
                        # Generate bounded LLM insight (Day 4.2)
                        insight_context = {
                            'symbol': detected_symbol,
                            'price_data': price_payload,
                            'technical_levels': tech_levels
                        }
                        llm_insight = await self._generate_bounded_insight(insight_context, max_chars=250)
                        
                        # Add insight to price_payload
                        if price_payload:
                            price_payload['llm_insight'] = llm_insight
                        
                        response_text = MarketResponseFormatter.format_stock_snapshot_ideal(
                            detected_symbol,
                            company_name,
                            price_payload,
                            news_items,
                            tech_levels,
                            after_hours
                        )
                except Exception as e:
                    logger.warning(f"Fallback structured formatting failed: {e}")

                if not response_text:
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

    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Public entry point that routes between Responses API and legacy logic."""
        if self._has_responses_support():
            return await self._process_query_responses(query, conversation_history)
        return await self._process_query_chat(query, conversation_history, stream)

    async def _stream_query_responses(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response using the Responses API while yielding tool progress."""
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        if conversation_history:
            messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": query})

        if self._check_morning_greeting(query, conversation_history):
            yield {"type": "tool_start", "tool": "get_market_overview"}
            overview_result = await self._execute_tool("get_market_overview", {})
            yield {"type": "tool_result", "tool": "get_market_overview", "data": overview_result}
            response_text = MarketResponseFormatter.format_market_brief(overview_result)
            for chunk in response_text.split():
                yield {"type": "content", "text": chunk + " "}
            yield {"type": "done"}
            return

        responses_client = self._responses_client
        if not responses_client:
            async for chunk in self._stream_query_chat(query, conversation_history):
                yield chunk
            return

        response_messages = self._convert_messages_for_responses(messages)

        try:
            response = await responses_client.create(
                model=self.model,
                input=response_messages,
                tools=self._get_tool_schemas(for_responses_api=True),
                temperature=self.temperature,
                max_output_tokens=4000
            )
        except Exception as exc:
            logger.error(f"Responses streaming call failed: {exc}")
            yield {"type": "error", "message": str(exc)}
            yield {"type": "done"}
            return

        collected_tool_calls: List[Dict[str, Any]] = []
        tool_results: Dict[str, Any] = {}

        required_action = getattr(response, "required_action", None)
        while required_action:
            submit = getattr(required_action, "submit_tool_outputs", None)
            if submit is None and isinstance(required_action, dict):
                submit = required_action.get("submit_tool_outputs")
            tool_calls = getattr(submit, "tool_calls", None)
            if tool_calls is None and isinstance(submit, dict):
                tool_calls = submit.get("tool_calls")

            tool_outputs_payload = []
            if tool_calls:
                for tool_call in tool_calls:
                    function = getattr(tool_call, "function", None)
                    if function is None and isinstance(tool_call, dict):
                        function = tool_call.get("function", {})
                    function = function or {}
                    arguments_json = getattr(function, "arguments", None)
                    if arguments_json is None and isinstance(function, dict):
                        arguments_json = function.get("arguments", "{}")
                    tool_name = getattr(function, "name", None)
                    if tool_name is None and isinstance(function, dict):
                        tool_name = function.get("name")
                    tool_name = tool_name or ""

                    try:
                        arguments = json.loads(arguments_json or "{}") if arguments_json is not None else {}
                    except json.JSONDecodeError:
                        arguments = {}

                    call_id = getattr(tool_call, "id", None)
                    if call_id is None and isinstance(tool_call, dict):
                        call_id = tool_call.get("id")

                    collected_tool_calls.append({
                        "id": call_id,
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(arguments)
                        }
                    })

                    tools_used.append(tool_name)
                    yield {"type": "tool_start", "tool": tool_name, "arguments": arguments}
                    result = await self._execute_tool_with_timeout(tool_name, arguments)
                    tool_results[tool_name] = result
                    yield {"type": "tool_result", "tool": tool_name, "data": result}

                    tool_outputs_payload.append({
                        "tool_call_id": call_id,
                        "output": json.dumps(result)
                    })

                submit_method = getattr(responses_client, "submit_tool_outputs", None)
                if submit_method and tool_outputs_payload:
                    try:
                        response = await submit_method(
                            response_id=getattr(response, "id", None),
                            tool_outputs=tool_outputs_payload
                        )
                    except Exception as exc:
                        logger.error(f"Failed to submit tool outputs while streaming: {exc}")
                        break
                else:
                    break

            required_action = getattr(response, "required_action", None)

        tools_used = list(dict.fromkeys(tools_used))

        response_text = self._extract_response_text(response)
        structured_payload = await self._generate_structured_summary(query, tools_used, tool_results)
        if not structured_payload:
            structured_payload = self._extract_structured_payload(response)

        formatted_response = None
        if collected_tool_calls and tool_results:
            formatted_response = await self._format_tool_response(
                collected_tool_calls,
                tool_results,
                messages
            )

        if formatted_response:
            response_text = formatted_response

        if response_text:
            for chunk in response_text.split():
                yield {"type": "content", "text": chunk + " "}

        if structured_payload:
            yield {"type": "structured", "data": structured_payload, "tools_used": tools_used}

        yield {"type": "done"}

    async def stream_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Public streaming entrypoint that prefers the Responses API."""
        if self._has_responses_support():
            async for chunk in self._stream_query_responses(query, conversation_history):
                yield chunk
            return

        async for chunk in self._stream_query_chat(query, conversation_history):
            yield chunk

    async def _stream_query_chat(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses with TRUE streaming and progressive tool execution.
        Implements Phase 1 of OpenAI response format migration.
        
        Yields:
            Dict with type and data for each chunk:
            - {"type": "content", "text": str} - Content chunks
            - {"type": "tool_start", "tool": str} - Tool execution started
            - {"type": "tool_result", "tool": str, "data": dict} - Tool completed
            - {"type": "done"} - Stream complete
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]
            
            if conversation_history:
                messages.extend(conversation_history[-10:])
            
            messages.append({"role": "user", "content": query})
            
            # Check for morning greeting trigger
            is_morning_greeting = self._check_morning_greeting(query, conversation_history)
            
            if is_morning_greeting:
                # Execute market overview and stream formatted result
                yield {"type": "tool_start", "tool": "get_market_overview"}
                overview_result = await self._execute_tool("get_market_overview", {})
                yield {"type": "tool_result", "tool": "get_market_overview", "data": overview_result}
                
                response_text = MarketResponseFormatter.format_market_brief(overview_result)
                for chunk in response_text.split():
                    yield {"type": "content", "text": chunk + " "}
                
                yield {"type": "done"}
                return
            
            # Create streaming response with tools
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tool_schemas(),
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=4000,
                stream=True  # Enable TRUE streaming
            )
            
            # Track state during streaming
            collected_tool_calls = []
            current_tool_call = None
            accumulated_content = ""
            tool_tasks = {}
            
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue
                
                # Stream content as it arrives
                if delta.content:
                    accumulated_content += delta.content
                    yield {"type": "content", "text": delta.content}
                
                # Handle tool calls progressively
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        if tool_call_delta.id:  # New tool call starting
                            if current_tool_call:
                                # Start execution of previous tool
                                tool_name = current_tool_call["function"]["name"]
                                tool_args = json.loads(current_tool_call["function"]["arguments"])
                                
                                yield {"type": "tool_start", "tool": tool_name}
                                
                                # Execute tool asynchronously
                                task = asyncio.create_task(
                                    self._execute_tool_with_timeout(tool_name, tool_args)
                                )
                                tool_tasks[tool_name] = task
                                collected_tool_calls.append(current_tool_call)
                            
                            # Start new tool call
                            current_tool_call = {
                                "id": tool_call_delta.id,
                                "function": {
                                    "name": tool_call_delta.function.name if tool_call_delta.function else "",
                                    "arguments": ""
                                }
                            }
                        
                        # Accumulate function arguments
                        if tool_call_delta.function and tool_call_delta.function.arguments:
                            current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments
            
            # Execute final tool if exists
            if current_tool_call:
                tool_name = current_tool_call["function"]["name"]
                tool_args = json.loads(current_tool_call["function"]["arguments"])
                
                yield {"type": "tool_start", "tool": tool_name}
                
                task = asyncio.create_task(
                    self._execute_tool_with_timeout(tool_name, tool_args)
                )
                tool_tasks[tool_name] = task
                collected_tool_calls.append(current_tool_call)
            
            # Yield tool results as they complete WITHOUT blocking
            if tool_tasks:
                # Create tasks to yield results as they complete
                async def yield_tool_results():
                    results = {}
                    for tool_name, task in tool_tasks.items():
                        try:
                            result = await task
                            results[tool_name] = result
                            # Don't yield here - we'll format after
                        except Exception as e:
                            logger.error(f"Tool {tool_name} failed: {e}")
                            results[tool_name] = {"error": str(e)}
                    return results
                
                # Get tool results
                tool_results = await yield_tool_results()
                
                # Yield results
                for tool_name, result in tool_results.items():
                    yield {"type": "tool_result", "tool": tool_name, "data": result}
                
                # If we had tools and no content yet, format the response
                if collected_tool_calls and not accumulated_content:
                    # Try to format structured response
                    formatted_response = await self._format_tool_response(
                        collected_tool_calls, tool_results, messages
                    )
                    
                    if formatted_response:
                        # Stream formatted response
                        for chunk in formatted_response.split():
                            yield {"type": "content", "text": chunk + " "}
            
            yield {"type": "done"}
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"type": "error", "message": str(e)}
            yield {"type": "done"}
    
    def _check_morning_greeting(self, query: str, conversation_history: Optional[List]) -> bool:
        """Check if query is a morning greeting trigger."""
        try:
            import pytz
            eastern = pytz.timezone('America/New_York')
            current_hour = datetime.now(eastern).hour
            
            if 4 <= current_hour < 11:
                is_first_message = not conversation_history or len(conversation_history) == 0
                normalized = query.lower().strip()
                
                greeting_triggers = [
                    normalized == "good morning",
                    normalized == "gm",
                    normalized.startswith("good morning "),
                    normalized.startswith("morning ")
                ]
                
                if is_first_message and any(greeting_triggers):
                    return True
        except ImportError:
            pass
        
        return False
    
    async def _format_tool_response(
        self,
        tool_calls: List[Dict],
        tool_results: Dict[str, Any],
        messages: List[Dict]
    ) -> Optional[str]:
        """Format tool results into structured response."""
        # Extract symbol if available
        symbol_arg = None
        for tc in tool_calls:
            try:
                args = json.loads(tc["function"]["arguments"])
                if isinstance(args, dict) and 'symbol' in args:
                    symbol_arg = args['symbol']
                    break
            except:
                continue
        
        if not symbol_arg:
            return None
        
        # Try to format with available data
        if 'get_stock_price' in tool_results or 'get_comprehensive_stock_data' in tool_results:
            try:
                price_payload = {}
                if 'get_comprehensive_stock_data' in tool_results:
                    raw_comp = tool_results.get('get_comprehensive_stock_data', {})
                    comp = self._unwrap_tool_result(raw_comp)
                    price_payload = comp.get('price_data', comp) if isinstance(comp, dict) else {}
                elif 'get_stock_price' in tool_results:
                    price_payload = self._unwrap_tool_result(tool_results.get('get_stock_price', {}))
                
                news_items = []
                if 'get_stock_news' in tool_results:
                    news_data = self._unwrap_tool_result(tool_results.get('get_stock_news', {}))
                    news_items = news_data.get('articles', news_data.get('news', []))
                
                tech_levels_source = self._unwrap_tool_result(tool_results.get('get_comprehensive_stock_data', {}))
                tech_levels = {}
                if isinstance(tech_levels_source, dict):
                    tech_levels = tech_levels_source.get('technical_levels', {})
                
                company_name = self._get_company_name(symbol_arg.upper())
                
                # Retrieve relevant knowledge from our vector knowledge base
                knowledge_context = []
                try:
                    # Check for detected patterns in comprehensive data
                    comp_data = tool_results.get('get_comprehensive_stock_data', {})
                    if isinstance(comp_data, dict):
                        patterns_data = comp_data.get('patterns', {})
                        detected_patterns = patterns_data.get('detected', [])
                        
                        # Get knowledge for detected patterns using semantic search
                        for pattern in detected_patterns[:2]:  # Top 2 patterns
                            pattern_type = pattern.get('type', '')
                            if pattern_type:
                                pattern_knowledge = await self.vector_retriever.get_pattern_knowledge(pattern_type)
                                if pattern_knowledge:
                                    knowledge_context.extend(pattern_knowledge[:1])  # Take best match
                    
                    # Get general market analysis knowledge based on price action
                    if price_payload:
                        change_percent = price_payload.get('change_percent', 0)
                        if abs(change_percent) > 3:
                            # Volatile movement - get volatility trading knowledge via semantic search
                            volatility_query = "trading volatile markets breakout momentum risk management"
                            volatility_knowledge = await self.vector_retriever.search_knowledge(
                                volatility_query, 
                                top_k=2, 
                                min_score=0.7
                            )
                            knowledge_context.extend(volatility_knowledge[:1])
                        
                    # Check for technical indicator insights
                    if tech_levels:
                        # Get support/resistance knowledge if levels are present
                        level_query = "support resistance levels technical analysis trading strategy"
                        level_knowledge = await self.vector_retriever.search_knowledge(
                            level_query,
                            top_k=2,
                            min_score=0.7
                        )
                        knowledge_context.extend(level_knowledge[:1])
                        
                except Exception as e:
                    logger.warning(f"Vector knowledge retrieval failed: {e}")
                
                # Format knowledge for LLM context with similarity scores
                knowledge_text = ""
                if knowledge_context:
                    knowledge_text = self.vector_retriever.format_knowledge_for_agent(knowledge_context)
                    logger.info(f"Retrieved {len(knowledge_context)} semantically relevant chunks for {symbol_arg}")
                
                # Generate bounded insight with knowledge context
                context = {
                    'symbol': symbol_arg.upper(),
                    'price_data': price_payload,
                    'technical_levels': tech_levels,
                    'knowledge': knowledge_text  # Add retrieved knowledge
                }
                llm_insight = await self._generate_bounded_insight(context, max_chars=250)
                
                if price_payload:
                    price_payload['llm_insight'] = llm_insight
                
                return MarketResponseFormatter.format_stock_snapshot_ideal(
                    symbol_arg.upper(),
                    company_name,
                    price_payload,
                    news_items,
                    tech_levels,
                    {}
                )
            except Exception as e:
                logger.error(f"Failed to format tool response: {e}")
                return None
        
        return None

    def clear_cache(self):
        """Clear the tool result cache."""
        self.cache.clear()
        logger.info("Agent orchestrator cache cleared")

    def _extract_response_text(self, response: Any) -> str:
        """Safely extract text output from a Responses API response object."""
        if response is None:
            return ""

        # First try direct text attribute (might exist in future API versions)
        text = getattr(response, "text", None)
        if isinstance(text, str):
            return text
            
        # OpenAI Responses API structure: response.output[].content[].text
        output_items = getattr(response, "output", None)
        if isinstance(output_items, list):
            collected = []
            for item in output_items:
                # Each item is a ResponseOutputMessage with content array
                item_content = getattr(item, "content", None)
                if isinstance(item_content, list):
                    for content_block in item_content:
                        # Each content block is ResponseOutputText with text field
                        block_text = getattr(content_block, "text", None)
                        if block_text:
                            collected.append(block_text)
                        # Also check dict format for compatibility
                        elif isinstance(content_block, dict):
                            dict_text = content_block.get("text")
                            if dict_text:
                                collected.append(dict_text)
            if collected:
                return "".join(collected)
        
        # Legacy fallback for older response formats
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, list):
            return "".join(segment or "" for segment in output_text)
        if isinstance(output_text, str):
            return output_text
        
        return ""

    def _extract_structured_payload(self, response: Any) -> Optional[Dict[str, Any]]:
        """Attempt to parse structured JSON payload from response output."""
        if response is None:
            return None

        raw_text = self._extract_response_text(response)
        if not raw_text:
            return None

        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
        return None


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
