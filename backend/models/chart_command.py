from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal


class ChartCommand(BaseModel):
    """Structured representation of a chart command returned by the agent."""

    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    legacy: Optional[str] = None

    class Config:
        frozen = True

    def to_legacy(self) -> str:
        """Return the legacy string representation for backwards compatibility."""
        if self.legacy:
            return self.legacy

        action = self.type.lower()
        payload = self.payload

        if action == "load" and "symbol" in payload:
            return f"LOAD:{payload['symbol']}"
        if action == "timeframe" and "value" in payload:
            return f"TIMEFRAME:{payload['value']}"
        if action == "indicator":
            indicator = payload.get("name") or payload.get("indicator")
            if indicator:
                enabled = payload.get("enabled")
                if enabled is None:
                    return f"INDICATOR:{indicator}"
                return f"{'ADD' if enabled else 'REMOVE'}:{indicator}"
        if action == "zoom" and "direction" in payload:
            direction = payload["direction"].upper()
            amount = payload.get("amount")
            return f"ZOOM:{direction}{amount if amount else ''}".rstrip()
        if action == "reset" and "target" in payload:
            target = payload["target"].upper()
            return f"RESET:{target}"
        if action == "crosshair" and "mode" in payload:
            mode = payload["mode"].upper()
            return f"CROSSHAIR:{mode}"
        if action == "drawing":
            style = payload.get("style")
            if style == "support" and "price" in payload:
                return f"SUPPORT:{payload['price']}"
            if style == "resistance" and "price" in payload:
                return f"RESISTANCE:{payload['price']}"
            if style == "trendline":
                start_price = payload.get("start_price")
                end_price = payload.get("end_price")
                start_time = payload.get("start_time")
                end_time = payload.get("end_time")
                if None not in (start_price, start_time, end_price, end_time):
                    return (
                        f"TRENDLINE:{start_price}:{start_time}:{end_price}:{end_time}"
                    )
            if style == "fibonacci":
                high = payload.get("high")
                low = payload.get("low")
                if None not in (high, low):
                    return f"FIBONACCI:{high}:{low}"
        if action == "pattern" and payload.get("pattern_id"):
            return f"PATTERN:{payload['pattern_id']}"

        # Fallback to JSON dump when no mapping exists
        return self.model_dump_json()

    @classmethod
    def from_legacy(cls, command: str) -> "ChartCommand":
        """Construct a ChartCommand from the legacy string format."""
        if not command:
            return cls(type="raw", payload={"value": command}, legacy=command)

        parts = command.split(":")
        prefix = parts[0].strip().upper()
        rest = parts[1:] if len(parts) > 1 else []

        mapping = {
            "LOAD": lambda: cls(
                type="load",
                payload={"symbol": rest[0].upper()} if rest else {},
                legacy=command,
            ),
            "TIMEFRAME": lambda: cls(
                type="timeframe",
                payload={"value": rest[0].upper()} if rest else {},
                legacy=command,
            ),
            "ADD": lambda: cls(
                type="indicator",
                payload={"name": rest[0].upper() if rest else None, "enabled": True},
                legacy=command,
            ),
            "REMOVE": lambda: cls(
                type="indicator",
                payload={"name": rest[0].upper() if rest else None, "enabled": False},
                legacy=command,
            ),
            "INDICATOR": lambda: cls(
                type="indicator",
                payload={"name": rest[0].upper() if rest else None, "enabled": True},
                legacy=command,
            ),
            "SUPPORT": lambda: cls(
                type="drawing",
                payload={"style": "support", "price": _safe_float(rest, 0)},
                legacy=command,
            ),
            "RESISTANCE": lambda: cls(
                type="drawing",
                payload={"style": "resistance", "price": _safe_float(rest, 0)},
                legacy=command,
            ),
            "TRENDLINE": lambda: cls(
                type="drawing",
                payload={
                    "style": "trendline",
                    "start_price": _safe_float(rest, 0),
                    "start_time": _safe_int(rest, 1),
                    "end_price": _safe_float(rest, 2),
                    "end_time": _safe_int(rest, 3),
                },
                legacy=command,
            ),
            "FIBONACCI": lambda: cls(
                type="drawing",
                payload={
                    "style": "fibonacci",
                    "high": _safe_float(rest, 0),
                    "low": _safe_float(rest, 1),
                },
                legacy=command,
            ),
            "ZOOM": lambda: cls(
                type="zoom",
                payload={
                    "direction": rest[0].upper() if rest else "IN",
                    "amount": rest[1] if len(rest) > 1 else None,
                },
                legacy=command,
            ),
            "RESET": lambda: cls(
                type="reset",
                payload={"target": rest[0].upper() if rest else "VIEW"},
                legacy=command,
            ),
            "CROSSHAIR": lambda: cls(
                type="crosshair",
                payload={"mode": rest[0].upper() if rest else "TOGGLE"},
                legacy=command,
            ),
            "PATTERN": lambda: cls(
                type="pattern",
                payload={"pattern_id": rest[0] if rest else None},
                legacy=command,
            ),
        }

        try:
            parser = mapping.get(prefix)
            if parser:
                return parser()
        except Exception:
            # Fallback to raw representation if parsing fails
            pass

        return cls(type="raw", payload={"value": command}, legacy=command)

    def dedupe_key(self) -> str:
        """Return a unique key for deduplication purposes."""
        payload_key = json.dumps(self.payload, sort_keys=True, default=str)
        return f"{self.type}:{payload_key}"


class OverlayConfig(BaseModel):
    """Overlay configuration for ChartCommandPayloadV2."""

    name: str
    type: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class IndicatorConfig(BaseModel):
    """Indicator configuration for ChartCommandPayloadV2."""

    name: str
    enabled: Optional[bool] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class ChartCommandPayloadV2(BaseModel):
    """Structured chart payload emitted alongside legacy chart commands."""

    version: Literal["2.0"] = "2.0"
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    overlays: List[OverlayConfig] = Field(default_factory=list)
    indicators: List[IndicatorConfig] = Field(default_factory=list)
    commands: List[ChartCommand] = Field(default_factory=list)
    notes: Optional[str] = None


def _safe_float(parts: Any, index: int) -> Optional[float]:
    try:
        if len(parts) > index and parts[index] not in (None, ""):
            return float(parts[index])
    except (ValueError, TypeError):
        return None
    return None


def _safe_int(parts: Any, index: int) -> Optional[int]:
    try:
        if len(parts) > index and parts[index] not in (None, ""):
            return int(float(parts[index]))
    except (ValueError, TypeError):
        return None
    return None
