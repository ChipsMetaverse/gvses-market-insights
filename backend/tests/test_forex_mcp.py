import json
from typing import Any, Dict

import pytest

from services.forex_mcp_client import ForexMCPClient


class _AsyncStub:
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload
        self.last_arguments: Optional[Dict[str, Any]] = None

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        self.last_arguments = {**arguments}
        assert name == "ffcal_get_calendar_events"
        return self.payload


@pytest.mark.asyncio
async def test_get_calendar_events_returns_parsed_payload(monkeypatch):
    client = ForexMCPClient(base_url="http://example")
    stub = _AsyncStub({"result": {"content": [{"text": json.dumps({"events": [{"id": "e1"}]})}]}})

    # Patch the underlying HTTP client to avoid real network I/O
    monkeypatch.setattr(client, "_client", stub, raising=False)

    result = await client.get_calendar_events(time_period="today", impact="high")

    assert result["events"] == [{"id": "e1"}]
    assert stub.last_arguments == {"time_period": "today", "impact": "high"}


def test_parse_calendar_payload_accepts_string_json():
    payload = {"events": [{"id": "abc"}]}
    raw = json.dumps(payload)

    result = ForexMCPClient._parse_calendar_payload(raw)

    assert result == payload


def test_parse_calendar_payload_raises_on_invalid_json():
    with pytest.raises(ValueError):
        ForexMCPClient._parse_calendar_payload("not-json")


def test_extract_json_string_handles_direct_dict():
    payload = {"events": [{"id": "xyz"}]}
    packed = {"result": {"json": payload}}

    extracted = ForexMCPClient._extract_json_string(packed)

    assert extracted is not None
    assert json.loads(extracted) == payload
