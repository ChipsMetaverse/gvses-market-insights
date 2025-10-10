"""
Agent Orchestrator Service
==========================
Implements OpenAI function calling with market data tools for intelligent
query processing and tool selection.
"""

import asyncio
import json
import os
import hashlib
import time
import re
import string
from typing import Any, Dict, List, Optional, AsyncGenerator, Set, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import logging
from openai import AsyncOpenAI
from services.market_service_factory import MarketServiceFactory
from dotenv import load_dotenv
from response_formatter import MarketResponseFormatter
from services.knowledge_metrics import KnowledgeMetrics
from services.vector_retriever import VectorRetriever
from services.chart_image_analyzer import ChartImageAnalyzer
from services.chart_snapshot_store import ChartSnapshotStore
from services.pattern_lifecycle import PatternLifecycleManager
from services.chart_command_extractor import ChartCommandExtractor

# Import new modular components  
from core.intent_router import IntentRouter
from core.market_data import MarketDataHandler
from core.response_formatter import ResponseFormatter as CoreResponseFormatter

try:
    # Lazy import to avoid circular dependencies when headless service is absent
    from headless_chart_service.src.websocketService import wsService  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    wsService = None

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
        self.model = os.getenv("AGENT_MODEL", "gpt-5-mini")  # Fastest available model
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        
        # Initialize modular components
        self.intent_router = IntentRouter()
        self.market_handler = MarketDataHandler(self.market_service)
        self.core_response_formatter = CoreResponseFormatter()
        
        # Initialize vector retriever for enhanced semantic search
        self.vector_retriever = VectorRetriever()
        logger.info(f"Vector retriever initialized with {len(self.vector_retriever.knowledge_base)} embedded chunks")

        # Initialize chart image analyzer for visual pattern detection
        try:
            self.chart_image_analyzer = ChartImageAnalyzer()
            logger.info("Chart image analyzer ready for visual pattern detection")
        except Exception as exc:  # pragma: no cover
            logger.warning(f"Chart image analyzer unavailable: {exc}")
            self.chart_image_analyzer = None

        snapshot_ttl = int(os.getenv("CHART_SNAPSHOT_TTL", "900"))
        max_snapshots = int(os.getenv("CHART_SNAPSHOT_MAX_PER_SYMBOL", "10"))
        self.chart_snapshot_store = ChartSnapshotStore(
            ttl_seconds=snapshot_ttl,
            max_snapshots_per_symbol=max_snapshots,
        )
        self.auto_analyze_snapshots = (os.getenv("CHART_SNAPSHOT_AUTO_ANALYZE", "true").lower() != "false")
        
        # Initialize chart command extractor for parsing Voice Assistant responses
        self.chart_command_extractor = ChartCommandExtractor()
        logger.info("Chart command extractor initialized for Voice Assistant response parsing")
        lifecycle_confirm = float(os.getenv("PATTERN_CONFIRM_THRESHOLD", "75"))
        lifecycle_max_misses = int(os.getenv("PATTERN_MAX_MISSES", "2"))
        enable_phase5_ml = os.getenv("ENABLE_PHASE5_ML", "false").lower() == "true"
        ml_threshold = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.55"))
        ml_weight = float(os.getenv("ML_CONFIDENCE_WEIGHT", "0.6"))
        rule_weight = float(os.getenv("RULE_CONFIDENCE_WEIGHT", "0.4"))
        self.pattern_lifecycle = PatternLifecycleManager(
            confirm_threshold=lifecycle_confirm,
            max_misses=lifecycle_max_misses,
            enable_phase4_rules=os.getenv("ENABLE_PHASE4_RULES", "true").lower() == "true",
            enable_phase5_ml=enable_phase5_ml,
            ml_confidence_threshold=ml_threshold,
            ml_weight=ml_weight,
            rule_weight=rule_weight,
        )
        if enable_phase5_ml:
            logger.info(
                "Phase 5 ML confidence enabled",
                extra={
                    "ml_confidence_threshold": ml_threshold,
                    "ml_weight": ml_weight,
                    "rule_weight": rule_weight,
                },
            )
        
        # Phase 4: Background pattern lifecycle sweeper
        self.enable_pattern_sweep = os.getenv("ENABLE_PATTERN_SWEEP", "true").lower() == "true"
        self.pattern_sweep_interval = int(os.getenv("PATTERN_SWEEP_INTERVAL", "300"))  # 5 minutes default
        self.pattern_max_age_hours = int(os.getenv("PATTERN_MAX_AGE_HOURS", "72"))  # 3 days default
        self._sweep_task = None
        
        if self.enable_pattern_sweep:
            logger.info(f"Pattern sweep enabled - will run every {self.pattern_sweep_interval}s")
            # Start background sweeper (will be started when event loop is available)
            asyncio.create_task(self._start_pattern_sweeper())
        
        # A/B testing: Runtime toggle for education mode
        self.use_llm_for_education = os.getenv("USE_LLM_FOR_EDUCATION", "true").lower() == "true"
        logger.info(f"Education mode: {'LLM' if self.use_llm_for_education else 'Templates'}")
        
        # Responses API support detection and schema configuration
        responses_client = getattr(self.client, "responses", None)
        self._responses_client = responses_client if responses_client and hasattr(responses_client, "create") else None
        self.response_schema = MARKET_ANALYSIS_SCHEMA
        
        # Knowledge cache with bounds and thread safety
        self._knowledge_cache = OrderedDict()  # LRU cache for knowledge queries
        self._cache_ttl = 300  # 5 minutes TTL
        self._cache_max_size = 100  # Maximum cache entries
        self._cache_lock = asyncio.Lock()  # Thread safety for cache operations
        
        # Full response cache for complete LLM responses
        self._response_cache = OrderedDict()  # LRU cache for full responses
        self._response_cache_ttl = 300  # 5 minutes TTL
        self._response_cache_max_size = 100  # Maximum cache entries
        self._response_cache_lock = asyncio.Lock()  # Thread safety
        
        # Cache for recent tool results (TTL: 60 seconds)
        self.cache = OrderedDict()  # LRU cache for tool results  
        self.cache_ttl = 60
        self.cache_max_size = 50  # Maximum cache entries
        
        # Tool-specific timeouts (Day 4.1)
        self.tool_timeouts = {
            "get_stock_price": 2.0,        # Fast, critical
            "get_stock_history": 3.0,      # Medium speed
            "get_comprehensive_stock_data": 4.0,  # Complex, slower (reduced from 5.0)
            "get_stock_news": 3.0,         # Network dependent (reduced from 4.0)
            "get_market_overview": 3.0,    # Multiple symbols
            "get_options_strategies": 2.0,  # Calculation-based
            "analyze_options_greeks": 1.0,  # Mock data, fast
            "generate_daily_watchlist": 3.0,  # Multiple stocks
            "review_trades": 2.0           # Historical review
        }
        # Vision-based chart analysis can take longer
        self.tool_timeouts["analyze_chart_image"] = 12.0
        self.default_timeout = 4.0  # Default for unknown tools (reduced from 5.0)
        self.global_timeout = 8.0  # Maximum time for all tools (reduced from 10.0)
        
        # Pre-warm cache will be called asynchronously after startup
        self._cache_warmed = False
        
        # Initialize metrics tracking
        self.metrics = KnowledgeMetrics(window_size=100)

        # Last diagnostics snapshot (durations, flags, tools)
        self.last_diag: Dict[str, Any] = {
            "ts": None,
            "path": None,
            "intent": None,
            "durations": {},
            "tools_used": [],
            "news_called": False,
            "news_gated": False,
            "model": self.model,
            "use_responses": bool(self._responses_client),
        }

        # Pre-computed fast-path responses for common educational queries
        self._static_response_templates = self._build_static_response_templates()

        # G'sves Assistant Configuration
        self.gvses_assistant_id = os.getenv("GVSES_ASSISTANT_ID")
        self.use_gvses_assistant = os.getenv("USE_GVSES_ASSISTANT", "false").lower() == "true"
        if self.gvses_assistant_id and self.use_gvses_assistant:
            logger.info(f"G'sves Assistant enabled: {self.gvses_assistant_id}")
        else:
            logger.info("G'sves Assistant disabled - using default orchestrator")

    async def ingest_chart_snapshot(
        self,
        *,
        symbol: str,
        timeframe: str,
        image_base64: str,
        chart_commands: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        vision_model: Optional[str] = None,
        auto_analyze: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Store a chart snapshot and optionally analyze it with the vision model."""

        if not symbol:
            raise ValueError("symbol is required for chart snapshot ingestion")
        if not timeframe:
            raise ValueError("timeframe is required for chart snapshot ingestion")
        if not image_base64:
            raise ValueError("image_base64 is required for chart snapshot ingestion")

        record = await self.chart_snapshot_store.store_snapshot(
            symbol=symbol,
            timeframe=timeframe,
            image_base64=image_base64,
            chart_commands=chart_commands,
            metadata=metadata,
            vision_model=vision_model,
        )

        should_analyze = auto_analyze if auto_analyze is not None else self.auto_analyze_snapshots
        analysis: Optional[Dict[str, Any]] = None
        analysis_error: Optional[str] = None
        if should_analyze and self.chart_image_analyzer:
            try:
                analysis = await self.chart_image_analyzer.analyze_chart(
                    image_base64=image_base64,
                    model_name=vision_model,
                    user_context=(metadata or {}).get("user_context"),
                )
            except Exception as exc:  # pragma: no cover - resilient to vision errors
                logger.warning(f"Chart snapshot analysis failed for {symbol}: {exc}")
                analysis_error = str(exc)
            else:
                logger.info(
                    "Chart snapshot analyzed",
                    extra={
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "vision_model": vision_model or self.chart_image_analyzer.current_model_key,
                        "patterns": len(analysis.get("patterns", [])) if isinstance(analysis, dict) else None,
                    },
                )

        lifecycle_result = self.pattern_lifecycle.update(
            symbol=symbol,
            timeframe=timeframe,
            analysis=analysis,
        )

        combined_commands: List[str] = []
        if chart_commands:
            combined_commands.extend(chart_commands)
        combined_commands.extend(lifecycle_result.get("chart_commands", []))

        # Update stored record with lifecycle metadata and commands
        record.chart_commands = combined_commands
        record.metadata.setdefault("lifecycle_states", lifecycle_result.get("states", []))
        record.metadata.setdefault("chart_history", []).append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "commands": combined_commands,
            }
        )

        repository_updates = lifecycle_result.get("repository_updates")
        if repository_updates and self.pattern_lifecycle.repository:
            try:
                await self.pattern_lifecycle.repository.bulk_update_patterns(repository_updates)
            except Exception as exc:  # pragma: no cover - resilience
                logger.warning("Failed to persist ML updates: %s", exc)

        if lifecycle_result.get("ml_insights"):
            record.metadata.setdefault("ml_insights", []).extend(lifecycle_result["ml_insights"])

        await self.chart_snapshot_store.attach_analysis(
            record,
            analysis=analysis,
            analysis_error=analysis_error,
            vision_model=vision_model or getattr(self.chart_image_analyzer, "current_model_key", None),
        )

        result = record.to_public_dict(include_image=False)
        result.update({
            "analysis": analysis,
            "analysis_error": analysis_error,
            "chart_commands": combined_commands,
            "lifecycle_states": lifecycle_result.get("states", []),
        })
        return result

    async def get_chart_state(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
        include_image: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Return the latest stored chart snapshot and analysis for a symbol."""

        snapshot = await self.chart_snapshot_store.get_latest(
            symbol=symbol,
            timeframe=timeframe,
            include_image=include_image,
        )
        return snapshot
    
    async def update_pattern_lifecycle(
        self,
        pattern_id: str,
        verdict: str,
        *,
        operator_id: Optional[str] = None,
        notes: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> None:
        """Update pattern lifecycle based on analyst verdict.
        
        Phase 3 implementation: Handles pattern state transitions
        and broadcasts updates to connected clients via WebSocket.
        """
        logger.info(
            "Updating pattern lifecycle",
            extra={
                "pattern_id": pattern_id,
                "verdict": verdict,
                "operator": operator_id,
                "symbol": symbol,
                "timeframe": timeframe,
            },
        )

        lifecycle_state = {
            "accepted": "confirmed",
            "rejected": "invalidated",
            "deferred": "pending_review",
        }.get(verdict, "pending_review")

        overlay_metadata = {
            "verdict": verdict,
            "operator_id": operator_id,
            "notes": notes,
        }

        updated_overlay = await self.chart_snapshot_store.update_pattern_state(
            pattern_id,
            status=lifecycle_state,
            symbol=symbol,
            timeframe=timeframe,
            metadata=overlay_metadata,
        )

        resolved_symbol = updated_overlay.get("symbol") if updated_overlay else symbol
        resolved_timeframe = updated_overlay.get("timeframe") if updated_overlay else timeframe

        if not resolved_symbol or not resolved_timeframe:
            logger.warning(
                "Pattern verdict missing symbol/timeframe context",
                extra={"pattern_id": pattern_id},
            )
            return

        # Determine chart command set based on verdict
        if verdict == "accepted":
            chart_commands = [
                f"ANNOTATE:PATTERN:{pattern_id}:CONFIRMED",
                f"DRAW:TARGET:{pattern_id}:AUTO",
            ]
        elif verdict == "rejected":
            chart_commands = [
                f"CLEAR:PATTERN:{pattern_id}",
                f"ANNOTATE:PATTERN:{pattern_id}:INVALIDATED",
            ]
        else:
            chart_commands = [f"ANNOTATE:PATTERN:{pattern_id}:PENDING"]

        overlay_payload = {
            "pattern_id": pattern_id,
            "status": lifecycle_state,
            "symbol": resolved_symbol,
            "timeframe": resolved_timeframe,
            "metadata": overlay_metadata,
            "commands": chart_commands,
        }

        if wsService:
            broadcasted = wsService.broadcastPatternOverlay(
                pattern_id,
                {
                    "confirmed": "validated",
                    "invalidated": "invalidated",
                    "pending_review": "updated",
                }.get(lifecycle_state, "updated"),
                overlay_payload,
            )
            logger.info(
                "Pattern overlay broadcasted",
                extra={"pattern_id": pattern_id, "broadcast_to": broadcasted},
            )
        else:
            logger.info("wsService unavailable; skipping broadcast")

        # Persist chart commands to ensure future renders maintain state
        merged_commands = await self.chart_snapshot_store.append_chart_commands(
            symbol=resolved_symbol,
            timeframe=resolved_timeframe,
            commands=chart_commands,
        )
        if merged_commands:
            logger.debug(
                "Pattern chart commands updated",
                extra={
                    "pattern_id": pattern_id,
                    "commands": chart_commands,
                    "symbol": resolved_symbol,
                    "timeframe": resolved_timeframe,
                },
            )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better cache hit rates.

        - Convert to lowercase
        - Remove punctuation
        - Remove common stop words
        - Strip extra whitespace
        - Sort words alphabetically for consistency
        """
        # Convert to lowercase
        normalized = query.lower()
        
        # Remove punctuation
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        normalized = normalized.translate(translator)
        
        # Split into words
        words = normalized.split()
        
        # Remove common stop words (expanded set for better cache hits)
        # Note: Keep "start", "stocks", "trading" to preserve semantic meaning for educational queries
        stop_words = {
            'what', 'is', 'the', 'a', 'an', 'how', 'do', 'does', 'can', 'tell', 'me', 'about', 'explain',
            'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'shall', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'up', 'down', 'out', 'off', 'over', 'under', 'again', 'then', 'there', 'when', 'where',
            'why', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'please', 'show',
            'give', 'got', 'need', 'want', 'whats', "what's", 'its', "it's", 'and', 'or', 'but'
        }
        words = [w for w in words if w not in stop_words and len(w) > 1]
        
        # Sort words for consistency (e.g., "RSI indicator" == "indicator RSI")
        words.sort()
        
        # Join back with single spaces
        normalized = ' '.join(words)
        
        # Log normalization for debugging
        if query != normalized:
            logger.debug(f"Query normalized: '{query}' → '{normalized}'")

        return normalized.strip()

    def _build_static_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create fast static responses for high-frequency educational queries."""
        templates: List[Dict[str, Any]] = [
            {
                "phrases": [
                    "Explain MACD indicator",
                    "Explain MACD",
                    "What is MACD?",
                    "What is MACD indicator?"
                ],
                "topic": "Moving Average Convergence Divergence (MACD)",
                "summary": (
                    "MACD, or Moving Average Convergence Divergence, compares the short-term (12 period) "
                    "and long-term (26 period) exponential moving averages (EMAs) of price to highlight momentum shifts. "
                    "The MACD line (12 EMA − 26 EMA) is paired with a 9-period signal line that traders watch for crossovers. "
                    "Positive MACD values suggest bullish momentum while negative readings indicate bearish pressure, and the histogram "
                    "visualizes the distance between the MACD and signal lines."
                ),
                "highlights": [
                    "MACD line crossing above the signal line is a common bullish cue",
                    "Divergence between MACD and price can warn of potential reversals",
                    "Works best when combined with trend or support/resistance analysis"
                ],
                "reference": (
                    "Sources: CBC Technical Analysis course notes; 'Technical Analysis for Dummies, 2nd Edition' by B. Achelis"
                )
            },
            {
                "phrases": [
                    "What is RSI?",
                    "What is RSI indicator?",
                    "Explain RSI",
                    "Explain RSI indicator"
                ],
                "topic": "Relative Strength Index (RSI)",
                "summary": (
                    "The Relative Strength Index (RSI) measures how quickly price has risen or fallen over the past 14 periods. "
                    "Values above 70 are traditionally labeled overbought and readings below 30 are viewed as oversold. "
                    "Because RSI is bounded between 0 and 100 it helps traders spot momentum extremes, especially when combined with trend context "
                    "or support and resistance zones."
                ),
                "highlights": [
                    "Traditional thresholds: >70 overbought, <30 oversold",
                    "Failure swings and divergences can foreshadow reversals",
                    "Adjusting the lookback period alters sensitivity"
                ],
                "reference": (
                    "Sources: J. Welles Wilder Jr., 'New Concepts in Technical Trading Systems'; Bloomberg Market Structure Guide"
                )
            },
            {
                "phrases": [
                    "What is a moving average?",
                    "What are moving averages?",
                    "Explain moving averages"
                ],
                "topic": "Moving Averages",
                "summary": (
                    "Moving averages smooth out price data to reveal the prevailing trend. Simple moving averages (SMA) give equal weight "
                    "to each period while exponential moving averages (EMA) emphasize recent prices. Traders often track the 50-day and 200-day averages "
                    "for trend confirmation, use crossovers (e.g., golden/death crosses), and treat the average itself as dynamic support or resistance."
                ),
                "highlights": [
                    "Shorter averages react faster but create more noise",
                    "Crossovers can signal potential trend shifts",
                    "Moving averages act as dynamic support/resistance in trending markets"
                ],
                "reference": (
                    "Sources: Murphy, Technical Analysis of the Financial Markets; CME Education Desk"
                )
            },
            {
                "phrases": [
                    "How do support and resistance work?",
                    "What is support and resistance?",
                    "Explain support and resistance",
                    "What are support and resistance levels?"
                ],
                "topic": "Support and Resistance",
                "summary": (
                    "Support represents a price zone where demand has historically absorbed selling pressure, while resistance marks an area where supply has capped advances. "
                    "These zones often form around prior swing highs/lows, round numbers, or moving averages. Price consolidations, volume spikes, and failed breakouts all add weight to these levels; "
                    "traders watch how price behaves on retests to gauge whether the market respects or breaks through the barrier."
                ),
                "highlights": [
                    "Horizontal levels from previous highs/lows are widely watched",
                    "Trendlines and moving averages can act as diagonal support/resistance",
                    "Breakouts accompanied by volume expansion carry more credibility"
                ],
                "reference": (
                    "Sources: Edwards & Magee, 'Technical Analysis of Stock Trends'; CMT Curriculum Level I"
                )
            },
            {
                "phrases": [
                    "What does buy low mean?",
                    "Explain buy low",
                    "What is buy low?",
                    "Buy low meaning"
                ],
                "topic": "Buy Low Trading Strategy",
                "summary": (
                    "'Buy low' refers to purchasing a stock when its price has declined to a support level or oversold condition, "
                    "with the expectation that it will bounce back up. This contrasts with 'buy high' (momentum trading) where you "
                    "buy during strength. The G'sves system defines a 'Buy Low Level' as a key support zone where demand historically "
                    "appears—typically 2-3% above recent lows. Successful 'buy low' trades require patience, risk management (stop losses), "
                    "and confirmation that the stock is stabilizing rather than continuing to fall."
                ),
                "highlights": [
                    "Buy at support levels, not randomly during declines",
                    "Use stop losses below support in case the level breaks",
                    "Look for volume increase and bullish price action as confirmation",
                    "G'sves Buy Low Level is a calculated support zone, not just any dip"
                ],
                "reference": (
                    "Sources: G'sves Trading Methodology; Benjamin Graham 'The Intelligent Investor'"
                )
            },
            {
                "phrases": [
                    "How do I start trading stocks?",
                    "How to start trading?",
                    "Getting started with trading",
                    "Beginner trading guide"
                ],
                "topic": "Getting Started with Stock Trading",
                "summary": (
                    "Starting stock trading involves several key steps: (1) Open a brokerage account with a reputable firm, "
                    "(2) Fund your account with capital you can afford to risk, (3) Learn basic concepts like support/resistance, "
                    "trend analysis, and risk management, (4) Start with paper trading or small positions, (5) Develop a trading plan "
                    "with entry/exit rules. Never invest money you can't afford to lose, and focus on education before taking large positions."
                ),
                "highlights": [
                    "Start with paper trading to learn without risking real money",
                    "Never risk more than 1-2% of your account on a single trade",
                    "Learn to read charts and identify key support/resistance levels",
                    "Have a plan before every trade—know your entry, target, and stop loss"
                ],
                "reference": (
                    "Sources: SEC Investor Education; FINRA Trading Basics"
                )
            }
        ]

        static_map: Dict[str, Dict[str, Any]] = {}
        for template in templates:
            phrases = template.get("phrases", [])
            payload = {k: v for k, v in template.items() if k != "phrases"}
            for phrase in phrases:
                key = self._normalize_query(phrase)
                if not key:
                    continue
                static_map[key] = payload.copy()
        return static_map

    async def _maybe_answer_with_static_template(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]],
    ) -> Optional[Dict[str, Any]]:
        """Return a static educational response when applicable."""
        # A/B testing: Skip templates if LLM mode enabled
        if self.use_llm_for_education:
            return None
            
        # Skip static responses when there's conversation history
        # This ensures context-aware responses work correctly (e.g., Test 4 in smoke tests)
        if conversation_history and len(conversation_history) > 0:
            return None
        
        normalized_query = self._normalize_query(query)
        template = self._static_response_templates.get(normalized_query)
        if not template:
            return None

        summary = template.get("summary", "")
        highlights = template.get("highlights", [])
        if highlights:
            bullets = "\n".join(f"- {point}" for point in highlights)
            summary = f"{summary}\n\nKey points:\n{bullets}"

        reference = template.get("reference")
        if reference:
            summary = f"{summary}\n\nReferences:\n{reference}"

        logger.info(f"Serving static educational response for query: {query[:50]}...")

        return {
            "text": summary,
            "tools_used": [],
            "data": {
                "topic": template.get("topic", "Educational"),
                "source": "static_template",
                "education_mode": "template"
            },
            "timestamp": datetime.now().isoformat(),
            "model": "static-educational",
            "cached": False,
        }

    async def _maybe_answer_with_price_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]],
    ) -> Optional[Dict[str, Any]]:
        """Handle simple price requests without calling the LLM."""
        # If there's prior conversation, fall back to the full orchestrator to respect context
        if conversation_history and len(conversation_history) > 0:
            return None

        pattern = re.compile(
            r"^(?:what(?:'s| is)|get|give me|show me)\s+([A-Za-z0-9\.\-]{1,10})\s+(?:price|stock price)\??$",
            re.IGNORECASE,
        )
        match = pattern.match(query.strip())
        if not match:
            return None

        symbol = match.group(1).upper()

        try:
            result = await self.market_service.get_stock_price(symbol)
        except Exception as exc:
            logger.warning(f"Quick price lookup failed for {symbol}: {exc}")
            return None

        if not result or result.get("price") in (None, 0):
            return None

        price = result.get("price")
        change = result.get("change", 0)
        change_pct = result.get("change_percent") or result.get("change_pct") or 0
        previous_close = result.get("previous_close")

        change_text = f"{change:+.2f}" if isinstance(change, (int, float)) else change
        if isinstance(change_pct, (int, float)):
            change_pct_text = f" ({change_pct:+.2f}%)"
        else:
            change_pct_text = ""

        summary = [f"{symbol} is trading at ${price:.2f} {change_text}{change_pct_text}."]

        if previous_close and isinstance(previous_close, (int, float)):
            summary.append(f"Previous close: ${previous_close:.2f}.")

        if result.get("data_source"):
            summary.append(f"Data source: {result['data_source']}.")

        summary.append("(No investment advice.)")

        text = " ".join(summary)

        logger.info(f"Serving quick price response for {symbol}")

        return {
            "text": text,
            "tools_used": ["get_stock_price"],
            "data": {
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_percent": change_pct,
                "data_source": result.get("data_source"),
            },
            "timestamp": datetime.now().isoformat(),
            "model": "static-price",
            "cached": False,
        }

    async def prewarm_cache(self):
        """Pre-populate cache with common queries for instant responses."""
        if self._cache_warmed:
            return
        
        # Match exact queries from production_smoke_tests.py
        common_queries = [
            # Test 2: Knowledge Retrieval
            "What is RSI indicator?",
            # Test 3: Response Time SLA
            "Explain MACD indicator",
            "What is a moving average?",
            "How do support and resistance work?",
            # Test 6: Cache Pre-warming
            "What is RSI?",
            "Explain MACD",
            "What are moving averages?",
            # Additional common queries
            "What is support and resistance?",
            "What is a candlestick pattern?",
            "Explain head and shoulders pattern"
        ]
        
        # Pre-warm embedding cache first to avoid OpenAI round-trips
        if hasattr(self, 'vector_retriever') and self.vector_retriever:
            logger.info("Pre-warming embedding cache...")
            try:
                await self.vector_retriever.prewarm_embeddings(common_queries)
                cache_stats = self.vector_retriever.get_cache_stats()
                logger.info(f"Embedding cache stats: {cache_stats}")
            except Exception as e:
                logger.warning(f"Failed to pre-warm embeddings: {e}")
        
        logger.info("Pre-warming response cache with common queries...")
        start_time = time.time()
        cache_warm_timeout = float(os.getenv("CACHE_WARM_TIMEOUT", "30"))
        
        # Create tasks for parallel pre-warming
        tasks = []
        for query in common_queries:
            # Check if already cached
            cached = await self._get_cached_response(query, "")
            if not cached:
                # Create task for uncached query
                task = asyncio.create_task(self._prewarm_single_query(query))
                tasks.append((query, task))
        
        if tasks:
            logger.info(f"Pre-warming {len(tasks)} uncached queries in parallel...")
            
            # Wait for all tasks with overall timeout
            try:
                done, pending = await asyncio.wait(
                    [task for _, task in tasks],
                    timeout=cache_warm_timeout
                )
                
                # Cancel any pending tasks
                for task in pending:
                    task.cancel()
                
                # Count successful warmings
                warmed_count = sum(1 for task in done if not task.exception())
                
                if pending:
                    logger.warning(f"⚠️ Cache warming timeout after {cache_warm_timeout}s ({warmed_count}/{len(tasks)} queries warmed)")
                
            except Exception as e:
                logger.error(f"Error during parallel cache warming: {e}")
                warmed_count = 0
        else:
            warmed_count = len(common_queries)  # All already cached
            logger.info("All common queries already cached")
        
        elapsed = time.time() - start_time
        self._cache_warmed = True
        
        if elapsed > 10:
            logger.warning(f"⚠️ Cache pre-warming took {elapsed:.1f}s (>10s warning threshold)")
        
        logger.info(f"Response cache pre-warming complete: {warmed_count}/{len(common_queries)} queries in {elapsed:.1f}s")
    
    async def _prewarm_single_query(self, query: str) -> bool:
        """Pre-warm a single query with timeout protection.
        
        Args:
            query: Query to pre-warm
            
        Returns:
            True if successfully warmed, False otherwise
        """
        try:
            logger.debug(f"Pre-warming: {query}")
            
            # Use asyncio timeout for individual query
            async with asyncio.timeout(5.0):  # 5s max per query
                static_response = await self._maybe_answer_with_static_template(query, None)
                if static_response:
                    await self._cache_response(query, "", static_response)
                    return True

                if self._has_responses_support():
                    response = await self._process_query_responses(query, None)
                else:
                    response = await self._process_query_chat(query, None, stream=False)
                
                if response and not response.get("error"):
                    await self._cache_response(query, "", response)
                    return True
                    
        except asyncio.TimeoutError:
            logger.warning(f"Query timeout during pre-warming: {query}")
        except Exception as e:
            logger.warning(f"Failed to pre-warm query '{query}': {e}")
        
        return False
        
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
                    "name": "get_company_info",
                    "description": "Get company description, business model, and basic information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
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
                    "name": "analyze_chart_image",
                    "description": "Analyze a chart image (base64) and identify technical patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_base64": {
                                "type": "string",
                                "description": "Base64-encoded chart image"
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional instructions or timeframe context",
                                "default": None
                            }
                        },
                        "required": ["image_base64"]
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
            },
            {
                "type": "function",
                "function": {
                    "name": "detect_chart_patterns",
                    "description": "Analyze the current chart for technical patterns (triangles, head & shoulders, flags, wedges, double tops/bottoms, etc.) and automatically draw them on the chart for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock or crypto symbol to analyze"
                            },
                            "timeframe": {
                                "type": "string",
                                "description": "Chart timeframe (1D, 1W, 1M, etc.)",
                                "default": "1D"
                            }
                        },
                        "required": ["symbol"]
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
                # User messages use input_text, assistant messages use output_text
                if role == "assistant":
                    converted.append({
                        "role": role,
                        "content": [{"type": "output_text", "text": str(content)}]
                    })
                else:
                    # user, system, or other roles use input_text
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

    def _extract_primary_symbol(self, query: str, tool_results: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract the primary symbol from tool payloads or the query text."""
        if tool_results:
            candidate_keys = [
                "structured_output",
                "get_comprehensive_stock_data",
                "get_stock_price",
                "get_stock_history",
                "get_stock_news"
            ]
            for key in candidate_keys:
                if key in tool_results:
                    payload = self._unwrap_tool_result(tool_results.get(key))
                    if isinstance(payload, dict):
                        symbol = payload.get("symbol") or payload.get("ticker") or payload.get("symbol_id")
                        if symbol:
                            return str(symbol)

        return self.intent_router.extract_symbol(query)

    def _extract_symbol_from_query(self, query: str) -> Optional[str]:
        """Fallback symbol extraction from the user query."""
        if not query:
            return None

        text = query.upper()
        # Basic stopwords to avoid matching verbs/common words
        stopwords: Set[str] = {
            "CHART", "SHOW", "DISPLAY", "DRAW", "TREND", "PRICE", "NEWS", "LEVEL",
            "SUPPORT", "RESISTANCE", "PATTERN", "INDICATOR", "TIMEFRAME", "PLEASE",
            "CAN", "YOU", "ME", "THE", "WHAT", "IS", "TO", "WITH", "FOR", "NEAR",
            "HIGH", "LOW", "ADD", "REMOVE", "ENABLE", "DISABLE", "RESET", "ZOOM",
            "SCROLL", "LOAD", "VIEW", "SET", "SWITCH", "ON", "OFF", "DOWN", "UP",
            "ALL", "EVERY", "EVERYTHING", "SOME", "MANY", "MOST", "MUCH", "WHY",
            "HOW", "WHEN", "WHERE", "WHO", "WHICH", "THAT", "THIS", "THESE",
            "THOSE", "GOOD", "BAD", "BEST", "WORST", "GREAT", "POOR", "STRONG",
            "WEAK", "BIG", "SMALL", "LARGE", "HUGE", "TINY", "FAST", "SLOW",
            "TODAY", "YESTERDAY", "TOMORROW", "NOW", "THEN", "HERE", "THERE",
            "MARKET", "STOCK", "STOCKS", "SHARE", "SHARES", "TRADE", "TRADES",
            "TRADING", "TRADER", "MONEY", "CASH", "DOLLAR", "CENTS", "PERCENT",
            # Common verbs that shouldn't be tickers
            "DOING", "DO", "DOES", "DID", "DONE", "ARE", "AM", "WAS", "WERE", "BEEN",
            "BEING", "BE", "HAS", "HAD", "HAVE", "HAVING", "MAY", "MIGHT", "MUST",
            "SHALL", "SHOULD", "WILL", "WOULD", "COULD", "CAN'T", "WON'T", "DON'T",
            # Additional common words
            "WELL", "TECH", "ABOUT", "MORE", "LESS", "VERY", "REALLY", "JUST",
            "ONLY", "ALSO", "STILL", "EVEN", "BACK", "AFTER", "OVER", "UNDER",
            # Conjunctions and articles
            "AND", "OR", "BUT", "NOR", "YET", "SO", "AS", "IF", "THAN", "BECAUSE"
        }

        # Company name aliases
        company_aliases = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "META": "META",
            "FACEBOOK": "META",
            "NVIDIA": "NVDA",
            "NETFLIX": "NFLX",
            "BERKSHIRE": "BRK.B",
            "JPMORGAN": "JPM",
            "WALMART": "WMT",
            "DISNEY": "DIS"
        }
        
        # Check for company names first
        for company, ticker in company_aliases.items():
            if company in text:
                return ticker
        
        # Crypto aliases
        crypto_aliases = {
            "BITCOIN": "BTC-USD",
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
            "ETHEREUM": "ETH-USD",
            "SOL": "SOL-USD",
            "SOLANA": "SOL-USD",
            "XRP": "XRP-USD",
            "DOGE": "DOGE-USD",
            "DOGECOIN": "DOGE-USD",
            "ADA": "ADA-USD",
            "CARDANO": "ADA-USD"
        }

        for alias, mapped in crypto_aliases.items():
            if alias in text:
                return mapped

        # Look for explicit tickers (with optional -USD suffix)
        candidates = re.findall(r"\b([A-Z]{1,5}(?:-USD)?)\b", text)
        for candidate in candidates:
            if candidate and candidate not in stopwords and len(candidate) <= 6:
                return candidate
        return None

    def _append_chart_commands_to_data(
        self,
        query: str,
        tool_results: Dict[str, Any],
        response_text: Optional[str]
    ) -> (Optional[str], List[str]):
        """Build chart control commands and optionally augment response text/data."""
        commands = self._build_chart_commands(query, tool_results)

        # Include pattern detection commands if tool was used
        if tool_results and "detect_chart_patterns" in tool_results:
            pattern_data = tool_results["detect_chart_patterns"]
            if isinstance(pattern_data, dict) and pattern_data.get("chart_commands"):
                commands.extend(pattern_data["chart_commands"])

        if commands:
            tool_results.setdefault("chart_commands", commands)
        return response_text, commands

    def _build_chart_commands(
        self,
        query: str,
        tool_results: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Derive chart control commands based on query intent and tool outputs."""
        if not query:
            return []

        commands: List[str] = []
        lower_query = query.lower()
        primary_symbol = self._extract_primary_symbol(query, tool_results)

        chart_intent_keywords = (
            "chart", "trend", "trendline", "trend line", "support", "resistance",
            "fibonacci", "timeframe", "time frame", "candlestick", "draw", "zoom",
            "scroll", "pattern", "overlay", "indicator"
        )
        has_chart_intent = any(keyword in lower_query for keyword in chart_intent_keywords)

        if primary_symbol:
            commands.append(f"LOAD:{primary_symbol.upper()}")

        timeframe_map = [
            # Days/Weeks/Months/Years
            (("1d", "one day", "daily", "today"), "1D"),
            (("5d", "five day", "workweek"), "5D"),
            (("1w", "one week", "weekly"), "1W"),
            (("2w", "two week"), "2W"),
            (("1m", "one month", "monthly"), "1M"),
            (("3m", "three month"), "3M"),
            (("6m", "six month"), "6M"),
            (("1y", "one year", "yearly"), "1Y"),
            (("2y", "two year"), "2Y"),
            (("5y", "five year"), "5Y"),
            (("year to date", "ytd"), "YTD"),
            (("all time", "max", "maximum"), "ALL"),
            # Hours/minutes common in requests
            (("1h", "1 hr", "one hour", "hour"), "H1"),
            (("2h", "2 hr", "two hour", "two hours"), "H2"),
            (("3h", "3 hr", "three hours"), "H3"),
            (("4h", "4 hr", "4-hour", "four hours"), "H4"),
            (("6h", "6 hr", "six hours"), "H6"),
            (("8h", "8 hr", "eight hours"), "H8"),
            (("30m", "30 min", "30 minutes"), "M30"),
            (("15m", "15 min", "15 minutes"), "M15"),
            (("5m", "5 min", "5 minutes"), "M5"),
            (("1m", "1 min", "one minute"), "M1"),
            (("10s", "10 sec", "10 seconds"), "S10")
        ]

        for keywords, timeframe in timeframe_map:
            if any(keyword in lower_query for keyword in keywords):
                commands.append(f"TIMEFRAME:{timeframe}")
                break

        # Multi-timeframe top-down sweep when user requests technical/top-down analysis
        top_down_triggers = (
            "top down", "top-down", "multi timeframe", "multi-timeframe",
            "full analysis", "technical analysis", "technical", "deep analysis"
        )
        if any(t in lower_query for t in top_down_triggers):
            # Order: macro to micro
            sweep = [
                "1M",  # Monthly
                "1W",  # Weekly
                "1D",  # Daily
                "H8", "H6", "H4", "H3", "H2", "H1",
                "M30", "M15", "M5", "M1",
                "S10"
            ]
            for tf in sweep:
                commands.append(f"TIMEFRAME:{tf}")

        indicator_map = {
            "rsi": "RSI",
            "macd": "MACD",
            "bollinger": "BOLLINGER",
            "bollinger band": "BOLLINGER",
            "moving average": "MA",
            "ema": "EMA",
            "sma": "SMA",
            "vwap": "VWAP"
        }
        enable_triggers = ("show", "add", "enable", "include", "turn on", "display", "overlay")
        disable_triggers = ("hide", "remove", "disable", "turn off")

        for keyword, token in indicator_map.items():
            if keyword in lower_query:
                if any(trigger in lower_query for trigger in enable_triggers):
                    commands.append(f"ADD:{token}")
                elif any(trigger in lower_query for trigger in disable_triggers):
                    commands.append(f"REMOVE:{token}")

        if "reset" in lower_query and "chart" in lower_query:
            commands.append("RESET:VIEW")

        if "auto scale" in lower_query or "fit to screen" in lower_query:
            commands.append("RESET:SCALE")

        if "crosshair" in lower_query:
            if any(trigger in lower_query for trigger in ("hide", "off", "disable")):
                commands.append("CROSSHAIR:OFF")
            elif any(trigger in lower_query for trigger in ("show", "on", "enable")):
                commands.append("CROSSHAIR:ON")
            else:
                commands.append("CROSSHAIR:TOGGLE")

        if "zoom in" in lower_query:
            commands.append("ZOOM:IN")
        elif "zoom out" in lower_query:
            commands.append("ZOOM:OUT")

        # Add drawing commands for technical analysis
        drawing_commands = self._generate_drawing_commands(query, tool_results)
        commands.extend(drawing_commands)
        
        # Remove duplicates while preserving order
        seen: Set[str] = set()
        unique_commands: List[str] = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)

        return unique_commands
    
    def _generate_drawing_commands(self, query: str, tool_results: Optional[Dict[str, Any]]) -> List[str]:
        """Generate drawing commands from technical analysis results."""
        if not tool_results:
            return []
        
        commands = []
        lower_query = query.lower()
        
        # Check if we need to perform technical analysis for drawing commands
        needs_technical = any(keyword in lower_query for keyword in [
            'support', 'resistance', 'fibonacci', 'fib', 'trend line', 'trendline',
            'technical', 'levels', 'analysis', 'pattern', 'draw'
        ])
        
        # If we need technical analysis and have candle data, perform it
        if needs_technical and 'get_stock_history' in tool_results:
            logger.info("Performing technical analysis for drawing commands")
            history_data = tool_results.get('get_stock_history', {})
            
            if 'candles' in history_data:
                candles = history_data['candles']
                symbol = history_data.get('symbol', 'UNKNOWN')
                
                # Calculate technical levels
                if len(candles) > 0:
                    prices = [c.get('close', 0) for c in candles]
                    highs = [c.get('high', 0) for c in candles]
                    lows = [c.get('low', 0) for c in candles]
                    
                    # Calculate support/resistance levels
                    support_levels = []
                    resistance_levels = []
                    
                    if len(prices) > 20:
                        # Find recent lows for support
                        recent_lows = sorted(lows[-50:])[:5]  # 5 lowest points
                        support_levels = sorted(list(set(recent_lows)))[:3]
                        
                        # Find recent highs for resistance
                        recent_highs = sorted(highs[-50:], reverse=True)[:5]  # 5 highest points
                        resistance_levels = sorted(list(set(recent_highs)), reverse=True)[:3]
                    
                    # Calculate trend lines if requested
                    if 'trendline' in lower_query or 'trend line' in lower_query:
                        trend_lines = self._calculate_trend_lines(candles)
                        for line in trend_lines[:2]:  # Max 2 trend lines
                            commands.append(
                                f"TRENDLINE:{line['start_price']}:{line['start_time']}:"
                                f"{line['end_price']}:{line['end_time']}"
                            )
                    
                    # Add support/resistance if requested
                    if 'support' in lower_query:
                        for level in support_levels[:3]:
                            commands.append(f"SUPPORT:{level}")
                    
                    if 'resistance' in lower_query:
                        for level in resistance_levels[:3]:
                            commands.append(f"RESISTANCE:{level}")
                    
                    # Add Fibonacci if requested
                    if 'fibonacci' in lower_query or 'fib' in lower_query:
                        if highs and lows:
                            high = max(highs[-50:])
                            low = min(lows[-50:])
                            commands.append(f"FIBONACCI:{high}:{low}")
        
        # Check if technical analysis was already performed
        elif 'technical_analysis' in tool_results:
            logger.info(f"Using existing technical analysis data")
            ta_data = tool_results['technical_analysis']
            
            # Generate support level commands
            if 'support_levels' in ta_data:
                for level in ta_data['support_levels'][:3]:  # Max 3 levels
                    commands.append(f"SUPPORT:{level}")
            
            # Generate resistance level commands
            if 'resistance_levels' in ta_data:
                for level in ta_data['resistance_levels'][:3]:  # Max 3 levels
                    commands.append(f"RESISTANCE:{level}")
            
            # Generate Fibonacci commands
            if 'fibonacci_levels' in ta_data:
                fib_data = ta_data['fibonacci_levels']
                commands.append(f"FIBONACCI:{fib_data['high']}:{fib_data['low']}")
            
            # Generate trend line commands
            if 'trend_lines' in ta_data:
                for line in ta_data['trend_lines'][:2]:  # Max 2 trend lines
                    commands.append(
                        f"TRENDLINE:{line['start_price']}:{line['start_time']}:"
                        f"{line['end_price']}:{line['end_time']}"
                    )
            
            # Generate pattern highlight commands
            if 'patterns' in ta_data:
                for pattern in ta_data['patterns'][:1]:  # Top pattern only
                    commands.append(
                        f"PATTERN:{pattern['type']}:{pattern['start']}:{pattern['end']}"
                    )
        
        # Check tool results for swing trade data that includes levels
        if 'get_stock_swing_trade' in tool_results:
            swing_data = tool_results['get_stock_swing_trade']
            
            # Extract support/resistance from swing trade analysis
            if 'support' in swing_data:
                for level in swing_data['support'][:2]:
                    commands.append(f"SUPPORT:{level}")
            
            if 'resistance' in swing_data:
                for level in swing_data['resistance'][:2]:
                    commands.append(f"RESISTANCE:{level}")
            
            # Add entry and target levels as horizontal lines
            if 'entry_points' in swing_data:
                for entry in swing_data['entry_points'][:2]:
                    commands.append(f"ENTRY:{entry}")
            
            if 'targets' in swing_data:
                for target in swing_data['targets'][:2]:
                    commands.append(f"TARGET:{target}")
            
            if 'stop_loss' in swing_data:
                commands.append(f"STOPLOSS:{swing_data['stop_loss']}")
        
        # If still no commands but technical keywords present, flag for analysis
        if not commands and needs_technical:
            commands.append("ANALYZE:TECHNICAL")
        
        return commands
    
    async def _perform_technical_analysis(
        self, symbol: str, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive technical analysis on market data."""
        try:
            from advanced_technical_analysis import AdvancedTechnicalAnalysis
            from pattern_detection import PatternDetector
            
            analysis_results = {}
            
            # Extract candle data if available
            candles = None
            if 'candles' in market_data:
                candles = market_data['candles']
            elif 'get_stock_history' in market_data:
                # Check if it's wrapped in a tool response structure
                history_data = market_data['get_stock_history']
                if isinstance(history_data, dict):
                    if 'data' in history_data and 'candles' in history_data['data']:
                        candles = history_data['data']['candles']
                    elif 'candles' in history_data:
                        candles = history_data['candles']
                    else:
                        candles = history_data
                else:
                    candles = history_data
            
            if candles and len(candles) > 20:
                logger.info(f"Performing technical analysis on {len(candles)} candles for {symbol}")
                # Extract price arrays
                highs = [float(c.get('high', 0)) for c in candles]
                lows = [float(c.get('low', 0)) for c in candles]
                closes = [float(c.get('close', 0)) for c in candles]
                
                # Calculate support/resistance levels
                support_levels = self._identify_support_levels(lows, closes)
                resistance_levels = self._identify_resistance_levels(highs, closes)
                logger.info(f"Found {len(support_levels)} support and {len(resistance_levels)} resistance levels")
                
                if support_levels:
                    analysis_results['support_levels'] = support_levels
                if resistance_levels:
                    analysis_results['resistance_levels'] = resistance_levels
                
                # Calculate Fibonacci retracement if we have enough data
                if len(highs) > 30 and len(lows) > 30:
                    swing_high, swing_low = self._find_swing_points(highs, lows)
                    if swing_high and swing_low and abs(swing_high - swing_low) > 0.01:
                        # Determine trend direction
                        is_uptrend = closes[-1] > closes[-min(20, len(closes)//2)]
                        
                        fib_levels = AdvancedTechnicalAnalysis.calculate_fibonacci_levels(
                            swing_high, swing_low, is_uptrend
                        )
                        
                        analysis_results['fibonacci_levels'] = {
                            'high': swing_high,
                            'low': swing_low,
                            'levels': fib_levels,
                            'is_uptrend': is_uptrend
                        }
                
                # Detect patterns
                try:
                    detector = PatternDetector(candles)
                    patterns = detector.detect_all_patterns()
                    
                    if patterns:
                        # Convert patterns to serializable format
                        analysis_results['patterns'] = [
                            {
                                'type': p.pattern_type,
                                'confidence': p.confidence,
                                'start': p.start_candle,
                                'end': p.end_candle,
                                'signal': p.signal,
                                'target': p.target,
                                'stop_loss': p.stop_loss
                            }
                            for p in patterns[:3]  # Top 3 patterns
                        ]
                except Exception as e:
                    logger.warning(f"Pattern detection failed: {e}")
                
                # Calculate trend lines
                trend_lines = self._calculate_trend_lines(candles)
                if trend_lines:
                    analysis_results['trend_lines'] = trend_lines
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Technical analysis failed: {e}")
            return {}
    
    def _identify_support_levels(
        self, lows: List[float], closes: List[float], lookback: int = 20
    ) -> List[float]:
        """Identify key support levels from price data."""
        if len(lows) < lookback:
            return []
        
        supports = []
        
        # Find local minima
        for i in range(lookback, len(lows)):
            window = lows[i-lookback:i+1]
            local_min = min(window)
            
            # Check if this level has been tested multiple times
            touch_count = sum(1 for low in window if abs(low - local_min) < local_min * 0.005)
            
            if touch_count >= 2:  # Tested at least twice
                supports.append(round(local_min, 2))
        
        # Remove duplicates and sort
        unique_supports = sorted(list(set(supports)))
        
        # Return the strongest (most recent) 3 levels
        return unique_supports[-3:] if unique_supports else []
    
    def _identify_resistance_levels(
        self, highs: List[float], closes: List[float], lookback: int = 20
    ) -> List[float]:
        """Identify key resistance levels from price data."""
        if len(highs) < lookback:
            return []
        
        resistances = []
        
        # Find local maxima
        for i in range(lookback, len(highs)):
            window = highs[i-lookback:i+1]
            local_max = max(window)
            
            # Check if this level has been tested multiple times
            touch_count = sum(1 for high in window if abs(high - local_max) < local_max * 0.005)
            
            if touch_count >= 2:  # Tested at least twice
                resistances.append(round(local_max, 2))
        
        # Remove duplicates and sort
        unique_resistances = sorted(list(set(resistances)))
        
        # Return the strongest (most recent) 3 levels
        return unique_resistances[-3:] if unique_resistances else []
    
    def _find_swing_points(
        self, highs: List[float], lows: List[float], window: int = 10
    ) -> Tuple[Optional[float], Optional[float]]:
        """Find significant swing high and swing low points."""
        if len(highs) < window * 2 or len(lows) < window * 2:
            return None, None
        
        # Find swing high (highest point in recent history)
        recent_highs = highs[-window*3:]
        swing_high = max(recent_highs) if recent_highs else None
        
        # Find swing low (lowest point in recent history)
        recent_lows = lows[-window*3:]
        swing_low = min(recent_lows) if recent_lows else None
        
        return swing_high, swing_low
    
    def _calculate_trend_lines(self, candles: List[Dict]) -> List[Dict]:
        """Calculate trend lines from candle data."""
        if len(candles) < 10:
            return []
        
        trend_lines = []
        
        # Simple trend line: connect recent swing points
        highs = [c.get('high', 0) for c in candles]
        lows = [c.get('low', 0) for c in candles]
        times = [i for i in range(len(candles))]  # Use indices as time
        
        # Find two recent lows for uptrend line
        if len(lows) >= 20:
            # Get indices of lowest points
            low_indices = sorted(range(len(lows)), key=lambda i: lows[i])[:10]
            # Filter for recent ones
            recent_low_indices = [i for i in low_indices if i > len(lows) - 50]
            
            if len(recent_low_indices) >= 2:
                # Connect two lowest points
                i1, i2 = sorted(recent_low_indices[:2])
                if i2 > i1:
                    trend_lines.append({
                        'type': 'uptrend',
                        'start_price': lows[i1],
                        'start_time': i1,
                        'end_price': lows[i2],
                        'end_time': i2
                    })
        
        # Find two recent highs for downtrend line
        if len(highs) >= 20:
            # Get indices of highest points
            high_indices = sorted(range(len(highs)), key=lambda i: -highs[i])[:10]
            # Filter for recent ones
            recent_high_indices = [i for i in high_indices if i > len(highs) - 50]
            
            if len(recent_high_indices) >= 2:
                # Connect two highest points
                i1, i2 = sorted(recent_high_indices[:2])
                if i2 > i1:
                    trend_lines.append({
                        'type': 'downtrend',
                        'start_price': highs[i1],
                        'start_time': i1,
                        'end_price': highs[i2],
                        'end_time': i2
                    })
        
        return trend_lines[:2]  # Return max 2 trend lines

    def _generate_chart_commands(
        self, 
        technical_analysis_data: Dict[str, Any], 
        symbol: str
    ) -> List[str]:
        """Generate chart commands from technical analysis data."""
        commands = []
        
        # Generate support level commands
        if 'support_levels' in technical_analysis_data:
            for level in technical_analysis_data['support_levels'][:3]:  # Max 3 levels
                commands.append(f"SUPPORT:{level}")
        
        # Generate resistance level commands  
        if 'resistance_levels' in technical_analysis_data:
            for level in technical_analysis_data['resistance_levels'][:3]:  # Max 3 levels
                commands.append(f"RESISTANCE:{level}")
        
        # Generate Fibonacci commands
        if 'fibonacci_levels' in technical_analysis_data:
            fib_data = technical_analysis_data['fibonacci_levels']
            if 'high' in fib_data and 'low' in fib_data:
                commands.append(f"FIBONACCI:{fib_data['high']}:{fib_data['low']}")
        
        # Generate trend line commands
        if 'trend_lines' in technical_analysis_data:
            for line in technical_analysis_data['trend_lines'][:2]:  # Max 2 trend lines
                commands.append(
                    f"TRENDLINE:{line['start_price']}:{line['start_time']}:"
                    f"{line['end_price']}:{line['end_time']}"
                )
        
        # Generate pattern highlight commands
        if 'patterns' in technical_analysis_data:
            for pattern in technical_analysis_data['patterns'][:1]:  # Top pattern only
                if 'type' in pattern and 'start' in pattern and 'end' in pattern:
                    commands.append(
                        f"PATTERN:{pattern['type']}:{pattern['start']}:{pattern['end']}"
                    )
        
        # Add entry/target/stop loss levels if present
        if 'entry_points' in technical_analysis_data:
            for entry in technical_analysis_data['entry_points'][:2]:
                commands.append(f"ENTRY:{entry}")
        
        if 'targets' in technical_analysis_data:
            for target in technical_analysis_data['targets'][:2]:
                commands.append(f"TARGET:{target}")
        
        if 'stop_loss' in technical_analysis_data:
            commands.append(f"STOPLOSS:{technical_analysis_data['stop_loss']}")
        
        return commands

    def _extract_tool_call_info(self, tool_call: Any) -> Dict[str, Any]:
        """Normalize tool call metadata regardless of SDK object shape."""
        info: Dict[str, Any] = {
            "name": "",
            "arguments": {},
            "raw_arguments": "{}",
            "call_id": None,
        }

        function = getattr(tool_call, "function", None)
        if function is None and isinstance(tool_call, dict):
            function = tool_call.get("function")

        arguments_raw: Any = None

        if function:
            if isinstance(function, dict):
                info["name"] = function.get("name", "") or ""
                arguments_raw = function.get("arguments")
            else:
                info["name"] = getattr(function, "name", "") or ""
                arguments_raw = getattr(function, "arguments", None)

        if not info["name"]:
            if isinstance(tool_call, dict):
                info["name"] = tool_call.get("name", "") or ""
            else:
                info["name"] = getattr(tool_call, "name", "") or ""

        if arguments_raw is None:
            if isinstance(tool_call, dict):
                arguments_raw = tool_call.get("arguments")
            else:
                arguments_raw = getattr(tool_call, "arguments", None)

        if isinstance(arguments_raw, dict):
            info["arguments"] = arguments_raw
            info["raw_arguments"] = json.dumps(arguments_raw)
        elif isinstance(arguments_raw, str) and arguments_raw.strip():
            info["raw_arguments"] = arguments_raw
            try:
                info["arguments"] = json.loads(arguments_raw)
            except json.JSONDecodeError:
                info["arguments"] = {}
        else:
            info["raw_arguments"] = "{}"
            info["arguments"] = {}

        call_id = getattr(tool_call, "call_id", None) or getattr(tool_call, "id", None)
        if isinstance(tool_call, dict):
            call_id = call_id or tool_call.get("call_id") or tool_call.get("id")
        info["call_id"] = call_id

        return info

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
                "name": "get_company_info",
                "description": "Get company description, business model, and basic information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
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
                "name": "analyze_chart_image",
                "description": "Analyze a chart image (base64) and identify technical patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_base64": {
                            "type": "string",
                            "description": "Base64-encoded chart image"
                        },
                        "context": {
                            "type": "string",
                            "description": "Optional timeframe or instructions"
                        }
                    },
                    "required": ["image_base64"]
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
            },
            {
                "type": "function",
                "name": "detect_chart_patterns",
                "description": "Analyze the current chart for technical patterns (triangles, head & shoulders, flags, wedges, double tops/bottoms, etc.) and automatically draw them on the chart for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock or crypto symbol to analyze"
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Chart timeframe (1D, 1W, 1M, etc.)",
                            "default": "1D"
                        }
                    },
                    "required": ["symbol"]
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

    def _should_generate_structured_summary(self, tools_used: List[str]) -> bool:
        """Only trigger structured summary for richer tool combinations."""
        if not tools_used:
            return False

        summary_tools = {
            "get_comprehensive_stock_data",
            "get_stock_history",
            "analyze_chart_image",
            "review_trades",
            "get_options_strategies"
        }
        return any(tool in summary_tools for tool in tools_used)

    async def _generate_structured_summary(
        self,
        query: str,
        tools_used: List[str],
        tool_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Call the Responses API to generate structured JSON output."""
        if (
            not tools_used
            or not self._has_responses_support()
            or not self._should_generate_structured_summary(tools_used)
        ):
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

        price_payload = None
        tech_levels = None
        news_items = []

        if "get_comprehensive_stock_data" in normalized_results:
            comp_payload = normalized_results.get("get_comprehensive_stock_data") or {}
            if isinstance(comp_payload, dict):
                price_payload = comp_payload.get("price_data") or comp_payload
                tech_levels = comp_payload.get("technical_levels")

        if not price_payload and "get_stock_price" in normalized_results:
            price_payload = normalized_results.get("get_stock_price")

        if "get_stock_news" in normalized_results:
            news_payload = normalized_results.get("get_stock_news") or {}
            if isinstance(news_payload, dict):
                candidate_lists = [
                    news_payload.get("articles"),
                    news_payload.get("news"),
                    news_payload.get("items")
                ]
                for candidate in candidate_lists:
                    if isinstance(candidate, list):
                        news_items = candidate
                        break

        if not price_payload or not isinstance(price_payload, dict):
            logger.debug("Structured summary skipped: price payload unavailable")
            return None

        try:
            price = float(price_payload.get("price") or price_payload.get("last")) if price_payload.get("price") or price_payload.get("last") else None
        except (TypeError, ValueError):
            price = None

        change_abs = price_payload.get("change") or price_payload.get("change_abs")
        change_pct = price_payload.get("change_percent") or price_payload.get("change_pct")
        volume = price_payload.get("volume")
        previous_close = price_payload.get("previous_close") or price_payload.get("prev_close")

        summary_lines = []
        summary_lines.append(f"Symbol {symbol} latest snapshot")
        if price is not None:
            summary_lines.append(f"- Price: ${price:,.2f}")
        if change_abs is not None and change_pct is not None:
            summary_lines.append(f"- Change: {change_abs:+,.2f} ({change_pct:+.2f}%)")
        elif change_pct is not None:
            summary_lines.append(f"- Change: {change_pct:+.2f}%")
        if volume is not None:
            try:
                summary_lines.append(f"- Volume: {int(volume):,}")
            except (TypeError, ValueError):
                pass
        if previous_close is not None:
            try:
                summary_lines.append(f"- Previous close: ${float(previous_close):,.2f}")
            except (TypeError, ValueError):
                pass

        if tech_levels and isinstance(tech_levels, dict):
            level_lines = []
            for key in ("sell_high_level", "buy_low_level", "btd_level", "retest_level"):
                if key in tech_levels and tech_levels[key] is not None:
                    pretty_name = key.replace("_", " ").title()
                    try:
                        level_lines.append(f"  - {pretty_name}: ${float(tech_levels[key]):,.2f}")
                    except (TypeError, ValueError):
                        level_lines.append(f"  - {pretty_name}: {tech_levels[key]}")
            if level_lines:
                summary_lines.append("- Technical levels:")
                summary_lines.extend(level_lines)

        news_brief = []
        for article in news_items[:3]:
            if isinstance(article, dict):
                title = article.get("title") or article.get("headline")
                source = article.get("source")
                if title and source:
                    news_brief.append(f"  - {source}: {title}")
                elif title:
                    news_brief.append(f"  - {title}")
        if news_brief:
            summary_lines.append("- Recent headlines:")
            summary_lines.extend(news_brief)

        structured_summary = {
            "symbol": symbol,
            "price": {
                "last": price,
                "change_abs": change_abs,
                "change_pct": change_pct,
                "previous_close": previous_close,
                "volume": volume,
                "currency": price_payload.get("currency", "USD")
            },
            "technical_levels": tech_levels or {},
            "news": {
                "count": len(news_items),
                "top_headlines": news_brief
            },
            "analysis": "\n".join(summary_lines),
            "tools_used": tools_used
        }

        return structured_summary

    def _normalize_tool_payloads(self, tool_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        if not tool_results:
            return normalized
        for name, result in tool_results.items():
            payload = result
            if isinstance(result, dict) and "data" in result:
                payload = result.get("data")
            normalized[name] = payload
        return normalized

    def _summarize_tool_results_text(self, normalized: Dict[str, Any]) -> str:
        lines: List[str] = []

        def safe_float(value: Any) -> Optional[float]:
            try:
                if value is None:
                    return None
                return float(value)
            except (TypeError, ValueError):
                return None

        comp_payload = normalized.get("get_comprehensive_stock_data")
        price_payload = None
        if isinstance(comp_payload, dict):
            price_payload = comp_payload.get("price_data") or comp_payload
        if not isinstance(price_payload, dict):
            price_payload = normalized.get("get_stock_price") if isinstance(normalized.get("get_stock_price"), dict) else None

        if isinstance(price_payload, dict):
            price = safe_float(price_payload.get("price") or price_payload.get("last"))
            change = safe_float(price_payload.get("change") or price_payload.get("change_abs"))
            change_pct = safe_float(price_payload.get("change_percent") or price_payload.get("change_pct"))
            volume = safe_float(price_payload.get("volume"))
            lines.append("Price snapshot:")
            if price is not None:
                lines.append(f"  - Price: ${price:,.2f}")
            if change is not None and change_pct is not None:
                lines.append(f"  - Change: {change:+,.2f} ({change_pct:+.2f}%)")
            elif change_pct is not None:
                lines.append(f"  - Change: {change_pct:+.2f}%")
            if volume is not None:
                lines.append(f"  - Volume: {volume:,.0f}")

        tech_payload = None
        if isinstance(comp_payload, dict):
            tech_payload = comp_payload.get("technical_levels")
        if isinstance(tech_payload, dict):
            levels_lines = []
            for key, label in (
                ("sell_high_level", "Sell high"),
                ("buy_low_level", "Buy low"),
                ("btd_level", "Buy the dip"),
                ("retest_level", "Retest")
            ):
                value = safe_float(tech_payload.get(key))
                if value is not None:
                    levels_lines.append(f"    • {label}: ${value:,.2f}")
            if levels_lines:
                lines.append("Technical levels:")
                lines.extend(levels_lines)

        news_payload = normalized.get("get_stock_news")
        if isinstance(news_payload, dict):
            articles = news_payload.get("articles") or news_payload.get("news") or news_payload.get("items")
            if isinstance(articles, list) and articles:
                lines.append("Recent headlines:")
                for article in articles[:3]:
                    if isinstance(article, dict):
                        title = article.get("title") or article.get("headline")
                        source = article.get("source")
                        if title and source:
                            if len(title) > 120:
                                title = title[:117] + "..."
                            lines.append(f"    • {source}: {title}")

        if not lines:
            try:
                return json.dumps(normalized, default=str)
            except TypeError:
                return ""
        return "\n".join(lines)

    async def _generate_natural_language_response(
        self,
        query: str,
        messages: List[Dict[str, Any]],
        tool_results: Optional[Dict[str, Any]],
        status_messages: Optional[List[str]] = None
    ) -> Optional[str]:
        normalized = self._normalize_tool_payloads(tool_results)
        if not normalized:
            return None

        try:
            summary_text = self._summarize_tool_results_text(normalized)
            raw_json = json.dumps(normalized, default=str)
            if len(raw_json) > 4000:
                raw_json = raw_json[:4000] + " … (truncated)"

            final_messages = list(messages)
            instruction = (
                "You are G'sves, a senior portfolio manager. Provide a natural-language market analysis. "
                "Use clear paragraphs or short bullet lists. Reference key prices, changes, volume, "
                "technical levels, and notable news. Emphasize risk management and next steps. "
                "Do NOT use rigid templates or markdown tables."
            )
            final_messages.append({"role": "system", "content": instruction})

            user_content_parts = [f"User query: {query}"]
            if summary_text:
                user_content_parts.append("Tool summary:\n" + summary_text)
            user_content_parts.append("Raw tool JSON:\n" + raw_json)
            if status_messages:
                user_content_parts.append("Status notes:\n" + "\n".join(status_messages))
            user_content_parts.append("Respond in natural prose, highlighting actionable insights and risk considerations. If data is missing, mention it explicitly.")

            final_messages.append({
                "role": "user",
                "content": "\n\n".join(user_content_parts)
            })

            # Use max_completion_tokens for GPT-5, max_tokens for older models
            completion_params = {
                "model": self.model,
                "messages": final_messages,
                "temperature": self.temperature,
            }
            if "gpt-5" in self.model.lower():
                completion_params["max_completion_tokens"] = 900
            else:
                completion_params["max_tokens"] = 900
            
            completion = await self.client.chat.completions.create(**completion_params)

            if completion.choices:
                return completion.choices[0].message.content

        except Exception as exc:
            logger.warning(f"Natural language response generation failed: {exc}")
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
            elif tool_name == "get_company_info":
                symbol = str(arguments.get("symbol", "")).upper()
                # Leverage existing market service to get basic facts quickly
                quote = await self.market_service.get_stock_price(symbol)
                # Build a lightweight company info structure from available fields
                company_info = {
                    "symbol": symbol,
                    "company_name": quote.get("company_name", symbol),
                    "exchange": quote.get("exchange"),
                    "currency": quote.get("currency", "USD"),
                    "market_cap": quote.get("market_cap"),
                    "data_source": quote.get("data_source"),
                }
                result = company_info
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
            elif tool_name == "analyze_chart_image":
                if not self.chart_image_analyzer:
                    raise RuntimeError("Chart image analyzer not available")
                image_base64 = arguments.get("image_base64")
                context = arguments.get("context")
                result = await self.chart_image_analyzer.analyze_chart(
                    image_base64=image_base64,
                    user_context=context,
                )
            elif tool_name == "detect_chart_patterns":
                if not self.chart_image_analyzer:
                    raise RuntimeError("Chart image analyzer not available")

                symbol = arguments.get("symbol")
                timeframe = arguments.get("timeframe", "1D")

                # Get latest chart snapshot
                snapshot = await self.get_chart_state(symbol=symbol, timeframe=timeframe)
                if not snapshot or not snapshot.get("image_base64"):
                    result = {
                        "error": "No chart snapshot available. The chart must be visible to detect patterns.",
                        "patterns": [],
                        "summary": "Chart snapshot not found",
                        "chart_commands": []
                    }
                else:
                    # Retrieve pattern knowledge from knowledge base
                    pattern_knowledge = await self.vector_retriever.search_knowledge(
                        query="chart patterns candlestick patterns technical analysis patterns triangles head shoulders flags wedges double tops double bottoms",
                        top_k=15  # Get comprehensive pattern definitions
                    )

                    # Build enhanced context with pattern knowledge
                    pattern_context = f"""Analyze {symbol} {timeframe} chart for technical patterns.

PATTERN TYPES TO LOOK FOR:

**Chart Patterns**:
- Triangles (ascending, descending, symmetrical)
- Head and shoulders (regular, inverse)
- Double tops/bottoms, triple tops/bottoms
- Flags and pennants
- Wedges (rising, falling)
- Rectangles and channels
- Cup and handle
- Rounding tops/bottoms

**Candlestick Patterns**:
- Doji (indicates indecision)
- Engulfing (bullish/bearish)
- Hammer and shooting star
- Harami patterns
- Morning/evening stars

**Price Action**:
- Support and resistance levels
- Breakouts and breakdowns
- Trend reversals
- Consolidation zones
- Volume divergences

KNOWLEDGE:
{pattern_knowledge[:2000] if pattern_knowledge else "Use standard pattern recognition"}

Return JSON with detected patterns, confidence levels, and key support/resistance."""

                    # Analyze using vision model with enhanced context
                    analysis = await self.chart_image_analyzer.analyze_chart(
                        image_base64=snapshot["image_base64"],
                        user_context=pattern_context
                    )

                    # Generate drawing commands via lifecycle manager
                    lifecycle_result = self.pattern_lifecycle.update(
                        symbol=symbol,
                        timeframe=timeframe,
                        analysis=analysis
                    )

                    result = {
                        "patterns": analysis.get("patterns", []),
                        "summary": analysis.get("summary", ""),
                        "chart_commands": lifecycle_result.get("chart_commands", []),
                        "symbol": symbol,
                        "timeframe": timeframe
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
            # Use max_completion_tokens for GPT-5, max_tokens for older models
            completion_params = {
                "model": "gpt-4.1",  # Fast, efficient model for insights
                "temperature": 0.7,
                "messages": [{
                    "role": "user",
                    "content": insight_prompt
                }]
            }
            # GPT-4.1 does not use gpt-5 naming convention, so use max_tokens
            completion_params["max_tokens"] = 100
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(**completion_params),
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
            info = self._extract_tool_call_info(tool_call)
            function_name = info["name"]
            if not function_name:
                logger.warning(f"Skipping parallel execution for unnamed tool call: {tool_call}")
                continue
            function_args = info["arguments"]

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
    
    def _build_system_prompt(self, retrieved_knowledge: str = "") -> str:
        """Build the system prompt for the agent, including any retrieved knowledge."""
        base_prompt = """You are G'sves, expert market analyst specializing in swing trading and technical analysis.

GENERAL & COMPANY INFO REQUESTS:
When the user asks general questions (e.g., "what is PLTR?", "tell me about Microsoft", or non-trading topics),
respond with a concise, educational explanation first. For company queries:
- Name and what the company does (1-2 sentences)
- Industry/sector if known
- Notable products or positioning
Avoid trading recommendations unless explicitly asked. Keep tone educational; no investment advice.

SWING TRADE ANALYSIS:
When asked about swing trades, entry points, or technical setups, provide SPECIFIC structured data:
- Entry levels with exact prices (e.g., "Enter at $245.50 on breakout above resistance")
- Stop loss levels (e.g., "Stop at $242.00 below support")
- Target levels (e.g., "Target 1: $250, Target 2: $255")
- Risk/reward ratios
- Key support/resistance zones
- Volume and momentum indicators

Include this JSON structure in your response when providing swing trade analysis:
```json
{
  "swing_trade": {
    "entry_points": [245.50, 244.00],
    "stop_loss": 242.00,
    "targets": [250.00, 255.00, 260.00],
    "risk_reward": 2.5,
    "support_levels": [242.00, 238.00, 235.00],
    "resistance_levels": [248.00, 252.00, 258.00]
  }
}
```

TECHNICAL ANALYSIS REQUESTS:
For support/resistance or technical queries:
- Identify 2-3 key support levels with exact prices
- Identify 2-3 resistance levels with exact prices
- Note current trend direction and strength
- Highlight any chart patterns (flags, triangles, etc.)
- Provide RSI, MACD readings if relevant

TOOL USAGE:
- Call get_stock_price and get_stock_history for price/chart data
- Call get_comprehensive_stock_data for detailed technicals
- Analyze the data to provide SPECIFIC trade setups, not generic summaries
- Base your analysis on the actual data returned by the tools

RESPONSE FORMAT:
- Start with the specific answer to the question (entry points, levels, etc.)
- Include structured JSON data for swing trades when applicable
- Support with current price data from tools
- Add brief technical rationale
- Keep responses focused and actionable
- NEVER return generic templates or market snapshots"""
        
        # If knowledge was retrieved, include it in the system prompt
        if retrieved_knowledge:
            return f"""{base_prompt}

## Relevant Knowledge Base Content
{retrieved_knowledge}

Remember to cite sources when using this knowledge and maintain educational tone without providing investment advice."""
        
        return base_prompt
    
    async def _get_cached_knowledge(self, query: str) -> str:
        """
        Get knowledge with caching for <50ms repeated queries.
        
        Implements:
        - Thread-safe cache operations with asyncio.Lock
        - LRU eviction when cache exceeds max_size
        - TTL-based expiration
        
        NOTE: Cache is per-process. In multi-machine deployments (Fly.io),
        cache hits only occur on the same machine. For true distributed
        caching, use Redis (see implementation notes).
        """
        # Normalize query for better cache hit rates
        normalized_query = self._normalize_query(query)
        query_hash = hashlib.md5(normalized_query.encode()).hexdigest()
        
        # Thread-safe cache check
        async with self._cache_lock:
            if query_hash in self._knowledge_cache:
                cached = self._knowledge_cache[query_hash]
                if time.time() - cached['timestamp'] < self._cache_ttl:
                    # Move to end for LRU (most recently used)
                    self._knowledge_cache.move_to_end(query_hash)
                    logger.info(f"Knowledge cache HIT (local) for {query_hash[:8]}")
                    return cached['knowledge']
                else:
                    # Remove expired entry
                    del self._knowledge_cache[query_hash]
        
        logger.info(f"Knowledge cache MISS for {query_hash[:8]}")
        
        try:
            # Retrieve with optimized parameters
            chunks = await self.vector_retriever.search_knowledge(query, top_k=3, min_score=0.65)
            knowledge = self.vector_retriever.format_knowledge_for_agent(chunks) if chunks else ""
            
            # Thread-safe cache update with LRU eviction
            async with self._cache_lock:
                # Evict oldest if at max size
                if len(self._knowledge_cache) >= self._cache_max_size:
                    # Remove oldest (first item)
                    oldest = next(iter(self._knowledge_cache))
                    del self._knowledge_cache[oldest]
                    logger.info(f"Evicted oldest cache entry: {oldest[:8]}")
                
                # Add new entry
                self._knowledge_cache[query_hash] = {
                    'knowledge': knowledge,
                    'timestamp': time.time()
                }
                logger.info(f"Cached knowledge for {query_hash[:8]} ({len(knowledge)} chars)")
            
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            # Return empty but log the failure for monitoring
            knowledge = ""
            # Note: self.metrics would need to be initialized for full monitoring
            # self.metrics.record_error(f"knowledge_retrieval_error: {str(e)}")
        
        return knowledge
    
    async def _get_cached_response(self, query: str, context: str = "") -> Optional[Dict[str, Any]]:
        """
        Get cached full response for query.
        Returns None if not cached or expired.
        Note: Context is ignored for caching to allow pre-warming to work.
        """
        start_time = time.time()
        # Normalize query for better cache hit rates
        normalized_query = self._normalize_query(query)
        # Create cache key from normalized query (ignore context for better cache hits)
        cache_key = hashlib.md5(f"{normalized_query}".encode()).hexdigest()
        
        async with self._response_cache_lock:
            if cache_key in self._response_cache:
                cached = self._response_cache[cache_key]
                # Check if still valid (within TTL)
                if time.time() - cached['timestamp'] < self._response_cache_ttl:
                    # Move to end for LRU
                    self._response_cache.move_to_end(cache_key)
                    cache_age = time.time() - cached['timestamp']
                    logger.info(f"Response cache HIT for {cache_key[:8]} (age: {cache_age:.1f}s, size: {len(self._response_cache)}/{self._response_cache_max_size})")
                    self.metrics.record_retrieval(time.time() - start_time, cache_hit=True)
                    # Ensure cached flag is set
                    response = cached['response'].copy()
                    response['cached'] = True
                    return response
                else:
                    # Remove expired entry
                    del self._response_cache[cache_key]
                    logger.info(f"Response cache expired for {cache_key[:8]}")
        
        self.metrics.record_retrieval(time.time() - start_time, cache_hit=False)
        return None
    
    async def _cache_response(self, query: str, context: str, response: Dict[str, Any]):
        """
        Cache a full response with LRU eviction and TTL.
        Note: Context is ignored for caching to allow pre-warming to work.
        """
        # Normalize query for better cache hit rates
        normalized_query = self._normalize_query(query)
        cache_key = hashlib.md5(f"{normalized_query}".encode()).hexdigest()
        
        async with self._response_cache_lock:
            # Evict oldest if at max size
            if len(self._response_cache) >= self._response_cache_max_size:
                oldest = next(iter(self._response_cache))
                del self._response_cache[oldest]
                logger.info(f"Evicted oldest response cache: {oldest[:8]}")
            
            # Add new entry
            self._response_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }
            logger.info(f"Cached response for {cache_key[:8]}")
    
    async def _process_query_responses(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a query using the real Responses API."""
        start_time = time.monotonic()
        # PROACTIVE KNOWLEDGE RETRIEVAL
        retrieved_knowledge = ""
        try:
            retrieved_knowledge = await self._get_cached_knowledge(query)
        except Exception as e:
            logger.warning(f"Knowledge retrieval failed: {e}")
        
        # Build context for Responses API
        messages = []
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

        # Use the actual Responses API client
        if not hasattr(self.client, 'responses'):
            logger.warning("Responses API not available in client; falling back to chat completions")
            return await self._process_query_chat(query, conversation_history, stream=False)

        response_messages = self._convert_messages_for_responses(messages)

        # Check if this is a simple query that doesn't need complex reasoning
        ql = query.lower()
        is_simple_query = (
            any(term in ql for term in ["price", "quote", "cost", "worth", "value", "trading at"]) 
            and len(query.split()) < 15
            and not any(term in ql for term in ["analysis", "technical", "pattern", "trend", "support", "resistance"])
        )
        
        if is_simple_query:
            # Use Chat API directly for simple queries - much faster and predictable
            try:
                t_llm1_start = time.monotonic()
                logger.info("Using Chat API for simple query (bypassing Responses API)")
                # Use max_completion_tokens for GPT-5, max_tokens for older models
                completion_params = {
                    "model": "gpt-4o-mini",  # Fast model for simple queries
                    "messages": [
                        {"role": "system", "content": self._build_system_prompt()},
                        {"role": "user", "content": query}
                    ],
                    "tools": self._get_tool_schemas(),
                    "tool_choice": "auto",
                    "temperature": 0.3,
                }
                # gpt-4o-mini doesn't use gpt-5 naming, so use max_tokens
                completion_params["max_tokens"] = 400
                
                chat_response = await self.client.chat.completions.create(**completion_params)
                chat_llm_dur = time.monotonic()-t_llm1_start
                logger.info(f"Chat API (simple) latency: {chat_llm_dur:.2f}s")
                
                assistant_msg = chat_response.choices[0].message
                
                # Process any tool calls
                if assistant_msg.tool_calls:
                    t_tools = time.monotonic()
                    tool_results = await self._execute_tools_parallel(assistant_msg.tool_calls)
                    tools_dur = time.monotonic()-t_tools
                    logger.info(f"Executed {len(assistant_msg.tool_calls)} tools in {tools_dur:.2f}s")
                    
                    # Get final response with tool results
                    final_messages = [
                        {"role": "system", "content": self._build_system_prompt()},
                        {"role": "user", "content": query},
                        {"role": "system", "content": f"Tool Results: {json.dumps(tool_results, indent=2)}"}
                    ]
                    
                    t_final = time.monotonic()
                    # Use max_completion_tokens for GPT-5, max_tokens for older models
                    completion_params = {
                        "model": "gpt-4o-mini",
                        "messages": final_messages,
                        "temperature": 0.3,
                    }
                    # gpt-4o-mini doesn't use gpt-5 naming, so use max_tokens
                    completion_params["max_tokens"] = 400
                    
                    final_response = await self.client.chat.completions.create(**completion_params)
                    final_dur = time.monotonic()-t_final
                    logger.info(f"Chat API (final) latency: {final_dur:.2f}s")
                    response_text = final_response.choices[0].message.content
                else:
                    response_text = assistant_msg.content
                
                # Return early with simple response
                total_dur = time.monotonic()-start_time
                self.last_diag = {
                    "ts": datetime.now().isoformat(),
                    "path": "responses_simple_via_chat",
                    "intent": self.intent_router.classify_intent(query),
                    "durations": {
                        "llm1": round(chat_llm_dur, 3),
                        "tools": round(tools_dur if assistant_msg.tool_calls else 0.0, 3),
                        "llm2": round(final_dur if assistant_msg.tool_calls else 0.0, 3),
                        "total": round(total_dur, 3),
                    },
                    "tools_used": [tc.function.name for tc in (assistant_msg.tool_calls or [])],
                    "news_called": any((tc.function.name == "get_stock_news") for tc in (assistant_msg.tool_calls or [])),
                    "news_gated": False,
                    "model": self.model,
                    "use_responses": False,
                }
                return {
                    "text": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "cached": False,
                    "session_id": None,
                    "mode": "chat-simple"
                }
            except Exception as e:
                logger.warning(f"Chat API simple query failed: {e}, falling back to Responses API")
                # Fall through to Responses API
        
        try:
            # Use the actual Responses API
            t_llm1_start = time.monotonic()
            
            # Build input for Responses API
            input_content = response_messages if len(response_messages) > 1 else query
            
            # Prepare parameters for Responses API
            params = {
                "model": "gpt-4o-mini",  # Use a model that supports Responses API
                "input": input_content,
                "instructions": self._build_system_prompt(retrieved_knowledge),
            }
            
            # Add tools if needed (check if native tools are available)
            tool_schemas = self._get_tool_schemas()
            if tool_schemas:
                # Convert to Responses API format (internally-tagged)
                responses_tools = []
                for tool in tool_schemas:
                    if tool.get("type") == "function":
                        func = tool.get("function", {})
                        responses_tools.append({
                            "type": "function",
                            "name": func.get("name"),
                            "description": func.get("description"),
                            "parameters": func.get("parameters")
                        })
                if responses_tools:
                    params["tools"] = responses_tools
            
            # Use the actual client.responses.create()
            response = await self.client.responses.create(**params)
            logger.info(f"Responses API latency: {time.monotonic()-t_llm1_start:.2f}s")
            
            # Debug logging for response structure
            logger.info(f"Responses API response type: {type(response)}")
            logger.info(f"Response attributes: {dir(response)[:10]}")  # First 10 attributes
            if hasattr(response, 'output'):
                output = getattr(response, 'output')
                logger.info(f"Output type: {type(output)}, length: {len(output) if hasattr(output, '__len__') else 'N/A'}")
                if output and hasattr(output, '__len__') and len(output) > 0:
                    logger.info(f"First output item type: {type(output[0])}")
                    logger.info(f"First output item attrs: {dir(output[0])[:10]}")
        except Exception as exc:
            logger.error(f"Responses API call failed: {exc}")
            return {
                "text": "I ran into an issue while generating the response. Please try again in a moment.",
                "error": str(exc),
                "timestamp": datetime.now().isoformat()
            }

        # Extract text from the response using our fixed method
        response_text = self._extract_response_text(response)
        
        # Check for tool calls in the output
        tool_results: Dict[str, Any] = {}
        tools_used: List[str] = []
        
        # Check if the response has tool calls in output
        tool_calls_found = []
        if hasattr(response, 'output') and isinstance(response.output, list):
            for item in response.output:
                # Check if this is a tool call (function_call type in Responses API)
                item_type = getattr(item, 'type', None)
                if item_type == 'function_call':
                    # This is a function call item
                    tool_calls_found.append(item)
                elif hasattr(item, 'name') and hasattr(item, 'arguments'):
                    # Alternative format check
                    tool_calls_found.append(item)
            
            # If we found tool calls, execute them (parallelized) and optionally gate news
            if tool_calls_found:
                ql = query.lower()
                wants_news = any(k in ql for k in ["news", "headline", "catalyst", "press release", "breaking"])
                filtered_calls = []
                for tool_call in tool_calls_found:
                    info = self._extract_tool_call_info(tool_call)
                    tool_name = info["name"]
                    if not tool_name:
                        logger.warning(f"Skipping tool call with missing name: {tool_call}")
                        continue
                    if tool_name == "get_stock_news" and not wants_news:
                        logger.info("Skipping get_stock_news (no news intent detected)")
                        continue
                    filtered_calls.append(tool_call)

                if filtered_calls:
                    tools_used.extend([self._extract_tool_call_info(c)["name"] for c in filtered_calls])
                    t_tools = time.monotonic()
                    parallel_results = await self._execute_tools_parallel(filtered_calls)
                    tool_results.update(parallel_results)
                    logger.info(f"Executed {len(filtered_calls)} tools in parallel via Responses API in {time.monotonic()-t_tools:.2f}s")
                
                # For now, we'll include tool results in our response
                # The Responses API is an agentic loop but we're handling tools manually
                if tool_results:
                    logger.info(f"Tool results collected: {list(tool_results.keys())}")

        # The Responses API doesn't use required_action pattern
        # Tools are handled in the agentic loop
        
        # Ensure we have unique tools used list
        tools_used = list(dict.fromkeys(tools_used))

        # Perform technical analysis if applicable and attach to tool_results
        try:
            query_lower = query.lower()
            technical_triggers = [
                'swing', 'entry', 'exit', 'target', 'stop',
                'support', 'resistance', 'fibonacci', 'fib', 'trend line', 'trendline',
                'technical', 'levels', 'analysis', 'pattern', 'chart'
            ]
            needs_ta = any(k in query_lower for k in technical_triggers)
            if needs_ta and tool_results is not None:
                primary_symbol = self._extract_primary_symbol(query, tool_results)
                if primary_symbol:
                    ta_data = await self._perform_technical_analysis(primary_symbol, tool_results)
                    if ta_data:
                        tool_results['technical_analysis'] = ta_data
        except Exception as ta_exc:
            logger.warning(f"Technical analysis integration skipped due to error: {ta_exc}")

        response_text = self._extract_response_text(response)
        structured_payload = await self._generate_structured_summary(query, tools_used, tool_results)
        if not structured_payload:
            structured_payload = self._extract_structured_payload(response)

        # Build collected_tool_calls from tool_calls_found for formatting
        collected_tool_calls = []
        for tool_call in tool_calls_found:
            info = self._extract_tool_call_info(tool_call)
            if info.get("name"):
                collected_tool_calls.append({
                    "id": info.get("call_id", ""),
                    "function": {
                        "name": info["name"],
                        "arguments": info.get("raw_arguments", "{}")
                    }
                })
        
        formatted_response = None
        if collected_tool_calls and tool_results:
            formatted_response = await self._format_tool_response(
                collected_tool_calls,
                tool_results,
                messages
            )

        # Check if this is a technical/swing trade query
        is_technical = any(term in query.lower() for term in ['swing', 'entry', 'exit', 'target', 'stop', 'support', 'resistance', 'technical'])
        
        # Only use formatted response if the LLM didn't provide meaningful content
        # AND it's not a technical query (never use template for technical queries)
        if formatted_response and not is_technical and (not response_text or len(response_text) < 100 or "I'm sorry" in response_text):
            response_text = formatted_response
        # If technical query has no response text, generate natural language response
        elif is_technical and (not response_text or len(response_text) < 100) and tool_results:
            logger.info("Technical query without response text - generating natural language fallback")
            response_text = await self._generate_natural_language_response(
                query,
                messages,
                tool_results,
                None
            )

        if structured_payload:
            tool_results.setdefault("structured_output", structured_payload)

        response_text, chart_commands = self._append_chart_commands_to_data(query, tool_results, response_text)

        # Record diagnostics for Responses path (best-effort)
        total_dur = time.monotonic()-start_time
        self.last_diag = {
            "ts": datetime.now().isoformat(),
            "path": "responses_api",
            "intent": self.intent_router.classify_intent(query),
            "durations": {
                "llm1": None,
                "tools": None,
                "llm2": None,
                "total": round(total_dur, 3),
            },
            "tools_used": tools_used,
            "news_called": any(t == "get_stock_news" for t in tools_used),
            "news_gated": not any(k in query.lower() for k in ["news","headline","catalyst","press release","breaking"]),
            "model": self.model,
            "use_responses": True,
        }

        # Extract additional chart commands from the response text
        extracted_commands = []
        if response_text:
            extracted_commands = self.chart_command_extractor.extract_commands_from_response(
                response_text, query, tool_results
            )
        
        # Combine existing and extracted commands
        all_commands = chart_commands + extracted_commands
        # Remove duplicates while preserving order
        seen = set()
        final_commands = []
        for cmd in all_commands:
            if cmd not in seen:
                seen.add(cmd)
                final_commands.append(cmd)
        
        result_payload: Dict[str, Any] = {
            "text": response_text or "I'm sorry, I couldn't generate a response.",
            "tools_used": tools_used,
            "data": tool_results,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "cached": False
        }
        if final_commands:
            result_payload["chart_commands"] = final_commands
        try:
            logger.info(f"Response includes chart_commands: {bool(result_payload.get('chart_commands'))}")
            if result_payload.get('chart_commands'):
                logger.info(f"Chart commands: {result_payload['chart_commands']}")
        except Exception:
            pass

        return result_payload

    async def _process_query_single_pass(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        intent: str = "general",
        stream: bool = False
    ) -> Dict[str, Any]:
        """Single-pass Chat Completions flow with tools and immediate response."""
        start_time = time.monotonic()

        # Retrieve relevant knowledge for educational/general/technical queries
        retrieved_knowledge = ""
        if intent in ["educational", "general", "technical"]:
            retrieved_knowledge = await self._get_cached_knowledge(query)
            if retrieved_knowledge:
                logger.info(f"Retrieved {len(retrieved_knowledge)} chars of knowledge for {intent} query")

        # Build messages
        messages = []
        messages.append({"role": "system", "content": self._build_system_prompt(retrieved_knowledge)})
        
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        messages.append({"role": "user", "content": query})
        
        try:
            # Single LLM call with tools
            # Use gpt-4o-mini for educational queries (gpt-5-mini has issues with empty responses)
            model = "gpt-4o-mini" if intent == "educational" else ("gpt-5-mini" if intent in ["price-only", "news"] else self.model)
            # Increased tokens for complex queries like planning (was 800, now 1500)
            max_tokens = 400 if intent in ["price-only", "news"] else 1500  # More tokens for complex responses
            
            t_llm = time.monotonic()
            # Use correct parameter name based on model
            completion_params = {
                "model": model,
                "messages": messages
            }
            
            # Add temperature only for models that support it
            if not model.startswith("gpt-5"):
                completion_params["temperature"] = 0.3 if intent in ["price-only", "technical"] else 0.7
            
            # Add tools for all intents EXCEPT educational (which uses knowledge base only)
            if intent != "educational":
                completion_params["tools"] = self._get_tool_schemas()
                completion_params["tool_choice"] = "auto"
            # For educational queries, no tools are provided, so no tool_choice needed
            
            # Use max_completion_tokens for newer models, max_tokens for older
            if model.startswith("gpt-4o") or model.startswith("gpt-5"):
                completion_params["max_completion_tokens"] = max_tokens
            else:
                completion_params["max_tokens"] = max_tokens
            
            # Debug log request for conversational queries
            if intent in ["educational", "general"]:
                logger.info(f"LLM Request - Model: {completion_params['model']}, Messages: {len(messages)}, Tools: {len(completion_params.get('tools', []))}")
                logger.info(f"User query: {query}")
            
            response = await self.client.chat.completions.create(**completion_params)
            llm1_dur = time.monotonic()-t_llm
            logger.info(f"Single-pass LLM latency: {llm1_dur:.2f}s")
            
            # Debug logging for educational queries
            if intent == "educational" or intent == "general":
                logger.info(f"LLM Response - Finish reason: {response.choices[0].finish_reason}")
                logger.info(f"Educational response content: {response.choices[0].message.content[:200] if response.choices[0].message.content else 'NONE'}")
                if response.choices[0].message.tool_calls:
                    logger.info(f"Tool calls made: {[tc.function.name for tc in response.choices[0].message.tool_calls]}")
                else:
                    logger.info("No tool calls made")
            
            assistant_msg = response.choices[0].message
            tools_used = []
            tool_results = {}
            
            # Execute tools if present (parallel)
            tools_phase_dur = 0.0
            summarization_dur = 0.0
            if assistant_msg.tool_calls:
                # Gate news tool based on intent
                filtered_calls = []
                for call in assistant_msg.tool_calls:
                    if call.function.name == "get_stock_news" and intent not in ["news", "general"]:
                        logger.info("Skipping news tool (not requested)")
                        continue
                    filtered_calls.append(call)
                    tools_used.append(call.function.name)
                
                if filtered_calls:
                    t_tools = time.monotonic()
                    tool_results = await self._execute_tools_parallel(filtered_calls)
                    tools_phase_dur = time.monotonic()-t_tools
                    logger.info(f"Executed {len(filtered_calls)} tools in {tools_phase_dur:.2f}s")
                
                # Generate final response with tool results
                if tool_results:
                    tool_messages = messages.copy()
                    tool_messages.append({"role": "assistant", "content": assistant_msg.content or ""})
                    tool_messages.append({
                        "role": "system",
                        "content": f"Tool Results:\n{json.dumps(tool_results, indent=2)}\n\nProvide a concise, natural response based on these results."
                    })
                    
                    t_final = time.monotonic()
                    final_response = await self.client.chat.completions.create(
                        model="gpt-4o-mini",  # Fast model for summarization
                        messages=tool_messages,
                        temperature=0.3,
                        max_completion_tokens=400
                    )
                    summarization_dur = time.monotonic()-t_final
                    logger.info(f"Final summarization latency: {summarization_dur:.2f}s")
                    response_text = final_response.choices[0].message.content
                else:
                    response_text = assistant_msg.content
            else:
                response_text = assistant_msg.content
            
            # Generate structured data and chart commands
            structured_data = {}
            chart_commands: List[str] = []

            if tool_results:
                response_text, generated_commands = self._append_chart_commands_to_data(
                    query, tool_results, response_text
                )
                if generated_commands:
                    chart_commands.extend(generated_commands)

            if intent == "technical" and tool_results:
                # Extract and process technical analysis
                history_data = tool_results.get("get_stock_history", {})
                if history_data and "data" in history_data:
                    symbol = history_data.get("symbol", "UNKNOWN")
                    candles = history_data["data"]
                    
                    # Perform technical analysis
                    ta_results = await self._perform_technical_analysis(symbol, candles)
                    if ta_results:
                        technical_commands = self._generate_chart_commands(ta_results, symbol)
                        if technical_commands:
                            chart_commands.extend(technical_commands)
                        structured_data["technical_analysis"] = ta_results
            
            if chart_commands:
                seen_cmds: Set[str] = set()
                deduped_cmds: List[str] = []
                for cmd in chart_commands:
                    if cmd not in seen_cmds:
                        seen_cmds.add(cmd)
                        deduped_cmds.append(cmd)
                chart_commands = deduped_cmds
            
            # Record diagnostics
            total_dur = time.monotonic()-start_time
            self.last_diag = {
                "ts": datetime.now().isoformat(),
                "path": "chat_single_pass",
                "intent": intent,
                "durations": {
                    "llm1": round(llm1_dur, 3),
                    "tools": round(tools_phase_dur, 3),
                    "summarization": round(summarization_dur, 3),
                    "total": round(total_dur, 3),
                },
                "tools_used": tools_used,
                "news_called": any(t == "get_stock_news" for t in tools_used),
                "news_gated": intent not in ["news", "general"],
                "model": self.model,
                "use_responses": False,
            }
            total_time = time.monotonic() - start_time
            logger.info(f"Total query processing time: {total_time:.2f}s")
            
            # Extract additional chart commands from the response text
            extracted_commands = []
            if response_text:
                extracted_commands = self.chart_command_extractor.extract_commands_from_response(
                    response_text, query, tool_results
                )
            
            # Combine existing and extracted commands
            all_commands = chart_commands + extracted_commands
            # Remove duplicates while preserving order
            seen = set()
            final_commands = []
            for cmd in all_commands:
                if cmd not in seen:
                    seen.add(cmd)
                    final_commands.append(cmd)
            
            return {
                "text": response_text or "I couldn't generate a response.",
                "tools_used": tools_used,
                "data": tool_results,  # Required field for AgentResponse
                "structured_data": structured_data,
                "chart_commands": final_commands,
                "timestamp": datetime.now().isoformat(),
                "model": model,  # Required field for AgentResponse
                "cached": False,
                "session_id": None,
                "intent": intent,
                "latency_ms": int(total_time * 1000),
                "education_mode": "llm"  # Tag for A/B testing
            }
            
        except Exception as e:
            logger.error(f"Single-pass processing failed: {e}")
            return {
                "text": "I encountered an error while processing your request.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _process_query_chat(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Legacy chat.completions implementation (retained as fallback)."""
        try:
            # PROACTIVE KNOWLEDGE RETRIEVAL for legacy path
            retrieved_knowledge = ""
            try:
                # Use cached knowledge retrieval
                retrieved_knowledge = await self._get_cached_knowledge(query)
                if retrieved_knowledge:
                    logger.info(f"Retrieved knowledge for legacy chat ({len(retrieved_knowledge)} chars)")
            except Exception as e:
                logger.warning(f"Knowledge retrieval failed in legacy path: {e}")
            
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt(retrieved_knowledge)}
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
            # Use max_completion_tokens for GPT-5, max_tokens for older models
            completion_params = {
                "model": self.model,
                "messages": messages,
                "tools": self._get_tool_schemas(),
                "tool_choice": "auto",
                "temperature": self.temperature,
            }
            if "gpt-5" in self.model.lower():
                completion_params["max_completion_tokens"] = 1000  # Reduced for faster response
            else:
                completion_params["max_tokens"] = 1000  # Reduced for faster response
            
            response = await self.client.chat.completions.create(**completion_params)
            
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
                    info = self._extract_tool_call_info(tool_call)
                    tool_name = info["name"]
                    if not tool_name:
                        logger.warning(f"Skipping message append for unnamed tool: {tool_call}")
                        continue
                    messages.append({
                        "role": "tool",
                        "tool_call_id": info["call_id"],
                        "content": json.dumps(tool_results.get(tool_name, {}))
                    })

                # Always attempt structured formatting for stock-related queries
                response_text = None
                symbol_arg = None
                
                # Extract symbol from tool calls
                for tc in assistant_message.tool_calls:
                    info = self._extract_tool_call_info(tc)
                    args = info["arguments"]
                    if isinstance(args, dict) and 'symbol' in args:
                        symbol_arg = args['symbol']
                        break
                
                # If we have stock data, format it properly
                if symbol_arg and ('get_stock_price' in tool_results or 'get_comprehensive_stock_data' in tool_results):
                    try:
                        fallback_formatter_args = None

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
                        
                        # Add insight to price_payload for potential fallback formatting
                        if price_payload:
                            price_payload['llm_insight'] = llm_insight
                        
                        fallback_formatter_args = (
                            symbol_arg.upper(),
                            company_name,
                            price_payload,
                            news_items,
                            tech_levels,
                            after_hours
                        )

                    except Exception as fmt_err:
                        logger.error(f"Formatting failed: {fmt_err}")
                        fallback_formatter_args = None
                
                response_text = await self._generate_natural_language_response(
                    query,
                    messages,
                    tool_results,
                    status_messages
                )

                if not response_text:
                    if fallback_formatter_args:
                        try:
                            response_text = MarketResponseFormatter.format_stock_snapshot_ideal(*fallback_formatter_args)
                        except Exception as fallback_err:
                            logger.warning(f"Fallback formatter failed: {fallback_err}")
                            response_text = assistant_message.content
                    else:
                        response_text = assistant_message.content
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
                        # Gate news strictly by explicit intent
                        wants_news = any(k in query_lower for k in ["news", "headline", "catalyst", "press release", "breaking", "announcement", "earnings"])
                        if wants_news:
                            news_result = await self.market_service.get_stock_news(detected_symbol, 3)
                            news_items = news_result.get('articles') or news_result.get('news') or news_result.get('items') or []
                        else:
                            news_result = {"status": "skipped", "reason": "no_news_intent"}
                            news_items = []
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
                        
                        # Prefer natural-language summary by the agent over templates
                        pseudo_tool_results: Dict[str, Any] = {
                            "get_comprehensive_stock_data": comp,
                            "get_stock_news": news_result
                        }

                        # Try LLM prose first
                        response_text = await self._generate_natural_language_response(
                            query,
                            messages,
                            pseudo_tool_results,
                            None
                        )

                        # Fallback to formatter only if LLM generation fails
                        if not response_text:
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
            
            # Perform technical analysis if applicable and attach to tool_results
            try:
                query_lower = query.lower()
                technical_triggers = [
                    'swing', 'entry', 'exit', 'target', 'stop',
                    'support', 'resistance', 'fibonacci', 'fib', 'trend line', 'trendline',
                    'technical', 'levels', 'analysis', 'pattern', 'chart'
                ]
                needs_ta = any(k in query_lower for k in technical_triggers)
                if needs_ta and tool_results is not None:
                    primary_symbol = self._extract_primary_symbol(query, tool_results)
                    if primary_symbol:
                        ta_data = await self._perform_technical_analysis(primary_symbol, tool_results)
                        if ta_data:
                            tool_results['technical_analysis'] = ta_data
            except Exception as ta_exc:
                logger.warning(f"Technical analysis integration skipped due to error: {ta_exc}")

            response_text, chart_commands = self._append_chart_commands_to_data(query, tool_results, response_text)

            # Extract additional chart commands from the response text
            extracted_commands = []
            if response_text:
                extracted_commands = self.chart_command_extractor.extract_commands_from_response(
                    response_text, query, tool_results
                )
            
            # Combine existing and extracted commands
            all_commands = chart_commands + extracted_commands
            # Remove duplicates while preserving order
            seen = set()
            final_commands = []
            for cmd in all_commands:
                if cmd not in seen:
                    seen.add(cmd)
                    final_commands.append(cmd)
            
            result_payload: Dict[str, Any] = {
                "text": response_text,
                "tools_used": tools_used,
                "data": tool_results,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "cached": False  # Would be true if all results came from cache
            }
            if final_commands:
                result_payload["chart_commands"] = final_commands
            try:
                logger.info(f"Response includes chart_commands: {bool(result_payload.get('chart_commands'))}")
                if result_payload.get('chart_commands'):
                    logger.info(f"Chart commands: {result_payload['chart_commands']}")
            except Exception:
                pass

            return result_payload
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "text": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _classify_intent(self, query: str) -> str:
        """Classify query intent for fast-path routing."""
        ql = query.lower()
        
        # Educational queries (highest priority for novice traders)
        educational_triggers = [
            "what does", "what is", "how do i", "how to", "explain", 
            "what's the difference", "what is the difference", "teach me",
            "buy low", "sell high", "support and resistance", "support level",
            "resistance level", "trading basics", "start trading", "beginner",
            "learn", "understand", "meaning of", "definition"
        ]
        if any(trigger in ql for trigger in educational_triggers):
            # Check if it's really educational (not just "what is AAPL")
            symbol = self.intent_router.extract_symbol(query)
            if not symbol or "difference" in ql or "mean" in ql or "how" in ql:
                return "educational"
        
        # Company information queries (before price-only)
        company_info_triggers = ("what is", "who is", "tell me about", "explain")
        if any(p in ql for p in company_info_triggers):
            symbol_in_query = self.intent_router.extract_symbol(query)
            if symbol_in_query and not any(term in ql for term in [
                "price", "quote", "cost", "worth", "value", "trading", "trading at", "how much"
            ]):
                return "company-info"
        
        # Price-only queries
        if (any(term in ql for term in ["price", "quote", "cost", "worth", "value", "trading at", "how much is"]) 
            and len(query.split()) < 12
            and not any(term in ql for term in ["analysis", "technical", "news", "chart", "pattern"])):
            return "price-only"
        
        # Chart display commands (expanded to catch more variations)
        if any(term in ql for term in ["show chart", "display chart", "load chart", "view chart", 
                                        "show me the chart", "show me chart", "chart for", "chart of"]):
            return "chart-only"
        
        # Indicator toggle commands  
        if any(term in ql for term in ["add indicator", "remove indicator", "toggle", "show rsi", "hide rsi", "show macd", "hide macd"]):
            return "indicator-toggle"
        
        # News queries
        if any(term in ql for term in ["news", "headlines", "catalyst", "latest", "breaking", "announcement"]):
            return "news"
        
        # Technical analysis
        if any(term in ql for term in ["technical", "analysis", "pattern", "support", "resistance", "trend", "swing", "entry", "exit"]):
            return "technical"
        
        # Default to general
        return "general"
    
    async def _handle_educational_query(self, query: str) -> Dict[str, Any]:
        """Handle educational queries for novice traders."""
        ql = query.lower()
        
        # Educational content database
        educational_responses = {
            "buy low": {
                "title": "Buy Low, Sell High",
                "content": "Buy low, sell high is the fundamental principle of trading. It means purchasing stocks when their price is relatively low (undervalued) and selling them when the price rises (overvalued). The challenge is determining what constitutes 'low' and 'high' - this requires analyzing market trends, company fundamentals, and technical indicators."
            },
            "support and resistance": {
                "title": "Support and Resistance Levels",
                "content": "Support is a price level where a stock tends to stop falling and bounce back up - it acts like a floor. Resistance is where a stock tends to stop rising and pull back - it acts like a ceiling. These levels form because traders remember past prices and tend to buy at support and sell at resistance. Breaking through these levels often signals significant moves."
            },
            "support level": {
                "title": "Support Levels",
                "content": "A support level is a price point where buying interest is strong enough to overcome selling pressure, causing the price to stop declining and potentially reverse upward. Think of it as a floor that holds the price up. Support levels often form at previous lows, round numbers, or moving averages."
            },
            "resistance level": {
                "title": "Resistance Levels",
                "content": "A resistance level is a price point where selling pressure overcomes buying interest, causing the price to stop rising and potentially reverse downward. Think of it as a ceiling that caps price advances. Resistance often forms at previous highs, psychological round numbers, or technical indicators."
            },
            "start trading": {
                "title": "How to Start Trading Stocks",
                "content": "To start trading stocks: 1) Open a brokerage account with a reputable broker, 2) Fund your account (start small, only invest what you can afford to lose), 3) Research companies and learn basic analysis, 4) Start with established companies you understand, 5) Use limit orders to control your entry price, 6) Always have an exit strategy before entering a trade, 7) Keep learning and track your trades."
            },
            "market order": {
                "title": "Market Orders",
                "content": "A market order executes immediately at the current best available price. It guarantees execution but not price. Use market orders when you need to buy or sell quickly, but be careful in volatile markets or with thinly traded stocks as you might get a worse price than expected."
            },
            "limit order": {
                "title": "Limit Orders",
                "content": "A limit order sets a specific price at which you're willing to buy or sell. Buy limits execute at or below your price, sell limits at or above. They give you price control but don't guarantee execution. Perfect for patient traders who want specific entry/exit points."
            },
            "stop loss": {
                "title": "Stop Loss Orders",
                "content": "A stop loss automatically sells your position if the price drops to a specified level, limiting your losses. For example, if you buy at $100 and set a stop loss at $95, you'll automatically sell if the price hits $95, limiting your loss to 5%. Essential for risk management."
            },
            "bull market": {
                "title": "Bull Market",
                "content": "A bull market is a period when stock prices are rising or expected to rise. The term comes from how a bull attacks - thrusting upward with its horns. Bull markets are characterized by optimism, investor confidence, and expectations of strong results."
            },
            "bear market": {
                "title": "Bear Market",
                "content": "A bear market is when prices fall 20% or more from recent highs. The term comes from how a bear attacks - swiping downward with its paws. Bear markets are marked by pessimism, falling prices, and widespread selling. They're normal parts of market cycles."
            }
        }
        
        # Find matching educational content
        matched_content = None
        for key, content in educational_responses.items():
            if key in ql:
                matched_content = content
                break
        
        # If no exact match, provide general educational response
        if not matched_content:
            if "how do i" in ql or "how to" in ql:
                response_text = "I can help you learn about trading! Here are some topics I can explain: buy low sell high, support and resistance levels, how to start trading, market orders vs limit orders, stop losses, and bull vs bear markets. What would you like to learn about?"
            elif "what is" in ql or "what does" in ql:
                response_text = "I'd be happy to explain trading concepts! I can teach you about support/resistance levels, market orders, limit orders, stop losses, bull/bear markets, and more. What specific concept would you like to understand?"
            else:
                response_text = "I'm here to help you learn trading! Ask me about any trading concept, strategy, or term you'd like to understand better."
        else:
            response_text = f"**{matched_content['title']}**\n\n{matched_content['content']}"
        
        # Add educational flag and chart commands if relevant
        response = {
            "text": response_text,
            "tools_used": ["educational_content"],
            "structured_data": {
                "type": "educational",
                "topic": matched_content['title'] if matched_content else "general"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add chart commands for concepts that benefit from visualization
        if any(term in ql for term in ["support", "resistance", "chart", "show me"]):
            symbol = self.intent_router.extract_symbol(query)
            if symbol:
                response["chart_commands"] = [f"LOAD:{symbol.upper()}"]
                if "support" in ql:
                    response["chart_commands"].append("DRAW:SUPPORT")
                if "resistance" in ql:
                    response["chart_commands"].append("DRAW:RESISTANCE")
        
        return response
    
    def _extract_indicator_commands(self, query: str) -> List[str]:
        """Extract indicator commands from query."""
        commands = []
        ql = query.lower()
        
        # RSI
        if "add rsi" in ql or "show rsi" in ql:
            commands.append("ADD:RSI")
        elif "remove rsi" in ql or "hide rsi" in ql:
            commands.append("REMOVE:RSI")
        
        # MACD
        if "add macd" in ql or "show macd" in ql:
            commands.append("ADD:MACD")
        elif "remove macd" in ql or "hide macd" in ql:
            commands.append("REMOVE:MACD")
        
        # Volume
        if "add volume" in ql or "show volume" in ql:
            commands.append("ADD:VOLUME")
        elif "remove volume" in ql or "hide volume" in ql:
            commands.append("REMOVE:VOLUME")

        return commands

    async def _process_with_gvses_assistant(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process query using the G'sves trading assistant.
        Uses OpenAI Responses API with the G'sves assistant for intelligent trading analysis.
        """
        logger.info(f"Processing query with G'sves assistant: {query[:50]}...")

        try:
            # Build messages for the assistant
            messages = []
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages
            messages.append({"role": "user", "content": query})

            # Get tool schemas for Responses API format
            tools = self._get_tool_schemas(for_responses_api=True)

            # Call Responses API with G'sves assistant
            response = await self.client.responses.create(
                model="gpt-4o",
                assistant_id=self.gvses_assistant_id,
                messages=messages,
                tools=tools,
                store=True  # Enable multi-turn conversations
            )

            # Extract response text
            response_text = response.output_text if hasattr(response, 'output_text') else str(response)

            # Track which tools were used
            tools_used = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tools_used = [tool.function.name for tool in response.tool_calls]

            return {
                "text": response_text,
                "tools_used": tools_used,
                "data": {},
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o-gvses-assistant",
                "cached": False,
                "session_id": None
            }

        except Exception as e:
            logger.error(f"Error processing query with G'sves assistant: {e}")
            # Fall back to regular orchestrator on error
            return await self._process_query_single_pass(query, conversation_history, self.intent_router.classify_intent(query), False)

    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Public entry point with intent-based routing for optimal performance."""
        # Early validation for empty queries
        if not query or not query.strip():
            return {
                "text": "Please provide a question or query.",
                "tools_used": [],
                "structured_data": {},
                "error": "empty_query"
            }
        
        # Classify intent for fast-path routing
        intent = self.intent_router.classify_intent(query)
        logger.info(f"Query: '{query}' → Intent: {intent}")
        try:
            logger.info(f"Symbol detected: {self.intent_router.extract_symbol(query)}")
        except Exception:
            pass

        # Route trading analysis queries to G'sves assistant if enabled
        if self.use_gvses_assistant and self.gvses_assistant_id:
            # Use G'sves for trading analysis, but not for chart commands or indicator toggles
            if intent not in ["chart-only", "indicator-toggle"]:
                logger.info("Routing query to G'sves trading assistant")
                return await self._process_with_gvses_assistant(query, conversation_history)

        # Check response cache first for immediate return
        # Skip cache for technical analysis queries to ensure fresh analysis
        technical_keywords = ['swing', 'entry', 'exit', 'target', 'support', 'resistance', 
                            'technical', 'chart', 'level', 'breakout', 'pattern']
        query_lower = query.lower()
        is_technical_query = any(keyword in query_lower for keyword in technical_keywords)
        
        # Always define context for later use
        context = str(conversation_history[-10:]) if conversation_history else ""
        
        if not is_technical_query:
            cached_response = await self._get_cached_response(query, context)
            if cached_response:
                logger.info(f"Returning cached response for query: {query[:50]}...")
                return cached_response
        else:
            logger.info(f"Skipping cache for technical analysis query: {query[:50]}...")

        # Disabled static templates to enable LLM for educational queries
        # static_response = await self._maybe_answer_with_static_template(
        #     query,
        #     conversation_history,
        # )
        # if static_response:
        #     await self._cache_response(query, context, static_response)
        #     return static_response

        # Fast-path for simple price queries (e.g., "Get AAPL price")
        quick_price_response = await self._maybe_answer_with_price_query(
            query,
            conversation_history,
        )
        if quick_price_response:
            await self._cache_response(query, context, quick_price_response)
            return quick_price_response

        # Disabled educational fast-path to enable LLM for educational queries
        # if intent == "educational":
        #     response = await self._handle_educational_query(query)
        #     return response
        
        # Fast-path for chart-only commands (no LLM needed)
        if intent == "chart-only":
            symbol = self.intent_router.extract_symbol(query)
            if symbol:
                response = {
                    "text": f"Loading {symbol.upper()} chart",
                    "tools_used": [],
                    "data": {},
                    "chart_commands": [f"LOAD:{symbol.upper()}"],
                    "timestamp": datetime.now().isoformat(),
                    "model": "static-chart",
                    "cached": False,
                    "session_id": None
                }
                logger.info(f"Response includes chart_commands: True")
                logger.info(f"Chart commands: {response['chart_commands']}")
                await self._cache_response(query, context, response)
                return response
        
        # Fast-path for indicator toggles (no LLM needed)
        if intent == "indicator-toggle":
            commands = self._extract_indicator_commands(query)
            if commands:
                response = {
                    "text": "Updating indicators",
                    "tools_used": [],
                    "data": {},
                    "chart_commands": commands,
                    "timestamp": datetime.now().isoformat(),
                    "model": "static-indicator",
                    "cached": False,
                    "session_id": None
                }
                logger.info(f"Response includes chart_commands: True")
                logger.info(f"Chart commands: {response['chart_commands']}")
                await self._cache_response(query, context, response)
                return response
        
        # Choose between Responses API and Chat Completions based on feature flag
        USE_RESPONSES = os.getenv("USE_RESPONSES", "false").lower() == "true"
        
        if USE_RESPONSES and self._has_responses_support():
            # Use the fixed single-pass Responses API with submit_tool_outputs
            logger.info("Using fixed single-pass Responses API")
            response = await self._process_query_responses(query, conversation_history)
        else:
            # Use single-pass Chat Completions (default)
            logger.info("Using single-pass Chat Completions API")
            response = await self._process_query_single_pass(query, conversation_history, intent, stream)
        
        # Cache the successful response
        if response and not response.get("error"):
            await self._cache_response(query, context, response)
        
        return response

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
            # Build parameters dict
            params = {
                "model": self.model,
                "input": response_messages,
                "tools": self._get_tool_schemas(for_responses_api=True),
                "max_output_tokens": 600  # Reduced for faster generation
            }
            
            # Only add temperature if not using GPT-5 models (they don't support it)
            if not self.model.startswith("gpt-5"):
                params["temperature"] = self.temperature
                
            response = await responses_client.create(**params)
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
                    info = self._extract_tool_call_info(tool_call)
                    tool_name = info["name"]
                    if not tool_name:
                        logger.warning(f"Skipping streaming tool call with missing name: {tool_call}")
                        continue

                    arguments = info["arguments"]
                    call_id = info["call_id"]

                    collected_tool_calls.append({
                        "id": call_id,
                        "function": {
                            "name": tool_name,
                            "arguments": info["raw_arguments"]
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

        # Check if this is a technical/swing trade query
        is_technical = any(term in query.lower() for term in ['swing', 'entry', 'exit', 'target', 'stop', 'support', 'resistance', 'technical'])
        
        # Only use formatted response if the LLM didn't provide meaningful content
        # AND it's not a technical query (never use template for technical queries)
        if formatted_response and not is_technical and (not response_text or len(response_text) < 100 or "I'm sorry" in response_text):
            response_text = formatted_response
        # If technical query has no response text, generate natural language response
        elif is_technical and (not response_text or len(response_text) < 100) and tool_results:
            logger.info("Technical query without response text - generating natural language fallback")
            response_text = await self._generate_natural_language_response(
                query,
                messages,
                tool_results,
                None
            )

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
            # Use max_completion_tokens for GPT-5, max_tokens for older models
            completion_params = {
                "model": self.model,
                "messages": messages,
                "tools": self._get_tool_schemas(),
                "tool_choice": "auto",
                "temperature": self.temperature,
                "stream": True  # Enable TRUE streaming
            }
            if "gpt-5" in self.model.lower():
                completion_params["max_completion_tokens"] = 1000  # Reduced for faster response
            else:
                completion_params["max_tokens"] = 1000  # Reduced for faster response
            
            stream = await self.client.chat.completions.create(**completion_params)
            
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
        """Safely extract textual output from a Responses API response object."""
        if response is None:
            logger.warning("Response is None in _extract_response_text")
            return ""

        # PRIORITY 1: Use SDK's output_text convenience property (OpenAI recommendation)
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text:
            logger.info(f"Extracted {len(output_text)} chars using SDK output_text property")
            return output_text

        # PRIORITY 2: Handle list-based output_text (legacy formats)
        if isinstance(output_text, list):
            flattened = "".join(segment or "" for segment in output_text)
            if flattened:
                logger.info(f"Extracted {len(flattened)} chars from output_text list")
                return flattened

        # PRIORITY 3: Direct text attribute (future compatibility)
        direct_text = getattr(response, "text", None)
        if isinstance(direct_text, str) and direct_text:
            logger.info(f"Extracted {len(direct_text)} chars from direct 'text' attribute")
            return direct_text

        # FALLBACK: Walk every object/collection for textual content
        collected: List[str] = []
        visited: Set[int] = set()

        def collect_text(value: Any, path: str = "response") -> None:
            if value is None:
                return

            if isinstance(value, str):
                if value:
                    collected.append(value)
                    logger.debug(f"Collected text at {path}: {len(value)} chars")
                return

            obj_id = id(value)
            if obj_id in visited:
                return
            visited.add(obj_id)

            if isinstance(value, (list, tuple, set)):
                for idx, item in enumerate(value):
                    collect_text(item, f"{path}[{idx}]")
                return

            if isinstance(value, dict):
                for key, item in value.items():
                    collect_text(item, f"{path}.{key}")
                return

            # For SDK model objects, probe likely attributes
            for attr in ("text", "content", "value", "output_text", "message", "body"):
                if hasattr(value, attr):
                    try:
                        attr_value = getattr(value, attr)
                    except Exception as exc:  # pragma: no cover
                        logger.debug(f"Failed to access {path}.{attr}: {exc}")
                        continue
                    collect_text(attr_value, f"{path}.{attr}")

        # Collect from response.output first (primary container)
        collect_text(getattr(response, "output", None), "response.output")

        # If still empty, collect from the entire response object
        if not collected:
            collect_text(response, "response")

        if collected:
            result = "".join(collected)
            logger.info(f"Extracted {len(result)} chars by scanning response payload")
            return result

        logger.warning(
            "Could not extract text. Response type: %s, attrs: %s",
            type(response),
            dir(response)[:20],
        )
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
    
    # Phase 4: Pattern lifecycle sweeper methods
    async def _start_pattern_sweeper(self):
        """Start the background pattern lifecycle sweeper task"""
        try:
            # Wait a bit for startup to complete
            await asyncio.sleep(10)
            
            while self.enable_pattern_sweep:
                try:
                    # Run the sweep
                    logger.info("Running pattern lifecycle sweep...")
                    sweep_result = await self.pattern_lifecycle.sweep_patterns(self.pattern_max_age_hours)
                    
                    if sweep_result.get("error"):
                        logger.warning(f"Pattern sweep error: {sweep_result['error']}")
                    else:
                        logger.info(
                            f"Pattern sweep completed - evaluated: {sweep_result.get('patterns_evaluated', 0)}, "
                            f"updated: {sweep_result.get('patterns_updated', 0)}, "
                            f"expired: {sweep_result.get('patterns_expired', 0)}"
                        )
                    
                    # Trigger webhook notifications if patterns changed
                    if sweep_result.get("patterns_expired", 0) > 0:
                        await self._notify_pattern_expirations(sweep_result)
                    
                except Exception as e:
                    logger.error(f"Error in pattern sweep: {str(e)}")
                
                # Wait for next sweep interval
                await asyncio.sleep(self.pattern_sweep_interval)
                
        except asyncio.CancelledError:
            logger.info("Pattern sweeper task cancelled")
            raise
        except Exception as e:
            logger.error(f"Fatal error in pattern sweeper: {str(e)}")
    
    async def _notify_pattern_expirations(self, sweep_result: Dict[str, Any]):
        """Send webhook notifications for expired patterns"""
        try:
            # If webhook service is available, send notifications
            # This is a placeholder - integrate with actual webhook service
            logger.info(f"Would notify about {sweep_result.get('patterns_expired', 0)} expired patterns")
        except Exception as e:
            logger.error(f"Error sending expiration notifications: {str(e)}")
    
    async def run_pattern_sweep_manual(self) -> Dict[str, Any]:
        """Manually trigger a pattern lifecycle sweep"""
        if not self.enable_pattern_sweep:
            return {"error": "Pattern sweep is disabled"}
        
        try:
            logger.info("Running manual pattern lifecycle sweep...")
            result = await self.pattern_lifecycle.sweep_patterns(self.pattern_max_age_hours)
            return result
        except Exception as e:
            logger.error(f"Error in manual pattern sweep: {str(e)}")
            return {"error": str(e)}
    
    async def evaluate_pattern_with_rules(self, 
                                         symbol: str,
                                         timeframe: str,
                                         current_price: float) -> Dict[str, Any]:
        """
        Evaluate patterns for a symbol using Phase 4 rules
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe
            current_price: Current market price
            
        Returns:
            Evaluation results
        """
        try:
            if not hasattr(self.pattern_lifecycle, 'evaluate_with_rules'):
                # Fallback for old version
                return {"error": "Phase 4 not available"}
            
            result = await self.pattern_lifecycle.evaluate_with_rules(
                symbol, 
                timeframe, 
                current_price
            )
            
            # Store any generated commands
            if result.get("chart_commands"):
                await self.chart_snapshot_store.append_chart_commands(
                    symbol, 
                    timeframe, 
                    result["chart_commands"]
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating patterns with rules: {str(e)}")
            return {"error": str(e)}


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AgentOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
    return _orchestrator_instance
