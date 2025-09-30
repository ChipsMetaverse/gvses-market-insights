"""
Feature Builder for Phase 5 ML Pattern Confidence
=================================================
Extracts ML features from pattern metadata, price history, and technical indicators
"""

import logging
import json
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FeatureSet:
    """Container for extracted features with metadata"""
    features: Dict[str, float]
    feature_names: List[str]
    extraction_time: datetime
    pattern_id: str
    version: str = "1.0"
    quality_score: float = 1.0

class PatternFeatureBuilder:
    """
    Extracts machine learning features from pattern data for confidence prediction
    
    Feature Categories:
    1. Pattern Geometry - Support/resistance levels, target distances
    2. Technical Indicators - RSI, MACD, Bollinger Bands, etc.
    3. Price Action - Volatility, momentum, trend strength
    4. Market Context - Volume, time of day, market sentiment
    5. Pattern History - Confidence evolution, age, lifecycle state
    """
    
    def __init__(self, feature_version: str = "1.0"):
        self.feature_version = feature_version
        self.feature_names = []
        self._initialize_feature_names()
    
    def _initialize_feature_names(self):
        """Initialize the list of feature names for consistency"""
        self.feature_names = [
            # Pattern Geometry Features (12 features)
            'support_distance_pct',
            'resistance_distance_pct', 
            'target_distance_pct',
            'risk_reward_ratio',
            'pattern_height_pct',
            'entry_risk_pct',
            'support_strength',
            'resistance_strength',
            'breakout_strength',
            'pattern_symmetry',
            'level_convergence',
            'fibonacci_alignment',
            
            # Technical Indicator Features (15 features)
            'rsi_value',
            'rsi_oversold',
            'rsi_overbought',
            'macd_signal',
            'macd_histogram',
            'macd_divergence',
            'bb_position',
            'bb_squeeze',
            'bb_width',
            'volume_sma_ratio',
            'volume_trend',
            'ema_20_distance',
            'ema_50_distance',
            'sma_cross_signal',
            'momentum_indicator',
            
            # Price Action Features (10 features)
            'volatility_5d',
            'volatility_20d',
            'price_momentum_5d',
            'price_momentum_20d',
            'trend_strength',
            'consolidation_score',
            'breakout_volume',
            'gap_presence',
            'candle_pattern_score',
            'price_position_range',
            
            # Market Context Features (8 features)
            'market_hour',
            'day_of_week',
            'days_since_earnings',
            'market_volatility_idx',
            'sector_performance',
            'correlation_spy',
            'options_activity',
            'news_sentiment',
            
            # Pattern History Features (5 features)
            'pattern_age_hours',
            'confidence_decay',
            'confidence_trend',
            'analyst_confirmations',
            'similar_pattern_success_rate'
        ]
    
    def extract_features(self, 
                        pattern_data: Dict[str, Any],
                        price_history: Optional[List[Dict]] = None,
                        market_data: Optional[Dict[str, Any]] = None) -> FeatureSet:
        """
        Extract comprehensive feature set from pattern data
        
        Args:
            pattern_data: Pattern metadata from pattern_events table
            price_history: Recent price/volume data for technical analysis
            market_data: Market context data (optional)
            
        Returns:
            FeatureSet with extracted features
        """
        try:
            features = {}
            pattern_id = pattern_data.get("id", "unknown")
            
            # Extract feature categories
            features.update(self._extract_geometry_features(pattern_data))
            features.update(self._extract_technical_features(pattern_data, price_history))
            features.update(self._extract_price_action_features(price_history))
            features.update(self._extract_market_context_features(market_data))
            features.update(self._extract_pattern_history_features(pattern_data))
            
            # Calculate feature quality score
            quality_score = self._calculate_quality_score(features, pattern_data)
            
            # Ensure all expected features are present
            features = self._ensure_complete_feature_set(features)
            
            return FeatureSet(
                features=features,
                feature_names=self.feature_names,
                extraction_time=datetime.now(timezone.utc),
                pattern_id=pattern_id,
                version=self.feature_version,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed for pattern {pattern_data.get('id')}: {str(e)}")
            # Return default feature set with low quality score
            return self._create_default_feature_set(pattern_data.get("id", "unknown"))
    
    def _extract_geometry_features(self, pattern_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from pattern geometry"""
        features = {}
        
        current_price = pattern_data.get("metadata", {}).get("current_price", 0.0)
        support = pattern_data.get("support", 0.0)
        resistance = pattern_data.get("resistance", 0.0)
        target = pattern_data.get("target", 0.0)
        entry = pattern_data.get("entry", current_price)
        
        if current_price > 0:
            # Distance features (as percentages)
            features['support_distance_pct'] = abs(current_price - support) / current_price if support else 0.0
            features['resistance_distance_pct'] = abs(resistance - current_price) / current_price if resistance else 0.0
            features['target_distance_pct'] = abs(target - current_price) / current_price if target else 0.0
            
            # Risk/reward calculation
            if support and target and entry:
                risk = abs(entry - support)
                reward = abs(target - entry)
                features['risk_reward_ratio'] = reward / risk if risk > 0 else 0.0
            else:
                features['risk_reward_ratio'] = 0.0
            
            # Pattern height (support to resistance range)
            if support and resistance:
                features['pattern_height_pct'] = abs(resistance - support) / current_price
            else:
                features['pattern_height_pct'] = 0.0
            
            # Entry risk (distance from entry to stop loss)
            features['entry_risk_pct'] = abs(entry - support) / current_price if support else 0.0
        else:
            # Default values when price is missing
            for key in ['support_distance_pct', 'resistance_distance_pct', 'target_distance_pct',
                       'risk_reward_ratio', 'pattern_height_pct', 'entry_risk_pct']:
                features[key] = 0.0
        
        # Level strength indicators (0-1 scale)
        features['support_strength'] = self._calculate_level_strength(support, pattern_data)
        features['resistance_strength'] = self._calculate_level_strength(resistance, pattern_data)
        features['breakout_strength'] = self._calculate_breakout_strength(pattern_data)
        
        # Pattern shape metrics
        features['pattern_symmetry'] = self._calculate_pattern_symmetry(pattern_data)
        features['level_convergence'] = self._calculate_level_convergence(support, resistance, current_price)
        features['fibonacci_alignment'] = self._calculate_fibonacci_alignment(pattern_data)
        
        return features
    
    def _extract_technical_features(self, 
                                   pattern_data: Dict[str, Any],
                                   price_history: Optional[List[Dict]]) -> Dict[str, float]:
        """Extract technical indicator features"""
        features = {}
        
        if not price_history:
            # Return default technical features
            return {
                'rsi_value': 50.0, 'rsi_oversold': 0.0, 'rsi_overbought': 0.0,
                'macd_signal': 0.0, 'macd_histogram': 0.0, 'macd_divergence': 0.0,
                'bb_position': 0.5, 'bb_squeeze': 0.0, 'bb_width': 0.0,
                'volume_sma_ratio': 1.0, 'volume_trend': 0.0,
                'ema_20_distance': 0.0, 'ema_50_distance': 0.0,
                'sma_cross_signal': 0.0, 'momentum_indicator': 0.0
            }
        
        # Extract price and volume arrays
        prices = [float(candle.get('close', 0)) for candle in price_history[-50:]]  # Last 50 periods
        volumes = [float(candle.get('volume', 0)) for candle in price_history[-50:]]
        
        if len(prices) < 14:  # Minimum for RSI calculation
            return self._extract_technical_features(pattern_data, None)  # Return defaults
        
        # RSI calculation (14-period)
        rsi = self._calculate_rsi(prices, 14)
        features['rsi_value'] = rsi
        features['rsi_oversold'] = 1.0 if rsi < 30 else 0.0
        features['rsi_overbought'] = 1.0 if rsi > 70 else 0.0
        
        # MACD features
        macd_line, signal_line, histogram = self._calculate_macd(prices)
        features['macd_signal'] = 1.0 if macd_line > signal_line else 0.0
        features['macd_histogram'] = histogram
        features['macd_divergence'] = self._detect_macd_divergence(prices, histogram)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices, 20, 2)
        current_price = prices[-1]
        features['bb_position'] = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
        features['bb_squeeze'] = 1.0 if (bb_upper - bb_lower) / bb_middle < 0.1 else 0.0
        features['bb_width'] = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0.0
        
        # Volume analysis
        if len(volumes) >= 20:
            volume_sma = sum(volumes[-20:]) / 20
            features['volume_sma_ratio'] = volumes[-1] / volume_sma if volume_sma > 0 else 1.0
            features['volume_trend'] = self._calculate_trend(volumes[-10:])
        else:
            features['volume_sma_ratio'] = 1.0
            features['volume_trend'] = 0.0
        
        # Moving averages
        if len(prices) >= 50:
            ema_20 = self._calculate_ema(prices, 20)
            ema_50 = self._calculate_ema(prices, 50)
            features['ema_20_distance'] = (current_price - ema_20) / current_price
            features['ema_50_distance'] = (current_price - ema_50) / current_price
            features['sma_cross_signal'] = 1.0 if ema_20 > ema_50 else 0.0
        else:
            features['ema_20_distance'] = 0.0
            features['ema_50_distance'] = 0.0
            features['sma_cross_signal'] = 0.0
        
        # Momentum indicator
        features['momentum_indicator'] = self._calculate_momentum(prices, 10)
        
        return features
    
    def _extract_price_action_features(self, price_history: Optional[List[Dict]]) -> Dict[str, float]:
        """Extract price action and volatility features"""
        features = {}
        
        if not price_history or len(price_history) < 10:
            return {
                'volatility_5d': 0.0, 'volatility_20d': 0.0,
                'price_momentum_5d': 0.0, 'price_momentum_20d': 0.0,
                'trend_strength': 0.0, 'consolidation_score': 0.0,
                'breakout_volume': 0.0, 'gap_presence': 0.0,
                'candle_pattern_score': 0.0, 'price_position_range': 0.5
            }
        
        prices = [float(candle.get('close', 0)) for candle in price_history]
        highs = [float(candle.get('high', 0)) for candle in price_history]
        lows = [float(candle.get('low', 0)) for candle in price_history]
        volumes = [float(candle.get('volume', 0)) for candle in price_history]
        
        # Volatility measures
        if len(prices) >= 5:
            features['volatility_5d'] = self._calculate_volatility(prices[-5:])
        else:
            features['volatility_5d'] = 0.0
            
        if len(prices) >= 20:
            features['volatility_20d'] = self._calculate_volatility(prices[-20:])
        else:
            features['volatility_20d'] = features['volatility_5d']
        
        # Price momentum
        if len(prices) >= 5:
            features['price_momentum_5d'] = (prices[-1] - prices[-5]) / prices[-5]
        else:
            features['price_momentum_5d'] = 0.0
            
        if len(prices) >= 20:
            features['price_momentum_20d'] = (prices[-1] - prices[-20]) / prices[-20]
        else:
            features['price_momentum_20d'] = features['price_momentum_5d']
        
        # Trend strength (0-1 scale)
        features['trend_strength'] = self._calculate_trend_strength(prices)
        
        # Consolidation score (how much price is ranging)
        features['consolidation_score'] = self._calculate_consolidation_score(highs, lows)
        
        # Breakout volume (volume spike indicator)
        features['breakout_volume'] = self._calculate_breakout_volume(volumes)
        
        # Gap detection
        features['gap_presence'] = self._detect_gaps(price_history)
        
        # Candlestick pattern recognition
        features['candle_pattern_score'] = self._analyze_candle_patterns(price_history[-5:])
        
        # Price position in recent range
        if len(highs) >= 20 and len(lows) >= 20:
            recent_high = max(highs[-20:])
            recent_low = min(lows[-20:])
            current_price = prices[-1]
            features['price_position_range'] = (current_price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
        else:
            features['price_position_range'] = 0.5
        
        return features
    
    def _extract_market_context_features(self, market_data: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Extract market context and timing features"""
        features = {}
        
        current_time = datetime.now(timezone.utc)
        
        # Time-based features
        features['market_hour'] = current_time.hour / 24.0  # Normalized to 0-1
        features['day_of_week'] = current_time.weekday() / 6.0  # Monday=0, Sunday=6, normalized
        
        # Market context (use defaults if market_data not provided)
        if market_data:
            features['days_since_earnings'] = market_data.get('days_since_earnings', 30) / 90.0  # Normalized
            features['market_volatility_idx'] = market_data.get('vix', 20) / 100.0  # VIX normalized
            features['sector_performance'] = market_data.get('sector_performance', 0.0)
            features['correlation_spy'] = market_data.get('spy_correlation', 0.5)
            features['options_activity'] = market_data.get('options_volume_ratio', 1.0)
            features['news_sentiment'] = market_data.get('news_sentiment', 0.0)
        else:
            # Default market context values
            features['days_since_earnings'] = 0.33  # ~30 days
            features['market_volatility_idx'] = 0.20  # VIX ~20
            features['sector_performance'] = 0.0
            features['correlation_spy'] = 0.5
            features['options_activity'] = 1.0
            features['news_sentiment'] = 0.0
        
        return features
    
    def _extract_pattern_history_features(self, pattern_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract features related to pattern lifecycle and history"""
        features = {}
        
        # Pattern age
        created_at = pattern_data.get('created_at')
        if isinstance(created_at, str):
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        else:
            created_time = created_at or datetime.now(timezone.utc)
        
        age_hours = (datetime.now(timezone.utc) - created_time).total_seconds() / 3600
        features['pattern_age_hours'] = min(age_hours / 168.0, 1.0)  # Normalized to weeks, capped at 1
        
        # Confidence evolution
        confidence = pattern_data.get('confidence', 0.5)
        features['confidence_decay'] = self._calculate_confidence_decay(confidence, age_hours)
        features['confidence_trend'] = self._calculate_confidence_trend(pattern_data)
        
        # Analyst interactions
        features['analyst_confirmations'] = float(pattern_data.get('metadata', {}).get('analyst_confirmations', 0))
        
        # Historical pattern success (would need database lookup in production)
        pattern_type = pattern_data.get('pattern_type', '')
        features['similar_pattern_success_rate'] = self._get_pattern_success_rate(pattern_type)
        
        return features
    
    # Helper methods for calculations
    
    def _calculate_level_strength(self, level: float, pattern_data: Dict[str, Any]) -> float:
        """Calculate strength of support/resistance level (0-1 scale)"""
        if not level:
            return 0.0
        
        # In production, this would analyze historical touches, volume at level, etc.
        # For now, use pattern confidence as proxy
        confidence = pattern_data.get('confidence', 0.5)
        return min(confidence, 1.0)
    
    def _calculate_breakout_strength(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate breakout strength indicator"""
        # Placeholder - would analyze volume, price action, momentum
        status = pattern_data.get('status', 'pending')
        if status == 'confirmed':
            return 0.8
        elif status == 'completed':
            return 1.0
        else:
            return 0.2
    
    def _calculate_pattern_symmetry(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate pattern symmetry score (0-1)"""
        # Placeholder - would analyze pattern geometry
        pattern_type = pattern_data.get('pattern_type', '')
        if 'triangle' in pattern_type or 'head_and_shoulders' in pattern_type:
            return 0.8
        return 0.5
    
    def _calculate_level_convergence(self, support: float, resistance: float, current_price: float) -> float:
        """Calculate how close support and resistance levels are converging"""
        if not support or not resistance or not current_price:
            return 0.0
        
        level_distance = abs(resistance - support) / current_price
        return max(0.0, 1.0 - level_distance * 10)  # Closer levels = higher convergence
    
    def _calculate_fibonacci_alignment(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate alignment with Fibonacci retracement levels"""
        # Placeholder - would calculate actual Fibonacci levels
        target = pattern_data.get('target', 0.0)
        support = pattern_data.get('support', 0.0)
        resistance = pattern_data.get('resistance', 0.0)
        
        if target and support and resistance:
            # Check if target aligns with common Fibonacci levels (0.618, 1.618, etc.)
            return 0.7  # Placeholder
        return 0.0
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD line, signal line, and histogram"""
        if len(prices) < 26:
            return 0.0, 0.0, 0.0
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        
        # For simplicity, use a simple moving average for signal line
        # In production, use EMA of MACD line
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Initial SMA
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int, std_dev: float) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            avg = sum(prices) / len(prices)
            return avg, avg, avg
        
        sma = sum(prices[-period:]) / period
        variance = sum((price - sma) ** 2 for price in prices[-period:]) / period
        std = math.sqrt(variance)
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper, sma, lower
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility (standard deviation of returns)"""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        if not returns:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return max(-1.0, min(1.0, slope * 10))  # Normalize to -1, 1 range
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength (0-1)"""
        if len(prices) < 10:
            return 0.0
        
        # Count consecutive higher highs/lower lows
        trend_count = 0
        for i in range(1, min(10, len(prices))):
            if prices[-i] > prices[-i-1]:
                trend_count += 1
            elif prices[-i] < prices[-i-1]:
                trend_count -= 1
        
        return abs(trend_count) / 9.0  # Normalize to 0-1
    
    def _calculate_consolidation_score(self, highs: List[float], lows: List[float]) -> float:
        """Calculate consolidation score (0-1, higher = more consolidating)"""
        if len(highs) < 10 or len(lows) < 10:
            return 0.0
        
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]
        
        high_range = max(recent_highs) - min(recent_highs)
        low_range = max(recent_lows) - min(recent_lows)
        avg_price = (sum(recent_highs) + sum(recent_lows)) / (2 * len(recent_highs))
        
        if avg_price == 0:
            return 0.0
        
        range_pct = (high_range + low_range) / (2 * avg_price)
        return max(0.0, 1.0 - range_pct * 20)  # Less range = more consolidation
    
    def _calculate_breakout_volume(self, volumes: List[float]) -> float:
        """Calculate volume breakout indicator"""
        if len(volumes) < 20:
            return 0.0
        
        recent_avg = sum(volumes[-20:-1]) / 19  # Exclude current volume
        current_vol = volumes[-1]
        
        if recent_avg == 0:
            return 0.0
        
        volume_ratio = current_vol / recent_avg
        return min(1.0, volume_ratio / 3.0)  # 3x volume = 1.0 score
    
    def _detect_gaps(self, price_history: List[Dict]) -> float:
        """Detect price gaps (0 or 1)"""
        if len(price_history) < 2:
            return 0.0
        
        for i in range(1, min(5, len(price_history))):  # Check last 5 periods
            prev_high = float(price_history[-i-1].get('high', 0))
            curr_low = float(price_history[-i].get('low', 0))
            
            if curr_low > prev_high:  # Gap up
                return 1.0
            
            prev_low = float(price_history[-i-1].get('low', 0))
            curr_high = float(price_history[-i].get('high', 0))
            
            if curr_high < prev_low:  # Gap down
                return 1.0
        
        return 0.0
    
    def _analyze_candle_patterns(self, recent_candles: List[Dict]) -> float:
        """Analyze candlestick patterns (0-1 score)"""
        if len(recent_candles) < 3:
            return 0.0
        
        # Simplified candlestick pattern recognition
        # In production, implement proper pattern recognition
        score = 0.0
        
        for candle in recent_candles:
            open_price = float(candle.get('open', 0))
            close_price = float(candle.get('close', 0))
            high_price = float(candle.get('high', 0))
            low_price = float(candle.get('low', 0))
            
            if open_price == 0 or close_price == 0:
                continue
            
            body_size = abs(close_price - open_price)
            total_range = high_price - low_price
            
            if total_range > 0:
                # Strong body = higher score
                score += body_size / total_range
        
        return min(1.0, score / len(recent_candles))
    
    def _detect_macd_divergence(self, prices: List[float], histogram: float) -> float:
        """Detect MACD divergence (simplified)"""
        # Placeholder - would implement proper divergence detection
        return 0.0
    
    def _calculate_momentum(self, prices: List[float], period: int) -> float:
        """Calculate momentum indicator"""
        if len(prices) < period + 1:
            return 0.0
        
        current_price = prices[-1]
        past_price = prices[-period-1]
        
        if past_price == 0:
            return 0.0
        
        momentum = (current_price - past_price) / past_price
        return max(-1.0, min(1.0, momentum * 5))  # Normalize to -1, 1 range
    
    def _calculate_confidence_decay(self, confidence: float, age_hours: float) -> float:
        """Calculate confidence decay over time"""
        # Exponential decay function
        decay_rate = 0.02  # 2% per hour
        decayed = confidence * math.exp(-decay_rate * age_hours)
        return decayed
    
    def _calculate_confidence_trend(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate confidence trend (increasing/decreasing)"""
        # Placeholder - would analyze confidence history
        status = pattern_data.get('status', 'pending')
        if status == 'confirmed':
            return 0.5
        elif status == 'completed':
            return 1.0
        else:
            return 0.0
    
    def _get_pattern_success_rate(self, pattern_type: str) -> float:
        """Get historical success rate for pattern type"""
        # Placeholder - would query database for historical success rates
        success_rates = {
            'head_and_shoulders': 0.65,
            'double_top': 0.70,
            'triangle': 0.55,
            'channel': 0.60,
            'flag': 0.75
        }
        return success_rates.get(pattern_type, 0.60)
    
    def _calculate_quality_score(self, features: Dict[str, float], pattern_data: Dict[str, Any]) -> float:
        """Calculate feature quality score based on data completeness"""
        total_features = len(self.feature_names)
        present_features = len([f for f in features.values() if f != 0.0])
        
        # Base score from feature completeness
        completeness_score = present_features / total_features
        
        # Penalize if key pattern data is missing
        penalties = 0.0
        if not pattern_data.get('support'):
            penalties += 0.1
        if not pattern_data.get('resistance'):
            penalties += 0.1
        if not pattern_data.get('target'):
            penalties += 0.1
        
        quality = max(0.0, completeness_score - penalties)
        return quality
    
    def _ensure_complete_feature_set(self, features: Dict[str, float]) -> Dict[str, float]:
        """Ensure all expected features are present with default values"""
        complete_features = {}
        
        for feature_name in self.feature_names:
            complete_features[feature_name] = features.get(feature_name, 0.0)
        
        return complete_features
    
    def _create_default_feature_set(self, pattern_id: str) -> FeatureSet:
        """Create default feature set when extraction fails"""
        default_features = {name: 0.0 for name in self.feature_names}
        
        return FeatureSet(
            features=default_features,
            feature_names=self.feature_names,
            extraction_time=datetime.now(timezone.utc),
            pattern_id=pattern_id,
            version=self.feature_version,
            quality_score=0.1  # Low quality for failed extraction
        )

def create_synthetic_pattern_data(pattern_type: str = "head_and_shoulders") -> Dict[str, Any]:
    """Create synthetic pattern data for testing"""
    return {
        "id": f"test_{pattern_type}_{int(datetime.now().timestamp())}",
        "symbol": "TEST",
        "pattern_type": pattern_type,
        "status": "confirmed",
        "confidence": 0.75,
        "support": 95.0,
        "resistance": 105.0,
        "target": 90.0,
        "entry": 94.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "current_price": 96.5,
            "analyst_confirmations": 2
        }
    }

def create_synthetic_price_history(days: int = 30) -> List[Dict]:
    """Create synthetic price history for testing"""
    import random
    
    price_history = []
    base_price = 100.0
    
    for i in range(days):
        # Add some random price movement
        change = random.uniform(-0.02, 0.02)  # ±2% daily change
        base_price *= (1 + change)
        
        high = base_price * random.uniform(1.001, 1.02)
        low = base_price * random.uniform(0.98, 0.999)
        volume = random.uniform(1000000, 5000000)
        
        price_history.append({
            "open": base_price,
            "high": high,
            "low": low,
            "close": base_price,
            "volume": volume,
            "timestamp": (datetime.now() - timedelta(days=days-i)).isoformat()
        })
    
    return price_history