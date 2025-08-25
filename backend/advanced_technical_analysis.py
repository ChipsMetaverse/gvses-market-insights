"""
Advanced Technical Analysis Module for G'sves Market Insights
Provides Fibonacci, MACD, Bollinger Bands, and advanced level calculations
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AdvancedTechnicalAnalysis:
    """Advanced technical analysis calculations"""
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float, is_uptrend: bool = True) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        """
        diff = high - low
        
        if is_uptrend:
            # Retracement levels from high
            levels = {
                'fib_0': high,
                'fib_236': high - (diff * 0.236),
                'fib_382': high - (diff * 0.382),
                'fib_500': high - (diff * 0.500),
                'fib_618': high - (diff * 0.618),
                'fib_786': high - (diff * 0.786),
                'fib_1000': low,
                # Extension levels
                'fib_1272': high + (diff * 0.272),
                'fib_1618': high + (diff * 0.618),
            }
        else:
            # Retracement levels from low
            levels = {
                'fib_0': low,
                'fib_236': low + (diff * 0.236),
                'fib_382': low + (diff * 0.382),
                'fib_500': low + (diff * 0.500),
                'fib_618': low + (diff * 0.618),
                'fib_786': low + (diff * 0.786),
                'fib_1000': high,
                # Extension levels
                'fib_1272': low - (diff * 0.272),
                'fib_1618': low - (diff * 0.618),
            }
            
        return {k: round(v, 2) for k, v in levels.items()}
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        """
        if len(prices) < slow_period:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
            
        prices_array = np.array(prices)
        
        # Calculate EMAs
        ema_fast = AdvancedTechnicalAnalysis._calculate_ema(prices_array, fast_period)
        ema_slow = AdvancedTechnicalAnalysis._calculate_ema(prices_array, slow_period)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        signal_line = AdvancedTechnicalAnalysis._calculate_ema(macd_line, signal_period)
        
        # MACD histogram
        histogram = macd_line[-1] - signal_line[-1]
        
        # Determine trend
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            trend = 'bullish_crossover'
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            trend = 'bearish_crossover'
        elif macd_line[-1] > signal_line[-1]:
            trend = 'bullish'
        else:
            trend = 'bearish'
            
        return {
            'macd': round(macd_line[-1], 3),
            'signal': round(signal_line[-1], 3),
            'histogram': round(histogram, 3),
            'trend': trend
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands
        """
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0, 'position': 0}
            
        prices_array = np.array(prices[-period:])
        
        # Middle band (SMA)
        middle = np.mean(prices_array)
        
        # Standard deviation
        std = np.std(prices_array)
        
        # Upper and lower bands
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        # Band width
        width = upper - lower
        
        # Current price position (0 = lower band, 1 = upper band)
        current_price = prices[-1]
        position = (current_price - lower) / width if width > 0 else 0.5
        
        return {
            'upper': round(upper, 2),
            'middle': round(middle, 2),
            'lower': round(lower, 2),
            'width': round(width, 2),
            'position': round(position, 3),
            'squeeze': bool(width < np.mean([abs(prices[i] - prices[i-1]) for i in range(max(-10, -len(prices)+1), 0)]))
        }
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        """
        if len(prices) < period + 1:
            return 50.0
            
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        if down == 0:
            return 100.0
            
        rs = up / down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        # Smooth the RSI
        for delta in deltas[period:]:
            if delta > 0:
                up = (up * (period - 1) + delta) / period
                down = (down * (period - 1)) / period
            else:
                up = (up * (period - 1)) / period
                down = (down * (period - 1) - delta) / period
                
            if down == 0:
                return 100.0
                
            rs = up / down
            rsi = 100.0 - (100.0 / (1.0 + rs))
            
        return round(rsi, 2)
    
    @staticmethod
    def calculate_stochastic(high: List[float], low: List[float], close: List[float], period: int = 14) -> Dict[str, float]:
        """
        Calculate Stochastic Oscillator
        """
        if len(close) < period:
            return {'k': 50, 'd': 50, 'signal': 'neutral'}
            
        # Calculate %K
        lowest_low = min(low[-period:])
        highest_high = max(high[-period:])
        
        if highest_high == lowest_low:
            k = 50
        else:
            k = ((close[-1] - lowest_low) / (highest_high - lowest_low)) * 100
            
        # %D is 3-period SMA of %K (simplified)
        d = k  # Simplified for single calculation
        
        # Determine signal
        if k > 80:
            signal = 'overbought'
        elif k < 20:
            signal = 'oversold'
        else:
            signal = 'neutral'
            
        return {
            'k': round(k, 2),
            'd': round(d, 2),
            'signal': signal
        }
    
    @staticmethod
    def calculate_advanced_levels(prices: List[float], volume: List[float], current_price: float) -> Dict[str, Any]:
        """
        Calculate advanced trading levels (LTB, ST, QE) with confluence
        """
        if len(prices) < 200:
            # Fallback for insufficient data
            return AdvancedTechnicalAnalysis._calculate_simple_levels(current_price)
            
        # Calculate moving averages
        ma_20 = np.mean(prices[-20:])
        ma_50 = np.mean(prices[-50:])
        ma_200 = np.mean(prices[-200:])
        
        # Find recent high and low
        recent_high = max(prices[-50:])
        recent_low = min(prices[-50:])
        
        # Calculate Fibonacci levels
        fib_levels = AdvancedTechnicalAnalysis.calculate_fibonacci_levels(
            recent_high, recent_low, current_price > ma_50
        )
        
        # Volume profile - find high volume nodes
        volume_nodes = AdvancedTechnicalAnalysis._find_volume_nodes(prices[-50:], volume[-50:])
        
        # Calculate Load the Boat (LTB) level
        # Confluence of 200-day MA, 61.8% Fib, and high volume node
        ltb_candidates = [
            ma_200,
            fib_levels['fib_618'],
            volume_nodes['support'] if volume_nodes else ma_200 * 0.95
        ]
        ltb = np.mean([x for x in ltb_candidates if x < current_price])
        if np.isnan(ltb) or ltb == 0:
            ltb = current_price * 0.92  # 8% below current
            
        # Calculate Swing Trade (ST) level
        # Confluence of 50-day MA, 50% Fib, and consolidation zone
        st_candidates = [
            ma_50,
            fib_levels['fib_500'],
            (ma_20 + ma_50) / 2
        ]
        st = np.mean([x for x in st_candidates if ltb < x < current_price])
        if np.isnan(st) or st == 0:
            st = current_price * 0.96  # 4% below current
            
        # Calculate Quick Entry (QE) level
        # Near recent highs or breakout zones
        qe_candidates = [
            recent_high * 0.98,  # Just below recent high
            ma_20,
            current_price * 1.02  # 2% above current for momentum
        ]
        qe = np.mean([x for x in qe_candidates if x > current_price])
        if np.isnan(qe) or qe == 0:
            qe = current_price * 1.03  # 3% above current
            
        return {
            'ltb_level': round(ltb, 2),
            'st_level': round(st, 2),
            'qe_level': round(qe, 2),
            'ma_20': round(ma_20, 2),
            'ma_50': round(ma_50, 2),
            'ma_200': round(ma_200, 2),
            'recent_high': round(recent_high, 2),
            'recent_low': round(recent_low, 2),
            'fib_levels': fib_levels,
            'volume_profile': volume_nodes
        }
    
    @staticmethod
    def identify_support_resistance(prices: List[float], volume: List[float]) -> Dict[str, List[Dict]]:
        """
        Identify support and resistance levels with strength ratings
        """
        if len(prices) < 20:
            return {'support': [], 'resistance': []}
            
        levels = []
        
        # Find local highs and lows
        for i in range(10, len(prices) - 10):
            # Local high
            if prices[i] == max(prices[i-10:i+11]):
                levels.append({
                    'price': prices[i],
                    'type': 'resistance',
                    'strength': AdvancedTechnicalAnalysis._calculate_level_strength(prices, prices[i], volume[i]),
                    'touches': AdvancedTechnicalAnalysis._count_touches(prices, prices[i])
                })
            # Local low
            elif prices[i] == min(prices[i-10:i+11]):
                levels.append({
                    'price': prices[i],
                    'type': 'support',
                    'strength': AdvancedTechnicalAnalysis._calculate_level_strength(prices, prices[i], volume[i]),
                    'touches': AdvancedTechnicalAnalysis._count_touches(prices, prices[i])
                })
        
        # Sort by strength and filter
        support_levels = sorted(
            [l for l in levels if l['type'] == 'support'],
            key=lambda x: x['strength'],
            reverse=True
        )[:5]
        
        resistance_levels = sorted(
            [l for l in levels if l['type'] == 'resistance'],
            key=lambda x: x['strength'],
            reverse=True
        )[:5]
        
        # Add descriptions
        for level in support_levels:
            level['description'] = AdvancedTechnicalAnalysis._describe_level(level)
            
        for level in resistance_levels:
            level['description'] = AdvancedTechnicalAnalysis._describe_level(level)
            
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }
    
    # Helper methods
    @staticmethod
    def _calculate_ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
            
        return ema
    
    @staticmethod
    def _find_volume_nodes(prices: List[float], volume: List[float]) -> Optional[Dict[str, float]]:
        """Find high volume price nodes"""
        if not prices or not volume:
            return None
            
        # Create price bins
        price_min, price_max = min(prices), max(prices)
        bins = np.linspace(price_min, price_max, 20)
        
        # Accumulate volume in each bin
        volume_profile = {}
        for p, v in zip(prices, volume):
            bin_idx = np.digitize(p, bins) - 1
            if 0 <= bin_idx < len(bins) - 1:
                bin_price = (bins[bin_idx] + bins[bin_idx + 1]) / 2
                volume_profile[bin_price] = volume_profile.get(bin_price, 0) + v
                
        if not volume_profile:
            return None
            
        # Find highest volume node
        max_volume_price = max(volume_profile, key=volume_profile.get)
        
        return {
            'support': round(max_volume_price * 0.98, 2),
            'resistance': round(max_volume_price * 1.02, 2),
            'poc': round(max_volume_price, 2)  # Point of Control
        }
    
    @staticmethod
    def _calculate_simple_levels(current_price: float) -> Dict[str, Any]:
        """Simple level calculation when insufficient data"""
        return {
            'ltb_level': round(current_price * 0.92, 2),  # 8% below
            'st_level': round(current_price * 0.96, 2),   # 4% below
            'qe_level': round(current_price * 1.03, 2),   # 3% above
            'ma_20': round(current_price * 0.99, 2),
            'ma_50': round(current_price * 0.97, 2),
            'ma_200': round(current_price * 0.93, 2),
            'recent_high': round(current_price * 1.05, 2),
            'recent_low': round(current_price * 0.95, 2),
            'fib_levels': {},
            'volume_profile': None
        }
    
    @staticmethod
    def _calculate_level_strength(prices: List[float], level: float, volume: float) -> str:
        """Calculate strength rating for a level"""
        touches = AdvancedTechnicalAnalysis._count_touches(prices, level)
        
        if touches >= 5:
            return "Strong"
        elif touches >= 3:
            return "Moderate"
        else:
            return "Weak"
    
    @staticmethod
    def _count_touches(prices: List[float], level: float, tolerance: float = 0.02) -> int:
        """Count how many times price touched a level"""
        touches = 0
        for price in prices:
            if abs(price - level) / level <= tolerance:
                touches += 1
        return touches
    
    @staticmethod
    def _describe_level(level: Dict) -> str:
        """Generate description for a support/resistance level"""
        touches = level['touches']
        strength = level['strength']
        
        if touches >= 5:
            return f"{strength} level tested {touches} times"
        elif touches >= 3:
            return f"{strength} historical pivot"
        else:
            return f"{strength} recent level"