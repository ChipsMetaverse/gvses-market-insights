"""
Command Builders for Phase 4
Convert pattern geometry and metadata into chart commands
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TrendlineCommandBuilder:
    """
    Converts pattern geometry into DRAW commands for chart rendering
    Compatible with headless_chart_service command validator
    """
    
    def __init__(self):
        self.command_sequence = 0
        
    def _generate_id(self, prefix: str = "auto") -> str:
        """Generate unique ID for draw commands"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def build_pattern_commands(self, 
                              pattern_data: Dict[str, Any],
                              action: str = "create") -> List[str]:
        """
        Build chart commands for a pattern
        
        Args:
            pattern_data: Pattern metadata with geometry
            action: 'create', 'update', or 'clear'
            
        Returns:
            List of chart commands
        """
        commands = []
        pattern_id = pattern_data.get("id", self._generate_id("pattern"))
        pattern_type = pattern_data.get("pattern_type", "").lower()
        
        if action == "clear":
            commands.append(f"CLEAR:PATTERN:{pattern_id}")
            return commands
        
        # Extract geometry data
        support = pattern_data.get("support")
        resistance = pattern_data.get("resistance") 
        target = pattern_data.get("target")
        entry = pattern_data.get("entry")
        stoploss = pattern_data.get("stoploss")
        trendlines = pattern_data.get("trendlines", [])
        levels = pattern_data.get("levels", [])
        
        # Build level commands
        if support:
            commands.append(f"DRAW:LEVEL:{pattern_id}_support:SUPPORT:{support}")
        if resistance:
            commands.append(f"DRAW:LEVEL:{pattern_id}_resistance:RESISTANCE:{resistance}")
        if target:
            commands.append(f"DRAW:TARGET:{pattern_id}_target:{target}")
        if entry:
            commands.append(f"ENTRY:{entry}")
        if stoploss:
            commands.append(f"STOPLOSS:{stoploss}")
            
        # Build trendline commands
        for i, trendline in enumerate(trendlines):
            tl_id = f"{pattern_id}_tl{i}"
            commands.extend(self._build_trendline_command(tl_id, trendline))
            
        # Build custom level commands
        for level in levels:
            level_id = f"{pattern_id}_{level.get('type', 'level')}"
            level_type = level.get("type", "LEVEL").upper()
            price = level.get("price")
            if price:
                commands.append(f"DRAW:LEVEL:{level_id}:{level_type}:{price}")
        
        # Add pattern annotation
        status = pattern_data.get("status", "pending")
        confidence = pattern_data.get("confidence", 0.5)
        annotation = f"{pattern_type.replace('_', ' ').title()} ({confidence:.0%})"
        commands.append(f"ANNOTATE:PATTERN:{pattern_id}:{status}:{annotation}")
        
        return commands
    
    def _build_trendline_command(self, 
                                 trendline_id: str,
                                 trendline_data: Dict[str, Any]) -> List[str]:
        """
        Build DRAW:TRENDLINE command from trendline data
        
        Expected trendline_data format:
        {
            "start": {"time": timestamp, "price": float},
            "end": {"time": timestamp, "price": float},
            "type": "support" | "resistance" | "channel",
            "style": "solid" | "dashed" | "dotted"
        }
        """
        commands = []
        
        start = trendline_data.get("start", {})
        end = trendline_data.get("end", {})
        tl_type = trendline_data.get("type", "trendline")
        style = trendline_data.get("style", "solid")
        
        if start and end:
            # Format: DRAW:TRENDLINE:id:start_time:start_price:end_time:end_price:style
            start_time = start.get("time", 0)
            start_price = start.get("price", 0)
            end_time = end.get("time", 0)
            end_price = end.get("price", 0)
            
            if start_time and start_price and end_time and end_price:
                commands.append(
                    f"DRAW:TRENDLINE:{trendline_id}:{start_time}:{start_price}:{end_time}:{end_price}:{style}"
                )
        
        return commands
    
    def build_lifecycle_commands(self,
                                old_status: str,
                                new_status: str,
                                pattern_data: Dict[str, Any]) -> List[str]:
        """
        Build commands for pattern lifecycle transitions
        
        Args:
            old_status: Previous pattern status
            new_status: New pattern status
            pattern_data: Pattern metadata
            
        Returns:
            List of chart commands for the transition
        """
        commands = []
        pattern_id = pattern_data.get("id", self._generate_id("pattern"))
        
        # Handle status transitions
        if new_status == "confirmed" and old_status == "pending":
            # Pattern confirmed - draw full geometry
            commands = self.build_pattern_commands(pattern_data, "create")
            logger.info(f"Pattern {pattern_id} confirmed - generated {len(commands)} commands")
            
        elif new_status == "completed":
            # Pattern completed - add completion annotation
            commands.append(f"ANNOTATE:PATTERN:{pattern_id}:completed:✓ Target Reached")
            
        elif new_status == "invalidated":
            # Pattern invalidated - clear overlays
            commands.append(f"CLEAR:PATTERN:{pattern_id}")
            commands.append(f"ANNOTATE:PATTERN:{pattern_id}:invalidated:✗ Invalidated")
            
        elif new_status == "expired":
            # Pattern expired - fade or clear
            commands.append(f"CLEAR:PATTERN:{pattern_id}")
            
        return commands
    
    def build_bulk_commands(self, 
                          patterns: List[Dict[str, Any]],
                          action: str = "create") -> List[str]:
        """
        Build commands for multiple patterns
        
        Args:
            patterns: List of pattern data
            action: Action to perform on all patterns
            
        Returns:
            Combined list of commands
        """
        all_commands = []
        for pattern in patterns:
            commands = self.build_pattern_commands(pattern, action)
            all_commands.extend(commands)
        return all_commands
    
    def extract_geometry_from_analyzer(self, 
                                      analyzer_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract pattern geometry from chart analyzer output
        
        Args:
            analyzer_output: Raw output from chart analysis
            
        Returns:
            Normalized geometry data
        """
        geometry = {
            "trendlines": [],
            "levels": []
        }
        
        # Extract detected patterns
        patterns = analyzer_output.get("patterns", [])
        for pattern in patterns:
            # Extract support/resistance from pattern
            if "support" in pattern:
                geometry["support"] = pattern["support"]
            if "resistance" in pattern:
                geometry["resistance"] = pattern["resistance"]
            if "target" in pattern:
                geometry["target"] = pattern["target"]
                
            # Extract trendlines if present
            if "trendlines" in pattern:
                for tl in pattern["trendlines"]:
                    geometry["trendlines"].append({
                        "start": tl.get("start"),
                        "end": tl.get("end"),
                        "type": tl.get("type", "trendline"),
                        "style": tl.get("style", "solid")
                    })
                    
            # Extract additional levels
            if "levels" in pattern:
                for level in pattern["levels"]:
                    geometry["levels"].append({
                        "type": level.get("type", "level"),
                        "price": level.get("price")
                    })
        
        # Extract key levels from technical analysis
        analysis = analyzer_output.get("technical_analysis", {})
        if "key_levels" in analysis:
            for level in analysis["key_levels"]:
                geometry["levels"].append({
                    "type": level.get("type", "level"),
                    "price": level.get("value")
                })
        
        return geometry

class IndicatorCommandBuilder:
    """
    Builds commands for technical indicators
    """
    
    def __init__(self):
        self.supported_indicators = [
            "RSI", "MACD", "EMA", "SMA", "BOLLINGER", 
            "VOLUME", "STOCHASTIC", "ATR", "VWAP"
        ]
    
    def build_indicator_command(self, 
                               indicator: str,
                               params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build INDICATOR command
        
        Args:
            indicator: Indicator name
            params: Optional parameters
            
        Returns:
            Indicator command string
        """
        indicator = indicator.upper()
        if indicator not in self.supported_indicators:
            logger.warning(f"Unsupported indicator: {indicator}")
            return ""
            
        if params:
            # Format: INDICATOR:RSI:period=14,overbought=70
            param_str = ",".join([f"{k}={v}" for k, v in params.items()])
            return f"INDICATOR:{indicator}:{param_str}"
        else:
            return f"INDICATOR:{indicator}"
    
    def build_indicator_set(self, pattern_type: str) -> List[str]:
        """
        Build default indicator set for a pattern type
        
        Args:
            pattern_type: Type of pattern
            
        Returns:
            List of indicator commands
        """
        commands = []
        
        if pattern_type in ["head_and_shoulders", "double_top"]:
            # Reversal patterns - use momentum indicators
            commands.append(self.build_indicator_command("RSI"))
            commands.append(self.build_indicator_command("MACD"))
            commands.append(self.build_indicator_command("VOLUME"))
            
        elif pattern_type in ["triangle", "flag", "channel"]:
            # Continuation patterns - use trend indicators
            commands.append(self.build_indicator_command("EMA", {"period": 20}))
            commands.append(self.build_indicator_command("EMA", {"period": 50}))
            commands.append(self.build_indicator_command("BOLLINGER"))
            
        else:
            # Default set
            commands.append(self.build_indicator_command("RSI"))
            commands.append(self.build_indicator_command("VOLUME"))
            
        return commands