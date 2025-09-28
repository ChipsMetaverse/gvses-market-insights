from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternState:
    """Track lifecycle metadata for a chart pattern."""

    pattern_id: str
    status: str = "pending"
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0
    bias: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    misses: int = 0


class PatternLifecycleManager:
    """Manage pattern lifecycle transitions and derived chart commands."""

    def __init__(
        self,
        *,
        confirm_threshold: float = 75.0,
        max_misses: int = 2,
    ) -> None:
        self.confirm_threshold = confirm_threshold
        self.max_misses = max_misses
        self._states: Dict[Tuple[str, str], Dict[str, PatternState]] = {}

    def update(
        self,
        *,
        symbol: str,
        timeframe: str,
        analysis: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Update lifecycle state based on latest analysis output."""

        if not analysis or not isinstance(analysis, dict):
            return {
                "states": self._current_states(symbol, timeframe),
                "chart_commands": [],
            }

        patterns = analysis.get("patterns") or []
        key = (symbol.upper(), timeframe)
        states = self._states.setdefault(key, {})
        commands: List[str] = []
        summary: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()

        for pattern in patterns:
            pattern_id = pattern.get("pattern_id") or self._derive_pattern_id(pattern)
            if not pattern_id:
                continue

            seen_ids.add(pattern_id)
            existing_state = states.get(pattern_id)
            if not existing_state:
                existing_state = PatternState(pattern_id=pattern_id)
                states[pattern_id] = existing_state
                commands.append(f"ANNOTATE:PATTERN:{pattern_id}:pending")

            transitions = self._apply_pattern_update(existing_state, pattern)
            if transitions:
                commands.extend(transitions)

            summary.append(self._state_summary(existing_state))

        # Handle patterns that disappeared (potential invalidation)
        for pattern_id, state in list(states.items()):
            if pattern_id in seen_ids:
                continue

            state.misses += 1
            if state.status in {"completed", "invalidated"}:
                continue

            if state.misses >= self.max_misses:
                state.status = "invalidated"
                state.last_updated = datetime.utcnow()
                commands.append(f"CLEAR:PATTERN:{pattern_id}")
                commands.append(f"ANNOTATE:PATTERN:{pattern_id}:invalidated")
            summary.append(self._state_summary(state))

        # Deduplicate commands while preserving order
        deduped_commands: List[str] = []
        seen: set[str] = set()
        for cmd in commands:
            if cmd in seen:
                continue
            deduped_commands.append(cmd)
            seen.add(cmd)

        return {
            "states": summary,
            "chart_commands": deduped_commands,
        }

    def _apply_pattern_update(self, state: PatternState, pattern: Dict[str, Any]) -> List[str]:
        commands: List[str] = []
        state.last_updated = datetime.utcnow()
        state.confidence = float(pattern.get("confidence") or 0)
        state.bias = pattern.get("bias")
        state.metadata = pattern
        state.misses = 0

        previous_status = state.status
        next_status = self._determine_status(state, pattern)
        state.status = next_status

        if previous_status != next_status:
            commands.extend(self._commands_for_transition(state.pattern_id, next_status, pattern))
        elif next_status == "confirmed":
            # Emit level commands on refresh to ensure chart sync
            commands.extend(self._draw_level_commands(state.pattern_id, pattern))

        return commands

    def _determine_status(self, state: PatternState, pattern: Dict[str, Any]) -> str:
        status = state.status or "pending"
        confidence = state.confidence
        action = (pattern.get("recommended_action") or "").lower()

        if status == "pending":
            if confidence >= self.confirm_threshold or action in {"consider_entry", "take_profit"}:
                return "confirmed"
            return "pending"

        if status == "confirmed":
            if action == "take_profit":
                return "completed"
            return "confirmed"

        return status

    def _commands_for_transition(self, pattern_id: str, status: str, pattern: Dict[str, Any]) -> List[str]:
        commands: List[str] = [f"ANNOTATE:PATTERN:{pattern_id}:{status}"]

        if status == "confirmed":
            commands.extend(self._draw_level_commands(pattern_id, pattern))
        elif status in {"completed", "invalidated"}:
            commands.append(f"CLEAR:PATTERN:{pattern_id}")

        return commands

    def _draw_level_commands(self, pattern_id: str, pattern: Dict[str, Any]) -> List[str]:
        commands: List[str] = []
        levels = pattern.get("key_levels") or {}

        for label, values in levels.items():
            if not isinstance(values, (list, tuple)):
                values = [values]
            for value in values:
                try:
                    price = float(value)
                except (TypeError, ValueError):
                    continue
                level_type = label.lower()
                if level_type not in {"support", "resistance", "pivot", "target"}:
                    level_type = "pivot"
                commands.append(f"DRAW:LEVEL:{pattern_id}:{level_type}:{price:.4f}")

        targets = pattern.get("targets") or []
        for target in targets:
            try:
                price = float(target)
            except (TypeError, ValueError):
                continue
            commands.append(f"DRAW:TARGET:{pattern_id}:{price:.4f}")

        return commands

    def _derive_pattern_id(self, pattern: Dict[str, Any]) -> Optional[str]:
        pattern_type = pattern.get("category") or pattern.get("pattern") or pattern.get("type")
        summary = pattern.get("summary") or pattern.get("description") or ""
        if not pattern_type:
            return None
        base = pattern_type.replace(" ", "_").lower()
        suffix = hash(f"{pattern_type}:{summary}") & 0xFFFF
        return f"{base}_{suffix:04x}"

    def _state_summary(self, state: PatternState) -> Dict[str, Any]:
        return {
            "pattern_id": state.pattern_id,
            "status": state.status,
            "confidence": state.confidence,
            "bias": state.bias,
            "first_seen": state.first_seen.isoformat(),
            "last_updated": state.last_updated.isoformat(),
        }

    def _current_states(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        states = self._states.get((symbol.upper(), timeframe))
        if not states:
            return []
        return [self._state_summary(state) for state in states.values()]
