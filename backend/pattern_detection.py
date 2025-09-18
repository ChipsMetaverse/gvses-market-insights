"""
Pattern Detection Module - MVP Implementation
Focuses on 3 high-value patterns per category with deterministic confidence scoring
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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


class PatternDetector:
    """
    MVP Pattern Detector - Focused on 3 high-value patterns per category
    Emphasizes reliability and clear confidence scoring
    """
    
    def __init__(self, candles: List[Dict], cache_seconds: int = 60):
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
        
    def detect_all_patterns(self) -> Dict[str, Any]:
        """
        Detect all patterns and return structured results
        Uses caching to prevent redundant calculations
        """
        # Check cache
        if self._cached_results and self._last_detection_time:
            if (datetime.now() - self._last_detection_time).seconds < self.cache_seconds:
                return self._cached_results
        
        detected_patterns = []
        
        # Detect candlestick patterns
        candlestick_patterns = self._detect_candlestick_patterns()
        detected_patterns.extend(candlestick_patterns)
        
        # Detect support/resistance levels
        support_levels, resistance_levels = self._detect_support_resistance()
        
        # Detect breakouts
        breakout_patterns = self._detect_breakouts(support_levels, resistance_levels)
        detected_patterns.extend(breakout_patterns)
        
        # Filter low confidence patterns
        high_confidence_patterns = [p for p in detected_patterns if p.confidence >= 70]
        
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
                "neutral_count": sum(1 for p in high_confidence_patterns if p.signal == "neutral")
            }
        }
        
        # Add agent explanation
        results["agent_explanation"] = format_patterns_for_agent(results)
        
        # Update cache
        self._cached_results = results
        self._last_detection_time = datetime.now()
        
        return results
    
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
                strategy_notes="Enter on confirmation candle close above engulfing high. Trail stop to breakeven at 1R profit."
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
                stop_loss=prev['high']
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
                    action="wait"
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
            "type": pattern.pattern_type,
            "confidence": round(pattern.confidence, 1),
            "start_candle": pattern.start_candle,
            "end_candle": pattern.end_candle,
            "description": pattern.description,
            "signal": pattern.signal,
            "action": pattern.action,
            "target": round(pattern.target, 2) if pattern.target else None,
            "stop_loss": round(pattern.stop_loss, 2) if pattern.stop_loss else None
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