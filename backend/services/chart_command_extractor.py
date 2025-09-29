"""
Chart Command Extractor
Extracts chart commands from Voice Assistant responses containing technical analysis.
"""

import re
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ChartCommandExtractor:
    """Extracts chart commands from Voice Assistant text responses."""
    
    def extract_commands_from_response(
        self, 
        response_text: str, 
        query: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Extract chart commands from Voice Assistant response text.
        
        Args:
            response_text: The Voice Assistant's text response
            query: The original user query
            data: Additional data from the response
            
        Returns:
            List of chart commands to execute
        """
        commands = []
        
        if not response_text:
            return commands
        
        # Parse support and resistance levels
        support_commands = self._extract_support_resistance(response_text, "support")
        resistance_commands = self._extract_support_resistance(response_text, "resistance")
        commands.extend(support_commands)
        commands.extend(resistance_commands)
        
        # Parse Fibonacci levels
        fib_commands = self._extract_fibonacci(response_text)
        commands.extend(fib_commands)
        
        # Parse entry/stop/target levels
        trade_commands = self._extract_trade_levels(response_text)
        commands.extend(trade_commands)
        
        # Parse indicator mentions
        indicator_commands = self._extract_indicators(response_text, query)
        commands.extend(indicator_commands)
        
        # Parse drawing commands
        drawing_commands = self._extract_drawing_commands(response_text)
        commands.extend(drawing_commands)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        
        if unique_commands:
            logger.info(f"Extracted {len(unique_commands)} chart commands from response")
            logger.debug(f"Commands: {unique_commands}")
        
        return unique_commands
    
    def _extract_support_resistance(self, text: str, level_type: str) -> List[str]:
        """Extract support or resistance levels from text."""
        commands = []
        text_lower = text.lower()
        
        # Pattern 1: "support at $XXX" or "resistance at $XXX"
        pattern1 = rf"{level_type}(?:\s+level)?(?:\s+at)?\s+\$?([\d,]+\.?\d*)"
        matches1 = re.finditer(pattern1, text_lower)
        
        # Pattern 2: "support levels: $XXX, $YYY" or similar
        pattern2 = rf"{level_type}\s+levels?[:\s]+([^.]+)"
        matches2 = re.finditer(pattern2, text_lower)
        
        # Pattern 3: "$XXX support" or "$XXX resistance"
        pattern3 = rf"\$?([\d,]+\.?\d*)\s+{level_type}"
        matches3 = re.finditer(pattern3, text_lower)
        
        # Process pattern 1 matches
        for match in matches1:
            price_str = match.group(1).replace(",", "")
            try:
                price = float(price_str)
                cmd = f"{level_type.upper()}:{price}"
                commands.append(cmd)
            except ValueError:
                pass
        
        # Process pattern 2 matches (lists of levels)
        for match in matches2:
            levels_text = match.group(1)
            # Extract all numbers from the levels text
            numbers = re.findall(r"\$?([\d,]+\.?\d*)", levels_text)
            for num_str in numbers[:3]:  # Limit to first 3 levels
                try:
                    price = float(num_str.replace(",", ""))
                    cmd = f"{level_type.upper()}:{price}"
                    commands.append(cmd)
                except ValueError:
                    pass
        
        # Process pattern 3 matches
        for match in matches3:
            price_str = match.group(1).replace(",", "")
            try:
                price = float(price_str)
                cmd = f"{level_type.upper()}:{price}"
                commands.append(cmd)
            except ValueError:
                pass
        
        return commands
    
    def _extract_fibonacci(self, text: str) -> List[str]:
        """Extract Fibonacci retracement levels from text."""
        commands = []
        text_lower = text.lower()
        
        # Look for Fibonacci mentions with price ranges
        if "fibonacci" in text_lower or "fib" in text_lower:
            # Extract all prices mentioned
            prices = re.findall(r"\$?([\d,]+\.?\d*)", text)
            prices_float = []
            for p in prices:
                try:
                    prices_float.append(float(p.replace(",", "")))
                except ValueError:
                    pass
            
            # If we have at least 2 prices, use min and max for Fibonacci
            if len(prices_float) >= 2:
                low = min(prices_float)
                high = max(prices_float)
                commands.append(f"FIBONACCI:{low}:{high}")
        
        return commands
    
    def _extract_trade_levels(self, text: str) -> List[str]:
        """Extract entry, stop loss, and target levels from text."""
        commands = []
        text_lower = text.lower()
        
        # Entry patterns
        entry_patterns = [
            r"entry(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"enter(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"buy(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
        ]
        
        # Stop loss patterns
        stop_patterns = [
            r"stop(?:\s+loss)?(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"stop-loss(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"sl(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
        ]
        
        # Target patterns
        target_patterns = [
            r"target(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"take(?:\s+profit)?(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
            r"tp(?:\s+at)?\s+\$?([\d,]+\.?\d*)",
        ]
        
        entry = None
        stop = None
        target = None
        
        # Extract entry
        for pattern in entry_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    entry = float(match.group(1).replace(",", ""))
                    break
                except ValueError:
                    pass
        
        # Extract stop loss
        for pattern in stop_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    stop = float(match.group(1).replace(",", ""))
                    break
                except ValueError:
                    pass
        
        # Extract target
        for pattern in target_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    target = float(match.group(1).replace(",", ""))
                    break
                except ValueError:
                    pass
        
        # Build command if we have at least one level
        cmd_parts = []
        if entry:
            cmd_parts.append(f"ENTRY:{entry}")
        if stop:
            cmd_parts.append(f"STOP:{stop}")
        if target:
            cmd_parts.append(f"TARGET:{target}")
        
        if cmd_parts:
            commands.append(" ".join(cmd_parts))
        
        return commands
    
    def _extract_indicators(self, text: str, query: str) -> List[str]:
        """Extract indicator commands from text."""
        commands = []
        combined_text = (text + " " + query).lower()
        
        indicator_map = {
            "rsi": "RSI",
            "macd": "MACD",
            "ema": "EMA",
            "sma": "SMA",
            "bollinger": "BOLLINGER",
            "stochastic": "STOCHASTIC",
            "volume": "VOLUME",
        }
        
        # Check if user wants to show/add indicators
        show_keywords = ["show", "add", "display", "turn on", "enable", "overlay"]
        has_show_intent = any(keyword in combined_text for keyword in show_keywords)
        
        if has_show_intent:
            for indicator_key, indicator_name in indicator_map.items():
                if indicator_key in combined_text:
                    commands.append(f"INDICATOR:{indicator_name}:ON")
        
        return commands
    
    def _extract_drawing_commands(self, text: str) -> List[str]:
        """Extract drawing commands from text."""
        commands = []
        text_lower = text.lower()
        
        # Trendline patterns
        if "trendline" in text_lower or "trend line" in text_lower:
            # Try to extract price points
            prices = re.findall(r"\$?([\d,]+\.?\d*)", text)
            prices_float = []
            for p in prices:
                try:
                    prices_float.append(float(p.replace(",", "")))
                except ValueError:
                    pass
            
            if len(prices_float) >= 2:
                commands.append(f"TRENDLINE:{prices_float[0]}:{prices_float[1]}")
        
        # Pattern drawing commands
        pattern_types = ["triangle", "wedge", "flag", "head and shoulders", "double top", "double bottom"]
        for pattern in pattern_types:
            if pattern in text_lower:
                commands.append(f"PATTERN:{pattern.upper().replace(' ', '_')}")
        
        return commands