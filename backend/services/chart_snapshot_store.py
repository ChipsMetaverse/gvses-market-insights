"""Chart snapshot storage utilities.

Provides in-memory storage for chart snapshots and accompanying
analysis results. Designed to be modular so it can be swapped out
for Redis/Postgres in production.
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Deque, Dict, List, Optional


@dataclass
class ChartSnapshotRecord:
    """Container for a single chart snapshot."""

    symbol: str
    timeframe: str
    captured_at: datetime
    image_base64: str
    chart_commands: List[str]
    metadata: Dict[str, Any]
    vision_model: Optional[str]
    analysis: Optional[Dict[str, Any]]

    def to_public_dict(self, include_image: bool = False) -> Dict[str, Any]:
        data = asdict(self)
        if not include_image:
            data.pop("image_base64", None)
        return data


class ChartSnapshotStore:
    """Lightweight in-memory chart snapshot store with TTL enforcement."""

    def __init__(
        self,
        ttl_seconds: int = 900,
        max_snapshots_per_symbol: int = 10,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_snapshots_per_symbol = max_snapshots_per_symbol
        self._lock = asyncio.Lock()
        self._snapshots: Dict[str, Deque[ChartSnapshotRecord]] = {}

    async def store_snapshot(
        self,
        symbol: str,
        timeframe: str,
        image_base64: str,
        chart_commands: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        vision_model: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
    ) -> ChartSnapshotRecord:
        record = ChartSnapshotRecord(
            symbol=symbol.upper(),
            timeframe=timeframe,
            captured_at=datetime.utcnow(),
            image_base64=image_base64,
            chart_commands=list(chart_commands or []),
            metadata=dict(metadata or {}),
            vision_model=vision_model,
            analysis=analysis,
        )

        async with self._lock:
            queue = self._snapshots.setdefault(record.symbol, deque())
            queue.append(record)
            self._prune(queue)
            return record

    async def get_latest(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
        include_image: bool = False,
    ) -> Optional[Dict[str, Any]]:
        symbol_key = symbol.upper()
        async with self._lock:
            queue = self._snapshots.get(symbol_key)
            if not queue:
                return None

            for record in reversed(queue):
                if timeframe is None or record.timeframe == timeframe:
                    if self._is_expired(record):
                        continue
                    return record.to_public_dict(include_image=include_image)

            return None

    async def list_snapshots(
        self,
        symbol: str,
        include_image: bool = False,
    ) -> List[Dict[str, Any]]:
        symbol_key = symbol.upper()
        async with self._lock:
            queue = self._snapshots.get(symbol_key, deque())
            valid = [r for r in queue if not self._is_expired(r)]
            return [r.to_public_dict(include_image=include_image) for r in valid]

    def _prune(self, queue: Deque[ChartSnapshotRecord]) -> None:
        cutoff = datetime.utcnow() - timedelta(seconds=self.ttl_seconds)
        while queue and queue[0].captured_at < cutoff:
            queue.popleft()
        while len(queue) > self.max_snapshots_per_symbol:
            queue.popleft()

    def _is_expired(self, record: ChartSnapshotRecord) -> bool:
        return (datetime.utcnow() - record.captured_at).total_seconds() > self.ttl_seconds
