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
    analysis_error: Optional[str] = None

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
        # Phase 3: Pattern verdict storage
        self._pattern_verdicts: List[Dict[str, Any]] = []
        self._pattern_verdicts_by_pattern: Dict[str, List[Dict[str, Any]]] = {}
        # Phase 3: Pattern overlays and lifecycle state tracking
        self._pattern_overlays: Dict[str, Dict[str, Any]] = {}
        self._symbol_patterns: Dict[str, Dict[str, Dict[str, Any]]] = {}

    async def store_snapshot(
        self,
        symbol: str,
        timeframe: str,
        image_base64: str,
        chart_commands: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        vision_model: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        analysis_error: Optional[str] = None,
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
            analysis_error=analysis_error,
        )

        async with self._lock:
            queue = self._snapshots.setdefault(record.symbol, deque())
            queue.append(record)
            self._prune(queue)
            if analysis and isinstance(analysis, dict):
                await self._upsert_patterns_locked(
                    symbol=record.symbol,
                    timeframe=record.timeframe,
                    patterns=analysis.get("patterns", []),
                )
            return record

    async def attach_analysis(
        self,
        record: ChartSnapshotRecord,
        *,
        analysis: Optional[Dict[str, Any]] = None,
        analysis_error: Optional[str] = None,
        vision_model: Optional[str] = None,
    ) -> ChartSnapshotRecord:
        async with self._lock:
            if analysis is not None:
                record.analysis = analysis
            if analysis_error is not None:
                record.analysis_error = analysis_error
            if vision_model is not None:
                record.vision_model = vision_model
            record.metadata.setdefault("analysis_history", []).append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "vision_model": vision_model,
                    "success": analysis is not None,
                }
            )
            if analysis and isinstance(analysis, dict):
                await self._upsert_patterns_locked(
                    symbol=record.symbol,
                    timeframe=record.timeframe,
                    patterns=analysis.get("patterns", []),
                )
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

    # Phase 3: Pattern Verdict Management
    
    async def store_pattern_verdict(self, verdict_data: Dict[str, Any]) -> None:
        """Store a pattern verdict for audit trail."""
        async with self._lock:
            # Store in main list
            self._pattern_verdicts.append(verdict_data)
            
            # Index by pattern ID for quick lookup
            pattern_id = verdict_data["pattern_id"]
            if pattern_id not in self._pattern_verdicts_by_pattern:
                self._pattern_verdicts_by_pattern[pattern_id] = []
            self._pattern_verdicts_by_pattern[pattern_id].append(verdict_data)
            
            # Keep only last 1000 verdicts in memory (production would use DB)
            if len(self._pattern_verdicts) > 1000:
                self._pattern_verdicts = self._pattern_verdicts[-1000:]
    
    async def get_pattern_history(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        operator_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve pattern verdict history with optional filtering."""
        async with self._lock:
            results = []
            
            # Filter verdicts based on criteria
            for verdict in reversed(self._pattern_verdicts):
                if symbol and verdict.get("symbol") != symbol:
                    continue
                if timeframe and verdict.get("timeframe") != timeframe:
                    continue
                if operator_id and verdict.get("operator_id") != operator_id:
                    continue
                
                # Add pattern metadata if available from the snapshot
                verdict_copy = dict(verdict)
                if verdict_copy.get("symbol"):
                    # Try to find related snapshot for pattern metadata
                    queue = self._snapshots.get(verdict_copy["symbol"], deque())
                    for record in reversed(queue):
                        if record.analysis and "patterns" in record.analysis:
                            for pattern in record.analysis["patterns"]:
                                if pattern.get("id") == verdict_copy["pattern_id"]:
                                    verdict_copy["pattern_type"] = pattern.get("type")
                                    verdict_copy["confidence"] = pattern.get("confidence")
                                    break
                
                results.append(verdict_copy)
                
                if len(results) >= limit:
                    break

            return results

    async def _upsert_patterns_locked(
        self,
        *,
        symbol: str,
        timeframe: str,
        patterns: List[Dict[str, Any]],
    ) -> None:
        """Store or update pattern overlays for a symbol/timeframe."""
        symbol = symbol.upper()
        timeframe = timeframe.upper()

        if not patterns:
            return

        symbol_map = self._symbol_patterns.setdefault(symbol, {})
        timeframe_map = symbol_map.setdefault(timeframe, {})

        for pattern in patterns:
            pattern_id = pattern.get("id") or pattern.get("pattern_id")
            if not pattern_id:
                continue
            overlay = dict(pattern)
            overlay["id"] = pattern_id
            overlay.setdefault("status", "pending")
            overlay.setdefault("updated_at", datetime.utcnow().isoformat())
            overlay.setdefault("symbol", symbol)
            overlay.setdefault("timeframe", timeframe)
            timeframe_map[pattern_id] = overlay
            self._pattern_overlays[pattern_id] = {
                **overlay,
                "symbol": symbol,
                "timeframe": timeframe,
            }

    async def get_pattern_overlays(
        self,
        symbol: str,
        timeframe: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        symbol = symbol.upper()
        async with self._lock:
            symbol_map = self._symbol_patterns.get(symbol, {})
            if timeframe:
                overlays = symbol_map.get(timeframe.upper(), {})
                return list(overlays.values())
            all_overlays: List[Dict[str, Any]] = []
            for timeframe_map in symbol_map.values():
                all_overlays.extend(timeframe_map.values())
            return all_overlays

    async def update_pattern_state(
        self,
        pattern_id: str,
        *,
        status: str,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        async with self._lock:
            overlay = self._pattern_overlays.get(pattern_id)
            if not overlay:
                # Attempt to resolve from supplied context
                if symbol and timeframe:
                    symbol_map = self._symbol_patterns.get(symbol.upper(), {})
                    timeframe_map = symbol_map.get(timeframe.upper(), {})
                    overlay = timeframe_map.get(pattern_id)
            if not overlay:
                overlay = {
                    "id": pattern_id,
                    "status": status,
                    "symbol": symbol.upper() if symbol else None,
                    "timeframe": timeframe.upper() if timeframe else None,
                    "metadata": {},
                }
            overlay["status"] = status
            overlay["updated_at"] = datetime.utcnow().isoformat()
            if metadata:
                overlay.setdefault("metadata", {}).update(metadata)

            resolved_symbol = overlay.get("symbol") or (symbol.upper() if symbol else None)
            resolved_timeframe = overlay.get("timeframe") or (timeframe.upper() if timeframe else None)
            if resolved_symbol and resolved_timeframe:
                symbol_map = self._symbol_patterns.setdefault(resolved_symbol, {})
                timeframe_map = symbol_map.setdefault(resolved_timeframe, {})
                timeframe_map[pattern_id] = overlay

            self._pattern_overlays[pattern_id] = overlay
            return dict(overlay)

    async def remove_pattern_overlay(self, pattern_id: str) -> None:
        async with self._lock:
            overlay = self._pattern_overlays.pop(pattern_id, None)
            if not overlay:
                return
            symbol = overlay.get("symbol")
            timeframe = overlay.get("timeframe")
            if not symbol or not timeframe:
                return
            symbol_map = self._symbol_patterns.get(symbol, {})
            timeframe_map = symbol_map.get(timeframe, {})
            timeframe_map.pop(pattern_id, None)

    async def append_chart_commands(
        self,
        *,
        symbol: str,
        timeframe: str,
        commands: List[str],
    ) -> Optional[List[str]]:
        if not commands:
            return None

        symbol_key = symbol.upper()
        timeframe_key = timeframe.upper()

        async with self._lock:
            queue = self._snapshots.get(symbol_key)
            if not queue:
                return None
            for record in reversed(queue):
                if record.timeframe == timeframe_key:
                    existing = record.chart_commands or []
                    merged = existing + [cmd for cmd in commands if cmd not in existing]
                    record.chart_commands = merged
                    record.metadata.setdefault("chart_history", []).append(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "commands": commands,
                            "source": "pattern_verdict",
                        }
                    )
                    return merged
        return None
