"""Request telemetry utilities.

Provides helpers for gathering user-centric request metadata so we can log
client IP, user-agent, and session attribution in a consistent format.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from services.database_service import get_database_service

from fastapi import Request


@dataclass
class RequestTelemetry:
    """Telemetry snapshot captured from an incoming HTTP request."""

    request_id: str
    path: str
    method: str
    client_ip: Optional[str]
    forwarded_for: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    user_id: Optional[str]
    duration_ms: Optional[float] = None
    cost_summary: Optional[Dict[str, Any]] = None

    def for_logging(self, **overrides: Any) -> Dict[str, Any]:
        """Return a dict suitable for passing to logger.extra."""
        payload = asdict(self)
        payload.update(overrides)
        return payload

    def with_duration(self, duration_ms: float) -> "RequestTelemetry":
        """Return a copy of telemetry enriched with request duration."""
        clone = RequestTelemetry(**asdict(self))
        clone.duration_ms = round(duration_ms, 3)
        return clone

    def with_cost_summary(self, summary: Optional[Dict[str, Any]]) -> "RequestTelemetry":
        """Return telemetry enriched with cost summary data."""
        clone = RequestTelemetry(**asdict(self))
        clone.cost_summary = summary
        return clone


def build_request_telemetry(
    request: Request,
    request_id: str,
    *,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> RequestTelemetry:
    """Capture metadata for the current request.

    Args:
        request: FastAPI request object
        request_id: Correlated request ID
        session_id: Optional session identifier supplied by client
        user_id: Optional application user identifier

    Returns:
        RequestTelemetry containing request metadata.
    """
    # FastAPI's Request exposes client host/port tuple via request.client
    client_ip: Optional[str] = None
    if request.client:
        client_ip = request.client.host

    forwarded_for = request.headers.get("x-forwarded-for")
    user_agent = request.headers.get("user-agent")

    return RequestTelemetry(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        client_ip=client_ip,
        forwarded_for=forwarded_for,
        user_agent=user_agent,
        session_id=session_id,
        user_id=user_id,
    )


async def persist_request_log(telemetry: RequestTelemetry, extra: Dict[str, Any]) -> None:
    """Persist a request log entry for later analytics."""
    try:
        db_service = get_database_service()
    except Exception:
        # Database not configured; skip persistence
        return

    payload = telemetry.for_logging(**extra)

    entry = {
        "request_id": telemetry.request_id,
        "path": telemetry.path,
        "method": telemetry.method,
        "client_ip": telemetry.client_ip,
        "forwarded_for": telemetry.forwarded_for,
        "user_agent": telemetry.user_agent,
        "session_id": telemetry.session_id,
        "user_id": telemetry.user_id,
        "duration_ms": telemetry.duration_ms,
        "cost_summary": telemetry.cost_summary,
        "event": payload.get("event"),
        "query": payload.get("query"),
        "extra": extra,
    }

    try:
        await db_service.log_request_event(
            event=payload.get("event") or "agent_request",
            telemetry=entry,
            metadata=extra,
        )
    except Exception:
        # Logging failures should never break request handling
        return
