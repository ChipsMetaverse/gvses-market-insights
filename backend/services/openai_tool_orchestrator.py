"""
OpenAI Tool Orchestration Layer
===============================
Provides intelligent tool selection, chaining, and optimization for OpenAI Realtime API.
Handles complex tool workflows while maintaining natural conversation flow.
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .openai_tool_mapper import get_openai_tool_mapper

logger = logging.getLogger(__name__)


class ToolPriority(Enum):
    """Priority levels for tool execution."""
    CRITICAL = 1    # Real-time data that must be current
    HIGH = 2        # Important but can tolerate slight delays
    MEDIUM = 3      # Standard priority
    LOW = 4         # Background or cache-friendly operations


@dataclass
class ToolContext:
    """Context information for intelligent tool selection."""
    user_query: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    symbols_mentioned: List[str] = field(default_factory=list)
    intent: Optional[str] = None
    timeframe: Optional[str] = None
    analysis_depth: str = "standard"  # basic, standard, comprehensive


@dataclass
class ToolExecution:
    """Tracks individual tool execution."""
    tool_name: str
    call_id: str
    arguments: Dict[str, Any]
    priority: ToolPriority
    start_time: datetime
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None


class OpenAIToolOrchestrator:
    """
    Orchestrates tool execution for OpenAI Realtime API with intelligent chaining,
    caching, and performance optimization.
    """
    
    def __init__(self):
        self.tool_mapper = None
        self.execution_cache = {}  # Tool result caching
        self.execution_history = []  # Track recent executions
        self.context_analyzer = ContextAnalyzer()
        self.tool_chains = self._initialize_tool_chains()
        
    async def initialize(self):
        """Initialize the orchestrator with tool mapper."""
        if not self.tool_mapper:
            self.tool_mapper = await get_openai_tool_mapper()
            logger.info("Tool orchestrator initialized successfully")
    
    def _initialize_tool_chains(self) -> Dict[str, List[str]]:
        """Define common tool chains for complex queries."""
        return {
            "stock_analysis": [
                "get_stock_quote",
                "get_stock_history", 
                "get_technical_indicators",
                "get_analyst_ratings"
            ],
            "market_overview": [
                "get_market_overview",
                "get_market_movers",
                "get_sector_performance"
            ],
            "news_analysis": [
                "get_stock_news",
                "get_market_news", 
                "get_cnbc_sentiment"
            ],
            "comprehensive_stock": [
                "get_stock_quote",
                "get_stock_history",
                "get_stock_news",
                "get_technical_indicators",
                "get_analyst_ratings",
                "get_insider_trading"
            ],
            "crypto_analysis": [
                "get_crypto_price",
                "get_crypto_market_data",
                "get_defi_data"
            ],
            "comparison_analysis": [
                "get_stock_quote",  # For each symbol
                "get_technical_indicators",  # For each symbol
                "get_sector_performance"  # Overall context
            ]
        }
    
    async def orchestrate_tools(
        self, 
        context: ToolContext,
        requested_tools: List[Dict[str, Any]] = None
    ) -> List[ToolExecution]:
        """
        Orchestrate tool execution based on context and requested tools.
        
        Args:
            context: User query context and intent
            requested_tools: Explicit tool requests from OpenAI
            
        Returns:
            List of tool executions with results
        """
        if not self.tool_mapper:
            await self.initialize()
        
        try:
            # Analyze context to determine optimal tool chain
            if requested_tools:
                # Use explicit tool requests from OpenAI
                tool_plan = self._create_execution_plan_from_requests(requested_tools, context)
            else:
                # Intelligent tool selection based on context
                tool_plan = await self._create_intelligent_execution_plan(context)
            
            logger.info(f"Executing {len(tool_plan)} tools for query: {context.user_query}")
            
            # Execute tools with dependency management
            results = await self._execute_tool_plan(tool_plan)
            
            # Update execution history
            self._update_execution_history(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Tool orchestration failed: {e}")
            return []
    
    def _create_execution_plan_from_requests(
        self,
        tool_requests: List[Dict[str, Any]],
        context: ToolContext
    ) -> List[ToolExecution]:
        """Create execution plan from explicit OpenAI tool requests."""
        plan = []
        
        for i, request in enumerate(tool_requests):
            tool_name = request.get("name", "")
            arguments = request.get("arguments", {})
            call_id = request.get("call_id", f"req_{i}")
            
            # Determine priority based on tool type
            priority = self._determine_tool_priority(tool_name, context)
            
            execution = ToolExecution(
                tool_name=tool_name,
                call_id=call_id,
                arguments=arguments,
                priority=priority,
                start_time=datetime.now()
            )
            
            plan.append(execution)
        
        return plan
    
    async def _create_intelligent_execution_plan(self, context: ToolContext) -> List[ToolExecution]:
        """Create intelligent tool execution plan based on context analysis."""
        intent = await self.context_analyzer.analyze_intent(context)
        context.intent = intent
        
        # Select appropriate tool chain
        tool_chain = self._select_tool_chain(intent, context)
        
        plan = []
        for i, tool_name in enumerate(tool_chain):
            # Generate arguments based on context
            arguments = self._generate_tool_arguments(tool_name, context)
            
            # Skip if no valid arguments (tool not applicable)
            if not arguments:
                continue
            
            priority = self._determine_tool_priority(tool_name, context)
            
            execution = ToolExecution(
                tool_name=tool_name,
                call_id=f"auto_{i}_{tool_name}",
                arguments=arguments,
                priority=priority,
                start_time=datetime.now()
            )
            
            plan.append(execution)
        
        return plan
    
    def _select_tool_chain(self, intent: str, context: ToolContext) -> List[str]:
        """Select the most appropriate tool chain for the given intent."""
        # Map intents to tool chains
        intent_mapping = {
            "stock_analysis": "comprehensive_stock",
            "price_query": ["get_stock_quote"],
            "market_overview": "market_overview", 
            "news_request": "news_analysis",
            "crypto_query": "crypto_analysis",
            "comparison": "comparison_analysis",
            "technical_analysis": ["get_technical_indicators", "get_support_resistance"],
            "earnings": ["get_earnings_calendar", "get_analyst_ratings"]
        }
        
        chain_key = intent_mapping.get(intent, "stock_analysis")
        
        if isinstance(chain_key, list):
            return chain_key
        
        return self.tool_chains.get(chain_key, ["get_stock_quote"])
    
    def _generate_tool_arguments(self, tool_name: str, context: ToolContext) -> Dict[str, Any]:
        """Generate appropriate arguments for a tool based on context."""
        args = {}
        
        # Extract symbols from context
        symbols = context.symbols_mentioned or ["SPY"]  # Default to market
        primary_symbol = symbols[0] if symbols else "SPY"
        
        # Common argument patterns
        if "symbol" in tool_name or "stock" in tool_name:
            args["symbol"] = primary_symbol
            
        if "crypto" in tool_name:
            # Handle crypto symbol mapping
            crypto_symbols = [s for s in symbols if "-USD" in s or s in ["BTC", "ETH", "ADA"]]
            if crypto_symbols:
                args["symbol"] = crypto_symbols[0]
            else:
                return {}  # Skip crypto tools if no crypto symbols
        
        if "history" in tool_name:
            days = self._extract_timeframe_days(context.timeframe or "1M")
            args["days"] = days
            
        if "news" in tool_name:
            args["limit"] = 10 if context.analysis_depth == "comprehensive" else 5
            
        if "technical" in tool_name:
            args["indicators"] = ["sma", "rsi", "macd"] if context.analysis_depth == "comprehensive" else ["sma", "rsi"]
            
        # Add symbol if not already present but tool requires it
        tool_schema = self.tool_mapper.schema_cache.get(tool_name, {})
        input_schema = tool_schema.get("inputSchema", {})
        required_fields = input_schema.get("required", [])
        
        if "symbol" in required_fields and "symbol" not in args:
            args["symbol"] = primary_symbol
        
        return args
    
    def _extract_timeframe_days(self, timeframe: str) -> int:
        """Convert timeframe strings to days."""
        timeframe_map = {
            "1D": 1, "1d": 1,
            "1W": 7, "1w": 7,
            "1M": 30, "1m": 30,
            "3M": 90, "3m": 90,
            "6M": 180, "6m": 180,
            "1Y": 365, "1y": 365,
            "YTD": self._get_ytd_days(),
            "ytd": self._get_ytd_days()
        }
        
        return timeframe_map.get(timeframe, 30)  # Default 1 month
    
    def _get_ytd_days(self) -> int:
        """Calculate days since start of year."""
        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)
        return (now - start_of_year).days
    
    def _determine_tool_priority(self, tool_name: str, context: ToolContext) -> ToolPriority:
        """Determine execution priority for a tool."""
        # Critical tools that need real-time data
        critical_tools = ["get_stock_quote", "get_crypto_price", "get_market_overview"]
        
        # High priority tools for immediate needs
        high_priority_tools = ["get_stock_news", "get_market_movers", "get_technical_indicators"]
        
        # Medium priority tools
        medium_priority_tools = ["get_stock_history", "get_analyst_ratings", "get_insider_trading"]
        
        if tool_name in critical_tools:
            return ToolPriority.CRITICAL
        elif tool_name in high_priority_tools:
            return ToolPriority.HIGH
        elif tool_name in medium_priority_tools:
            return ToolPriority.MEDIUM
        else:
            return ToolPriority.LOW
    
    async def _execute_tool_plan(self, plan: List[ToolExecution]) -> List[ToolExecution]:
        """Execute tool plan with dependency management and optimization."""
        # Sort by priority
        plan.sort(key=lambda x: x.priority.value)
        
        # Group by priority for batch execution
        priority_groups = {}
        for execution in plan:
            priority = execution.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(execution)
        
        completed_executions = []
        
        # Execute by priority groups
        for priority in sorted(priority_groups.keys(), key=lambda x: x.value):
            group = priority_groups[priority]
            logger.info(f"Executing {len(group)} {priority.name} priority tools")
            
            # Execute tools in parallel within priority group
            tasks = []
            for execution in group:
                tasks.append(self._execute_single_tool(execution))
            
            # Wait for all tools in this priority group
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for execution, result in zip(group, results):
                if isinstance(result, Exception):
                    execution.error = str(result)
                    logger.error(f"Tool {execution.tool_name} failed: {result}")
                else:
                    execution.result = result
                    execution.duration = (datetime.now() - execution.start_time).total_seconds()
                
                completed_executions.append(execution)
        
        return completed_executions
    
    async def _execute_single_tool(self, execution: ToolExecution) -> Dict[str, Any]:
        """Execute a single tool with caching support."""
        # Check cache first
        cache_key = self._generate_cache_key(execution.tool_name, execution.arguments)
        
        if cache_key in self.execution_cache:
            cached_entry = self.execution_cache[cache_key]
            
            # Check if cache is still valid (5 minutes for quotes, 1 hour for history)
            cache_lifetime = self._get_cache_lifetime(execution.tool_name)
            if datetime.now() - cached_entry["timestamp"] < cache_lifetime:
                logger.info(f"Using cached result for {execution.tool_name}")
                return cached_entry["result"]
        
        # Execute tool via tool mapper
        result = await self.tool_mapper.execute_tool(execution.tool_name, execution.arguments)
        
        # Cache the result
        self.execution_cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now()
        }
        
        # Clean up old cache entries (keep last 100)
        if len(self.execution_cache) > 100:
            oldest_entries = sorted(
                self.execution_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )[:len(self.execution_cache) - 100]
            
            for old_key, _ in oldest_entries:
                del self.execution_cache[old_key]
        
        return result
    
    def _generate_cache_key(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate cache key for tool execution."""
        # Sort arguments for consistent keys
        sorted_args = json.dumps(arguments, sort_keys=True)
        return f"{tool_name}:{sorted_args}"
    
    def _get_cache_lifetime(self, tool_name: str) -> timedelta:
        """Get cache lifetime for different tool types."""
        # Real-time data needs shorter cache
        realtime_tools = ["get_stock_quote", "get_crypto_price", "get_market_movers"]
        
        # News and history can be cached longer
        cacheable_tools = ["get_stock_history", "get_stock_news", "get_analyst_ratings"]
        
        if tool_name in realtime_tools:
            return timedelta(minutes=1)  # Very short cache for real-time data
        elif tool_name in cacheable_tools:
            return timedelta(minutes=30)  # Longer cache for less volatile data
        else:
            return timedelta(minutes=5)  # Default cache lifetime
    
    def _update_execution_history(self, executions: List[ToolExecution]):
        """Update execution history for performance tracking."""
        self.execution_history.extend(executions)
        
        # Keep only recent history (last 50 executions)
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the orchestrator."""
        if not self.execution_history:
            return {"status": "no_data"}
        
        recent_executions = [e for e in self.execution_history if e.duration is not None]
        
        if not recent_executions:
            return {"status": "no_completed_executions"}
        
        successful_executions = [e for e in recent_executions if e.result and not e.error]
        failed_executions = [e for e in recent_executions if e.error]
        
        avg_duration = sum(e.duration for e in successful_executions) / len(successful_executions) if successful_executions else 0
        
        return {
            "total_executions": len(recent_executions),
            "successful_executions": len(successful_executions),
            "failed_executions": len(failed_executions),
            "success_rate": len(successful_executions) / len(recent_executions) * 100,
            "average_duration": round(avg_duration, 2),
            "cache_size": len(self.execution_cache),
            "most_used_tools": self._get_most_used_tools()
        }
    
    def _get_most_used_tools(self) -> List[Tuple[str, int]]:
        """Get the most frequently used tools."""
        tool_counts = {}
        for execution in self.execution_history:
            tool_counts[execution.tool_name] = tool_counts.get(execution.tool_name, 0) + 1
        
        return sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]


class ContextAnalyzer:
    """Analyzes user context to determine intent and optimize tool selection."""
    
    def __init__(self):
        self.intent_patterns = {
            "price_query": [
                r"what'?s?\s+.*?(?:trading|price|worth|cost)",
                r"how much.*?(?:trading|worth|cost)",
                r"price of",
                r"current.*?price",
                r"(?:quote|quotes) for"
            ],
            "market_overview": [
                r"market.*?(?:overview|summary|status)",
                r"how.*?(?:market|markets).*?(?:doing|performing)",
                r"(?:overall|general).*?market",
                r"market.*?(?:conditions|situation)"
            ],
            "news_request": [
                r"news.*?(?:about|on|for)",
                r"what.*?happening.*?(?:with|to)",
                r"latest.*?(?:news|updates|information)",
                r"any.*?news"
            ],
            "technical_analysis": [
                r"technical.*?analysis",
                r"(?:rsi|macd|moving average|support|resistance)",
                r"chart.*?analysis",
                r"indicators"
            ],
            "comparison": [
                r"compare.*?(?:to|with|versus|vs)",
                r"(?:better|worse).*?than",
                r"difference between",
                r"(?:versus|vs).*?"
            ],
            "crypto_query": [
                r"(?:bitcoin|btc|ethereum|eth|crypto|cryptocurrency)",
                r"digital.*?(?:currency|asset)",
                r"(?:defi|nft|blockchain)"
            ]
        }
    
    async def analyze_intent(self, context: ToolContext) -> str:
        """Analyze user intent from query text."""
        query_lower = context.user_query.lower()
        
        # Extract symbols mentioned in the query
        context.symbols_mentioned = self._extract_symbols(context.user_query)
        
        # Extract timeframe if mentioned
        context.timeframe = self._extract_timeframe(context.user_query)
        
        # Determine analysis depth
        if any(word in query_lower for word in ["comprehensive", "detailed", "full", "complete"]):
            context.analysis_depth = "comprehensive"
        elif any(word in query_lower for word in ["quick", "brief", "simple", "basic"]):
            context.analysis_depth = "basic"
        
        # Match intent patterns
        import re
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    logger.info(f"Detected intent: {intent} from query: {context.user_query}")
                    return intent
        
        # Default intent
        return "stock_analysis"
    
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query text."""
        import re
        
        # Common symbol patterns
        symbols = []
        
        # Direct symbol mentions (2-5 uppercase letters)
        symbol_matches = re.findall(r'\b[A-Z]{2,5}\b', query)
        symbols.extend(symbol_matches)
        
        # Common company name mappings
        company_mappings = {
            "apple": "AAPL",
            "microsoft": "MSFT", 
            "google": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "nvidia": "NVDA",
            "meta": "META",
            "facebook": "META",
            "netflix": "NFLX",
            "bitcoin": "BTC-USD",
            "ethereum": "ETH-USD"
        }
        
        query_lower = query.lower()
        for company, symbol in company_mappings.items():
            if company in query_lower:
                symbols.append(symbol)
        
        # Remove duplicates and return
        return list(set(symbols))
    
    def _extract_timeframe(self, query: str) -> Optional[str]:
        """Extract timeframe from query text."""
        import re
        
        # Timeframe patterns
        timeframe_patterns = {
            r"(?:last|past)\s+(\d+)\s+days?": lambda m: f"{m.group(1)}D",
            r"(?:last|past)\s+week": lambda m: "1W", 
            r"(?:last|past)\s+month": lambda m: "1M",
            r"(?:last|past)\s+(\d+)\s+months?": lambda m: f"{m.group(1)}M",
            r"(?:last|past)\s+year": lambda m: "1Y",
            r"year\s+to\s+date|ytd": lambda m: "YTD",
            r"today": lambda m: "1D",
            r"this\s+week": lambda m: "1W",
            r"this\s+month": lambda m: "1M",
            r"this\s+year": lambda m: "YTD"
        }
        
        query_lower = query.lower()
        for pattern, extractor in timeframe_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                return extractor(match)
        
        return None


# Global instance
_orchestrator = None

async def get_openai_tool_orchestrator() -> OpenAIToolOrchestrator:
    """Get or create the global tool orchestrator instance."""
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = OpenAIToolOrchestrator()
        await _orchestrator.initialize()
    
    return _orchestrator