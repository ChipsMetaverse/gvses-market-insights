"""
Function Registry for Chart Controls
Unified function calling system that works with:
- Direct function calls from OpenAI Agent Builder
- Widget actions from ChatKit
- Voice commands
"""

import json
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FunctionDefinition:
    """OpenAI-compatible function definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable


class ChartFunctionRegistry:
    """
    Registry of chart control functions

    Supports OpenAI function calling format and widget actions
    """

    def __init__(self):
        self.functions: Dict[str, FunctionDefinition] = {}
        self._register_chart_functions()

    def register(self, func_def: FunctionDefinition):
        """Register a function"""
        self.functions[func_def.name] = func_def
        logger.info(f"Registered function: {func_def.name}")

    def _register_chart_functions(self):
        """Register all chart control functions"""

        # Function: change_chart_symbol
        self.register(FunctionDefinition(
            name="change_chart_symbol",
            description="Changes the trading chart to display a different stock symbol. Use this when the user wants to view a specific stock.",
            parameters={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA, NVDA, MSFT)"
                    }
                },
                "required": ["symbol"],
                "additionalProperties": False
            },
            handler=self._change_chart_symbol
        ))

        # Function: set_chart_timeframe
        self.register(FunctionDefinition(
            name="set_chart_timeframe",
            description="Changes the chart timeframe to show different time intervals. Use this when the user wants to see data at a different granularity.",
            parameters={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
                        "description": "Chart timeframe: 1m (1 minute), 5m (5 minutes), 15m (15 minutes), 30m (30 minutes), 1h (1 hour), 4h (4 hours), 1d (1 day), 1w (1 week), 1M (1 month)"
                    }
                },
                "required": ["timeframe"],
                "additionalProperties": False
            },
            handler=self._set_chart_timeframe
        ))

        # Function: toggle_chart_indicator
        self.register(FunctionDefinition(
            name="toggle_chart_indicator",
            description="Toggles a technical indicator on or off on the chart. Use this when the user wants to add or remove technical analysis indicators.",
            parameters={
                "type": "object",
                "properties": {
                    "indicator": {
                        "type": "string",
                        "enum": ["sma", "ema", "bollinger", "rsi", "macd", "volume"],
                        "description": "Technical indicator: sma (Simple Moving Average), ema (Exponential Moving Average), bollinger (Bollinger Bands), rsi (Relative Strength Index), macd (MACD), volume (Volume bars)"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether to enable (true) or disable (false) the indicator"
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period for the indicator (optional, defaults vary by indicator)",
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["indicator", "enabled"],
                "additionalProperties": False
            },
            handler=self._toggle_chart_indicator
        ))

        # Function: highlight_chart_pattern
        self.register(FunctionDefinition(
            name="highlight_chart_pattern",
            description="Highlights support/resistance levels or chart patterns. Use this when the user asks about technical levels or patterns.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "enum": ["support", "resistance", "trendline", "fibonacci", "channel"],
                        "description": "Pattern type to highlight"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price level for support/resistance (optional for other patterns)"
                    }
                },
                "required": ["pattern"],
                "additionalProperties": False
            },
            handler=self._highlight_chart_pattern
        ))

    async def _change_chart_symbol(self, symbol: str) -> Dict[str, Any]:
        """Change chart symbol"""
        # Store command for frontend polling
        command = {
            "action": "change_symbol",
            "symbol": symbol.upper()
        }

        # This will be implemented to integrate with existing chart command storage
        logger.info(f"Chart command: change symbol to {symbol}")

        return {
            "success": True,
            "message": f"Chart updated to {symbol.upper()}",
            "command": command
        }

    async def _set_chart_timeframe(self, timeframe: str) -> Dict[str, Any]:
        """Set chart timeframe"""
        command = {
            "action": "set_timeframe",
            "timeframe": timeframe
        }

        logger.info(f"Chart command: set timeframe to {timeframe}")

        return {
            "success": True,
            "message": f"Timeframe changed to {timeframe}",
            "command": command
        }

    async def _toggle_chart_indicator(self, indicator: str, enabled: bool, period: Optional[int] = None) -> Dict[str, Any]:
        """Toggle chart indicator"""
        command = {
            "action": "toggle_indicator",
            "indicator": indicator,
            "enabled": enabled
        }

        if period is not None:
            command["period"] = period

        action_verb = "enabled" if enabled else "disabled"
        logger.info(f"Chart command: {action_verb} {indicator} indicator")

        return {
            "success": True,
            "message": f"{indicator.upper()} indicator {action_verb}",
            "command": command
        }

    async def _highlight_chart_pattern(self, pattern: str, price: Optional[float] = None) -> Dict[str, Any]:
        """Highlight chart pattern"""
        command = {
            "action": "highlight_pattern",
            "pattern": pattern
        }

        if price is not None:
            command["price"] = price

        logger.info(f"Chart command: highlight {pattern}" + (f" at {price}" if price else ""))

        return {
            "success": True,
            "message": f"Highlighted {pattern}" + (f" at ${price}" if price else ""),
            "command": command
        }

    async def call_function(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a registered function

        Args:
            name: Function name
            arguments: Function arguments

        Returns:
            Function result
        """
        if name not in self.functions:
            raise ValueError(f"Unknown function: {name}")

        func_def = self.functions[name]

        try:
            result = await func_def.handler(**arguments)
            logger.info(f"Function {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing function {name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_openai_tools(self) -> list:
        """
        Get function definitions in OpenAI format

        Returns:
            List of tool definitions for OpenAI API
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": func_def.name,
                    "description": func_def.description,
                    "parameters": func_def.parameters,
                    "strict": True
                }
            }
            for func_def in self.functions.values()
        ]

    def get_function_schemas(self) -> Dict[str, Any]:
        """
        Get function schemas for documentation

        Returns:
            Dictionary of function schemas
        """
        return {
            name: {
                "description": func_def.description,
                "parameters": func_def.parameters
            }
            for name, func_def in self.functions.items()
        }


# Global registry instance
chart_function_registry = ChartFunctionRegistry()
