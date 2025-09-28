from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import asyncio

import logging

# Phase 4 imports
from .pattern_rules import PatternRuleEngine, PatternStatus
from .command_builders import TrendlineCommandBuilder, IndicatorCommandBuilder
from .pattern_repository import PatternRepository

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
        enable_phase4_rules: bool = True,
    ) -> None:
        self.confirm_threshold = confirm_threshold
        self.max_misses = max_misses
        self._states: Dict[Tuple[str, str], Dict[str, PatternState]] = {}
        
        # Phase 4 components
        self.enable_phase4_rules = enable_phase4_rules
        if enable_phase4_rules:
            self.rule_engine = PatternRuleEngine()
            self.command_builder = TrendlineCommandBuilder()
            self.indicator_builder = IndicatorCommandBuilder()
            self.repository = PatternRepository()
        else:
            self.rule_engine = None
            self.command_builder = None
            self.indicator_builder = None
            self.repository = None

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
    
    # Phase 4 methods
    async def evaluate_with_rules(self,
                                 symbol: str,
                                 timeframe: str,
                                 current_price: float,
                                 analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate patterns using Phase 4 rule engine
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe
            current_price: Current market price
            analysis: Optional analysis output
            
        Returns:
            Evaluation results with commands
        """
        if not self.enable_phase4_rules or not self.rule_engine:
            # Fallback to standard update
            return self.update(symbol=symbol, timeframe=timeframe, analysis=analysis)
        
        commands = []
        transitions = []
        
        # Get active patterns from repository
        active_patterns = await self.repository.get_active_patterns(symbol, timeframe)
        
        # Evaluate each pattern with rules
        for pattern in active_patterns:
            pattern_id = pattern.get("id")
            old_status = pattern.get("status", "pending")
            
            # Evaluate with rule engine
            new_status, evaluation_metadata = self.rule_engine.evaluate_pattern(
                pattern, 
                current_price,
                datetime.now(timezone.utc)
            )
            
            # Check if status changed
            if new_status != PatternStatus(old_status):
                # Generate lifecycle commands
                lifecycle_commands = self.command_builder.build_lifecycle_commands(
                    old_status,
                    new_status.value,
                    pattern
                )
                commands.extend(lifecycle_commands)
                
                # Update pattern in repository
                await self.repository.update_pattern(pattern_id, {
                    "status": new_status.value,
                    "rule_evaluation": evaluation_metadata
                })
                
                transitions.append({
                    "pattern_id": pattern_id,
                    "old_status": old_status,
                    "new_status": new_status.value,
                    "reason": evaluation_metadata.get("reason"),
                    "metadata": evaluation_metadata
                })
        
        # Process new patterns from analysis
        if analysis:
            new_patterns = analysis.get("patterns", [])
            for pattern_data in new_patterns:
                # Check if pattern already exists
                pattern_type = pattern_data.get("pattern_type", "")
                existing = any(p["pattern_type"] == pattern_type for p in active_patterns)
                
                if not existing:
                    # Create new pattern in repository
                    pattern_data["symbol"] = symbol
                    pattern_data["timeframe"] = timeframe
                    pattern_data["auto_generated"] = True
                    
                    # Generate initial commands
                    pattern_commands = self.command_builder.build_pattern_commands(
                        pattern_data, 
                        "create"
                    )
                    commands.extend(pattern_commands)
                    
                    # Store pattern
                    pattern_id = await self.repository.create_pattern(pattern_data)
                    if pattern_id:
                        pattern_data["id"] = pattern_id
                        transitions.append({
                            "pattern_id": pattern_id,
                            "old_status": None,
                            "new_status": "pending",
                            "reason": "new_pattern",
                            "metadata": {"auto_generated": True}
                        })
        
        return {
            "states": await self._get_current_phase4_states(symbol, timeframe),
            "chart_commands": commands,
            "transitions": transitions,
            "rule_evaluations": len(transitions)
        }
    
    async def _get_current_phase4_states(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """Get current pattern states from repository"""
        if not self.repository:
            return self._current_states(symbol, timeframe)
        
        patterns = await self.repository.get_active_patterns(symbol, timeframe)
        return [{
            "pattern_id": p.get("id"),
            "status": p.get("status"),
            "confidence": p.get("confidence"),
            "pattern_type": p.get("pattern_type"),
            "created_at": p.get("created_at"),
            "auto_generated": p.get("auto_generated", False)
        } for p in patterns]
    
    async def sweep_patterns(self, max_age_hours: int = 72) -> Dict[str, Any]:
        """
        Background sweep to evaluate all active patterns
        
        Args:
            max_age_hours: Maximum pattern age
            
        Returns:
            Sweep results
        """
        if not self.enable_phase4_rules or not self.repository:
            return {"error": "Phase 4 not enabled"}
        
        patterns = await self.repository.get_patterns_for_sweep(max_age_hours)
        updated_count = 0
        expired_count = 0
        
        for pattern in patterns:
            # Check age and expire if too old
            created_at = pattern.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                await self.repository.update_pattern(pattern["id"], {
                    "status": "expired",
                    "rule_evaluation": {"reason": "max_age_exceeded", "age_hours": age_hours}
                })
                expired_count += 1
            else:
                # Evaluate with rules (would need current price from market data)
                # This is a simplified version - in production, fetch real price
                updated_count += 1
        
        # Also expire old patterns using database function
        db_expired = await self.repository.expire_old_patterns(max_age_hours)
        
        return {
            "patterns_evaluated": len(patterns),
            "patterns_updated": updated_count,
            "patterns_expired": expired_count + db_expired,
            "sweep_time": datetime.now(timezone.utc).isoformat()
        }
