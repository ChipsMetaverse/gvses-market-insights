#!/usr/bin/env python3
"""Phase 3 regression checks for backend + headless services.

These tests assume the following services are already running locally:

- FastAPI backend on http://localhost:8000
- Headless chart service on http://localhost:3100

The script exercises the Pattern Verdict API and the enhanced distributed
stats endpoint to guard against regressions introduced in Phase 3.
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import httpx

BACKEND_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
HEADLESS_URL = os.getenv("HEADLESS_BASE_URL", "http://localhost:3100")


async def submit_pattern_verdict(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Submit a verdict with full context and verify response payload."""
    pattern_id = f"regression-{uuid.uuid4().hex[:8]}"
    symbol = "AAPL"
    timeframe = "1D"

    payload = {
        "pattern_id": pattern_id,
        "verdict": "accepted",
        "symbol": symbol,
        "timeframe": timeframe,
        "operator_id": "regression-tester",
        "notes": f"Automated verdict at {datetime.now(timezone.utc).isoformat()}",
    }

    response = await client.post(
        f"{BACKEND_URL}/api/agent/pattern-verdict",
        json=payload,
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()

    # Basic sanity checks
    assert data["pattern_id"] == pattern_id
    assert data["verdict"] == "accepted"
    assert data["symbol"] == symbol
    assert data["timeframe"] == timeframe
    assert data["operator_id"] == "regression-tester"

    print("✅ Pattern verdict submission succeeded")
    return data


async def verify_pattern_history(
    client: httpx.AsyncClient,
    pattern_id: str,
    symbol: str,
    timeframe: str,
) -> None:
    """Confirm the verdict is persisted and includes full context."""
    # Small delay to allow background tasks to flush
    await asyncio.sleep(0.5)

    params = {
        "symbol": symbol,
        "timeframe": timeframe,
        "limit": 10,
    }
    response = await client.get(
        f"{BACKEND_URL}/api/agent/pattern-history",
        params=params,
        timeout=20.0,
    )
    response.raise_for_status()
    items = response.json()

    assert isinstance(items, list)
    match = next((item for item in items if item["pattern_id"] == pattern_id), None)
    assert match is not None, "Pattern verdict not found in history"
    assert match["symbol"] == symbol
    assert match["timeframe"] == timeframe

    print("✅ Pattern history reflects latest verdict")


async def verify_distributed_stats(client: httpx.AsyncClient) -> None:
    """Check headless distributed stats expose enhanced observability payload."""
    response = await client.get(f"{HEADLESS_URL}/distributed/stats", timeout=20.0)
    response.raise_for_status()
    stats = response.json()

    assert "enhanced" in stats, "Missing enhanced stats payload"
    enhanced = stats["enhanced"]

    workers = enhanced.get("workers", [])
    assert workers, "No worker metrics reported"
    worker = workers[0]
    for field in ("worker_id", "status", "cpu_usage", "memory_usage"):
        assert field in worker, f"Worker metric '{field}' missing"

    queue_stats = enhanced.get("queue_stats", {})
    assert "depth" in queue_stats and "processing" in queue_stats

    lease_stats = enhanced.get("lease_stats", {})
    assert {"active", "expired", "average_age_seconds"} <= lease_stats.keys()

    print("✅ Distributed stats include enhanced observability fields")


async def main() -> None:
    start = time.time()
    async with httpx.AsyncClient() as client:
        verdict = await submit_pattern_verdict(client)
        await verify_pattern_history(
            client,
            verdict["pattern_id"],
            verdict["symbol"],
            verdict["timeframe"],
        )
        await verify_distributed_stats(client)

    elapsed = time.time() - start
    print(f"\n🎉 Phase 3 regression checks completed in {elapsed:.1f}s")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except httpx.ConnectError as exc:
        print("❌ Unable to reach required service:", exc)
        print("   Ensure backend (8000) and headless chart service (3100) are running.")
        raise
