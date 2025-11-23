"""
Chart Control API Bridge for MCP Integration
Provides HTTP endpoints that MCP tools can call to control the frontend chart.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chart", tags=["Chart Control"])

# Chart state storage (in production, use Redis or database)
chart_state = {
    "current_symbol": "TSLA",
    "timeframe": "1d", 
    "indicators": {},
    "style": "candles",
    "last_command": None,
    "command_queue": []
}

# Request models
class ChangeSymbolRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")

class SetTimeframeRequest(BaseModel):
    timeframe: str = Field(..., description="Chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)")

class ToggleIndicatorRequest(BaseModel):
    indicator: str = Field(..., description="Technical indicator name (RSI, MACD, Moving Average, Bollinger Bands, Volume, Stochastic)")
    enabled: bool = Field(..., description="Whether to enable (true) or disable (false) the indicator")

class CaptureSnapshotRequest(BaseModel):
    include_data: bool = Field(default=False, description="Whether to include current market data in the response")

class SetStyleRequest(BaseModel):
    style: str = Field(..., description="Chart style (candles, line, area)")

# Response models
class ChartControlResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str
    command_id: str

class ChartStateResponse(BaseModel):
    symbol: str
    timeframe: str
    indicators: Dict[str, bool]
    style: str
    last_updated: str

# Utility functions
def generate_command_id() -> str:
    """Generate unique command ID for tracking."""
    return f"cmd_{int(datetime.now().timestamp() * 1000)}"

def add_command_to_queue(command_type: str, data: Dict[str, Any]) -> str:
    """Add command to the frontend processing queue."""
    command_id = generate_command_id()
    command = {
        "id": command_id,
        "type": command_type,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    chart_state["command_queue"].append(command)
    chart_state["last_command"] = command
    
    logger.info(f"Added chart command {command_type} with ID {command_id}")
    return command_id

# Chart Control Endpoints

@router.post("/change-symbol", response_model=ChartControlResponse)
async def change_chart_symbol(request: ChangeSymbolRequest):
    """Change the symbol displayed on the trading chart."""
    try:
        # Validate symbol format
        symbol = request.symbol.upper().strip()
        if not symbol or len(symbol) < 1 or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        
        # Add command to queue for frontend processing
        command_id = add_command_to_queue("symbol_change", {
            "symbol": symbol,
            "previous_symbol": chart_state["current_symbol"]
        })
        
        # Update state
        previous_symbol = chart_state["current_symbol"]
        chart_state["current_symbol"] = symbol
        
        return ChartControlResponse(
            success=True,
            message=f"Chart symbol changed from {previous_symbol} to {symbol}",
            data={
                "symbol": symbol,
                "previous_symbol": previous_symbol
            },
            timestamp=datetime.now().isoformat(),
            command_id=command_id
        )
        
    except Exception as e:
        logger.error(f"Error changing chart symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-timeframe", response_model=ChartControlResponse)
async def set_chart_timeframe(request: SetTimeframeRequest):
    """Set the timeframe for chart data display."""
    try:
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1w", "1M"]
        
        if request.timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
            )
        
        # Add command to queue
        command_id = add_command_to_queue("timeframe_change", {
            "timeframe": request.timeframe,
            "previous_timeframe": chart_state["timeframe"]
        })
        
        # Update state
        previous_timeframe = chart_state["timeframe"]
        chart_state["timeframe"] = request.timeframe
        
        return ChartControlResponse(
            success=True,
            message=f"Chart timeframe changed from {previous_timeframe} to {request.timeframe}",
            data={
                "timeframe": request.timeframe,
                "previous_timeframe": previous_timeframe
            },
            timestamp=datetime.now().isoformat(),
            command_id=command_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting chart timeframe: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toggle-indicator", response_model=ChartControlResponse)
async def toggle_chart_indicator(request: ToggleIndicatorRequest):
    """Toggle technical indicators on or off on the trading chart."""
    try:
        # Support both formal names and common aliases (case-insensitive)
        indicator_mapping = {
            "rsi": "RSI",
            "macd": "MACD", 
            "moving average": "Moving Average",
            "ma": "Moving Average",
            "sma": "Moving Average",
            "ema": "Moving Average",
            "bollinger bands": "Bollinger Bands",
            "bollinger": "Bollinger Bands",
            "bb": "Bollinger Bands",
            "volume": "Volume",
            "stochastic": "Stochastic",
            "stoch": "Stochastic"
        }
        
        # Normalize indicator name
        normalized_indicator = request.indicator.lower()
        if normalized_indicator in indicator_mapping:
            actual_indicator = indicator_mapping[normalized_indicator]
        elif request.indicator in indicator_mapping.values():
            actual_indicator = request.indicator
        else:
            valid_options = list(set(indicator_mapping.values()))
            raise HTTPException(
                status_code=400,
                detail=f"Invalid indicator. Must be one of: {', '.join(valid_options)} (or common aliases like sma, ema, bb, stoch)"
            )
        
        # Add command to queue
        command_id = add_command_to_queue("indicator_toggle", {
            "indicator": actual_indicator,
            "requested_indicator": request.indicator,
            "enabled": request.enabled,
            "previous_state": chart_state["indicators"].get(actual_indicator, False)
        })
        
        # Update state
        chart_state["indicators"][actual_indicator] = request.enabled
        
        action = "enabled" if request.enabled else "disabled"
        
        return ChartControlResponse(
            success=True,
            message=f"{actual_indicator} indicator {action} on chart (requested as '{request.indicator}')",
            data={
                "indicator": actual_indicator,
                "requested_indicator": request.indicator,
                "enabled": request.enabled,
                "all_indicators": chart_state["indicators"]
            },
            timestamp=datetime.now().isoformat(),
            command_id=command_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling chart indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/capture-snapshot", response_model=ChartControlResponse)
async def capture_chart_snapshot(request: CaptureSnapshotRequest):
    """Capture a screenshot of the current chart state."""
    try:
        # Add command to queue for frontend processing
        command_id = add_command_to_queue("capture_snapshot", {
            "include_data": request.include_data,
            "current_symbol": chart_state["current_symbol"],
            "timeframe": chart_state["timeframe"]
        })
        
        response_data = {
            "snapshot_requested": True,
            "include_data": request.include_data,
            "symbol": chart_state["current_symbol"],
            "timeframe": chart_state["timeframe"]
        }
        
        # If data is requested, include current chart state
        if request.include_data:
            response_data.update({
                "indicators": chart_state["indicators"],
                "style": chart_state["style"],
                "timestamp": datetime.now().isoformat()
            })
        
        return ChartControlResponse(
            success=True,
            message=f"Chart snapshot capture initiated for {chart_state['current_symbol']}",
            data=response_data,
            timestamp=datetime.now().isoformat(),
            command_id=command_id
        )
        
    except Exception as e:
        logger.error(f"Error capturing chart snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-style", response_model=ChartControlResponse)
async def set_chart_style(request: SetStyleRequest):
    """Set the chart display style (candles, line, area)."""
    try:
        valid_styles = ["candles", "line", "area"]
        
        if request.style not in valid_styles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
            )
        
        # Add command to queue
        command_id = add_command_to_queue("style_change", {
            "style": request.style,
            "previous_style": chart_state["style"]
        })
        
        # Update state
        previous_style = chart_state["style"]
        chart_state["style"] = request.style
        
        return ChartControlResponse(
            success=True,
            message=f"Chart style changed from {previous_style} to {request.style}",
            data={
                "style": request.style,
                "previous_style": previous_style
            },
            timestamp=datetime.now().isoformat(),
            command_id=command_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting chart style: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# State Management Endpoints

@router.get("/state", response_model=ChartStateResponse)
async def get_chart_state():
    """Get the current chart state."""
    return ChartStateResponse(
        symbol=chart_state["current_symbol"],
        timeframe=chart_state["timeframe"],
        indicators=chart_state["indicators"],
        style=chart_state["style"],
        last_updated=datetime.now().isoformat()
    )

@router.get("/commands")
async def get_command_queue():
    """Get the current command queue for frontend polling."""
    return {
        "commands": chart_state["command_queue"],
        "count": len(chart_state["command_queue"]),
        "last_command": chart_state["last_command"]
    }

@router.delete("/commands/{command_id}")
async def acknowledge_command(command_id: str):
    """Acknowledge that a command has been processed by the frontend."""
    try:
        # Remove command from queue
        chart_state["command_queue"] = [
            cmd for cmd in chart_state["command_queue"] 
            if cmd["id"] != command_id
        ]
        
        return {
            "success": True,
            "message": f"Command {command_id} acknowledged",
            "remaining_commands": len(chart_state["command_queue"])
        }
        
    except Exception as e:
        logger.error(f"Error acknowledging command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_chart_state():
    """Reset chart state to defaults."""
    global chart_state
    
    chart_state = {
        "current_symbol": "TSLA",
        "timeframe": "1d",
        "indicators": {},
        "style": "candles", 
        "last_command": None,
        "command_queue": []
    }
    
    return {
        "success": True,
        "message": "Chart state reset to defaults",
        "state": chart_state
    }