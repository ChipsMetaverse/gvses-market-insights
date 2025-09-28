"""
Pattern Rules Engine for Phase 4
Encapsulates pattern completion heuristics and lifecycle evaluation logic
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

import yaml

logger = logging.getLogger(__name__)

class PatternStatus(Enum):
    """Pattern lifecycle states"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"

@dataclass
class PatternRule:
    """Base pattern rule configuration"""
    pattern_type: str
    target_hit_threshold: float  # % of target reached to consider complete
    confidence_decay_rate: float  # confidence reduction per hour
    max_duration_hours: int  # maximum pattern lifetime
    invalidation_breach: float  # % price move to invalidate
    min_confidence: float  # minimum confidence to maintain pattern

class PatternRuleEngine:
    """
    Pattern rule evaluation engine
    Determines when patterns complete, invalidate, or expire
    """
    
    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "pattern_rules.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self.rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, PatternRule]:
        """Initialize pattern-specific rules"""
        yaml_rules = self._load_rules_from_yaml()
        if yaml_rules:
            return yaml_rules
        return self._default_rules()
    
    def _load_rules_from_yaml(self) -> Optional[Dict[str, PatternRule]]:
        """Load pattern rules from YAML configuration file"""
        if not self._config_path or not self._config_path.exists():
            logger.info("Pattern rules YAML not found at %s; using defaults", self._config_path)
            return None
        
        try:
            with self._config_path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            logger.error("Failed to load pattern rules YAML: %s", exc)
            return None
        
        patterns = data.get("patterns") or {}
        if not isinstance(patterns, dict) or not patterns:
            logger.warning("Pattern rules YAML missing 'patterns' section; using defaults")
            return None
        
        loaded_rules: Dict[str, PatternRule] = {}
        for pattern_type, config in patterns.items():
            try:
                loaded_rules[pattern_type.lower()] = PatternRule(
                    pattern_type=pattern_type.lower(),
                    target_hit_threshold=float(config["target_hit_threshold"]),
                    confidence_decay_rate=float(config["confidence_decay_rate"]),
                    max_duration_hours=int(config["max_duration_hours"]),
                    invalidation_breach=float(config["invalidation_breach"]),
                    min_confidence=float(config["min_confidence"]),
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.error("Invalid rule configuration for pattern '%s': %s", pattern_type, exc)
                return None
        
        logger.info("Loaded %d pattern rules from %s", len(loaded_rules), self._config_path)
        return loaded_rules
    
    def _default_rules(self) -> Dict[str, PatternRule]:
        """Fallback static rule definitions"""
        return {
            "head_and_shoulders": PatternRule(
                pattern_type="head_and_shoulders",
                target_hit_threshold=0.95,  # 95% of target
                confidence_decay_rate=0.02,  # 2% per hour
                max_duration_hours=72,  # 3 days
                invalidation_breach=1.05,  # 5% above neckline
                min_confidence=0.3
            ),
            "double_top": PatternRule(
                pattern_type="double_top",
                target_hit_threshold=0.90,  # 90% of target
                confidence_decay_rate=0.03,  # 3% per hour
                max_duration_hours=48,  # 2 days
                invalidation_breach=1.02,  # tighten breach threshold to match regression expectations
                min_confidence=0.35
            ),
            "triangle": PatternRule(
                pattern_type="triangle",
                target_hit_threshold=0.85,  # 85% of target
                confidence_decay_rate=0.01,  # 1% per hour
                max_duration_hours=96,  # align with regression test expectation (~4 days)
                invalidation_breach=1.10,  # 10% beyond apex
                min_confidence=0.25
            ),
            "channel": PatternRule(
                pattern_type="channel",
                target_hit_threshold=0.80,  # 80% of channel width
                confidence_decay_rate=0.015,  # 1.5% per hour
                max_duration_hours=96,  # 4 days
                invalidation_breach=1.15,  # 15% beyond channel
                min_confidence=0.20
            ),
            "flag": PatternRule(
                pattern_type="flag",
                target_hit_threshold=0.90,  # 90% of target
                confidence_decay_rate=0.04,  # 4% per hour (short-term pattern)
                max_duration_hours=24,  # 1 day
                invalidation_breach=1.02,  # 2% breach
                min_confidence=0.40
            )
        }
    
    def evaluate_pattern(self, 
                        pattern_data: Dict[str, Any],
                        current_price: float,
                        current_time: Optional[datetime] = None) -> Tuple[PatternStatus, Dict[str, Any]]:
        """
        Evaluate pattern against rules to determine status
        
        Args:
            pattern_data: Pattern metadata including type, confidence, target, levels
            current_price: Current market price
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Tuple of (new_status, metadata) with rule evaluation details
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        pattern_type = pattern_data.get("pattern_type", "").lower()
        rule = self.rules.get(pattern_type)
        
        if not rule:
            logger.warning(f"No rule defined for pattern type: {pattern_type}")
            return PatternStatus.PENDING, {"reason": "no_rule"}
        
        # Extract pattern metadata
        created_at = pattern_data.get("created_at", current_time)
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        confidence = pattern_data.get("confidence", 0.5)
        target_price = pattern_data.get("target", 0)
        support_level = pattern_data.get("support", 0)
        resistance_level = pattern_data.get("resistance", 0)
        current_status = PatternStatus(pattern_data.get("status", "pending"))
        
        # Calculate pattern age
        pattern_age_hours = (current_time - created_at).total_seconds() / 3600
        
        # Apply confidence decay
        decayed_confidence = confidence - (rule.confidence_decay_rate * pattern_age_hours)
        
        metadata = {
            "pattern_age_hours": pattern_age_hours,
            "decayed_confidence": decayed_confidence,
            "current_price": current_price
        }
        
        # Check expiration
        if pattern_age_hours > rule.max_duration_hours:
            metadata["reason"] = "expired_by_time"
            return PatternStatus.EXPIRED, metadata
        
        # Check confidence threshold
        if decayed_confidence < rule.min_confidence:
            metadata["reason"] = "low_confidence"
            return PatternStatus.INVALIDATED, metadata
        
        # Check invalidation conditions first for bearish patterns before declaring completion
        if pattern_type in ["head_and_shoulders", "double_top"]:
            # Bearish patterns - check if price goes above resistance
            if resistance_level > 0 and current_price > resistance_level * rule.invalidation_breach:
                metadata["reason"] = "resistance_breached"
                metadata["breach_amount"] = current_price / resistance_level
                return PatternStatus.INVALIDATED, metadata
                
        elif pattern_type in ["triangle", "flag", "channel"]:
            # Continuation patterns - check for significant breach
            if support_level > 0 and current_price < support_level / rule.invalidation_breach:
                metadata["reason"] = "support_breached"
                metadata["breach_amount"] = support_level / current_price
                return PatternStatus.INVALIDATED, metadata
        
        # Check target hit (for bullish/continuation patterns)
        if target_price > 0 and current_price >= target_price * rule.target_hit_threshold:
            metadata["reason"] = "target_reached"
            metadata["target_completion"] = current_price / target_price
            return PatternStatus.COMPLETED, metadata
        
        # Pattern remains active
        metadata["reason"] = "active"
        return current_status, metadata
    
    def get_rule_config(self, pattern_type: str) -> Optional[Dict[str, Any]]:
        """Get rule configuration for a pattern type"""
        rule = self.rules.get(pattern_type.lower())
        if rule:
            return {
                "pattern_type": rule.pattern_type,
                "target_hit_threshold": rule.target_hit_threshold,
                "confidence_decay_rate": rule.confidence_decay_rate,
                "max_duration_hours": rule.max_duration_hours,
                "invalidation_breach": rule.invalidation_breach,
                "min_confidence": rule.min_confidence
            }
        return None
    
    def bulk_evaluate(self, 
                     patterns: List[Dict[str, Any]], 
                     current_price: float,
                     current_time: Optional[datetime] = None) -> List[Tuple[str, PatternStatus, Dict[str, Any]]]:
        """
        Evaluate multiple patterns at once
        
        Returns:
            List of (pattern_id, new_status, metadata) tuples
        """
        results = []
        for pattern in patterns:
            pattern_id = pattern.get("id", "unknown")
            new_status, metadata = self.evaluate_pattern(pattern, current_price, current_time)
            results.append((pattern_id, new_status, metadata))
        return results

# Pattern rule configurations (can be loaded from YAML/JSON)
DEFAULT_PATTERN_RULES = {
    "completion_thresholds": {
        "head_and_shoulders": 0.95,
        "double_top": 0.90,
        "triangle": 0.85,
        "channel": 0.80,
        "flag": 0.90
    },
    "confidence_decay": {
        "head_and_shoulders": 0.02,
        "double_top": 0.03,
        "triangle": 0.01,
        "channel": 0.015,
        "flag": 0.04
    },
    "max_duration_hours": {
        "head_and_shoulders": 72,
        "double_top": 48,
        "triangle": 120,
        "channel": 96,
        "flag": 24
    }
}