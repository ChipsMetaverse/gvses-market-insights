"""
Knowledge Integration Module for OpenAI Agent Training
======================================================
Integrates technical analysis knowledge from training materials
to enhance the agent's market analysis capabilities.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalysisKnowledge:
    """
    Encapsulates technical analysis knowledge from training materials.
    Based on resources in /backend/training/knowledge/
    """
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.pattern_library = self._initialize_pattern_library()
        self.indicator_guide = self._initialize_indicator_guide()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load and structure knowledge from training materials."""
        return {
            "sources": [
                "CBC TA - Technical Analysis Guide",
                "Encyclopedia of Chart Patterns",
                "The Candlestick Trading Bible",
                "Price Action Patterns",
                "Technical Analysis for Dummies",
                "Crypto Revolution Technical Analysis"
            ],
            "core_concepts": self._get_core_concepts(),
            "chart_patterns": self._get_chart_patterns(),
            "candlestick_patterns": self._get_candlestick_patterns(),
            "technical_indicators": self._get_technical_indicators(),
            "trading_strategies": self._get_trading_strategies()
        }
    
    def _get_core_concepts(self) -> Dict[str, str]:
        """Core technical analysis concepts from the knowledge base."""
        return {
            "support_resistance": """
                Support: Price level where buying interest is strong enough to overcome selling pressure.
                Resistance: Price level where selling interest overcomes buying pressure.
                These levels act as psychological barriers and often become self-fulfilling prophecies.
                Breaking these levels with volume confirms trend continuation.
            """,
            
            "trend_analysis": """
                Uptrend: Series of higher highs and higher lows.
                Downtrend: Series of lower highs and lower lows.
                Sideways/Range: Price oscillates between support and resistance.
                Trend strength measured by: angle of ascent/descent, volume, and momentum indicators.
            """,
            
            "volume_analysis": """
                Volume confirms price movement - "volume precedes price".
                Rising prices on increasing volume = bullish confirmation.
                Rising prices on decreasing volume = potential reversal warning.
                Climax volume often marks trend exhaustion.
            """,
            
            "market_psychology": """
                Markets move in cycles driven by fear and greed.
                Accumulation → Markup → Distribution → Markdown phases.
                Sentiment extremes often mark turning points.
                Crowd behavior creates predictable patterns.
            """,
            
            "risk_management": """
                Position sizing: Never risk more than 1-2% per trade.
                Stop losses: Place below support (longs) or above resistance (shorts).
                Risk/Reward ratio: Minimum 1:2, preferably 1:3 or better.
                Diversification: Spread risk across uncorrelated assets.
            """
        }
    
    def _get_chart_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Chart patterns from Encyclopedia of Chart Patterns."""
        return {
            "cup_and_handle": {
                "type": "continuation",
                "reliability": "high",
                "description": "U-shaped base followed by small consolidation",
                "target": "Height of cup added to breakout point",
                "volume": "Increase on breakout",
                "timeframe": "Weeks to months",
                "success_rate": 0.65
            },
            
            "head_and_shoulders": {
                "type": "reversal",
                "reliability": "high",
                "description": "Three peaks with middle highest (head)",
                "target": "Head height from neckline",
                "volume": "Decreases through pattern",
                "timeframe": "Weeks to months",
                "success_rate": 0.70
            },
            
            "triangle_ascending": {
                "type": "continuation",
                "reliability": "medium-high",
                "description": "Rising lows with flat resistance",
                "target": "Triangle height from breakout",
                "volume": "Decreases until breakout",
                "timeframe": "Days to weeks",
                "success_rate": 0.63
            },
            
            "double_bottom": {
                "type": "reversal",
                "reliability": "high",
                "description": "Two similar lows with peak between",
                "target": "Pattern height from neckline break",
                "volume": "Higher on second bottom",
                "timeframe": "Weeks to months",
                "success_rate": 0.68
            },
            
            "flag": {
                "type": "continuation",
                "reliability": "high",
                "description": "Brief consolidation after sharp move",
                "target": "Flagpole height from breakout",
                "volume": "Light during flag formation",
                "timeframe": "Days to weeks",
                "success_rate": 0.71
            },
            
            "wedge": {
                "type": "reversal/continuation",
                "reliability": "medium",
                "description": "Converging trend lines both slanted",
                "target": "Pattern height at widest point",
                "volume": "Decreases through pattern",
                "timeframe": "Weeks",
                "success_rate": 0.60
            }
        }
    
    def _get_candlestick_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Candlestick patterns from The Candlestick Trading Bible."""
        return {
            "doji": {
                "type": "reversal",
                "description": "Open equals close, signals indecision",
                "reliability": "medium",
                "context_required": "Trend exhaustion point",
                "variations": ["dragonfly", "gravestone", "long-legged"]
            },
            
            "hammer": {
                "type": "reversal",
                "description": "Small body, long lower wick at bottom",
                "reliability": "high",
                "context_required": "Downtrend",
                "confirmation": "Next candle closes above hammer high"
            },
            
            "engulfing": {
                "type": "reversal",
                "description": "Second candle completely engulfs first",
                "reliability": "high",
                "context_required": "Established trend",
                "variations": ["bullish_engulfing", "bearish_engulfing"]
            },
            
            "morning_star": {
                "type": "reversal",
                "description": "Three-candle bullish reversal pattern",
                "reliability": "high",
                "context_required": "Downtrend",
                "confirmation": "Volume increase on third candle"
            },
            
            "shooting_star": {
                "type": "reversal",
                "description": "Small body, long upper wick at top",
                "reliability": "medium-high",
                "context_required": "Uptrend",
                "confirmation": "Next candle closes below star low"
            }
        }
    
    def _get_technical_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Technical indicators configuration and interpretation."""
        return {
            "RSI": {
                "full_name": "Relative Strength Index",
                "type": "momentum",
                "range": [0, 100],
                "overbought": 70,
                "oversold": 30,
                "default_period": 14,
                "interpretation": {
                    "above_70": "Overbought - potential reversal or consolidation",
                    "below_30": "Oversold - potential bounce or reversal",
                    "divergence": "Price/RSI divergence signals potential reversal",
                    "50_line": "Momentum shift when crossing 50"
                }
            },
            
            "MACD": {
                "full_name": "Moving Average Convergence Divergence",
                "type": "trend/momentum",
                "components": ["MACD line", "Signal line", "Histogram"],
                "default_settings": "12, 26, 9",
                "interpretation": {
                    "cross_above": "Bullish signal when MACD crosses above signal",
                    "cross_below": "Bearish signal when MACD crosses below signal",
                    "histogram_expansion": "Trend strength increasing",
                    "divergence": "Potential trend reversal"
                }
            },
            
            "moving_averages": {
                "full_name": "Moving Averages",
                "type": "trend",
                "common_periods": [20, 50, 100, 200],
                "types": ["SMA", "EMA"],
                "interpretation": {
                    "price_above": "Bullish bias",
                    "price_below": "Bearish bias",
                    "golden_cross": "50 MA crosses above 200 MA - major bullish",
                    "death_cross": "50 MA crosses below 200 MA - major bearish",
                    "dynamic_support": "MAs often act as support/resistance"
                }
            },
            
            "bollinger_bands": {
                "full_name": "Bollinger Bands",
                "type": "volatility",
                "components": ["Upper band", "Middle (20 SMA)", "Lower band"],
                "default_settings": "20, 2",
                "interpretation": {
                    "squeeze": "Low volatility, potential breakout coming",
                    "expansion": "High volatility, trend in progress",
                    "walk_the_band": "Strong trend when price hugs band",
                    "mean_reversion": "Price tends to return to middle band"
                }
            },
            
            "volume_indicators": {
                "OBV": {
                    "full_name": "On Balance Volume",
                    "interpretation": "Cumulative volume confirms price trend"
                },
                "VWAP": {
                    "full_name": "Volume Weighted Average Price",
                    "interpretation": "Institutional reference point, acts as support/resistance"
                },
                "volume_profile": {
                    "interpretation": "Shows price levels with most trading activity"
                }
            }
        }
    
    def _get_trading_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Trading strategies from the knowledge base."""
        return {
            "trend_following": {
                "description": "Trade in direction of established trend",
                "entry": "Pullback to support in uptrend, resistance in downtrend",
                "exit": "Trend line break or momentum divergence",
                "indicators": ["Moving averages", "MACD", "ADX"],
                "risk_management": "Stop below recent swing low/high"
            },
            
            "breakout_trading": {
                "description": "Enter on break of key levels",
                "entry": "Close above resistance or below support with volume",
                "exit": "Target based on pattern measurement",
                "indicators": ["Volume", "ATR for volatility"],
                "risk_management": "Stop at opposite side of consolidation"
            },
            
            "mean_reversion": {
                "description": "Fade extremes expecting return to average",
                "entry": "Oversold/overbought with divergence",
                "exit": "Return to moving average or neutral RSI",
                "indicators": ["RSI", "Bollinger Bands", "Stochastic"],
                "risk_management": "Tight stops beyond extremes"
            },
            
            "momentum_trading": {
                "description": "Buy strength, sell weakness",
                "entry": "New highs/lows with strong momentum",
                "exit": "Momentum divergence or exhaustion",
                "indicators": ["RSI", "MACD", "Rate of Change"],
                "risk_management": "Trail stops with ATR"
            }
        }
    
    def _initialize_pattern_library(self) -> Dict[str, Any]:
        """Initialize comprehensive pattern recognition library."""
        return {
            "bullish_patterns": [
                "cup_and_handle", "inverse_head_and_shoulders", "double_bottom",
                "triple_bottom", "ascending_triangle", "bull_flag", "falling_wedge",
                "morning_star", "bullish_engulfing", "hammer"
            ],
            
            "bearish_patterns": [
                "head_and_shoulders", "double_top", "triple_top",
                "descending_triangle", "bear_flag", "rising_wedge",
                "evening_star", "bearish_engulfing", "shooting_star"
            ],
            
            "neutral_patterns": [
                "symmetrical_triangle", "rectangle", "pennant",
                "doji", "spinning_top", "inside_bar"
            ]
        }
    
    def _initialize_indicator_guide(self) -> Dict[str, List[str]]:
        """Initialize indicator selection guide by market condition."""
        return {
            "trending_market": [
                "moving_averages", "MACD", "ADX", "parabolic_SAR"
            ],
            
            "ranging_market": [
                "RSI", "stochastic", "bollinger_bands", "support_resistance"
            ],
            
            "volatile_market": [
                "ATR", "bollinger_bands", "keltner_channels", "standard_deviation"
            ],
            
            "volume_analysis": [
                "OBV", "volume_profile", "accumulation_distribution", "money_flow"
            ]
        }
    
    def get_pattern_analysis(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis for a specific pattern."""
        patterns = self.knowledge_base.get("chart_patterns", {})
        return patterns.get(pattern_name)
    
    def get_indicator_interpretation(self, indicator: str, value: float) -> str:
        """Get interpretation for indicator value."""
        indicators = self.knowledge_base.get("technical_indicators", {})
        
        if indicator.upper() == "RSI":
            rsi_config = indicators.get("RSI", {})
            if value > rsi_config.get("overbought", 70):
                return rsi_config["interpretation"]["above_70"]
            elif value < rsi_config.get("oversold", 30):
                return rsi_config["interpretation"]["below_30"]
            else:
                return f"RSI at {value:.1f} - neutral momentum"
        
        return f"{indicator} at {value}"
    
    def get_market_condition_indicators(self, condition: str) -> List[str]:
        """Get recommended indicators for market condition."""
        return self.indicator_guide.get(condition, [])
    
    def enhance_analysis_with_patterns(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance market analysis with pattern recognition insights."""
        enhanced = {
            "original_data": price_data,
            "pattern_analysis": {},
            "indicator_suggestions": [],
            "trading_bias": "neutral",
            "key_insights": []
        }
        
        # Process detected patterns if present
        if "patterns" in price_data and "detected" in price_data["patterns"]:
            detected_patterns = price_data["patterns"]["detected"]
            
            if detected_patterns:
                # Analyze overall pattern sentiment
                bullish_count = sum(1 for p in detected_patterns if p.get("signal") == "bullish")
                bearish_count = sum(1 for p in detected_patterns if p.get("signal") == "bearish")
                
                # Determine trading bias
                if bullish_count > bearish_count:
                    enhanced["trading_bias"] = "bullish"
                elif bearish_count > bullish_count:
                    enhanced["trading_bias"] = "bearish"
                
                # Get detailed analysis for the highest confidence pattern
                highest_confidence = max(detected_patterns, key=lambda p: p.get("confidence", 0))
                pattern_info = self.get_pattern_analysis(highest_confidence["type"])
                
                if pattern_info:
                    enhanced["pattern_analysis"] = {
                        "primary_pattern": highest_confidence["type"],
                        "reliability": pattern_info.get("reliability", "unknown"),
                        "typical_target": pattern_info.get("target", "Pattern height projection"),
                        "volume_requirement": pattern_info.get("volume", "Normal"),
                        "timeframe": pattern_info.get("timeframe", "Variable"),
                        "success_rate": pattern_info.get("success_rate", 0.5)
                    }
                    
                    # Add actionable insights
                    enhanced["key_insights"].append(
                        f"{highest_confidence['type'].replace('_', ' ').title()} detected with "
                        f"{highest_confidence['confidence']:.0f}% confidence - {pattern_info.get('reliability', 'medium')} reliability pattern"
                    )
        
        # Process support/resistance levels
        if "patterns" in price_data and "active_levels" in price_data["patterns"]:
            levels = price_data["patterns"]["active_levels"]
            if levels.get("support"):
                enhanced["key_insights"].append(f"Key support at ${levels['support'][0]:.2f}")
            if levels.get("resistance"):
                enhanced["key_insights"].append(f"Key resistance at ${levels['resistance'][0]:.2f}")
        
        # Add pattern-based insights for technical levels
        if "technical_levels" in price_data:
            levels = price_data["technical_levels"]
            # Analyze price position relative to levels
            current_price = price_data.get("price", 0)
            
            if current_price and levels:
                # Check proximity to levels
                for level_name, level_price in levels.items():
                    if level_price and abs(current_price - level_price) / current_price < 0.01:
                        enhanced["key_insights"].append(
                            f"Price approaching {level_name} level at ${level_price:.2f}"
                        )
        
        # Suggest relevant indicators based on market conditions
        if "volatility" in price_data:
            if price_data["volatility"] > 0.02:  # High volatility
                enhanced["indicator_suggestions"] = self.get_market_condition_indicators("volatile_market")
                enhanced["key_insights"].append("High volatility - consider Bollinger Bands and ATR for risk management")
            else:
                enhanced["indicator_suggestions"] = self.get_market_condition_indicators("ranging_market")
                enhanced["key_insights"].append("Range-bound conditions - RSI and support/resistance levels are key")
        
        return enhanced


class AgentKnowledgeEnhancer:
    """
    Enhances agent responses with technical analysis knowledge.
    """
    
    def __init__(self):
        self.ta_knowledge = TechnicalAnalysisKnowledge()
        self.context_patterns = self._load_context_patterns()
    
    def _load_context_patterns(self) -> Dict[str, Any]:
        """Load contextual patterns for enhanced responses."""
        return {
            "technical_question_keywords": [
                "RSI", "MACD", "support", "resistance", "pattern",
                "technical", "chart", "indicator", "signal"
            ],
            
            "pattern_question_keywords": [
                "pattern", "formation", "setup", "chart"
            ],
            
            "strategy_keywords": [
                "strategy", "approach", "trade", "position"
            ]
        }
    
    def should_enhance_with_ta(self, user_query: str) -> bool:
        """Determine if technical analysis knowledge should be added."""
        query_lower = user_query.lower()
        
        # Check for technical keywords
        for keyword in self.context_patterns["technical_question_keywords"]:
            if keyword.lower() in query_lower:
                return True
        
        return False
    
    def enhance_response(self, 
                         user_query: str,
                         base_response: str,
                         market_data: Dict[str, Any]) -> str:
        """Enhance response with technical analysis insights."""
        
        if not self.should_enhance_with_ta(user_query):
            return base_response
        
        # Add technical context
        enhanced = base_response
        
        # Check for RSI in data
        if "RSI" in market_data:
            rsi_interpretation = self.ta_knowledge.get_indicator_interpretation(
                "RSI", market_data["RSI"]
            )
            enhanced += f"\n\nTechnical Context: {rsi_interpretation}"
        
        # Add pattern recognition if relevant
        query_lower = user_query.lower()
        if any(keyword in query_lower for keyword in self.context_patterns["pattern_question_keywords"]):
            # Add pattern analysis
            patterns = self.ta_knowledge.pattern_library.get("bullish_patterns", [])
            enhanced += f"\n\nKey patterns to watch: Look for formations like {', '.join(patterns[:3])}"
        
        return enhanced
    
    def get_educational_context(self, topic: str) -> Optional[str]:
        """Get educational context about a technical topic."""
        
        # Check core concepts
        concepts = self.ta_knowledge.knowledge_base.get("core_concepts", {})
        for concept_key, concept_text in concepts.items():
            if topic.lower() in concept_key.lower():
                return concept_text.strip()
        
        # Check indicators
        indicators = self.ta_knowledge.knowledge_base.get("technical_indicators", {})
        for indicator_name, indicator_info in indicators.items():
            if topic.upper() == indicator_name or topic.lower() in indicator_name.lower():
                return f"{indicator_info.get('full_name', indicator_name)}: {json.dumps(indicator_info.get('interpretation', {}), indent=2)}"
        
        return None
    
    def format_technical_narrative(self,
                                  symbol: str,
                                  technical_data: Dict[str, Any]) -> str:
        """Format technical analysis into natural narrative."""
        
        narrative_parts = []
        
        # Price action context
        if "price" in technical_data and "change_percent" in technical_data:
            trend = "up" if technical_data["change_percent"] > 0 else "down"
            narrative_parts.append(
                f"{symbol} is trading {trend} {abs(technical_data['change_percent']):.2f}% "
            )
        
        # RSI context
        if "RSI" in technical_data:
            rsi_value = technical_data["RSI"]
            rsi_context = self.ta_knowledge.get_indicator_interpretation("RSI", rsi_value)
            narrative_parts.append(rsi_context)
        
        # MACD context
        if "MACD" in technical_data:
            macd_info = self.ta_knowledge.knowledge_base["technical_indicators"]["MACD"]
            if technical_data.get("MACD_signal", 0) > 0:
                narrative_parts.append(macd_info["interpretation"]["cross_above"])
            else:
                narrative_parts.append(macd_info["interpretation"]["cross_below"])
        
        # Moving average context
        if "MA_50" in technical_data and "MA_200" in technical_data:
            if technical_data["MA_50"] > technical_data["MA_200"]:
                narrative_parts.append("The 50-day MA above 200-day suggests bullish trend")
            else:
                narrative_parts.append("The 50-day MA below 200-day suggests bearish trend")
        
        return " ".join(narrative_parts)


# Global knowledge enhancer instance
knowledge_enhancer = AgentKnowledgeEnhancer()