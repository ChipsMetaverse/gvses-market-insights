"""
Test Chart Command Structured Serialization
============================================
Regression tests for Phase 1 backend fixes ensuring all code paths
emit both legacy and structured chart command formats.

Tests cover:
1. Chart-only intent fast-path
2. Indicator-toggle intent fast-path
3. Voice query endpoint
"""

import pytest
from datetime import datetime
from services.agent_orchestrator import get_orchestrator

# Import app lazily to avoid initialization issues during collection
def get_test_client():
    """Get FastAPI test client."""
    from fastapi.testclient import TestClient
    from mcp_server import app as fastapi_app  # Alias the app to avoid conflict
    client = TestClient(app=fastapi_app)
    return client


class TestChartOnlyIntentStructuredCommands:
    """Test chart-only intent fast-path emits structured commands."""

    @pytest.mark.asyncio
    async def test_chart_only_intent_includes_structured_format(self):
        """Chart-only queries should return both legacy and structured formats."""
        orchestrator = get_orchestrator()

        # Test simple chart load
        result = await orchestrator.process_query("show me TSLA")

        # Verify both formats present
        assert "chart_commands" in result, "Missing legacy chart_commands"
        assert "chart_commands_structured" in result, "Missing chart_commands_structured"

        # Verify structured format is a list
        assert isinstance(result["chart_commands_structured"], list), \
            "chart_commands_structured should be a list"

        # Verify at least one command
        assert len(result["chart_commands_structured"]) > 0, \
            "Should have at least one structured command"

        # Verify structured command has required fields
        cmd = result["chart_commands_structured"][0]
        assert "type" in cmd, "Structured command missing 'type' field"
        assert "payload" in cmd, "Structured command missing 'payload' field"

        # Verify command type and payload
        assert cmd["type"] == "load", f"Expected type 'load', got {cmd['type']}"
        assert "symbol" in cmd["payload"], "Payload missing 'symbol' field"
        assert cmd["payload"]["symbol"] == "TSLA", \
            f"Expected symbol 'TSLA', got {cmd['payload']['symbol']}"

    @pytest.mark.asyncio
    async def test_chart_only_intent_legacy_format_preserved(self):
        """Legacy format should still work for backwards compatibility."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("load AAPL chart")

        # Verify legacy format
        assert "chart_commands" in result
        assert isinstance(result["chart_commands"], list)
        assert len(result["chart_commands"]) > 0

        # Legacy format should be strings
        assert isinstance(result["chart_commands"][0], str), \
            "Legacy chart_commands should be strings"

        # Should contain symbol
        assert "AAPL" in result["chart_commands"][0], \
            "Legacy command should contain symbol"

    @pytest.mark.asyncio
    async def test_chart_only_intent_metadata_fields(self):
        """Structured format should include metadata fields."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("show NVDA")

        cmd = result["chart_commands_structured"][0]

        # Verify standard metadata fields
        assert "timestamp" in cmd, "Missing timestamp metadata"

        # Timestamp should be ISO format
        try:
            datetime.fromisoformat(cmd["timestamp"])
        except ValueError:
            pytest.fail("Timestamp not in ISO format")

    @pytest.mark.asyncio
    async def test_chart_only_multiple_symbols_handled(self):
        """Multiple symbol variations should all work."""
        orchestrator = get_orchestrator()

        test_cases = [
            "show me MSFT",
            "load GOOGL chart",
            "display SPY",
            "switch to AMZN"
        ]

        for query in test_cases:
            result = await orchestrator.process_query(query)

            assert "chart_commands_structured" in result, \
                f"Missing structured commands for query: {query}"
            assert len(result["chart_commands_structured"]) > 0, \
                f"No commands generated for query: {query}"


class TestIndicatorToggleStructuredCommands:
    """Test indicator-toggle intent fast-path emits structured commands."""

    @pytest.mark.asyncio
    async def test_indicator_toggle_includes_structured_format(self):
        """Indicator toggle queries should return structured format."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("show RSI")

        # Verify both formats present
        assert "chart_commands" in result
        assert "chart_commands_structured" in result

        # Verify structured format has indicator command
        structured_cmds = result["chart_commands_structured"]
        assert isinstance(structured_cmds, list)
        assert len(structured_cmds) > 0

        # At least one command should be an indicator
        indicator_found = any(
            cmd.get("type") == "indicator"
            for cmd in structured_cmds
        )
        assert indicator_found, "No indicator command found in structured format"

    @pytest.mark.asyncio
    async def test_indicator_toggle_payload_structure(self):
        """Indicator commands should have proper payload structure."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("add MACD")

        # Find indicator command
        structured_cmds = result["chart_commands_structured"]
        indicator_cmd = next(
            (cmd for cmd in structured_cmds if cmd.get("type") == "indicator"),
            None
        )

        assert indicator_cmd is not None, "No indicator command found"

        # Verify payload structure
        assert "payload" in indicator_cmd
        payload = indicator_cmd["payload"]

        # Should have indicator name
        assert "name" in payload or "indicator" in payload, \
            "Payload missing indicator name"

    @pytest.mark.asyncio
    async def test_indicator_toggle_multiple_indicators(self):
        """Multiple indicator types should all work."""
        orchestrator = get_orchestrator()

        test_cases = [
            "show RSI",
            "add MACD",
            "display Bollinger Bands",
            "toggle SMA"
        ]

        for query in test_cases:
            result = await orchestrator.process_query(query)

            assert "chart_commands_structured" in result, \
                f"Missing structured commands for: {query}"

            # Should have at least one command
            assert len(result["chart_commands_structured"]) > 0, \
                f"No commands for: {query}"


