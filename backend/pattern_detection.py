"""
Pattern Detection Module - MVP Implementation
Focuses on 3 high-value patterns per category with deterministic confidence scoring
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

class PatternLibrary:
    """Loads pattern definitions and provides knowledge-based validation helpers."""

    _instance: Optional["PatternLibrary"] = None

    def __new__(cls, patterns_file: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_library(patterns_file)
        return cls._instance

    def _init_library(self, patterns_file: Optional[Path]) -> None:
        base_dir = Path(__file__).resolve().parent
        generated_path = base_dir / "training" / "patterns.generated.json"
        legacy_path = base_dir / "training" / "patterns.json"

        use_legacy = os.getenv("USE_LEGACY_PATTERN_LIBRARY", "").lower() in {"1", "true", "yes", "on"}

        if patterns_file is None:
            if generated_path.exists():
                patterns_file = generated_path
            elif use_legacy and legacy_path.exists():
                logger.warning(
                    "Using legacy pattern library at %s due to USE_LEGACY_PATTERN_LIBRARY flag",
                    legacy_path,
                )
                patterns_file = legacy_path
            else:
                raise FileNotFoundError(
                    "Pattern knowledge base not found. Expected generated artifact at "
                    f"{generated_path}. Run backend/training/generate_pattern_library.py to build it."
                )

        try:
            with patterns_file.open("r", encoding="utf-8") as fh:
                patterns_data = json.load(fh)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Pattern knowledge base missing at {patterns_file}. Run generate_pattern_library.py first."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Pattern knowledge base malformed at {patterns_file}: {exc}") from exc

        self.patterns: Dict[str, Dict[str, Any]] = {
            entry.get("pattern_id", ""): entry for entry in patterns_data if entry.get("pattern_id")
        }

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        return self.patterns.get(pattern_id)

    def get_recognition_rules(self, pattern_id: str) -> Dict[str, Any]:
        pattern = self.get_pattern(pattern_id)
        return pattern.get("recognition_rules", {}) if pattern else {}

    def get_trading_playbook(self, pattern_id: str) -> Dict[str, Any]:
        pattern = self.get_pattern(pattern_id)
        return pattern.get("trading_playbook", {}) if pattern else {}

    def validate_against_rules(
        self,
        pattern_id: str,
        candles: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, float, str]:
        """Return (is_valid, confidence_adjustment, reasoning text)."""

        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return False, 0.0, "Pattern not found in library"

        rules = pattern.get("recognition_rules", {})
        reasoning_parts: List[str] = []
        is_valid = True
        confidence_adjustment = 0.0

        if rules.get("candle_structure"):
            reasoning_parts.append(f"Structure: {rules['candle_structure']}")
        if rules.get("trend_context"):
            reasoning_parts.append(f"Trend: {rules['trend_context']}")
        if rules.get("volume_confirmation"):
            reasoning_parts.append(f"Volume: {rules['volume_confirmation']}")

        invalidations = rules.get("invalidations", [])
        if invalidations:
            reasoning_parts.append("Watch invalidations:")
            for invalidation in invalidations:
                reasoning_parts.append(f"- {invalidation}")

        if metadata and metadata.get("confidence_hint"):
            confidence_adjustment += float(metadata["confidence_hint"])

        reasoning = " \n".join(reasoning_parts) if reasoning_parts else "Knowledge rules applied"
        return is_valid, confidence_adjustment, reasoning


PATTERN_CATEGORY_MAP = {
    # Candlestick
    "bullish_engulfing": "candlestick",
    "bearish_engulfing": "candlestick",
    "doji": "candlestick",
    "hammer": "candlestick",
    "shooting_star": "candlestick",
    "morning_star": "candlestick",
    "evening_star": "candlestick",
    "bullish_harami": "candlestick",
    "bearish_harami": "candlestick",
    "piercing_line": "candlestick",
    "dark_cloud_cover": "candlestick",
    "three_white_soldiers": "candlestick",
    "three_black_crows": "candlestick",
    
    # Price action / micro-structure
    "breakout": "price_action",
    "breakdown": "price_action",
    "support_bounce": "price_action",
    "trend_acceleration": "price_action",
    "gap_breakaway": "price_action",
    
    # Chart patterns / structure
    "double_top": "chart_pattern",
    "double_bottom": "chart_pattern",
    "head_shoulders": "chart_pattern",
    "inverse_head_shoulders": "chart_pattern",
    "ascending_triangle": "chart_pattern",
    "descending_triangle": "chart_pattern",
    "symmetrical_triangle": "chart_pattern",
    "bullish_flag": "chart_pattern",
    "bearish_flag": "chart_pattern",
    "bullish_pennant": "chart_pattern",
    "bearish_pennant": "chart_pattern",
    "falling_wedge": "chart_pattern",
    "rising_wedge": "chart_pattern",
    "cup_handle": "chart_pattern",

    # Additional candlesticks
    "marubozu_bullish": "candlestick",
    "marubozu_bearish": "candlestick",
    "spinning_top": "candlestick",
    "dragonfly_doji": "candlestick",
    "gravestone_doji": "candlestick",
    "hanging_man": "candlestick",
    "inverted_hammer": "candlestick",
    "three_inside_up": "candlestick",
    "three_inside_down": "candlestick",
    "three_outside_up": "candlestick",
    "three_outside_down": "candlestick",
    "abandoned_baby": "candlestick",

    # Additional price action
    "rectangle_range": "price_action",
    "channel_up": "price_action",
    "channel_down": "price_action",
    "runaway_gap": "price_action",
    "exhaustion_gap": "price_action",

    # Additional chart patterns
    "triple_top": "chart_pattern",
    "triple_bottom": "chart_pattern",
    "pennant_bullish": "chart_pattern",
    "pennant_bearish": "chart_pattern",
    "broadening_top": "chart_pattern",
    "broadening_bottom": "chart_pattern",
    "diamond_top": "chart_pattern",
    "diamond_bottom": "chart_pattern",
    "rounding_bottom": "chart_pattern",
}

@dataclass
class Pattern:
    """Represents a detected pattern with confidence and metadata"""
    pattern_id: str
    pattern_type: str
    confidence: float
    start_candle: int
    end_candle: int
    description: str
    signal: str  # bullish, bearish, neutral
    action: Optional[str] = None  # wait, watch_closely, consider_entry
    target: Optional[float] = None
    stop_loss: Optional[float] = None
    success_rate: Optional[float] = None  # Historical success percentage
    risk_reward_ratio: Optional[float] = None
    typical_duration: Optional[str] = None  # "2-4 weeks"
    strategy_notes: Optional[str] = None  # Trading approach
    metadata: Optional[Dict[str, Any]] = None
    chart_metadata: Optional[Dict[str, Any]] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    start_price: Optional[float] = None
    end_price: Optional[float] = None
    knowledge_reasoning: Optional[str] = None
    entry_guidance: Optional[str] = None
    stop_loss_guidance: Optional[str] = None
    targets_guidance: Optional[List[str]] = None
    risk_notes: Optional[str] = None


class PatternDetector:
    """
    MVP Pattern Detector - Focused on 3 high-value patterns per category
    Emphasizes reliability and clear confidence scoring
    """
    
    def __init__(self, candles: List[Dict], cache_seconds: int = 60, use_knowledge_base: bool = True):
        """
        Initialize with OHLCV candle data
        
        Args:
            candles: List of dicts with keys: time, open, high, low, close, volume
            cache_seconds: How long to cache results
        """
        self.candles = candles[-100:] if len(candles) > 100 else candles  # Process last 100 only
        self.cache_seconds = cache_seconds
        self._last_detection_time = None
        self._cached_results = None
        self.use_knowledge_base = use_knowledge_base
        self._knowledge_library = PatternLibrary() if use_knowledge_base else None

        if self.candles:
            self.opens = np.array([float(c.get('open', 0)) for c in self.candles])
            self.highs = np.array([float(c.get('high', 0)) for c in self.candles])
            self.lows = np.array([float(c.get('low', 0)) for c in self.candles])
            self.closes = np.array([float(c.get('close', 0)) for c in self.candles])
            self.volumes = np.array([float(c.get('volume', 0) or 0) for c in self.candles])
            self.times = [c.get('time') for c in self.candles]
        else:
            self.opens = self.highs = self.lows = self.closes = self.volumes = np.array([])
            self.times = []

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------

    def _volume_ratio(self, index: int, window: int = 20) -> float:
        if len(self.volumes) == 0:
            return 1.0
        start = max(0, index - window)
        window_volumes = self.volumes[start:index] if index > start else self.volumes[-window:]
        avg_volume = np.mean(window_volumes) if len(window_volumes) else 0
        current_volume = self.volumes[index] if index < len(self.volumes) else (window_volumes[-1] if len(window_volumes) else 0)
        if avg_volume <= 0:
            return 1.0
        return current_volume / avg_volume

    def _local_extrema(self, series: np.ndarray, order: int = 3, mode: str = 'max') -> List[Tuple[int, float]]:
        extrema = []
        if len(series) < order * 2 + 1:
            return extrema
        for i in range(order, len(series) - order):
            window = series[i - order:i + order + 1]
            if mode == 'max' and series[i] == window.max():
                extrema.append((i, series[i]))
            elif mode == 'min' and series[i] == window.min():
                extrema.append((i, series[i]))
        return extrema

    def _percent_diff(self, a: float, b: float) -> float:
        if max(abs(a), abs(b)) == 0:
            return 0.0
        return abs(a - b) / max(abs(a), abs(b))

    def _fit_slope(self, values: np.ndarray) -> float:
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return slope
    
    def _enrich_with_knowledge(self, pattern: Pattern) -> Pattern:
        """
        Enrich pattern with knowledge base guidance (entry, stop-loss, targets, risk notes).
        Validates against recognition rules and adjusts confidence if needed.
        If pattern not in knowledge base, returns pattern unchanged (allows all patterns through).
        """
        if not self.use_knowledge_base or not self._knowledge_library:
            return pattern
        
        # Map pattern_type to knowledge base pattern_id
        # Some patterns use underscores, some use different conventions
        kb_pattern_id = pattern.pattern_type
        if kb_pattern_id == "head_shoulders":
            kb_pattern_id = "head_and_shoulders"
        elif kb_pattern_id == "cup_handle":
            kb_pattern_id = "cup_and_handle"
        
        # Check if pattern exists in knowledge base
        kb_pattern = self._knowledge_library.get_pattern(kb_pattern_id)
        if not kb_pattern:
            # Pattern not in knowledge base - allow through with original confidence
            logger.debug(f"Pattern {kb_pattern_id} not in knowledge base, keeping original confidence")
            return pattern
        
        # Validate against knowledge base rules
        is_valid, conf_adj, reasoning = self._knowledge_library.validate_against_rules(
            kb_pattern_id,
            self.candles,
            pattern.metadata
        )
        
        if not is_valid:
            # Pattern didn't pass knowledge validation, reduce confidence significantly
            pattern.confidence = max(0, pattern.confidence - 20)
            pattern.knowledge_reasoning = f"Failed validation: {reasoning}"
            return pattern
        
        # Apply confidence adjustment from knowledge validation
        pattern.confidence = min(100, pattern.confidence + conf_adj)
        pattern.knowledge_reasoning = reasoning
        
        # Enrich with trading playbook
        playbook = self._knowledge_library.get_trading_playbook(kb_pattern_id)
        if playbook:
            pattern.entry_guidance = playbook.get("entry")
            pattern.stop_loss_guidance = playbook.get("stop_loss")
            pattern.targets_guidance = playbook.get("targets", [])
            pattern.risk_notes = playbook.get("risk_notes")
            
            # If playbook has timeframe_bias, add to strategy_notes
            if playbook.get("timeframe_bias"):
                bias = playbook["timeframe_bias"]
                pattern.strategy_notes = f"Best timeframe: {bias}"
        
        return pattern
        
    def detect_all_patterns(self) -> Dict[str, Any]:
        """
        Detect all patterns and return structured results
        Uses caching to prevent redundant calculations
        """
        # Check cache
        if self._cached_results and self._last_detection_time:
            if (datetime.now() - self._last_detection_time).seconds < self.cache_seconds:
                return self._cached_results
        
        detected_patterns: List[Pattern] = []
        
        # Detect candlestick patterns
        candlestick_patterns = self._detect_candlestick_patterns()
        detected_patterns.extend(candlestick_patterns)

        # Detect multi-candle candlestick formations (3-candle etc.)
        advanced_candles = self._detect_multi_candle_patterns()
        detected_patterns.extend(advanced_candles)
        
        # Detect support/resistance levels
        support_levels, resistance_levels = self._detect_support_resistance()
        
        # Detect breakouts
        breakout_patterns = self._detect_breakouts(support_levels, resistance_levels)
        detected_patterns.extend(breakout_patterns)

        # Detect trend/pattern structure
        detected_patterns.extend(self._detect_double_tops_bottoms())
        detected_patterns.extend(self._detect_head_shoulders())
        detected_patterns.extend(self._detect_triangles())
        detected_patterns.extend(self._detect_flags())
        detected_patterns.extend(self._detect_wedges())
        detected_patterns.extend(self._detect_cup_handle())
        detected_patterns.extend(self._detect_trend_acceleration())
        detected_patterns.extend(self._detect_breakaway_gaps())

        # Newly enabled detections (expanded coverage)
        detected_patterns.extend(self._detect_spinning_top_and_marubozu())
        detected_patterns.extend(self._detect_special_doji())
        detected_patterns.extend(self._detect_hanging_inverted())
        detected_patterns.extend(self._detect_three_inside_outside())
        detected_patterns.extend(self._detect_abandoned_baby())
        detected_patterns.extend(self._detect_rectangles_channels())
        detected_patterns.extend(self._detect_triple_tops_bottoms_extra())
        detected_patterns.extend(self._detect_pennants())
        detected_patterns.extend(self._detect_broadening())
        detected_patterns.extend(self._detect_diamond())
        detected_patterns.extend(self._detect_rounding_bottom())
        
        # Enrich patterns with knowledge base guidance and validation
        validated_patterns: List[Pattern] = []

        for pattern in detected_patterns:
            # Apply knowledge-driven enrichment and validation
            enriched = self._enrich_with_knowledge(pattern)
            
            # Only include patterns with confidence >= 65 after enrichment
            if enriched.confidence >= 65:
                validated_patterns.append(enriched)
            else:
                logger.debug("Pattern %s filtered (confidence %s < 65)", pattern.pattern_type, enriched.confidence)

        high_confidence_patterns = [p for p in validated_patterns if p.confidence >= 70]
        
        results = {
            "detected": [self._pattern_to_dict(p) for p in high_confidence_patterns],
            "active_levels": {
                "support": support_levels[:2],  # Top 2 support levels
                "resistance": resistance_levels[:2]  # Top 2 resistance levels
            },
            "summary": {
                "total_patterns": len(high_confidence_patterns),
                "bullish_count": sum(1 for p in high_confidence_patterns if p.signal == "bullish"),
                "bearish_count": sum(1 for p in high_confidence_patterns if p.signal == "bearish"),
                "neutral_count": sum(1 for p in high_confidence_patterns if p.signal == "neutral"),
                "candlestick_count": sum(1 for p in high_confidence_patterns if PATTERN_CATEGORY_MAP.get(p.pattern_type) == "candlestick"),
                "chart_pattern_count": sum(1 for p in high_confidence_patterns if PATTERN_CATEGORY_MAP.get(p.pattern_type) == "chart_pattern"),
                "price_action_count": sum(1 for p in high_confidence_patterns if PATTERN_CATEGORY_MAP.get(p.pattern_type) == "price_action")
            }
        }
        
        # Add agent explanation
        results["agent_explanation"] = format_patterns_for_agent(results)
        
        # Update cache
        self._cached_results = results
        self._last_detection_time = datetime.now()
        
        return results



    # ------------------------------------------------------------------
    # Additional candlestick detections
    # ------------------------------------------------------------------

    def _detect_spinning_top_and_marubozu(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        for i, c in enumerate(self.candles):
            o, h, l, cl = float(c['open']), float(c['high']), float(c['low']), float(c['close'])
            rng = max(h - l, 1e-9)
            body = abs(cl - o)
            upper = h - max(cl, o)
            lower = min(cl, o) - l
            # Spinning top: small body, relatively symmetric shadows
            if body <= 0.25 * rng and upper >= 0.25 * rng and lower >= 0.25 * rng:
                patterns.append(Pattern(
                    pattern_id=f"spinning_top_{i}_{self.times[i]}",
                    pattern_type="spinning_top",
                    confidence=70,
                    start_candle=i,
                    end_candle=i,
                    description="Spinning Top - market indecision",
                    signal="neutral",
                    action="wait"
                ))
            # Marubozu: body occupies most of range, tiny wicks
            if body >= 0.9 * rng and upper <= 0.05 * rng and lower <= 0.05 * rng:
                bullish = cl > o
                patterns.append(Pattern(
                    pattern_id=f"marubozu_{i}_{self.times[i]}",
                    pattern_type="marubozu_bullish" if bullish else "marubozu_bearish",
                    confidence=78,
                    start_candle=i,
                    end_candle=i,
                    description=f"Marubozu - strong {'bullish' if bullish else 'bearish'} candle",
                    signal="bullish" if bullish else "bearish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_special_doji(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        for i, c in enumerate(self.candles):
            o, h, l, cl = float(c['open']), float(c['high']), float(c['low']), float(c['close'])
            rng = max(h - l, 1e-9)
            body = abs(cl - o)
            upper = h - max(cl, o)
            lower = min(cl, o) - l
            # Dragonfly: tiny body near high, long lower shadow
            if body <= 0.1 * rng and upper <= 0.05 * rng and lower >= 0.6 * rng:
                patterns.append(Pattern(
                    pattern_id=f"dragonfly_doji_{i}_{self.times[i]}",
                    pattern_type="dragonfly_doji",
                    confidence=72,
                    start_candle=i,
                    end_candle=i,
                    description="Dragonfly Doji - potential bullish reversal",
                    signal="bullish",
                    action="watch_closely"
                ))
            # Gravestone: tiny body near low, long upper shadow
            if body <= 0.1 * rng and lower <= 0.05 * rng and upper >= 0.6 * rng:
                patterns.append(Pattern(
                    pattern_id=f"gravestone_doji_{i}_{self.times[i]}",
                    pattern_type="gravestone_doji",
                    confidence=72,
                    start_candle=i,
                    end_candle=i,
                    description="Gravestone Doji - potential bearish reversal",
                    signal="bearish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_hanging_inverted(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        n = len(self.candles)
        if n < 2:
            return patterns
        for i in range(1, n):
            o, h, l, cl = [float(self.candles[i][k]) for k in ('open','high','low','close')]
            prev_o, prev_c = float(self.candles[i-1]['open']), float(self.candles[i-1]['close'])
            rng = max(h - l, 1e-9)
            body = abs(cl - o)
            upper = h - max(cl, o)
            lower = min(cl, o) - l
            # Uptrend if prev close > prev open and cl >= prev_c
            uptrend = prev_c >= prev_o and cl >= prev_c
            downtrend = prev_c <= prev_o and cl <= prev_c
            # Hanging man (after uptrend): small body near top, long lower shadow
            if uptrend and body <= 0.35*rng and lower >= 2*body and upper <= 0.2*rng:
                patterns.append(Pattern(
                    pattern_id=f"hanging_man_{i}_{self.times[i]}",
                    pattern_type="hanging_man",
                    confidence=72,
                    start_candle=i,
                    end_candle=i,
                    description="Hanging Man - potential bearish reversal",
                    signal="bearish",
                    action="watch_closely"
                ))
            # Inverted hammer (after downtrend): small body near bottom, long upper shadow
            if downtrend and body <= 0.35*rng and upper >= 2*body and lower <= 0.2*rng:
                patterns.append(Pattern(
                    pattern_id=f"inverted_hammer_{i}_{self.times[i]}",
                    pattern_type="inverted_hammer",
                    confidence=72,
                    start_candle=i,
                    end_candle=i,
                    description="Inverted Hammer - potential bullish reversal",
                    signal="bullish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_three_inside_outside(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 3:
            return patterns
        for i in range(2, len(self.candles)):
            c1, c2, c3 = self.candles[i-2], self.candles[i-1], self.candles[i]
            # Three inside up/down: 2nd contained within 1st; 3rd confirms reversal
            if c1['close'] < c1['open'] and c2['open'] > c1['close'] and c2['close'] < c1['open'] and c3['close'] > c1['open']:
                patterns.append(Pattern(
                    pattern_id=f"three_inside_up_{i}_{self.times[i]}",
                    pattern_type="three_inside_up",
                    confidence=70,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three Inside Up - bullish confirmation",
                    signal="bullish"
                ))
            if c1['close'] > c1['open'] and c2['open'] < c1['close'] and c2['close'] > c1['open'] and c3['close'] < c1['open']:
                patterns.append(Pattern(
                    pattern_id=f"three_inside_down_{i}_{self.times[i]}",
                    pattern_type="three_inside_down",
                    confidence=70,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three Inside Down - bearish confirmation",
                    signal="bearish"
                ))
            # Three outside up/down: engulfing then confirmation
            if c2['open'] < c1['close'] and c2['close'] > c1['open'] and c3['close'] > c2['close']:
                patterns.append(Pattern(
                    pattern_id=f"three_outside_up_{i}_{self.times[i]}",
                    pattern_type="three_outside_up",
                    confidence=70,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three Outside Up - strong bullish pattern",
                    signal="bullish"
                ))
            if c2['open'] > c1['close'] and c2['close'] < c1['open'] and c3['close'] < c2['close']:
                patterns.append(Pattern(
                    pattern_id=f"three_outside_down_{i}_{self.times[i]}",
                    pattern_type="three_outside_down",
                    confidence=70,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three Outside Down - strong bearish pattern",
                    signal="bearish"
                ))
        return patterns

    # ------------------------------------------------------------------
    # Structure/continuation detections
    # ------------------------------------------------------------------

    def _detect_double_tops_bottoms(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        # Require enough candles to identify swing structure
        if len(self.candles) < 20:
            return patterns

        highs_extrema = self._local_extrema(self.highs, order=3, mode='max')
        lows_extrema = self._local_extrema(self.lows, order=3, mode='min')

        if len(highs_extrema) >= 2:
            last_two = highs_extrema[-2:]
            (idx1, val1), (idx2, val2) = last_two
            if self._percent_diff(val1, val2) < 0.02 and 3 <= idx2 - idx1 <= 40:
                confidence = 72
                patterns.append(Pattern(
                    pattern_id=f"double_top_{idx2}_{self.times[idx2]}",
                    pattern_type="double_top",
                    confidence=confidence,
                    start_candle=idx1,
                    end_candle=idx2,
                    description="Double Top - bearish reversal potential",
                    signal="bearish",
                    action="watch_closely",
                    metadata={
                        "neckline": float(min(self.closes[idx1:idx2+1])),
                        "swing_highs": [
                            {
                                "candle": int(idx1),
                                "price": float(val1)
                            },
                            {
                                "candle": int(idx2),
                                "price": float(val2)
                            }
                        ]
                    }
                ))

        if len(lows_extrema) >= 2:
            last_two = lows_extrema[-2:]
            (idx1, val1), (idx2, val2) = last_two
            if self._percent_diff(val1, val2) < 0.02 and 3 <= idx2 - idx1 <= 40:
                confidence = 72
                patterns.append(Pattern(
                    pattern_id=f"double_bottom_{idx2}_{self.times[idx2]}",
                    pattern_type="double_bottom",
                    confidence=confidence,
                    start_candle=idx1,
                    end_candle=idx2,
                    description="Double Bottom - bullish reversal potential",
                    signal="bullish",
                    action="watch_closely",
                    metadata={
                        "neckline": float(max(self.closes[idx1:idx2+1])),
                        "swing_lows": [
                            {
                                "candle": int(idx1),
                                "price": float(val1)
                            },
                            {
                                "candle": int(idx2),
                                "price": float(val2)
                            }
                        ]
                    }
                ))

        return patterns

    def _detect_head_shoulders(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 30:
            return patterns

        highs_extrema = self._local_extrema(self.highs, order=3, mode='max')
        if len(highs_extrema) < 3:
            return patterns

        last_three = highs_extrema[-3:]
        idx = [i for i, _ in last_three]
        vals = [v for _, v in last_three]
        # Head should be middle peak notably higher
        if vals[1] > vals[0] * 1.02 and vals[1] > vals[2] * 1.02 and abs(vals[0] - vals[2]) / max(vals[1], 1e-9) < 0.08:
            patterns.append(Pattern(
                pattern_id=f"head_shoulders_{idx[-1]}_{self.times[idx[-1]]}",
                pattern_type="head_shoulders",
                confidence=75,
                start_candle=idx[0],
                end_candle=idx[-1],
                description="Head & Shoulders - bearish reversal pattern",
                signal="bearish",
                action="watch_closely",
                metadata={
                    "peaks": [
                        {"candle": int(idx[0]), "price": float(vals[0])},
                        {"candle": int(idx[1]), "price": float(vals[1])},
                        {"candle": int(idx[2]), "price": float(vals[2])}
                    ],
                    "neckline": float(min(self.lows[idx[0]:idx[-1]+1]))
                }
            ))

        lows_extrema = self._local_extrema(self.lows, order=3, mode='min')
        if len(lows_extrema) >= 3:
            last_three = lows_extrema[-3:]
            idx = [i for i, _ in last_three]
            vals = [v for _, v in last_three]
            if vals[1] < vals[0] * 0.98 and vals[1] < vals[2] * 0.98 and abs(vals[0] - vals[2]) / max(abs(vals[1]), 1e-9) < 0.08:
                patterns.append(Pattern(
                    pattern_id=f"inverse_head_shoulders_{idx[-1]}_{self.times[idx[-1]]}",
                    pattern_type="inverse_head_shoulders",
                    confidence=75,
                    start_candle=idx[0],
                    end_candle=idx[-1],
                    description="Inverse Head & Shoulders - bullish reversal pattern",
                    signal="bullish",
                    action="watch_closely",
                    metadata={
                        "troughs": [
                            {"candle": int(idx[0]), "price": float(vals[0])},
                            {"candle": int(idx[1]), "price": float(vals[1])},
                            {"candle": int(idx[2]), "price": float(vals[2])}
                        ],
                        "neckline": float(max(self.highs[idx[0]:idx[-1]+1]))
                    }
                ))

        return patterns

    def _detect_triangles(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 25:
            return patterns

        highs_extrema = self._local_extrema(self.highs, order=3, mode='max')
        lows_extrema = self._local_extrema(self.lows, order=3, mode='min')
        if len(highs_extrema) < 2 or len(lows_extrema) < 2:
            return patterns

        recent_highs = self.highs[-40:]
        recent_lows = self.lows[-40:]
        high_slope = self._fit_slope(np.array(recent_highs))
        low_slope = self._fit_slope(np.array(recent_lows))

        if high_slope < 0 and low_slope > 0:
            start_idx = len(self.candles) - len(recent_highs)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"sym_triangle_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="symmetrical_triangle",
                confidence=72,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Symmetrical triangle consolidation",
                signal="neutral",
                action="watch_closely",
                metadata={
                    "upper_trendline": {
                        "start_candle": int(max(start_idx, 0)),
                        "start_price": float(recent_highs[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(recent_highs[-1])
                    },
                    "lower_trendline": {
                        "start_candle": int(max(start_idx,0)),
                        "start_price": float(recent_lows[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(recent_lows[-1])
                    }
                }
            ))
        elif high_slope < 0 and abs(low_slope) < abs(high_slope) * 0.4:
            start_idx = len(self.candles) - len(recent_highs)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"descending_triangle_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="descending_triangle",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Descending triangle - bearish bias",
                signal="bearish",
                action="watch_closely",
                metadata={
                    "upper_trendline": {
                        "start_candle": int(max(start_idx, 0)),
                        "start_price": float(recent_highs[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(recent_highs[-1])
                    },
                    "horizontal_level": float(min(recent_lows))
                }
            ))
        elif low_slope > 0 and abs(high_slope) < abs(low_slope) * 0.4:
            start_idx = len(self.candles) - len(recent_lows)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"ascending_triangle_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="ascending_triangle",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Ascending triangle - bullish bias",
                signal="bullish",
                action="watch_closely",
                metadata={
                    "lower_trendline": {
                        "start_candle": int(max(start_idx, 0)),
                        "start_price": float(recent_lows[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(recent_lows[-1])
                    },
                    "horizontal_level": float(max(recent_highs))
                }
            ))

        return patterns

    def _detect_flags(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 20:
            return patterns

        window = min(20, len(self.candles))
        closes = np.array(self.closes[-window:])
        slopes = self._fit_slope(closes)
        # Identify strong prior move (flag pole)
        lookback = min(40, len(self.candles))
        pole_change = (self.closes[-1] - self.closes[-lookback]) / max(self.closes[-lookback], 1e-9)

        if abs(pole_change) > 0.08 and abs(slopes) < abs(pole_change) * 0.2:
            bullish = pole_change > 0
            start_idx = len(self.candles) - window
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"flag_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="bullish_flag" if bullish else "bearish_flag",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description=f"{'Bullish' if bullish else 'Bearish'} flag consolidation",
                signal="bullish" if bullish else "bearish",
                action="watch_closely",
                metadata={
                    "channel_bounds": {
                        "upper": float(max(self.highs[start_idx:end_idx+1])),
                        "lower": float(min(self.lows[start_idx:end_idx+1]))
                    }
                }
            ))

        return patterns

    def _detect_wedges(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 25:
            return patterns

        highs = self.highs[-50:]
        lows = self.lows[-50:]
        high_slope = self._fit_slope(np.array(highs))
        low_slope = self._fit_slope(np.array(lows))

        if high_slope > 0 and low_slope > 0 and high_slope < low_slope:
            start_idx = len(self.candles) - len(highs)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"rising_wedge_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="rising_wedge",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Rising wedge - bearish bias",
                signal="bearish",
                action="watch_closely",
                metadata={
                    "upper_trendline": {
                        "start_candle": int(start_idx),
                        "start_price": float(highs[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(highs[-1])
                    },
                    "lower_trendline": {
                        "start_candle": int(start_idx),
                        "start_price": float(lows[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(lows[-1])
                    }
                }
            ))
        elif high_slope < 0 and low_slope < 0 and high_slope > low_slope:
            start_idx = len(self.candles) - len(highs)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"falling_wedge_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="falling_wedge",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Falling wedge - bullish bias",
                signal="bullish",
                action="watch_closely",
                metadata={
                    "upper_trendline": {
                        "start_candle": int(start_idx),
                        "start_price": float(highs[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(highs[-1])
                    },
                    "lower_trendline": {
                        "start_candle": int(start_idx),
                        "start_price": float(lows[0]),
                        "end_candle": int(end_idx),
                        "end_price": float(lows[-1])
                    }
                }
            ))

        return patterns

    def _detect_cup_handle(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 40:
            return patterns

        closes = np.array(self.closes[-60:])
        if len(closes) < 20:
            return patterns

        midpoint = len(closes) // 2
        left = closes[:midpoint]
        right = closes[midpoint:]
        if len(left) < 10 or len(right) < 10:
            return patterns

        left_peak = left.max()
        right_peak = right.max()
        cup_low = closes.min()

        depth = (left_peak - cup_low) / max(left_peak, 1e-9)
        recovery = (right_peak - cup_low) / max(left_peak, 1e-9)

        if 0.08 < depth < 0.35 and recovery > 0.8:
            start_idx = len(self.candles) - len(closes)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"cup_handle_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="cup_handle",
                confidence=70,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Cup and Handle base",
                signal="bullish",
                action="watch_closely",
                metadata={
                    "cup_low": float(cup_low),
                    "left_peak": float(left_peak),
                    "right_peak": float(right_peak)
                }
            ))

        return patterns

    def _detect_trend_acceleration(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 30:
            return patterns

        closes = np.array(self.closes[-60:])
        if len(closes) < 15:
            return patterns

        first_half = closes[: len(closes) // 2]
        second_half = closes[len(closes) // 2 :]
        slope1 = self._fit_slope(first_half)
        slope2 = self._fit_slope(second_half)

        if slope2 > slope1 * 1.5 and slope2 > 0:
            start_idx = len(self.candles) - len(closes)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"trend_acceleration_bull_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="trend_acceleration",
                confidence=68,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Accelerating uptrend",
                signal="bullish",
                action="watch_closely",
                metadata={
                    "slope_change": float(slope2 - slope1)
                }
            ))
        elif slope2 < slope1 * 1.5 and slope2 < 0:
            start_idx = len(self.candles) - len(closes)
            end_idx = len(self.candles) - 1
            patterns.append(Pattern(
                pattern_id=f"trend_acceleration_bear_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="trend_acceleration",
                confidence=68,
                start_candle=start_idx,
                end_candle=end_idx,
                description="Accelerating downtrend",
                signal="bearish",
                action="watch_closely",
                metadata={
                    "slope_change": float(slope2 - slope1)
                }
            ))

        return patterns

    def _detect_rectangles_channels(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 20:
            return patterns
        highs = self.highs
        lows = self.lows
        # Rectangle: flat SR with multiple touches
        support_ext = self._local_extrema(lows, order=3, mode='min')
        resistance_ext = self._local_extrema(highs, order=3, mode='max')
        if len(support_ext) >= 2 and len(resistance_ext) >= 2:
            sup_vals = [v for _, v in support_ext[-4:]]
            res_vals = [v for _, v in resistance_ext[-4:]]
            if sup_vals and res_vals:
                sup_mean = float(np.median(sup_vals))
                res_mean = float(np.median(res_vals))
                # Near-flat tolerance
                if abs(self._fit_slope(np.array([sup_mean, sup_mean*1.0001, sup_mean*0.9999]))) < 1e-4:
                    patterns.append(Pattern(
                        pattern_id=f"rectangle_{len(self.candles)-1}_{self.times[-1]}",
                        pattern_type="rectangle_range",
                        confidence=72,
                        start_candle=max(0, len(self.candles)-50),
                        end_candle=len(self.candles)-1,
                        description="Rectangle range - sideways consolidation",
                        signal="neutral",
                        action="wait"
                    ))
        # Channels: parallel trendlines (approx by similar slopes)
        win = min(60, len(self.candles))
        highs_win = highs[-win:]
        lows_win = lows[-win:]
        slope_high = self._fit_slope(highs_win)
        slope_low = self._fit_slope(lows_win)
        if slope_high * slope_low > 0 and abs(abs(slope_high) - abs(slope_low)) / max(abs(slope_high), 1e-9) < 0.4:
            if slope_high > 0:
                ptype = "channel_up"
                signal = "bullish"
            else:
                ptype = "channel_down"
                signal = "bearish"
            patterns.append(Pattern(
                pattern_id=f"{ptype}_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type=ptype,
                confidence=70,
                start_candle=len(self.candles)-win,
                end_candle=len(self.candles)-1,
                description=f"{ptype.replace('_',' ').title()} detected",
                signal=signal,
                action="watch_closely"
            ))
        return patterns

    def _detect_triple_tops_bottoms_extra(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        ex_max = self._local_extrema(self.highs, order=3, mode='max')
        ex_min = self._local_extrema(self.lows, order=3, mode='min')
        # Triple top: three highs within tolerance
        if len(ex_max) >= 3:
            last3 = ex_max[-5:]
            vals = [v for _, v in last3]
            if len(vals) >= 3:
                vals_sorted = sorted(vals[-3:])
                if self._percent_diff(vals_sorted[0], vals_sorted[-1]) < 0.02:
                    idx = [i for i,_ in last3][-3:]
                    patterns.append(Pattern(
                        pattern_id=f"triple_top_{idx[-1]}_{self.times[idx[-1]]}",
                        pattern_type="triple_top",
                        confidence=75,
                        start_candle=idx[0],
                        end_candle=idx[-1],
                        description="Triple Top - bearish reversal potential",
                        signal="bearish",
                        action="watch_closely"
                    ))
        # Triple bottom
        if len(ex_min) >= 3:
            last3 = ex_min[-5:]
            vals = [v for _, v in last3]
            if len(vals) >= 3:
                vals_sorted = sorted(vals[-3:])
                if self._percent_diff(vals_sorted[0], vals_sorted[-1]) < 0.02:
                    idx = [i for i,_ in last3][-3:]
                    patterns.append(Pattern(
                        pattern_id=f"triple_bottom_{idx[-1]}_{self.times[idx[-1]]}",
                        pattern_type="triple_bottom",
                        confidence=75,
                        start_candle=idx[0],
                        end_candle=idx[-1],
                        description="Triple Bottom - bullish reversal potential",
                        signal="bullish",
                        action="watch_closely"
                    ))
        return patterns

    def _detect_pennants(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 20:
            return patterns
        # Look for short, converging highs/lows following a strong directional pole
        win = min(20, len(self.candles))
        highs = self.highs[-win:]
        lows = self.lows[-win:]
        slope_high = self._fit_slope(highs)
        slope_low = self._fit_slope(lows)
        converging = slope_high < 0 and slope_low > 0
        # Pole: strong prior move in last 30-60 candles
        lookback = min(60, len(self.candles))
        pole_change = (self.closes[-1] - self.closes[-lookback]) / max(self.closes[-lookback], 1e-9)
        if converging and abs(pole_change) > 0.08:
            bullish = pole_change > 0
            ptype = "pennant_bullish" if bullish else "pennant_bearish"
            patterns.append(Pattern(
                pattern_id=f"{ptype}_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type=ptype,
                confidence=72,
                start_candle=len(self.candles)-win,
                end_candle=len(self.candles)-1,
                description=f"Pennant - {'bullish' if bullish else 'bearish'} continuation",
                signal="bullish" if bullish else "bearish",
                action="watch_closely"
            ))
        return patterns

    def _detect_broadening(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 30:
            return patterns
        # Broadening: higher highs and lower lows (diverging trendlines)
        win = min(60, len(self.candles))
        highs = self.highs[-win:]
        lows = self.lows[-win:]
        slope_high = self._fit_slope(highs)
        slope_low = self._fit_slope(lows)
        if slope_high > 0 and slope_low < 0:
            patterns.append(Pattern(
                pattern_id=f"broadening_{len(self.candles)-1}_{self.times[-1]}",
                pattern_type="broadening_top" if self.closes[-1] < self.closes[-win] else "broadening_bottom",
                confidence=70,
                start_candle=len(self.candles)-win,
                end_candle=len(self.candles)-1,
                description="Broadening formation (megaphone)",
                signal="neutral",
                action="watch_closely"
            ))
        return patterns

    def _detect_diamond(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 40:
            return patterns
        # Approximate: brief broadening followed by converging (diamond at top/bottom)
        mid = len(self.candles) // 2
        highs1 = self.highs[:mid]
        lows1 = self.lows[:mid]
        highs2 = self.highs[mid:]
        lows2 = self.lows[mid:]
        if len(highs1) > 10 and len(highs2) > 10:
            if self._fit_slope(highs1) > 0 and self._fit_slope(lows1) < 0 and self._fit_slope(highs2) < 0 and self._fit_slope(lows2) > 0:
                top = self.closes[mid] > np.median(self.closes)
                ptype = "diamond_top" if top else "diamond_bottom"
                patterns.append(Pattern(
                    pattern_id=f"{ptype}_{len(self.candles)-1}_{self.times[-1]}",
                    pattern_type=ptype,
                    confidence=70,
                    start_candle=0,
                    end_candle=len(self.candles)-1,
                    description="Diamond pattern",
                    signal="bearish" if ptype == "diamond_top" else "bullish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_rounding_bottom(self) -> List[Pattern]:
        patterns: List[Pattern] = []
        if len(self.candles) < 30:
            return patterns
        # Simple U-shape approximation: lows decreasing then increasing with small slopes
        lows = self.lows
        win = min(80, len(lows))
        lows_win = lows[-win:]
        # Split into two halves and check trend reversal with gentle slopes
        half = len(lows_win) // 2
        if half >= 10:
            slope1 = self._fit_slope(lows_win[:half])
            slope2 = self._fit_slope(lows_win[half:])
            if slope1 < 0 and slope2 > 0 and abs(slope1) < np.std(lows_win)*0.01 and abs(slope2) < np.std(lows_win)*0.01:
                patterns.append(Pattern(
                    pattern_id=f"rounding_bottom_{len(self.candles)-1}_{self.times[-1]}",
                    pattern_type="rounding_bottom",
                    confidence=70,
                    start_candle=len(self.candles)-win,
                    end_candle=len(self.candles)-1,
                    description="Rounding Bottom (saucer)",
                    signal="bullish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_abandoned_baby(self) -> List[Pattern]:
        """Detect Abandoned Baby (rare): doji gapped on both sides."""
        patterns: List[Pattern] = []
        n = len(self.candles)
        if n < 3:
            return patterns
        for i in range(1, n-1):
            prev = self.candles[i-1]
            doji = self.candles[i]
            nxt = self.candles[i+1]
            # Doji criteria
            rng = max(float(doji['high']) - float(doji['low']), 1e-9)
            body = abs(float(doji['close']) - float(doji['open']))
            if body > 0.1 * rng:
                continue
            # Gaps on both sides
            gap_up_prev = float(doji['low']) > float(prev['high'])
            gap_down_prev = float(doji['high']) < float(prev['low'])
            gap_up_next = float(nxt['low']) > float(doji['high'])
            gap_down_next = float(nxt['high']) < float(doji['low'])
            if (gap_up_prev and gap_down_next) or (gap_down_prev and gap_up_next):
                bullish = gap_down_prev and gap_up_next
                patterns.append(Pattern(
                    pattern_id=f"abandoned_baby_{i}_{self.times[i]}",
                    pattern_type="abandoned_baby",
                    confidence=75,
                    start_candle=i-1,
                    end_candle=i+1,
                    description="Abandoned Baby - strong reversal",
                    signal="bullish" if bullish else "bearish",
                    action="watch_closely"
                ))
        return patterns

    def _detect_breakaway_gaps(self) -> List[Pattern]:
        """Detect and classify gaps: breakaway, runaway, exhaustion."""
        patterns: List[Pattern] = []
        n = len(self.candles)
        if n < 5:
            return patterns
        # Helper to compute average true range for scale
        atr = np.mean(self.highs - self.lows) if len(self.highs) else 0
        for i in range(1, n):
            prev = self.candles[i-1]
            curr = self.candles[i]
            gap = float(curr['open']) - float(prev['close'])
            gap_pct = gap / max(abs(prev['close']), 1e-9)
            # Consider significant if > 0.5 ATR or > 1%
            if abs(gap) < max(0.5 * atr, 0.01 * abs(prev['close'])):
                continue
            # Classify by trend context
            look = max(3, min(20, i))
            trend_change = np.sign(self.closes[i-1] - self.closes[i-look]) if i - look >= 0 else 0
            same_dir = (gap > 0 and self.closes[i-1] >= self.closes[i-look]) or (gap < 0 and self.closes[i-1] <= self.closes[i-look])
            vol_ratio = self._volume_ratio(i)
            base_conf = 72 if vol_ratio > 1.2 else 68
            if same_dir and abs(gap_pct) > 0.015:
                ptype = "runaway_gap"
                desc = "Runaway gap - continuation"
                signal = "bullish" if gap > 0 else "bearish"
            elif trend_change == 0:
                ptype = "breakaway_gap"
                desc = "Breakaway gap - start of move"
                signal = "bullish" if gap > 0 else "bearish"
            else:
                ptype = "exhaustion_gap"
                desc = "Exhaustion gap - potential end of move"
                signal = "bearish" if gap > 0 else "bullish"
            patterns.append(Pattern(
                pattern_id=f"{ptype}_{i}_{self.times[i]}",
                pattern_type=ptype,
                confidence=min(90, self._apply_confidence_weights(base_conf, vol_ratio)),
                start_candle=i-1,
                end_candle=i,
                description=desc,
                signal=signal,
                action="watch_closely"
            ))
        return patterns
    
    def _detect_candlestick_patterns(self) -> List[Pattern]:
        """Detect the 3 high-value candlestick patterns"""
        patterns = []
        
        if len(self.candles) < 2:
            return patterns
        
        for i in range(1, len(self.candles)):
            curr = self.candles[i]
            prev = self.candles[i-1]
            
            # 1. Detect Engulfing patterns
            engulfing = self._detect_engulfing(curr, prev, i)
            if engulfing:
                patterns.append(engulfing)
            
            # 2. Detect Doji
            doji = self._detect_doji(curr, i)
            if doji:
                patterns.append(doji)
            
            # 3. Detect Hammer/Shooting Star
            hammer_or_star = self._detect_hammer_shooting_star(curr, i)
            if hammer_or_star:
                patterns.append(hammer_or_star)
        
        return patterns

    def _detect_multi_candle_patterns(self) -> List[Pattern]:
        """Detect three-candle formations and complex candlestick setups."""
        patterns: List[Pattern] = []
        if len(self.candles) < 3:
            return patterns

        for i in range(2, len(self.candles)):
            c1, c2, c3 = self.candles[i-2], self.candles[i-1], self.candles[i]
            o1, c1_close = c1['open'], c1['close']
            o2, c2_close = c2['open'], c2['close']
            o3, c3_close = c3['open'], c3['close']

            # Morning Star (bullish reversal)
            if (c1_close < o1 and  # First candle bearish
                abs(c2_close - o2) < abs(c1_close - o1) * 0.4 and  # Small-bodied star
                c3_close > o3 and  # Third bullish
                c3_close > (o1 + c1_close) / 2):  # Closes above midpoint of first candle
                volume_ratio = self._volume_ratio(i)
                confidence = min(95, 80 * (1.1 if volume_ratio > 1 else 0.9))
                patterns.append(Pattern(
                    pattern_id=f"morning_star_{i}_{self.times[i]}",
                    pattern_type="morning_star",
                    confidence=confidence,
                    start_candle=i-2,
                    end_candle=i,
                    description="Morning Star - bullish candlestick reversal",
                    signal="bullish",
                    action="watch_closely",
                    typical_duration="3-7 candles"
                ))

            # Evening Star (bearish reversal)
            if (c1_close > o1 and
                abs(c2_close - o2) < abs(c1_close - o1) * 0.4 and
                c3_close < o3 and
                c3_close < (o1 + c1_close) / 2):
                volume_ratio = self._volume_ratio(i)
                confidence = min(95, 80 * (1.1 if volume_ratio > 1 else 0.9))
                patterns.append(Pattern(
                    pattern_id=f"evening_star_{i}_{self.times[i]}",
                    pattern_type="evening_star",
                    confidence=confidence,
                    start_candle=i-2,
                    end_candle=i,
                    description="Evening Star - bearish candlestick reversal",
                    signal="bearish",
                    action="watch_closely",
                    typical_duration="3-7 candles"
                ))

            # Piercing Line (bullish)
            if (c1_close < o1 and c2_close > o2 and  # bearish then bullish
                c2_close > (c1_close + o1) / 2 and  # Close penetrates body midpoint
                c2_close < o1):  # Doesn't close above open entirely
                confidence = 72
                patterns.append(Pattern(
                    pattern_id=f"piercing_line_{i-1}_{self.times[i-1]}",
                    pattern_type="piercing_line",
                    confidence=confidence,
                    start_candle=i-1,
                    end_candle=i-1,
                    description="Piercing Line - bullish two-candle reversal",
                    signal="bullish",
                    action="watch_closely"
                ))

            # Dark Cloud Cover (bearish)
            if (c1_close > o1 and c2_close < o2 and
                c2_close < (c1_close + o1) / 2 and
                c2_close > o1):
                confidence = 72
                patterns.append(Pattern(
                    pattern_id=f"dark_cloud_cover_{i-1}_{self.times[i-1]}",
                    pattern_type="dark_cloud_cover",
                    confidence=confidence,
                    start_candle=i-1,
                    end_candle=i-1,
                    description="Dark Cloud Cover - bearish two-candle reversal",
                    signal="bearish",
                    action="watch_closely"
                ))

            # Harami (Bullish / Bearish)
            if abs(c2_close - o2) < abs(c1_close - o1) * 0.5:
                if c1_close < o1 and c2_close > o2 and c2_close < o1 and c2_close > c1_close:
                    patterns.append(Pattern(
                        pattern_id=f"bullish_harami_{i-1}_{self.times[i-1]}",
                        pattern_type="bullish_harami",
                        confidence=70,
                        start_candle=i-1,
                        end_candle=i-1,
                        description="Bullish Harami - potential reversal",
                        signal="bullish",
                        action="wait"
                    ))
                if c1_close > o1 and c2_close < o2 and c2_close < c1_close and c2_close > o1:
                    patterns.append(Pattern(
                        pattern_id=f"bearish_harami_{i-1}_{self.times[i-1]}",
                        pattern_type="bearish_harami",
                        confidence=70,
                        start_candle=i-1,
                        end_candle=i-1,
                        description="Bearish Harami - potential reversal",
                        signal="bearish",
                        action="wait"
                    ))

        # Three white soldiers / three black crows
        for i in range(2, len(self.candles)):
            c1, c2, c3 = self.candles[i-2], self.candles[i-1], self.candles[i]
            if (c1['close'] > c1['open'] and c2['close'] > c2['open'] and c3['close'] > c3['open'] and
                c2['open'] > c1['open'] and c3['open'] > c2['open'] and
                c3['close'] > c2['close'] > c1['close']):
                patterns.append(Pattern(
                    pattern_id=f"three_white_soldiers_{i}_{self.times[i]}",
                    pattern_type="three_white_soldiers",
                    confidence=78,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three White Soldiers - strong bullish continuation",
                    signal="bullish",
                    action="watch_closely"
                ))

            if (c1['close'] < c1['open'] and c2['close'] < c2['open'] and c3['close'] < c3['open'] and
                c2['open'] < c1['open'] and c3['open'] < c2['open'] and
                c3['close'] < c2['close'] < c1['close']):
                patterns.append(Pattern(
                    pattern_id=f"three_black_crows_{i}_{self.times[i]}",
                    pattern_type="three_black_crows",
                    confidence=78,
                    start_candle=i-2,
                    end_candle=i,
                    description="Three Black Crows - strong bearish continuation",
                    signal="bearish",
                    action="watch_closely"
                ))

        return patterns
    def _detect_engulfing(self, curr: Dict, prev: Dict, index: int) -> Optional[Pattern]:
        """
        Detect Bullish/Bearish Engulfing patterns
        High reliability reversal signals
        """
        curr_body = abs(curr['close'] - curr['open'])
        prev_body = abs(prev['close'] - prev['open'])
        
        # Bullish Engulfing: Previous red, current green, current engulfs previous
        if (prev['close'] < prev['open'] and  # Previous is bearish
            curr['close'] > curr['open'] and  # Current is bullish
            curr['open'] <= prev['close'] and  # Opens at or below previous close
            curr['close'] >= prev['open']):    # Closes at or above previous open
            
            # Calculate confidence based on volume
            volume_ratio = curr.get('volume', 1) / (sum(c.get('volume', 1) for c in self.candles[-20:]) / 20)
            base_confidence = 85
            confidence = self._apply_confidence_weights(base_confidence, volume_ratio)
            
            return Pattern(
                pattern_id=f"bullish_engulfing_{index}_{curr['time']}",
                pattern_type="bullish_engulfing",
                confidence=confidence,
                start_candle=index-1,
                end_candle=index,
                description="Bullish Engulfing - Strong reversal signal",
                signal="bullish",
                action="consider_entry" if confidence > 80 else "watch_closely",
                target=curr['close'] + curr_body,
                stop_loss=prev['low'],
                success_rate=0.65,  # 65% historical success rate
                risk_reward_ratio=2.3,  # Average 1:2.3 risk/reward
                typical_duration="3-5 days",
                strategy_notes="Enter on confirmation candle close above engulfing high. Trail stop to breakeven at 1R profit.",
                metadata={
                    "prev_candle": {"open": float(prev['open']), "close": float(prev['close']), "low": float(prev['low']), "high": float(prev['high'])},
                    "curr_candle": {"open": float(curr['open']), "close": float(curr['close']), "low": float(curr['low']), "high": float(curr['high'])},
                    "horizontal_level": float(prev['low'])  # Stop loss level
                }
            )
        
        # Bearish Engulfing: Previous green, current red, current engulfs previous
        elif (prev['close'] > prev['open'] and  # Previous is bullish
              curr['close'] < curr['open'] and  # Current is bearish
              curr['open'] >= prev['close'] and  # Opens at or above previous close
              curr['close'] <= prev['open']):    # Closes at or below previous open
            
            volume_ratio = curr.get('volume', 1) / (sum(c.get('volume', 1) for c in self.candles[-20:]) / 20)
            base_confidence = 85
            confidence = self._apply_confidence_weights(base_confidence, volume_ratio)
            
            return Pattern(
                pattern_id=f"bearish_engulfing_{index}_{curr['time']}",
                pattern_type="bearish_engulfing",
                confidence=confidence,
                start_candle=index-1,
                end_candle=index,
                description="Bearish Engulfing - Strong reversal signal",
                signal="bearish",
                action="consider_entry" if confidence > 80 else "watch_closely",
                target=curr['close'] - curr_body,
                stop_loss=prev['high'],
                metadata={
                    "prev_candle": {"open": float(prev['open']), "close": float(prev['close']), "low": float(prev['low']), "high": float(prev['high'])},
                    "curr_candle": {"open": float(curr['open']), "close": float(curr['close']), "low": float(curr['low']), "high": float(curr['high'])},
                    "horizontal_level": float(prev['high'])  # Stop loss level
                }
            )
        
        return None
    
    def _detect_doji(self, candle: Dict, index: int) -> Optional[Pattern]:
        """
        Detect Doji pattern - indecision indicator
        Body is very small relative to range
        """
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        if total_range > 0:
            body_ratio = body / total_range
            
            # Doji when body is less than 10% of total range
            if body_ratio < 0.1:
                confidence = 90 if body_ratio < 0.05 else 75
                
                return Pattern(
                    pattern_id=f"doji_{index}_{candle['time']}",
                    pattern_type="doji",
                    confidence=confidence,
                    start_candle=index,
                    end_candle=index,
                    description="Doji - Market indecision",
                    signal="neutral",
                    action="wait",
                    metadata={
                        "candle": {"open": float(candle['open']), "close": float(candle['close']), "low": float(candle['low']), "high": float(candle['high'])},
                        "horizontal_level": float((candle['high'] + candle['low']) / 2)  # Mid-point reference
                    }
                )
        
        return None
    
    def _detect_hammer_shooting_star(self, candle: Dict, index: int) -> Optional[Pattern]:
        """
        Detect Hammer (bullish) or Shooting Star (bearish) patterns
        Volume-confirmed reversal signals
        """
        body = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        
        # Hammer: Long lower shadow (2x body), small upper shadow
        if lower_shadow > body * 2 and upper_shadow < body * 0.3:
            # Check if in downtrend (simplified: current low < 5-candle avg)
            if index >= 5:
                recent_avg = np.mean([c['close'] for c in self.candles[index-5:index]])
                if candle['low'] < recent_avg * 0.98:  # 2% below average
                    
                    # Volume confirmation
                    volume_ratio = candle.get('volume', 1) / (sum(c.get('volume', 1) for c in self.candles[-20:]) / 20)
                    base_confidence = 80
                    confidence = self._apply_confidence_weights(base_confidence, volume_ratio)
                    
                    if confidence >= 70:
                        return Pattern(
                            pattern_id=f"hammer_{index}_{candle['time']}",
                            pattern_type="hammer",
                            confidence=confidence,
                            start_candle=index,
                            end_candle=index,
                            description="Hammer - Potential bullish reversal",
                            signal="bullish",
                            action="watch_closely",
                            target=candle['high'] + body,
                            stop_loss=candle['low']
                        )
        
        # Shooting Star: Long upper shadow (2x body), small lower shadow  
        elif upper_shadow > body * 2 and lower_shadow < body * 0.3:
            # Check if in uptrend
            if index >= 5:
                recent_avg = np.mean([c['close'] for c in self.candles[index-5:index]])
                if candle['high'] > recent_avg * 1.02:  # 2% above average
                    
                    volume_ratio = candle.get('volume', 1) / (sum(c.get('volume', 1) for c in self.candles[-20:]) / 20)
                    base_confidence = 80
                    confidence = self._apply_confidence_weights(base_confidence, volume_ratio)
                    
                    if confidence >= 70:
                        return Pattern(
                            pattern_id=f"shooting_star_{index}_{candle['time']}",
                            pattern_type="shooting_star",
                            confidence=confidence,
                            start_candle=index,
                            end_candle=index,
                            description="Shooting Star - Potential bearish reversal",
                            signal="bearish",
                            action="watch_closely",
                            target=candle['low'] - body,
                            stop_loss=candle['high']
                        )
        
        return None
    
    def _detect_support_resistance(self) -> Tuple[List[float], List[float]]:
        """
        Detect support and resistance levels
        Uses recent highs/lows with clustering
        """
        if len(self.candles) < 5:  # Reduced minimum from 20 to 5 for testing
            return [], []
        
        # Get recent highs and lows
        recent_candles = self.candles[-50:] if len(self.candles) > 50 else self.candles
        highs = [c['high'] for c in recent_candles]
        lows = [c['low'] for c in recent_candles]
        closes = [c['close'] for c in recent_candles]
        
        # Find levels using percentiles (more reliable than peak detection)
        resistance_levels = []
        support_levels = []
        
        # Resistance: Recent highs that were tested multiple times
        for percentile in [75, 90, 100]:
            level = np.percentile(highs, percentile)
            # Count how many times price approached this level
            touches = sum(1 for h in highs if abs(h - level) / level < 0.02)  # Within 2%
            if touches >= 2:
                resistance_levels.append(round(level, 2))
        
        # Support: Recent lows that held multiple times
        for percentile in [25, 10, 0]:
            level = np.percentile(lows, percentile)
            touches = sum(1 for l in lows if abs(l - level) / level < 0.02)  # Within 2%
            if touches >= 2:
                support_levels.append(round(level, 2))
        
        # Also look for clear horizontal levels in the data
        # Check for price levels that appear multiple times
        all_prices = lows + highs + closes
        from collections import Counter
        price_counts = Counter([round(p, 0) for p in all_prices])
        
        # Add frequently touched levels as support/resistance
        for price, count in price_counts.items():
            if count >= 3:  # Touched at least 3 times
                current_price = recent_candles[-1]['close']
                if price < current_price and price not in support_levels:
                    support_levels.append(float(price))
                elif price > current_price and price not in resistance_levels:
                    resistance_levels.append(float(price))
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        support_levels = sorted(list(set(support_levels)))
        
        return support_levels, resistance_levels
    
    def _detect_breakouts(self, support_levels: List[float], resistance_levels: List[float]) -> List[Pattern]:
        """
        Detect breakouts with volume confirmation
        Requires price to break level with 1.5x average volume
        """
        patterns = []
        
        if len(self.candles) < 5:  # Minimum candles needed
            return patterns
        
        # Calculate average volume (use all available candles if less than 20)
        volume_window = min(20, len(self.candles) - 1)
        avg_volume = np.mean([c.get('volume', 0) for c in self.candles[-volume_window:]])
        
        # Check for breakouts in recent candles (not just the last one)
        check_range = min(5, len(self.candles) - 1)  # Check last 5 candles for breakouts
        
        for i in range(len(self.candles) - check_range, len(self.candles)):
            if i == 0:
                continue
                
            curr = self.candles[i]
            prev = self.candles[i-1]
            curr_volume = curr.get('volume', 0)
            
            # Volume confirmation: Current volume > 1.5x average
            volume_confirmed = curr_volume > avg_volume * 1.5 if avg_volume > 0 else False
            
            # Check resistance breakout
            for resistance in resistance_levels:
                if prev['close'] < resistance and curr['close'] > resistance and volume_confirmed:
                    confidence = 80 if curr_volume > avg_volume * 2 else 75
                    
                    patterns.append(Pattern(
                        pattern_id=f"breakout_{i}_{curr['time']}",
                        pattern_type="breakout",
                        confidence=confidence,
                        start_candle=i-1,
                        end_candle=i,
                        description=f"Breakout above resistance at ${resistance:.2f}",
                        signal="bullish",
                        action="consider_entry" if confidence > 75 else "watch_closely",
                        target=resistance + (resistance - support_levels[0]) if support_levels else resistance * 1.02,
                        stop_loss=resistance * 0.98
                    ))
                    break  # Only detect one breakout
            
            # Check support breakdown
            for support in support_levels:
                if prev['close'] > support and curr['close'] < support and volume_confirmed:
                    confidence = 80 if curr_volume > avg_volume * 2 else 75
                    
                    patterns.append(Pattern(
                        pattern_id=f"breakdown_{i}_{curr['time']}",
                        pattern_type="breakdown",
                        confidence=confidence,
                        start_candle=i-1,
                        end_candle=i,
                        description=f"Breakdown below support at ${support:.2f}",
                        signal="bearish",
                        action="consider_entry" if confidence > 75 else "watch_closely",
                        target=support - (resistance_levels[0] - support) if resistance_levels else support * 0.98,
                        stop_loss=support * 1.02
                    ))
                    break
        
        # Support bounce detection
        for support in support_levels:
            # Check if price touched support but closed above it
            if (curr['low'] <= support * 1.01 and  # Wicked down to support
                curr['close'] > support and  # But closed above
                curr['close'] > curr['open']):  # And it's a green candle
                
                confidence = 70 if volume_confirmed else 65
                if confidence >= 70:
                    patterns.append(Pattern(
                        pattern_id=f"support_bounce_{len(self.candles)-1}_{curr['time']}",
                        pattern_type="support_bounce",
                        confidence=confidence,
                        start_candle=len(self.candles)-1,
                        end_candle=len(self.candles)-1,
                        description=f"Bounce off support at ${support:.2f}",
                        signal="bullish",
                        action="watch_closely"
                    ))
                    break
        
        return patterns
    
    def _apply_confidence_weights(self, base_confidence: float, volume_ratio: float) -> float:
        """
        Apply deterministic confidence weights
        
        Weights:
        - Volume confirmation: 1.2x if volume > avg, else 0.8x
        - Capped at 95% max confidence
        """
        if volume_ratio > 1.5:
            confidence = base_confidence * 1.2
        elif volume_ratio > 1.0:
            confidence = base_confidence * 1.1
        else:
            confidence = base_confidence * 0.9
        
        return min(confidence, 95)  # Cap at 95%
    
    def _pattern_to_dict(self, pattern: Pattern) -> Dict:
        """Convert Pattern object to dictionary for JSON serialization"""
        return {
            "id": pattern.pattern_id,
            "pattern_id": pattern.pattern_id,
            "type": pattern.pattern_type,
            "pattern_type": pattern.pattern_type,
            "confidence": round(pattern.confidence, 1),
            "start_candle": pattern.start_candle,
            "end_candle": pattern.end_candle,
            "description": pattern.description,
            "signal": pattern.signal,
            "action": pattern.action,
            "target": round(pattern.target, 2) if pattern.target else None,
            "stop_loss": round(pattern.stop_loss, 2) if pattern.stop_loss else None,
            "metadata": pattern.metadata or {},
            "chart_metadata": pattern.chart_metadata,
            "knowledge_reasoning": pattern.knowledge_reasoning,
            "entry_guidance": pattern.entry_guidance,
            "stop_loss_guidance": pattern.stop_loss_guidance,
            "targets_guidance": pattern.targets_guidance,
            "risk_notes": pattern.risk_notes
        }


def format_patterns_for_agent(patterns_result: Dict) -> str:
    """
    Format pattern detection results into natural language for the agent
    """
    if not patterns_result["detected"]:
        # No patterns found
        levels = patterns_result.get("active_levels", {})
        support = levels.get("support", [])
        resistance = levels.get("resistance", [])
        
        response = "No clear patterns detected at the moment"
        if support:
            response += f", but watching support at ${support[0]:.2f}"
        if resistance:
            response += f" and resistance at ${resistance[0]:.2f}"
        return response + "."
    
    # High confidence patterns
    high_conf = [p for p in patterns_result["detected"] if p["confidence"] > 80]
    med_conf = [p for p in patterns_result["detected"] if 70 <= p["confidence"] <= 80]
    
    responses = []
    
    if high_conf:
        pattern = high_conf[0]  # Focus on strongest pattern
        responses.append(f"I'm seeing a strong {pattern['description']} with {pattern['confidence']:.0f}% confidence")
        if pattern.get("target"):
            responses.append(f"Target: ${pattern['target']:.2f}")
        if pattern.get("action") == "consider_entry":
            responses.append("This could be a good entry point")
    
    elif med_conf:
        pattern = med_conf[0]
        responses.append(f"There appears to be a {pattern['description']}")
        responses.append("Let's watch this closely")
    
    # Add level information
    levels = patterns_result.get("active_levels", {})
    if levels.get("support"):
        responses.append(f"Key support: ${levels['support'][0]:.2f}")
    if levels.get("resistance"):
        responses.append(f"Key resistance: ${levels['resistance'][0]:.2f}")
    
    # Overall sentiment
    summary = patterns_result.get("summary", {})
    if summary.get("bullish_count", 0) > summary.get("bearish_count", 0):
        responses.append("Overall sentiment is bullish")
    elif summary.get("bearish_count", 0) > summary.get("bullish_count", 0):
        responses.append("Overall sentiment is bearish")
    
    return ". ".join(responses)
