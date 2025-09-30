"""
Pattern Structured Adapter
==========================
Converts MCP pattern detection summary strings into structured pattern objects
that can be processed by PatternLifecycleManager and ML confidence service.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PatternStructuredAdapter:
    """
    Adapter to convert MCP pattern detection results into structured format
    compatible with PatternLifecycleManager and ML enhancement pipeline.
    """
    
    def __init__(self):
        self.pattern_count = 0
    
    def convert_to_structured_patterns(
        self, 
        patterns_result: Dict[str, Any],
        symbol: str,
        timeframe: str = "1D"
    ) -> List[Dict[str, Any]]:
        """
        Convert pattern detection results to structured pattern objects.
        
        Args:
            patterns_result: Raw pattern detection output from PatternDetector
            symbol: Stock symbol for the patterns
            timeframe: Timeframe of the patterns (default: 1D)
            
        Returns:
            List of structured pattern dictionaries with IDs and metadata
        """
        structured_patterns = []
        
        # Process detected patterns
        detected = patterns_result.get("detected", [])
        for pattern_data in detected:
            # Generate unique pattern ID
            pattern_id = str(uuid4())
            
            # Extract pattern info
            pattern_type = pattern_data.get("type", "unknown")
            confidence = pattern_data.get("confidence", 50.0) / 100.0  # Convert to 0-1 range
            
            # Build structured pattern object
            structured_pattern = {
                "id": pattern_id,
                "pattern_id": pattern_id,  # Both formats for compatibility
                "symbol": symbol,
                "timeframe": timeframe,
                "pattern_type": pattern_type,
                "confidence": confidence,
                "status": "pending",
                "signal": pattern_data.get("signal", "neutral"),
                "description": pattern_data.get("description", f"Pattern {pattern_type}"),
                "start_candle": pattern_data.get("start_candle"),
                "end_candle": pattern_data.get("end_candle"),
                "target": pattern_data.get("target"),
                "stop_loss": pattern_data.get("stop_loss"),
                "entry": None,  # Will be calculated if needed
                "support": None,
                "resistance": None,
                "metadata": {
                    "action": pattern_data.get("action"),
                    "original_confidence": pattern_data.get("confidence"),
                    "detection_time": datetime.now(timezone.utc).isoformat(),
                    "adapter_version": "1.0.0"
                },
                "auto_generated": True,
                "ml_eligible": confidence >= 0.5  # Patterns with >50% confidence eligible for ML
            }
            
            # Add support/resistance from active levels if available
            levels = patterns_result.get("active_levels", {})
            if levels:
                support_levels = levels.get("support", [])
                resistance_levels = levels.get("resistance", [])
                
                if support_levels:
                    structured_pattern["support"] = support_levels[0]
                if resistance_levels:
                    structured_pattern["resistance"] = resistance_levels[0]
            
            structured_patterns.append(structured_pattern)
            self.pattern_count += 1
            
            logger.info(
                f"Structured pattern created: {pattern_id} - "
                f"{pattern_type} for {symbol} with confidence {confidence:.2f}"
            )
        
        # If no patterns detected but levels exist, create a range pattern
        if not structured_patterns and patterns_result.get("active_levels"):
            levels = patterns_result["active_levels"]
            support = levels.get("support", [None])[0]
            resistance = levels.get("resistance", [None])[0]
            
            if support and resistance:
                pattern_id = str(uuid4())
                structured_patterns.append({
                    "id": pattern_id,
                    "pattern_id": pattern_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "range_bound",
                    "confidence": 0.5,  # Default confidence for range patterns
                    "status": "pending",
                    "signal": "neutral",
                    "description": f"Range between ${support:.2f} - ${resistance:.2f}",
                    "support": support,
                    "resistance": resistance,
                    "target": resistance,
                    "stop_loss": support,
                    "metadata": {
                        "detection_time": datetime.now(timezone.utc).isoformat(),
                        "adapter_version": "1.0.0"
                    },
                    "auto_generated": True,
                    "ml_eligible": True
                })
                
                logger.info(
                    f"Range pattern created: {pattern_id} for {symbol} "
                    f"between ${support:.2f} - ${resistance:.2f}"
                )
        
        return structured_patterns
    
    def extract_patterns_from_response(
        self,
        agent_response: str,
        symbol: str
    ) -> List[Dict[str, Any]]:
        """
        Extract structured patterns from agent text response.
        This is a fallback for when only text is available.
        
        Args:
            agent_response: Text response from agent containing pattern descriptions
            symbol: Stock symbol
            
        Returns:
            List of structured pattern dictionaries
        """
        patterns = []
        
        # Parse common pattern mentions in text
        pattern_keywords = {
            "bullish engulfing": ("bullish_engulfing", "bullish", 0.7),
            "bearish engulfing": ("bearish_engulfing", "bearish", 0.7),
            "breakout": ("breakout", "bullish", 0.75),
            "breakdown": ("breakdown", "bearish", 0.75),
            "support bounce": ("support_bounce", "bullish", 0.65),
            "double top": ("double_top", "bearish", 0.7),
            "double bottom": ("double_bottom", "bullish", 0.7),
            "head and shoulders": ("head_shoulders", "bearish", 0.75),
            "inverse head and shoulders": ("inverse_head_shoulders", "bullish", 0.75),
            "flag": ("flag", "neutral", 0.6),
            "triangle": ("triangle", "neutral", 0.6),
            "wedge": ("wedge", "neutral", 0.6)
        }
        
        agent_response_lower = agent_response.lower()
        
        for keyword, (pattern_type, signal, confidence) in pattern_keywords.items():
            if keyword in agent_response_lower:
                pattern_id = str(uuid4())
                patterns.append({
                    "id": pattern_id,
                    "pattern_id": pattern_id,
                    "symbol": symbol,
                    "pattern_type": pattern_type,
                    "confidence": confidence,
                    "status": "pending",
                    "signal": signal,
                    "description": f"Detected {keyword} pattern from agent response",
                    "metadata": {
                        "source": "text_extraction",
                        "detection_time": datetime.now(timezone.utc).isoformat()
                    },
                    "auto_generated": True,
                    "ml_eligible": True
                })
                
                logger.info(f"Extracted pattern {pattern_type} from agent text for {symbol}")
        
        return patterns
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        return {
            "patterns_converted": self.pattern_count,
            "adapter_version": "1.0.0"
        }