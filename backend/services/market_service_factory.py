"""
Market Service Factory
======================
Hybrid factory that provides BOTH Direct API and MCP services for optimal performance.
- Direct API: Fast Yahoo Finance HTTP calls for price/history queries
- MCP: Comprehensive news from CNBC + Yahoo, Alpaca data support
"""

import logging
import os
from typing import Any, Optional, Dict, List
import asyncio
from datetime import datetime, timezone, timedelta

from services.database_service import get_database_service
from pattern_detection import PatternDetector

logger = logging.getLogger(__name__)


class MarketServiceWrapper:
    """
    Simple wrapper around the original market_service.py functions.
    Provides a consistent interface for the factory pattern.
    Includes intelligent crypto symbol detection.
    """
    
    # Popular cryptocurrency symbols that users expect to map to -USD pairs
    CRYPTO_SYMBOLS = {
        'BTC': 'BTC-USD',    # Bitcoin
        'ETH': 'ETH-USD',    # Ethereum
        'ADA': 'ADA-USD',    # Cardano
        'DOT': 'DOT-USD',    # Polkadot
        'SOL': 'SOL-USD',    # Solana
        'MATIC': 'MATIC-USD', # Polygon
        'AVAX': 'AVAX-USD',  # Avalanche
        'LTC': 'LTC-USD',    # Litecoin
        'XRP': 'XRP-USD',    # Ripple
        'DOGE': 'DOGE-USD',  # Dogecoin
        'SHIB': 'SHIB-USD',  # Shiba Inu
        'UNI': 'UNI-USD',    # Uniswap
        'LINK': 'LINK-USD',  # Chainlink
        'BCH': 'BCH-USD',    # Bitcoin Cash
        'XLM': 'XLM-USD',    # Stellar
    }
    
    def _map_crypto_symbol(self, symbol: str) -> tuple[str, str]:
        """
        Map crypto symbols to their -USD pairs for accurate pricing.
        
        Returns:
            tuple: (mapped_symbol, asset_type)
        """
        upper_symbol = symbol.upper()
        
        # If already in crypto format, keep as is
        if '-USD' in upper_symbol:
            return upper_symbol, 'crypto'
        
        # Check if it's a known crypto that should map to -USD
        if upper_symbol in self.CRYPTO_SYMBOLS:
            mapped_symbol = self.CRYPTO_SYMBOLS[upper_symbol]
            logger.info(f"Mapping crypto symbol {symbol} -> {mapped_symbol}")
            return mapped_symbol, 'crypto'
        
        # Not a crypto, treat as stock
        return upper_symbol, 'stock'
    
    def __init__(self):
        # Import the original MCP-based functions
        from services.market_service import (
            get_quote,
            get_ohlcv,
            humanize_market_cap,
            build_summary_table
        )
        from services.news_service import get_related_news
        
        # Store references to the functions
        self._get_quote = get_quote
        self._get_ohlcv = get_ohlcv
        self._get_news = get_related_news
        self.humanize_market_cap = humanize_market_cap
        self.build_summary_table = build_summary_table
    
    async def get_stock_price(self, symbol: str) -> dict:
        """Get stock price - includes crypto symbol mapping and intelligent routing."""
        
        # Map crypto symbols to proper format
        mapped_symbol, asset_type = self._map_crypto_symbol(symbol)
        
        # Try Alpaca first for real-time quotes (professional-grade) - but only for stocks
        if asset_type == 'stock':
            try:
                # Check if we can use Alpaca
                from services.market_service import get_quote_from_alpaca, ALPACA_AVAILABLE
                
                if ALPACA_AVAILABLE:
                    logger.info(f"Using Alpaca for {mapped_symbol} quote")
                    quote = await get_quote_from_alpaca(mapped_symbol)
                    quote["data_source"] = "alpaca"
                    quote["asset_type"] = asset_type
                    return quote
            except Exception as e:
                logger.warning(f"Alpaca quote failed: {e}, falling back to Yahoo Finance")
        
        # Use Yahoo Finance (supports both stocks and crypto)
        logger.info(f"Using Yahoo Finance for {mapped_symbol} quote (asset_type: {asset_type})")
        quote = await self._get_quote(mapped_symbol)
        
        # Normalize field names from MCP format to Direct format
        # MCP returns: last, prev_close, change_pct
        # Direct/endpoint expects: price, previous_close, change_percent
        if "last" in quote and "price" not in quote:
            quote["price"] = quote["last"]
        if "prev_close" in quote and "previous_close" not in quote:
            quote["previous_close"] = quote["prev_close"]
        if "change_pct" in quote and "change_percent" not in quote:
            quote["change_percent"] = quote["change_pct"]
        
        quote["data_source"] = "yahoo_mcp"
        quote["asset_type"] = asset_type
        
        # If we mapped a crypto symbol, update the response to show original symbol
        if mapped_symbol != symbol.upper():
            quote["original_symbol"] = symbol.upper()
            quote["mapped_from"] = f"{symbol.upper()} -> {mapped_symbol}"
        
        return quote
    
    async def get_stock_history(self, symbol: str, days: int = 50, interval: str = "1d") -> dict:
        """Get stock history - includes caching, crypto symbol mapping and intelligent routing.

        Args:
            symbol: Stock symbol
            days: Number of days to fetch
            interval: Data interval - '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
        """

        # Map crypto symbols to proper format
        mapped_symbol, asset_type = self._map_crypto_symbol(symbol)
        
        # Check cache first
        try:
            db_service = get_database_service()
            cached_candles = await db_service.get_market_candles(
                symbol=symbol.upper(),
                timeframe="1d",
                start_time=datetime.now(timezone.utc) - timedelta(days=days),
                limit=days * 2  # Get extra in case of weekends/holidays
            )
            
            if cached_candles and len(cached_candles) >= days * 0.7:  # At least 70% of expected data
                logger.info(f"Using cached data for {symbol}: {len(cached_candles)} candles")
                return {
                    "symbol": symbol.upper(),
                    "candles": cached_candles,
                    "period": f"{days}D",
                    "data_source": "cache",
                    "cached": True
                }
        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")
        
        # Try Alpaca first for chart data (professional-grade) - but only for stocks
        if asset_type == 'stock':
            try:
                # Check if we can use Alpaca
                from services.market_service import get_ohlcv_from_alpaca, ALPACA_AVAILABLE
                
                if ALPACA_AVAILABLE:
                    logger.info(f"Using Alpaca for {mapped_symbol} chart data")
                    candles = await get_ohlcv_from_alpaca(mapped_symbol, days)
                    
                    # Cache the data asynchronously
                    asyncio.create_task(self._cache_candles(symbol.upper(), "1d", candles, "alpaca"))
                    
                    return {
                        "symbol": symbol.upper(),
                        "candles": candles,
                        "period": f"{days}D",
                        "data_source": "alpaca",
                        "asset_type": asset_type
                    }
            except Exception as e:
                logger.warning(f"Alpaca chart data failed: {e}, falling back to Yahoo Finance")
        
        # Use Yahoo Finance (supports both stocks and crypto)
        logger.info(f"Using Yahoo Finance for {mapped_symbol} chart data (asset_type: {asset_type})")
        
        # Map days to range string for Yahoo
        if days <= 1:
            range_str = "1D"
        elif days <= 5:
            range_str = "5D" 
        elif days <= 30:
            range_str = "1M"
        elif days <= 90:
            range_str = "3M"
        elif days <= 180:
            range_str = "6M"
        elif days <= 365:
            range_str = "1Y"
        else:
            range_str = "5Y"
        
        candles = await self._get_ohlcv(mapped_symbol, range_str)
        
        # Cache the data asynchronously
        asyncio.create_task(self._cache_candles(symbol.upper(), "1d", candles, "yahoo_mcp"))
        
        result = {
            "symbol": symbol.upper(),
            "candles": candles,
            "period": range_str,
            "data_source": "yahoo_mcp",
            "asset_type": asset_type
        }
        
        # If we mapped a crypto symbol, include mapping info
        if mapped_symbol != symbol.upper():
            result["original_symbol"] = symbol.upper()
            result["mapped_from"] = f"{symbol.upper()} -> {mapped_symbol}"
        
        return result
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """Get stock news via MCP (includes CNBC and Yahoo) with caching."""
        
        # Check cache first
        try:
            db_service = get_database_service()
            cached_news = await db_service.get_market_news(
                symbol=symbol.upper(),
                days=1,  # Get news from last day
                limit=limit
            )
            
            if cached_news and len(cached_news) >= limit * 0.5:  # At least 50% of requested articles
                logger.info(f"Using cached news for {symbol}: {len(cached_news)} articles")
                return {
                    "symbol": symbol.upper(),
                    "articles": cached_news,
                    "total": len(cached_news),
                    "data_sources": ["Cache"],
                    "data_source": "cache",
                    "cached": True
                }
        except Exception as e:
            logger.warning(f"News cache lookup failed: {e}")
        
        # Fetch fresh news
        news = await self._get_news(symbol, limit)
        
        # Handle the "items" field from get_related_news
        articles = news.get("articles", news.get("news", news.get("items", [])))
        
        # Cache the news asynchronously
        if articles:
            asyncio.create_task(self._cache_news(articles, symbol.upper()))
        
        # Ensure consistent format
        return {
            "symbol": symbol.upper(),
            "articles": articles,
            "total": len(articles),
            "data_sources": ["Yahoo Finance", "CNBC"],  # MCP provides both
            "data_source": "mcp"
        }
    
    async def get_comprehensive_stock_data(self, symbol: str) -> dict:
        """Get comprehensive stock data via MCP."""
        try:
            # Get quote and history - request 6M for enough data for advanced TA (200+ candles)
            quote = await self._get_quote(symbol)
            candles = await self._get_ohlcv(symbol, "6M")  # Get 6 months for advanced TA
            
            # Calculate technical levels with advanced TA or fallback
            technical_levels = await self._calculate_technical_levels(symbol, candles, quote)

            # Detect chart patterns from candle data
            patterns_result: Dict[str, Any] = {"detected": []}
            try:
                if candles:
                    print(f"🔍 [{symbol}] Pattern detection starting with {len(candles)} candles")
                    logger.info(f"[{symbol}] Pattern detection: {len(candles)} candles available")
                    detector = PatternDetector(candles)
                    detected_patterns = detector.detect_all_patterns()
                    total_detected = len(detected_patterns.get('detected', [])) if isinstance(detected_patterns, dict) else 0
                    print(f"✅ [{symbol}] Patterns found: {total_detected} total")
                    logger.info(f"[{symbol}] Patterns found: {total_detected} total")
                    if isinstance(detected_patterns, dict):
                        detected = detected_patterns.get("detected", [])
                        
                        # Sort patterns by end_candle (most recent first, right to left on chart)
                        detected_sorted = sorted(
                            detected,
                            key=lambda p: p.get("end_candle", p.get("start_candle", 0)),
                            reverse=True  # Most recent first
                        )
                        
                        augmented_patterns = []
                        # Limit patterns to avoid overwhelming the frontend
                        # Can be configured via MAX_PATTERNS_PER_SYMBOL env var (default: 10)
                        max_patterns = int(os.getenv("MAX_PATTERNS_PER_SYMBOL", "10"))
                        patterns_to_process = detected_sorted[:max_patterns]
                        print(f"📊 [{symbol}] Processing {len(patterns_to_process)} of {len(detected)} detected patterns (limit: {max_patterns}, sorted by recency)")
                        
                        for pattern in patterns_to_process:
                            start_idx = pattern.get("start_candle")
                            end_idx = pattern.get("end_candle")
                            if start_idx is not None and 0 <= start_idx < len(candles):
                                pattern["start_time"] = candles[start_idx].get("time")
                                pattern["start_price"] = candles[start_idx].get("close")
                            if end_idx is not None and 0 <= end_idx < len(candles):
                                pattern["end_time"] = candles[end_idx].get("time")
                                pattern["end_price"] = candles[end_idx].get("close")

                            metadata = pattern.get("metadata", {})
                            if metadata:
                                chart_overlay = self._build_chart_metadata_from_pattern(metadata, candles)
                                if chart_overlay:
                                    pattern["chart_metadata"] = chart_overlay

                            # Add visual_config for pattern rendering (Phase 2A)
                            if start_idx is not None and end_idx is not None and start_idx < len(candles):
                                try:
                                    # Clamp end_idx to available data to prevent index out of range
                                    end_idx = min(end_idx, len(candles) - 1)
                                    
                                    pattern_type = pattern.get("pattern_type", pattern.get("type", ""))
                                    signal = pattern.get("signal", "neutral")
                                    confidence = pattern.get("confidence", 0)
                                    
                                    # Calculate boundary box
                                    candle_indices = list(range(start_idx, end_idx + 1))
                                    candle_highs = [candles[i].get("high", 0) for i in candle_indices if i < len(candles)]
                                    candle_lows = [candles[i].get("low", 0) for i in candle_indices if i < len(candles)]
                                    
                                    # Better default price handling - avoid None values
                                    default_price = (
                                        pattern.get("start_price") or 
                                        pattern.get("end_price") or 
                                        candles[start_idx].get("close", 0)
                                    )
                                    pattern_high = max(candle_highs) if candle_highs else default_price
                                    pattern_low = min(candle_lows) if candle_lows else default_price
                                    
                                    # Get timestamps
                                    start_time = pattern.get("start_time", candles[start_idx].get("time"))
                                    end_time = pattern.get("end_time", candles[end_idx].get("time"))
                                    
                                    # Fix for single-day patterns (Doji, Hammer, etc.)
                                    if end_time <= start_time:
                                        end_time = start_time + 86400  # Add 1 day
                                    
                                    pattern_color = self._get_pattern_color(pattern_type, signal)
                                    
                                    pattern["visual_config"] = {
                                        "candle_indices": candle_indices,
                                        "candle_overlay_color": pattern_color,
                                        "boundary_box": {
                                            "start_time": start_time,
                                            "end_time": end_time,
                                            "high": float(pattern_high),
                                            "low": float(pattern_low),
                                            "border_color": pattern_color,
                                            "border_width": 2,
                                            "fill_opacity": 0.1
                                        },
                                        "label": {
                                            "text": f"{pattern_type.replace('_', ' ').title()} ({confidence}%)",
                                            "position": "top_right",
                                            "background_color": pattern_color,
                                            "text_color": "#FFFFFF",
                                            "font_size": 12
                                        },
                                        "markers": self._generate_pattern_markers(pattern, candles, start_idx, end_idx)
                                    }
                                    
                                    logger.info(f"[{symbol}] Added visual_config to {pattern_type}: {len(candle_indices)} candles, {len(pattern['visual_config']['markers'])} markers")
                                except Exception as visual_error:
                                    logger.error(f"[{symbol}] Failed to add visual_config to {pattern.get('pattern_type', 'unknown')}: {visual_error}")
                                    # Continue without visual_config for this pattern - don't crash entire response
                                    pass

                            # Add pattern category (Reversal, Continuation, Neutral)
                            pattern_type = pattern.get("pattern_type", "").lower()
                            if any(x in pattern_type for x in ["engulfing", "hammer", "star", "head", "shoulders", "double", "triple", "reversal"]):
                                pattern["category"] = "Reversal"
                            elif any(x in pattern_type for x in ["flag", "pennant", "triangle", "channel", "cup"]):
                                pattern["category"] = "Continuation"
                            else:
                                pattern["category"] = "Neutral"
                            
                            augmented_patterns.append(pattern)
                        detected_patterns["detected"] = augmented_patterns
                        logger.info(f"[{symbol}] Returning top {len(augmented_patterns)} patterns with metadata")
                        print(f"🎯 [{symbol}] PATTERNS RESULT BEFORE RETURN:", patterns_result)
                        print(f"🎯 [{symbol}] AUGMENTED PATTERNS:", augmented_patterns)
                        for i, p in enumerate(augmented_patterns):
                            print(f"   Pattern {i}: {p.get('pattern_type')} - has_chart_metadata={bool(p.get('chart_metadata'))}")
                        patterns_result = detected_patterns
                else:
                    logger.warning(f"[{symbol}] No candles available for pattern detection")
            except Exception as pattern_error:
                logger.error(f"Pattern detection failed for {symbol}: {pattern_error}", exc_info=True)
                print(f"❌ [{symbol}] PATTERN DETECTION ERROR:", pattern_error)

            print(f"🚀 [{symbol}] FINAL RETURN - patterns_result:", patterns_result)
            print(f"🚀 [{symbol}] patterns_result type:", type(patterns_result))
            print(f"🚀 [{symbol}] patterns_result.detected length:", len(patterns_result.get('detected', [])))
            
            return {
                "symbol": symbol.upper(),
                "price_data": quote,
                "technical_levels": technical_levels,
                "patterns": patterns_result,
                "data_source": "mcp"
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive data: {e}")
            return {
                "symbol": symbol.upper(),
                "price_data": {},
                "technical_levels": {},
                "patterns": {"detected": []},
                "data_source": "error",
                "error": str(e)
            }
    
    async def warm_up(self):
        """Pre-warm MCP connection."""
        try:
            logger.info("Warming up MCP-based market service...")
            await self._get_quote("SPY")
            logger.info("Market service ready")
        except Exception as e:
            logger.warning(f"Market service warm-up failed: {e}")

    def _build_chart_metadata_from_pattern(self, metadata: Dict[str, Any], candles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert pattern metadata into chart overlay instructions."""

        if not metadata:
            return None

        chart_data: Dict[str, Any] = {"trendlines": [], "levels": []}

        def resolve_point(point_meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            index = point_meta.get("candle")
            price = point_meta.get("price")
            if index is None or price is None:
                return None
            if not (0 <= index < len(candles)):
                return None
            time_value = candles[index].get("time")
            return {
                "time": time_value,
                "price": float(price)
            }

        # Trendlines (upper/lower)
        for key in ["upper_trendline", "lower_trendline"]:
            trendline = metadata.get(key)
            if trendline:
                start_idx = trendline.get("start_candle")
                end_idx = trendline.get("end_candle")
                if start_idx is not None and end_idx is not None:
                    if 0 <= start_idx < len(candles) and 0 <= end_idx < len(candles):
                        chart_data["trendlines"].append({
                            "type": key,
                            "start": {
                                "time": candles[start_idx].get("time"),
                                "price": float(trendline.get("start_price", candles[start_idx].get("close", 0)))
                            },
                            "end": {
                                "time": candles[end_idx].get("time"),
                                "price": float(trendline.get("end_price", candles[end_idx].get("close", 0)))
                            }
                        })

        # Channel bounds or neckline/horizontal levels
        level_keys = {
            "horizontal_level": "resistance",
            "neckline": "neckline",
            "cup_low": "support",
            "left_peak": "resistance",
            "right_peak": "resistance"
        }

        for meta_key, level_type in level_keys.items():
            value = metadata.get(meta_key)
            if value is not None:
                chart_data["levels"].append({
                    "type": level_type,
                    "price": float(value)
                })

        channel_bounds = metadata.get("channel_bounds")
        if isinstance(channel_bounds, dict):
            upper = channel_bounds.get("upper")
            lower = channel_bounds.get("lower")
            if upper is not None:
                chart_data["levels"].append({
                    "type": "resistance",
                    "price": float(upper)
                })
            if lower is not None:
                chart_data["levels"].append({
                    "type": "support",
                    "price": float(lower)
                })

        swing_highs = metadata.get("swing_highs")
        if isinstance(swing_highs, list):
            for swing in swing_highs:
                point = resolve_point(swing)
                if point:
                    chart_data["levels"].append({
                        "type": "pivot_high",
                        "price": point["price"],
                        "time": point["time"]
                    })

        swing_lows = metadata.get("swing_lows")
        if isinstance(swing_lows, list):
            for swing in swing_lows:
                point = resolve_point(swing)
                if point:
                    chart_data["levels"].append({
                        "type": "pivot_low",
                        "price": point["price"],
                        "time": point["time"]
                    })

        troughs = metadata.get("troughs") or metadata.get("peaks")
        if isinstance(troughs, list):
            label = "pivot_low" if metadata.get("troughs") else "pivot_high"
            for swing in troughs:
                point = resolve_point(swing)
                if point:
                    chart_data["levels"].append({
                        "type": label,
                        "price": point["price"],
                        "time": point["time"]
                    })

        slope_change = metadata.get("slope_change")
        if slope_change is not None:
            chart_data.setdefault("annotations", []).append({
                "type": "trend_note",
                "value": float(slope_change)
            })

        # Remove empty buckets
        chart_data = {k: v for k, v in chart_data.items() if v}

        return chart_data or None

    def _get_pattern_color(self, pattern_type: str, signal: str) -> str:
        """Return color based on pattern bias."""
        if signal == "bullish":
            return "#10b981"  # Green
        elif signal == "bearish":
            return "#ef4444"  # Red
        else:
            return "#3b82f6"  # Blue (neutral)
    

    def _generate_pattern_markers(
        self,
        pattern: Dict[str, Any],
        candles: List[Dict[str, Any]],
        start_idx: int,
        end_idx: int
    ) -> List[Dict[str, Any]]:
        """Generate visual markers (arrows, circles) for pattern education."""
        markers = []
        pattern_type = pattern.get("pattern_type", pattern.get("type", ""))
        metadata = pattern.get("metadata", {})
        
        # Doji - circle marker at center
        if "doji" in pattern_type.lower():
            if start_idx < len(candles):
                candle = candles[start_idx]
                markers.append({
                    "type": "circle",
                    "time": candle.get("time"),
                    "price": candle.get("close"),
                    "color": "#3b82f6",
                    "radius": 8,
                    "label": "Doji (Indecision)"
                })
        
        # Bullish Engulfing - arrow up on engulfing candle
        elif pattern_type == "bullish_engulfing":
            if end_idx < len(candles):
                candle = candles[end_idx]
                markers.append({
                    "type": "arrow",
                    "direction": "up",
                    "time": candle.get("time"),
                    "price": candle.get("high"),
                    "color": "#10b981",
                    "label": "Engulfing Candle"
                })
        
        # Bearish Engulfing - arrow down on engulfing candle
        elif pattern_type == "bearish_engulfing":
            if end_idx < len(candles):
                candle = candles[end_idx]
                markers.append({
                    "type": "arrow",
                    "direction": "down",
                    "time": candle.get("time"),
                    "price": candle.get("low"),
                    "color": "#ef4444",
                    "label": "Engulfing Candle"
                })
        
        # Hammer - arrow up below candle
        elif "hammer" in pattern_type.lower():
            if start_idx < len(candles):
                candle = candles[start_idx]
                markers.append({
                    "type": "arrow",
                    "direction": "up",
                    "time": candle.get("time"),
                    "price": candle.get("low"),
                    "color": "#10b981",
                    "label": "Hammer"
                })
        
        # Shooting Star - arrow down above candle
        elif "shooting_star" in pattern_type.lower():
            if start_idx < len(candles):
                candle = candles[start_idx]
                markers.append({
                    "type": "arrow",
                    "direction": "down",
                    "time": candle.get("time"),
                    "price": candle.get("high"),
                    "color": "#ef4444",
                    "label": "Shooting Star"
                })
        
        # Head and Shoulders - mark left shoulder, head, right shoulder
        elif "head_shoulders" in pattern_type.lower() or "head_and_shoulders" in pattern_type.lower():
            if "left_shoulder" in metadata and "head" in metadata and "right_shoulder" in metadata:
                # Left shoulder
                ls_idx = metadata["left_shoulder"].get("candle") if isinstance(metadata["left_shoulder"], dict) else None
                if ls_idx is not None and 0 <= ls_idx < len(candles):
                    markers.append({
                        "type": "circle",
                        "time": candles[ls_idx].get("time"),
                        "price": candles[ls_idx].get("high"),
                        "color": "#ef4444",
                        "radius": 6,
                        "label": "Left Shoulder"
                    })
                
                # Head
                head_idx = metadata["head"].get("candle") if isinstance(metadata["head"], dict) else None
                if head_idx is not None and 0 <= head_idx < len(candles):
                    markers.append({
                        "type": "circle",
                        "time": candles[head_idx].get("time"),
                        "price": candles[head_idx].get("high"),
                        "color": "#ef4444",
                        "radius": 10,
                        "label": "Head"
                    })
                
                # Right shoulder
                rs_idx = metadata["right_shoulder"].get("candle") if isinstance(metadata["right_shoulder"], dict) else None
                if rs_idx is not None and 0 <= rs_idx < len(candles):
                    markers.append({
                        "type": "circle",
                        "time": candles[rs_idx].get("time"),
                        "price": candles[rs_idx].get("high"),
                        "color": "#ef4444",
                        "radius": 6,
                        "label": "Right Shoulder"
                    })
        
        # Double Top - mark both peaks
        elif "double_top" in pattern_type.lower():
            troughs = metadata.get("peaks") or metadata.get("troughs", [])
            for i, peak in enumerate(troughs[:2]):
                peak_idx = peak.get("candle") if isinstance(peak, dict) else None
                if peak_idx is not None and 0 <= peak_idx < len(candles):
                    markers.append({
                        "type": "circle",
                        "time": candles[peak_idx].get("time"),
                        "price": candles[peak_idx].get("high"),
                        "color": "#ef4444",
                        "radius": 8,
                        "label": f"Peak {i+1}"
                    })
        
        # Double Bottom - mark both bottoms
        elif "double_bottom" in pattern_type.lower():
            troughs = metadata.get("troughs") or metadata.get("peaks", [])
            for i, trough in enumerate(troughs[:2]):
                trough_idx = trough.get("candle") if isinstance(trough, dict) else None
                if trough_idx is not None and 0 <= trough_idx < len(candles):
                    markers.append({
                        "type": "circle",
                        "time": candles[trough_idx].get("time"),
                        "price": candles[trough_idx].get("low"),
                        "color": "#10b981",
                        "radius": 8,
                        "label": f"Bottom {i+1}"
                    })
        
        return markers

    async def _calculate_technical_levels(self, symbol: str, candles: list, quote: dict) -> dict:
        """
        Calculate technical levels with advanced TA module or fallback to simple calculations.
        Implements Day 3.1 of integration plan.
        """
        import asyncio
        import sys
        import os
        
        # Add parent directory to path to import advanced_technical_analysis
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            # Try to use advanced technical analysis with timeout
            from advanced_technical_analysis import AdvancedTechnicalAnalysis
            
            # Extract price and volume data for advanced TA
            prices = [c.get('close', c.get('c', 0)) for c in candles[-200:]]  # Last 200 candles
            volumes = [c.get('volume', c.get('v', 0)) for c in candles[-200:]]  # Last 200 volumes
            current_price = quote.get('price', quote.get('last', 0))
            
            # Check if we have enough data
            if len(prices) >= 50 and current_price > 0:
                # Apply 3-second timeout for advanced calculations
                async def calculate_with_timeout():
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None,
                        AdvancedTechnicalAnalysis.calculate_advanced_levels,
                        prices,
                        volumes,
                        current_price
                    )
                
                try:
                    result = await asyncio.wait_for(calculate_with_timeout(), timeout=3.0)
                    
                    # Ensure consistent field names (sell_high_level, buy_low_level, btd_level, retest_level)
                    return {
                        "sell_high_level": result.get("sell_high_level", current_price * 1.03),
                        "buy_low_level": result.get("buy_low_level", current_price * 0.96),
                        "btd_level": result.get("btd_level", current_price * 0.92),
                        "retest_level": result.get("retest_level", current_price * 0.98),
                        "ma_20": result.get("ma_20", current_price * 0.99),
                        "ma_50": result.get("ma_50", current_price * 0.97),
                        "ma_200": result.get("ma_200", current_price * 0.93),
                        "recent_high": result.get("recent_high", current_price * 1.05),
                        "recent_low": result.get("recent_low", current_price * 0.95),
                        "fib_levels": result.get("fib_levels", {}),
                        "volume_profile": result.get("volume_profile"),
                        "calculation_method": "advanced"
                    }
                except asyncio.TimeoutError:
                    logger.warning(f"Advanced TA calculation timed out for {symbol}, using fallback")
            else:
                logger.info(f"Insufficient data for advanced TA on {symbol} (only {len(prices)} candles)")
        
        except ImportError as e:
            logger.warning(f"Advanced TA module not available: {e}")
        except Exception as e:
            logger.error(f"Error in advanced TA calculation: {e}")
        
        # Fallback to simple calculations (original inline logic)
        current_price = quote.get('price', quote.get('last', 0))
        
        if current_price > 0:
            # Simple percentage-based levels
            return {
                "sell_high_level": round(current_price * 1.03, 2),  # 3% above for sell high
                "buy_low_level": round(current_price * 0.96, 2),  # 4% below for buy low
                "btd_level": round(current_price * 0.92, 2), # 8% below for buy the dip
                "retest_level": round(current_price * 0.98, 2), # 2% below for retest
                "ma_20": round(current_price * 0.99, 2),
                "ma_50": round(current_price * 0.97, 2),
                "ma_200": round(current_price * 0.93, 2),
                "recent_high": round(current_price * 1.05, 2),
                "recent_low": round(current_price * 0.95, 2),
                "fib_levels": {},
                "volume_profile": None,
                "calculation_method": "simple"
            }
        else:
            # No price data available
            return {
                "sell_high_level": 0,
                "buy_low_level": 0,
                "btd_level": 0,
                "retest_level": 0,
                "ma_20": 0,
                "ma_50": 0,
                "ma_200": 0,
                "recent_high": 0,
                "recent_low": 0,
                "fib_levels": {},
                "volume_profile": None,
                "calculation_method": "none"
            }
    
    async def get_market_overview(self) -> dict:
        """Get market overview using Alpaca ETF proxies with MCP fallback."""
        from datetime import datetime
        
        # ETF proxy symbols for market indices
        ETF_PROXIES = {
            "SPY": "sp500",    # S&P 500
            "QQQ": "nasdaq",   # NASDAQ
            "DIA": "dow",      # Dow Jones
            "VXX": "vix"       # Volatility Index
        }
        
        # Try Alpaca first for real-time ETF data
        try:
            from services.market_service import ALPACA_AVAILABLE, get_alpaca_service
            
            if ALPACA_AVAILABLE:
                logger.info("Using Alpaca for market overview (ETF proxies)")
                
                # Get Alpaca service instance
                alpaca_service = get_alpaca_service()
                
                # Fetch batch snapshots for all ETF proxies
                symbols = list(ETF_PROXIES.keys())
                snapshots = await alpaca_service.get_batch_snapshots(symbols)
                
                # Build indices data from ETF snapshots
                indices = {}
                for etf_symbol, index_name in ETF_PROXIES.items():
                    if etf_symbol in snapshots and "error" not in snapshots[etf_symbol]:
                        snapshot = snapshots[etf_symbol]
                        
                        # Get current price from latest trade
                        current_price = 0
                        if "latest_trade" in snapshot:
                            current_price = snapshot["latest_trade"]["price"]
                        elif "daily_bar" in snapshot:
                            current_price = snapshot["daily_bar"]["close"]
                        
                        # Calculate change from previous close
                        prev_close = 0
                        change = 0
                        change_percent = 0
                        
                        if "previous_daily_bar" in snapshot:
                            prev_close = snapshot["previous_daily_bar"]["close"]
                            if current_price and prev_close:
                                change = round(current_price - prev_close, 2)
                                change_percent = round((change / prev_close) * 100, 2)
                        
                        indices[index_name] = {
                            "value": current_price,
                            "change": change,
                            "change_percent": change_percent
                        }
                    else:
                        logger.warning(f"No Alpaca data for {etf_symbol}")
                
                # If we got at least some indices data, return it
                if indices:
                    # Try to get movers from MCP
                    movers = {}
                    try:
                        from .http_mcp_client import get_http_mcp_client as get_direct_mcp_client
                        client = await get_direct_mcp_client()
                        
                        # Get CNBC pre-market movers
                        cnbc_movers = await client.call_tool("get_cnbc_movers", {})
                        if cnbc_movers:
                            movers = cnbc_movers
                    except Exception as e:
                        logger.warning(f"Failed to get CNBC movers: {e}")
                    
                    return {
                        "indices": indices,
                        "movers": movers,
                        "data_source": "alpaca",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
        
        except Exception as e:
            logger.warning(f"Alpaca market overview failed: {e}, falling back to MCP")
        
        # Fallback to MCP market overview
        try:
            logger.info("Using MCP for market overview (Yahoo Finance)")
            from .http_mcp_client import get_http_mcp_client as get_direct_mcp_client
            client = await get_direct_mcp_client()
            
            # Get comprehensive market overview from MCP
            overview = await client.call_tool("get_market_overview", {})
            
            if overview:
                overview["data_source"] = "yahoo_mcp"
                return overview
            
        except Exception as e:
            logger.error(f"MCP market overview failed: {e}")
        
        # Return error if both methods fail
        raise ValueError("Unable to fetch market overview from any source")
    
    async def _cache_candles(self, symbol: str, timeframe: str, candles: List[Dict], source: str):
        """Helper method to cache candles asynchronously"""
        try:
            db_service = get_database_service()
            count = await db_service.save_market_candles(symbol, timeframe, candles, source)
            logger.info(f"Cached {count} candles for {symbol} from {source}")
        except Exception as e:
            logger.warning(f"Failed to cache candles for {symbol}: {e}")
    
    async def _cache_news(self, articles: List[Dict], symbol: Optional[str] = None):
        """Helper method to cache news asynchronously"""
        try:
            db_service = get_database_service()
            count = await db_service.save_market_news(articles, symbol)
            logger.info(f"Cached {count} news articles for {symbol or 'general'}")
        except Exception as e:
            logger.warning(f"Failed to cache news: {e}")


class HybridMarketService:
    """
    Hybrid service that intelligently uses BOTH Direct and MCP services.
    - Direct API for fast price/history queries
    - MCP for comprehensive news (CNBC + Yahoo)
    - Best of both worlds: speed AND comprehensive data
    """
    
    def __init__(self):
        self.direct_service = None
        self.mcp_service = None
        self.direct_available = False
        self.mcp_available = False
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize both services, allowing graceful degradation if one fails."""
        # Initialize Direct service
        try:
            from .direct_market_service import DirectMarketDataService
            self.direct_service = DirectMarketDataService()
            self.direct_available = True
            logger.info("Direct market service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Direct service: {e}")
            self.direct_available = False
        
        # Initialize MCP service
        try:
            self.mcp_service = MarketServiceWrapper()
            self.mcp_available = True
            logger.info("MCP market service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP service: {e}")
            self.mcp_available = False
        
        if not self.direct_available and not self.mcp_available:
            raise RuntimeError("Failed to initialize any market service")
    
    async def get_stock_price(self, symbol: str) -> dict:
        """Get stock price - prefer MCP/Alpaca for accurate data, fallback to Direct."""
        # Try MCP/Alpaca first (has better data quality including open price)
        if self.mcp_available:
            try:
                result = await self.mcp_service.get_stock_price(symbol)
                logger.info(f"Stock price fetched via {result.get('data_source', 'MCP')}")
                return result
            except Exception as e:
                logger.warning(f"MCP/Alpaca price fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_price(symbol)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_price(symbol)
        else:
            raise RuntimeError("No market service available")
    
    async def get_stock_history(self, symbol: str, days: int = 50, interval: str = "1d") -> dict:
        """Get stock history - prefer MCP/Alpaca for accurate data, fallback to Direct.

        Args:
            symbol: Stock symbol
            days: Number of days to fetch
            interval: Data interval - '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
        """
        # Try MCP/Alpaca first (has better data quality)
        if self.mcp_available:
            try:
                result = await self.mcp_service.get_stock_history(symbol, days, interval)
                logger.info(f"Stock history fetched via {result.get('data_source', 'MCP')}")
                return result
            except Exception as e:
                logger.warning(f"MCP/Alpaca history fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_history(symbol, days, interval)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_history(symbol, days, interval)
        else:
            raise RuntimeError("No market service available")
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """Get stock news - prefer MCP for CNBC + Yahoo, fallback to Direct."""
        if self.mcp_available:
            try:
                return await self.mcp_service.get_stock_news(symbol, limit)
            except Exception as e:
                logger.warning(f"MCP news fetch failed: {e}")
                if self.direct_available:
                    return await self.direct_service.get_stock_news(symbol, limit)
                raise
        elif self.direct_available:
            return await self.direct_service.get_stock_news(symbol, limit)
        else:
            raise RuntimeError("No market service available")
    
    async def get_comprehensive_stock_data(self, symbol: str) -> dict:
        """Get comprehensive data - prefer MCP/Alpaca for accurate data, fallback to Direct."""
        results = {}
        
        # Try MCP/Alpaca first (has complete data including open price and year high/low)
        if self.mcp_available:
            try:
                data = await self.mcp_service.get_comprehensive_stock_data(symbol)
                results = data
                logger.info(f"Comprehensive data fetched via {data.get('data_source', 'MCP')}")
            except Exception as e:
                logger.warning(f"MCP/Alpaca comprehensive data failed: {e}")
                if self.direct_available:
                    data = await self.direct_service.get_comprehensive_stock_data(symbol)
                    results = data
        elif self.direct_available:
            data = await self.mcp_service.get_comprehensive_stock_data(symbol)
            results = data
        
        # Try to enhance with MCP news if available and not already included
        if self.mcp_available and "news" not in results:
            try:
                news_data = await self.mcp_service.get_stock_news(symbol, 5)
                results["news"] = news_data.get("articles", [])
            except Exception as e:
                logger.warning(f"Failed to add MCP news to comprehensive data: {e}")
        
        return results
    
    async def get_market_overview(self) -> dict:
        """Get market overview - delegate to MCP service which has Alpaca-first implementation."""
        if self.mcp_available:
            try:
                return await self.mcp_service.get_market_overview()
            except Exception as e:
                logger.error(f"MCP market overview failed: {e}")
                raise
        else:
            raise RuntimeError("Market overview not available - MCP service required")
    
    async def get_service_info(self) -> dict:
        """Return consolidated service info for health checks."""
        info = self.get_service_status().copy()
        info["direct_available"] = self.direct_available
        info["mcp_available"] = self.mcp_available

        mcp_status = {}
        if self.mcp_available:
            try:
                mcp_status = await self.get_mcp_status()
            except Exception as e:
                logger.warning(f"Failed to collect MCP status: {e}")
        info["mcp_status"] = mcp_status

        return info

    async def search_assets(
        self,
        query: str,
        limit: int = 20,
        asset_classes: List[str] = None
    ) -> list:
        """
        Search for symbols across multiple asset classes (stocks, crypto, forex).

        Args:
            query: Search query (symbol or company/coin name)
            limit: Max results per asset class
            asset_classes: List of ['stock', 'crypto', 'forex'] or None for all

        Returns:
            List of search results with asset_class field
        """
        import asyncio
        from services.crypto_aggregator import CryptoAggregatorService
        from services.forex_pairs import search_forex_pairs

        # Default to all asset classes if not specified
        if asset_classes is None:
            asset_classes = ['stock', 'crypto', 'forex']

        all_results = []
        tasks = []

        # Create async tasks for each requested asset class
        if 'stock' in asset_classes:
            tasks.append(('stock', self._search_stocks(query, limit)))

        if 'crypto' in asset_classes:
            tasks.append(('crypto', self._search_crypto(query, limit)))

        if 'forex' in asset_classes:
            # Forex search is synchronous, wrap in async
            tasks.append(('forex', self._search_forex_async(query, limit)))

        # Execute all searches in parallel
        if tasks:
            task_labels, task_coroutines = zip(*tasks)
            results_list = await asyncio.gather(*task_coroutines, return_exceptions=True)

            for label, result in zip(task_labels, results_list):
                if isinstance(result, Exception):
                    logger.warning(f"{label.capitalize()} search failed: {result}")
                elif result:
                    all_results.extend(result)

        # Deduplicate by symbol-asset_class combination (allow same symbol across different markets)
        seen_entries = set()
        unique_results = []
        for result in all_results:
            symbol = result.get('symbol', '').upper()
            asset_class = result.get('asset_class', 'unknown')
            # Use symbol + asset_class as unique key to allow same symbol in different markets
            # e.g., "SUI" can appear as both "SUI-crypto" and "SUI-stock"
            entry_key = f"{symbol}-{asset_class}"
            if symbol and entry_key not in seen_entries:
                seen_entries.add(entry_key)
                unique_results.append(result)

        logger.info(f"Multi-market search for '{query}': {len(unique_results)} total results")
        return unique_results[:limit * len(asset_classes)]

    async def _search_stocks(self, query: str, limit: int) -> list:
        """Search stocks via Alpaca."""
        try:
            from services.market_service import search_assets_with_alpaca, ALPACA_AVAILABLE

            if ALPACA_AVAILABLE:
                logger.info(f"Searching stocks via Alpaca: '{query}'")
                results = await search_assets_with_alpaca(query, limit)
                # Ensure asset_class is set
                for result in results:
                    result['asset_class'] = 'stock'
                return results
        except Exception as e:
            logger.warning(f"Alpaca stock search failed: {e}")

        return []

    async def _search_crypto(self, query: str, limit: int) -> list:
        """Search crypto via Alpaca + CoinGecko aggregation."""
        try:
            from services.market_service import get_alpaca_service
            from services.crypto_aggregator import CryptoAggregatorService

            alpaca_service = get_alpaca_service()
            if alpaca_service and alpaca_service.is_available:
                aggregator = CryptoAggregatorService(alpaca_service)
                logger.info(f"Searching crypto via Alpaca + CoinGecko: '{query}'")
                results = await aggregator.search_all_crypto(query, limit)
                return results
        except Exception as e:
            logger.warning(f"Crypto search failed: {e}")

        return []

    async def _search_forex_async(self, query: str, limit: int) -> list:
        """Search forex pairs (static list)."""
        try:
            from services.forex_pairs import search_forex_pairs

            logger.info(f"Searching forex pairs: '{query}'")
            forex_results = search_forex_pairs(query, limit)

            # Format to match other search results
            formatted = []
            for pair in forex_results:
                formatted.append({
                    "symbol": pair["symbol"],
                    "name": pair["name"],
                    "exchange": "FOREX",
                    "asset_class": "forex",
                    "tradable": False,  # Forex data-only via Yahoo Finance
                    "status": "active",
                    "category": pair["category"],
                    "description": pair["description"]
                })

            return formatted
        except Exception as e:
            logger.warning(f"Forex search failed: {e}")

        return []
    
    async def warm_up(self):
        """Warm up both services, don't fail if one doesn't work."""
        tasks = []
        
        if self.direct_available and self.direct_service:
            tasks.append(self._warm_up_direct())
        
        if self.mcp_available and self.mcp_service:
            tasks.append(self._warm_up_mcp())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Hybrid service warm-up complete - Direct: {self.direct_available}, MCP: {self.mcp_available}")
    
    async def _warm_up_direct(self):
        """Warm up Direct service."""
        try:
            await self.direct_service.warm_up()
        except Exception as e:
            logger.warning(f"Direct service warm-up failed: {e}")
    
    async def _warm_up_mcp(self):
        """Warm up MCP service."""
        try:
            await self.mcp_service.warm_up()
        except Exception as e:
            logger.warning(f"MCP service warm-up failed: {e}")
    
    def get_service_status(self) -> dict:
        """Get status of both services for health checks."""
        return {
            "direct": "operational" if self.direct_available else "unavailable",
            "mcp": "operational" if self.mcp_available else "unavailable",
            "mode": "hybrid"
        }
    
    async def get_mcp_status(self) -> dict:
        """
        Get detailed MCP service status for health checks.
        Returns initialization status, availability, and connection details.
        """
        return {
            "initialized": self.mcp_available,
            "available": self.mcp_available,
            "service": "http_mcp_client",
            "endpoint": "http://127.0.0.1:3001/mcp",
            "mode": "hybrid" if self.direct_available and self.mcp_available else "fallback"
        }


class MarketServiceFactory:
    """
    Factory that provides the HybridMarketService with BOTH Direct and MCP capabilities.
    No more either/or - we use both services intelligently!
    """
    
    _instance = None
    _service_mode = None
    
    @classmethod
    def get_service(cls, force_refresh: bool = False):
        """
        Get the hybrid market service that uses both Direct and MCP.
        
        Args:
            force_refresh: Force creation of new instance
            
        Returns:
            HybridMarketService with both Direct and MCP capabilities
        """
        if cls._instance is None or force_refresh:
            logger.info("Initializing Hybrid market service with both Direct and MCP capabilities")
            cls._instance = HybridMarketService()
            cls._service_mode = "Hybrid (Direct + MCP)"
        
        return cls._instance
    
    @classmethod
    async def initialize_service(cls):
        """
        Initialize and warm up the appropriate service.
        Should be called during app startup.
        """
        service = cls.get_service()
        logger.info(f"Attempting to warm up service in {cls._service_mode} mode...")
        
        try:
            await service.warm_up()
            logger.info(f"Market service initialized and warmed up successfully in {cls._service_mode} mode")
        except Exception as e:
            logger.warning(f"Market service warm-up failed in {cls._service_mode} mode: {e}")
            logger.info("Market service initialized but warm-up failed - service may have cold start")
        
        return service
    
    @classmethod
    def get_service_mode(cls) -> str:
        """
        Get the current service mode for health checks.
        """
        if cls._service_mode is None:
            cls._service_mode = "Hybrid (Direct + MCP)"
        
        return cls._service_mode
    
    @classmethod
    def get_service_status(cls) -> dict:
        """
        Get detailed status of both services.
        """
        if cls._instance and hasattr(cls._instance, 'get_service_status'):
            return cls._instance.get_service_status()
        return {
            "direct": "unknown",
            "mcp": "unknown",
            "mode": "not_initialized"
        }