from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

from .http_mcp_client import HTTPMCPClient

logger = logging.getLogger(__name__)


class ForexMCPClient:
    """Wrapper around HTTPMCPClient for Forex Factory calendar tools."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or os.getenv("FOREX_MCP_URL", "http://127.0.0.1:3002/mcp")
        self._client = HTTPMCPClient(base_url=self.base_url)

    async def ensure_connection(self) -> None:
        """Ensure the underlying MCP session is initialized."""

        await self._client.initialize()

    async def get_calendar_events(
        self,
        *,
        time_period: str = "today",
        start: Optional[str] = None,
        end: Optional[str] = None,
        impact: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch economic calendar events using the MCP tool."""

        arguments: Dict[str, Any] = {"time_period": time_period}
        if start:
            arguments["start"] = start
        if end:
            arguments["end"] = end
        if impact:
            arguments["impact"] = impact

        logger.info(
            "Calling Forex MCP calendar tool", extra={"time_period": time_period, "start": start, "end": end, "impact": impact}
        )

        result = await self._client.call_tool("ffcal_get_calendar_events", arguments)
        payload = self._parse_calendar_payload(result)
        payload.setdefault("time_period", time_period)
        return payload

    @staticmethod
    def _parse_calendar_payload(result: Any) -> Dict[str, Any]:
        """Normalize the MCP tool response into a calendar dictionary."""

        json_blob = ForexMCPClient._extract_json_string(result)
        if not json_blob:
            raise ValueError("Forex MCP response did not contain content")

        try:
            data = json.loads(json_blob)
        except json.JSONDecodeError as exc:
            logger.error("Failed to decode Forex MCP response", exc_info=exc)
            raise ValueError("Invalid JSON returned by Forex MCP server") from exc

        if not isinstance(data, dict):
            raise ValueError("Forex MCP response must decode into an object")

        data.setdefault("events", [])
        return data

    @staticmethod
    def _extract_json_string(result: Any) -> Optional[str]:
        """Extract the JSON payload string from various MCP response formats."""

        if result is None:
            return None

        if isinstance(result, str):
            return result

        if isinstance(result, dict):
            # Already parsed calendar payload
            if "events" in result and isinstance(result["events"], list):
                return json.dumps(result)

            # FastMCP HTTP format: {"jsonrpc": "2.0", "result": {...}}
            inner = result.get("result") if "result" in result else result
            if isinstance(inner, dict):
                # Content list (text segments)
                content = inner.get("content")
                if isinstance(content, list):
                    fragments = [item.get("text") for item in content if isinstance(item, dict) and item.get("text")]
                    if fragments:
                        return "".join(fragments)

                # Explicit text field
                if isinstance(inner.get("text"), str):
                    return inner["text"]

                # JSON field already parsed
                if inner.get("json") is not None:
                    return json.dumps(inner["json"])

            # Some implementations embed payload directly under "content"
            if isinstance(result.get("content"), list):
                fragments = [item.get("text") for item in result["content"] if isinstance(item, dict) and item.get("text")]
                if fragments:
                    return "".join(fragments)

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                text_value = first.get("text")
                if isinstance(text_value, str):
                    return text_value
                if first.get("json") is not None:
                    return json.dumps(first["json"])

        return None


_global_client: Optional[ForexMCPClient] = None
_client_lock = asyncio.Lock()


async def get_forex_mcp_client() -> ForexMCPClient:
    """Return a singleton ForexMCPClient instance."""

    global _global_client
    async with _client_lock:
        if _global_client is None:
            _global_client = ForexMCPClient()
            await _global_client.ensure_connection()
    return _global_client


async def reset_forex_mcp_client() -> None:
    """Reset the cached Forex MCP client (useful for tests)."""

    global _global_client
    async with _client_lock:
        _global_client = None