class TestVoiceQueryEndpointStructuredCommands:
    """Test voice query endpoint returns structured commands."""

    def test_voice_query_endpoint_includes_structured_format(self):
        """Voice query endpoint should return chart_commands_structured."""
        client = get_test_client()
        response = client.post(
            "/api/agent/voice-query",
            json={
                "query": "load Apple chart",
                "session_id": "test-session-123"
            }
        )

        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"

        data = response.json()

        # Verify both formats in response
        assert "chart_commands" in data or data.get("chart_commands") is not None, \
            "chart_commands field missing or null"
        assert "chart_commands_structured" in data or data.get("chart_commands_structured") is not None, \
            "chart_commands_structured field missing or null"

    def test_voice_query_endpoint_structured_format_valid(self):
        """Structured format from voice endpoint should be valid."""
        client = get_test_client()
        response = client.post(
            "/api/agent/voice-query",
            json={
                "query": "show me Tesla",
                "session_id": "test-session-456"
            }
        )

        data = response.json()

        # If structured commands present, validate structure
        if data.get("chart_commands_structured"):
            structured_cmds = data["chart_commands_structured"]

            assert isinstance(structured_cmds, list), \
                "chart_commands_structured should be a list"

            # Validate each command has required fields
            for cmd in structured_cmds:
                assert isinstance(cmd, dict), "Command should be a dict"
                assert "type" in cmd, "Command missing 'type' field"
                assert "payload" in cmd, "Command missing 'payload' field"

    def test_voice_query_endpoint_session_id_preserved(self):
        """Session ID should be preserved in response."""
        client = get_test_client()
        test_session_id = "test-session-789"

        response = client.post(
            "/api/agent/voice-query",
            json={
                "query": "show NVDA chart",
                "session_id": test_session_id
            }
        )

        data = response.json()

        assert data.get("session_id") == test_session_id, \
            "Session ID not preserved in response"


class TestStructuredFormatConsistency:
    """Test consistency between legacy and structured formats."""

    @pytest.mark.asyncio
    async def test_structured_and_legacy_formats_equivalent(self):
        """Structured format should represent same commands as legacy."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("show me TSLA")

        legacy_cmds = result.get("chart_commands", [])
        structured_cmds = result.get("chart_commands_structured", [])

        # Should have same number of commands
        assert len(legacy_cmds) == len(structured_cmds), \
            f"Command count mismatch: {len(legacy_cmds)} legacy vs {len(structured_cmds)} structured"

        # First command should reference same symbol
        if structured_cmds and "symbol" in structured_cmds[0].get("payload", {}):
            symbol_from_structured = structured_cmds[0]["payload"]["symbol"]

            # Legacy command should contain the symbol
            assert any(symbol_from_structured in cmd for cmd in legacy_cmds), \
                f"Symbol {symbol_from_structured} not found in legacy commands"

    @pytest.mark.asyncio
    async def test_serialization_deduplication(self):
        """Serializer should deduplicate commands."""
        orchestrator = get_orchestrator()

        # Process query that might generate duplicate commands
        result = await orchestrator.process_query("show AAPL chart on AAPL")

        structured_cmds = result.get("chart_commands_structured", [])

        # Extract unique command signatures
        signatures = set()
        for cmd in structured_cmds:
            sig = (
                cmd.get("type"),
                cmd.get("payload", {}).get("symbol")
            )
            signatures.add(sig)

        # Should not have duplicate signatures
        assert len(signatures) == len(structured_cmds), \
            "Found duplicate commands in serialized output"


class TestErrorHandling:
    """Test error scenarios preserve structured format."""

    @pytest.mark.asyncio
    async def test_empty_query_returns_valid_structure(self):
        """Empty queries should return valid response structure."""
        orchestrator = get_orchestrator()

        result = await orchestrator.process_query("")

        # Should return a response (even if error)
        assert isinstance(result, dict)
        assert "text" in result

        # chart_commands fields should be present or None
        if "chart_commands" in result:
            assert result["chart_commands"] is None or isinstance(result["chart_commands"], list)
        if "chart_commands_structured" in result:
            assert result["chart_commands_structured"] is None or isinstance(result["chart_commands_structured"], list)

    def test_voice_query_endpoint_invalid_json_handled(self):
        """Voice endpoint should handle invalid JSON gracefully."""
        client = get_test_client()
        response = client.post(
            "/api/agent/voice-query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return error, not crash
        assert response.status_code in [400, 422], \
            f"Expected 400/422 for invalid JSON, got {response.status_code}"


# Test markers for selective execution
pytestmark = [
    pytest.mark.integration,  # These are integration tests
    pytest.mark.phase1,        # Phase 1 regression coverage
]
