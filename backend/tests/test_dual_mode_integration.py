import os
from typing import Generator

import pytest

from services import agent_orchestrator as orchestrator_module


@pytest.fixture(autouse=True)
def reset_orchestrator() -> Generator[None, None, None]:
    """Ensure each test gets a fresh orchestrator instance."""
    original_instance = orchestrator_module._orchestrator_instance  # type: ignore[attr-defined]
    orchestrator_module._orchestrator_instance = None  # type: ignore[attr-defined]
    yield
    orchestrator_module._orchestrator_instance = original_instance  # type: ignore[attr-defined]


async def _process_query(sample_query: str) -> dict:
    orchestrator = orchestrator_module.get_orchestrator()
    return await orchestrator.process_query(sample_query)


@pytest.mark.asyncio
async def test_hybrid_mode_keeps_legacy_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy-first (hybrid) mode should continue emitting legacy commands."""
    monkeypatch.setenv("PREFER_STRUCTURED_CHART_COMMANDS", "false")
    monkeypatch.setenv("ENABLE_STRUCTURED_CHART_OBJECTS", "false")
    orchestrator_module._orchestrator_instance = None  # type: ignore[attr-defined]

    result = await _process_query("show me TSLA")

    assert "chart_commands" in result and result["chart_commands"], "Legacy commands missing in hybrid mode"
    assert "chart_commands_structured" in result and result["chart_commands_structured"], (
        "Structured commands should still be present in hybrid mode"
    )
    assert "chart_objects" not in result, "chart_objects should not be exposed when structured objects disabled"


@pytest.mark.asyncio
async def test_structured_first_mode_prefers_structured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Structured-first mode should expose chart_objects and omit legacy list."""
    monkeypatch.setenv("PREFER_STRUCTURED_CHART_COMMANDS", "true")
    monkeypatch.setenv("ENABLE_STRUCTURED_CHART_OBJECTS", "true")
    orchestrator_module._orchestrator_instance = None  # type: ignore[attr-defined]

    result = await _process_query("show me AAPL")

    assert "chart_commands_structured" in result and result["chart_commands_structured"], (
        "Structured commands missing when prefer flag enabled"
    )
    assert "chart_objects" in result and result["chart_objects"], "chart_objects payload missing"
    assert "chart_commands" not in result, "Legacy commands should be suppressed in structured-first mode"


@pytest.mark.asyncio
async def test_structured_objects_disabled_hides_field(monkeypatch: pytest.MonkeyPatch) -> None:
    """ENABLE_STRUCTURED_CHART_OBJECTS flag should toggle chart_objects output."""
    monkeypatch.setenv("ENABLE_STRUCTURED_CHART_OBJECTS", "false")
    monkeypatch.setenv("PREFER_STRUCTURED_CHART_COMMANDS", "true")
    orchestrator_module._orchestrator_instance = None  # type: ignore[attr-defined]

    result = await _process_query("load NVDA chart")

    assert "chart_objects" not in result, "chart_objects should be absent when flag disabled"
    assert "chart_commands_structured" in result and result["chart_commands_structured"], (
        "Structured commands should still be emitted even without chart_objects"
    )
