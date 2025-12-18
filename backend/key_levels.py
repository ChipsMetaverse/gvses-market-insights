"""
Key Levels Generator - Phase 3
Generates 5 key horizontal price levels from pivot data.
Uses actual pivot structure instead of simple min/max.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from pivot_detector_mtf import PivotPoint


class KeyLevelsGenerator:
    """
    Generate 5 key trading levels:
    - BL (Buy Low / Bottom Line): Most significant recent pivot low
    - SH (Swing High / Sell High): Most significant recent pivot high
    - BTD (Buy The Dip): Secondary pivot low for dip buying
    - PDH (Previous Day High): From daily timeframe data
    - PDL (Previous Day Low): From daily timeframe data
    """

    def __init__(self, lookback_bars: int = 50):
        """
        Args:
            lookback_bars: How many recent bars to consider for key levels
        """
        self.lookback_bars = lookback_bars

    def generate_all_levels(
        self,
        pivot_highs: List[PivotPoint],
        pivot_lows: List[PivotPoint],
        candles: List[Dict[str, Any]],
        daily_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate all 5 key levels.

        Args:
            pivot_highs: Detected pivot highs
            pivot_lows: Detected pivot lows
            candles: Full candle data
            daily_data: Optional dict with 'pdh' and 'pdl' from daily timeframe

        Returns:
            Dictionary of key levels with prices and metadata
        """
        # Get recent pivots only
        recent_highs = self._get_recent_pivots(pivot_highs, candles)
        recent_lows = self._get_recent_pivots(pivot_lows, candles)

        levels = {}

        # BL (Buy Low) - Most significant recent low
        bl_level = self._calculate_bl(recent_lows, candles)
        if bl_level:
            levels['BL'] = bl_level

        # SH (Sell High) - Most significant recent high
        sh_level = self._calculate_sh(recent_highs, candles)
        if sh_level:
            levels['SH'] = sh_level

        # BTD (Buy The Dip) - Secondary low for dip buying
        btd_level = self._calculate_btd(recent_lows, candles, bl_price=bl_level['price'] if bl_level else None)
        if btd_level:
            levels['BTD'] = btd_level

        # PDH/PDL from daily data if available
        if daily_data and 'pdh' in daily_data and 'pdl' in daily_data:
            # Always add PDH/PDL - they are important reference levels
            # even if they overlap with other levels (SH/BL)
            levels['PDH'] = {
                'price': daily_data['pdh'],
                'label': 'PDH',
                'color': '#ff9800',  # Orange
                'style': 'dotted',
                'width': 1
            }

            levels['PDL'] = {
                'price': daily_data['pdl'],
                'label': 'PDL',
                'color': '#ff9800',  # Orange
                'style': 'dotted',
                'width': 1
            }

        return levels

    def _get_recent_pivots(
        self,
        pivots: List[PivotPoint],
        candles: List[Dict[str, Any]]
    ) -> List[PivotPoint]:
        """
        Filter pivots to only recent ones (within lookback window).

        Args:
            pivots: All pivots
            candles: Candle data

        Returns:
            Recent pivots only
        """
        if not pivots or not candles:
            return []

        # Get cutoff index
        cutoff_index = max(0, len(candles) - self.lookback_bars)

        # Filter pivots
        return [p for p in pivots if p.index >= cutoff_index]

    def _calculate_bl(
        self,
        pivot_lows: List[PivotPoint],
        candles: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate BL (Buy Low) level.

        Strategy:
        - Find the lowest pivot low in recent range
        - This is the strongest support level

        Args:
            pivot_lows: Recent pivot lows
            candles: Candle data

        Returns:
            Level dictionary or None
        """
        if not pivot_lows:
            return None

        # Find lowest pivot
        bl_pivot = min(pivot_lows, key=lambda p: p.price)

        return {
            'price': bl_pivot.price,
            'label': 'BL',
            'color': '#4caf50',  # Green
            'style': 'dashed',
            'width': 2,
            'metadata': {
                'pivot_index': bl_pivot.index,
                'timestamp': bl_pivot.timestamp
            }
        }

    def _calculate_sh(
        self,
        pivot_highs: List[PivotPoint],
        candles: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate SH (Sell High) level.

        Strategy:
        - Find the highest pivot high in recent range
        - This is the strongest resistance level

        Args:
            pivot_highs: Recent pivot highs
            candles: Candle data

        Returns:
            Level dictionary or None
        """
        if not pivot_highs:
            return None

        # Find highest pivot
        sh_pivot = max(pivot_highs, key=lambda p: p.price)

        return {
            'price': sh_pivot.price,
            'label': 'SH',
            'color': '#f44336',  # Red
            'style': 'dashed',
            'width': 2,
            'metadata': {
                'pivot_index': sh_pivot.index,
                'timestamp': sh_pivot.timestamp
            }
        }

    def _calculate_btd(
        self,
        pivot_lows: List[PivotPoint],
        candles: List[Dict[str, Any]],
        bl_price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate BTD (Buy The Dip) level using 200-day moving average.

        Strategy:
        - Calculate simple moving average (SMA) from closing prices
        - Uses up to 200 periods, or all available if less than 200
        - Represents typical long-term trend support level
        - Horizontal line showing institutional buy zone

        Args:
            pivot_lows: Not used (kept for API compatibility)
            candles: Candle data for SMA calculation
            bl_price: BL price if already calculated

        Returns:
            Level dictionary with MA or None if insufficient data
        """
        if not candles or len(candles) < 50:
            # Need at least 50 candles for meaningful MA
            return None

        # For BTD: Use exactly 200 periods (last 200 candles) for true 200 SMA
        # This matches the standard definition of a 200-period Simple Moving Average
        period = min(200, len(candles))
        selected_candles = candles[-period:]  # Last 200 candles
        closing_prices = [candle['close'] for candle in selected_candles]

        # Debug: Log the date range being used for BTD calculation
        if len(selected_candles) > 0:
            from datetime import datetime
            first_candle_time = selected_candles[0].get('time', 0)
            last_candle_time = selected_candles[-1].get('time', 0)
            first_date = datetime.fromtimestamp(first_candle_time).strftime('%Y-%m-%d') if first_candle_time else 'unknown'
            last_date = datetime.fromtimestamp(last_candle_time).strftime('%Y-%m-%d') if last_candle_time else 'unknown'
            print(f"[BTD DEBUG] Total candles available: {len(candles)}, Using last {period} candles")
            print(f"[BTD DEBUG] Date range: {first_date} to {last_date}")
            print(f"[BTD DEBUG] First close: ${selected_candles[0]['close']:.2f}, Last close: ${selected_candles[-1]['close']:.2f}")

        # Calculate simple moving average of last 200 periods
        sma_value = sum(closing_prices) / len(closing_prices)
        print(f"[BTD DEBUG] Calculated {period}-period SMA: ${sma_value:.2f}")

        # NOTE: Always show BTD (200 SMA) - it's a critical institutional indicator
        # Removed 1% proximity filter that was hiding TSLA's BTD ($379 vs BL $382 = 0.98%)

        # Always label as "200 SMA" for consistency across all timeframes
        label = 'BTD (200 SMA)'

        return {
            'price': sma_value,
            'label': label,
            'color': '#2196f3',  # Blue
            'style': 'dashed',
            'width': 2,
            'metadata': {
                'period': period,
                'type': 'sma',
                'description': f'{period}-period simple moving average'
            }
        }

    def levels_to_api_format(
        self,
        levels: Dict[str, Dict[str, Any]],
        candles: List[Dict[str, Any]],
        timeframe: str = "1d"  # NEW: Timeframe for extension calculation
    ) -> List[Dict[str, Any]]:
        """
        Convert key levels to API format for frontend.

        FIXED: Now uses timeframe-aware extension like trendlines.
        - Intraday (1m-4H): Extends ±1-2 trading days only
        - Daily+: Uses full dataset as before

        Args:
            levels: Dictionary of key levels
            candles: Candle data for time range
            timeframe: Chart timeframe (1m, 5m, 15m, 30m, 1H, 2H, 4H, 1d, 1wk, 1mo)

        Returns:
            List of level objects for API response
        """
        if not candles:
            return []

        # For intraday: Limit to recent bars only (same as trendline logic)
        if timeframe in ["1m", "5m", "15m", "30m", "1H", "2H", "4H"]:
            # Limit to ~1 trading day of bars
            max_lookback_bars = 390  # ~6.5 hours for 1m bars (1 trading day)
            if timeframe == "5m":
                max_lookback_bars = 78  # ~6.5 hours for 5m bars
            elif timeframe == "15m":
                max_lookback_bars = 26  # ~6.5 hours for 15m bars
            elif timeframe == "30m":
                max_lookback_bars = 13  # ~6.5 hours for 30m bars
            elif timeframe in ["1H", "2H", "4H"]:
                max_lookback_bars = 7   # ~1 trading day for hourly bars

            # Use recent bars only
            lookback_start = max(0, len(candles) - max_lookback_bars)
            start_time = candles[lookback_start]['time']

            # Extend 1-2 days into future (same as trendlines)
            extension_days = 1 if timeframe in ["1m", "5m", "15m", "30m"] else 2
            end_time = candles[-1]['time'] + (extension_days * 86400)
        else:
            # Daily+: Use full dataset as before
            start_time = candles[0]['time']
            # Extend 30 days into future (same as trendlines)
            end_time = candles[-1]['time'] + (30 * 86400)

        api_levels = []

        for level_name, level_data in levels.items():
            api_levels.append({
                "type": "key_level",
                "start": {"time": start_time, "price": level_data['price']},
                "end": {"time": end_time, "price": level_data['price']},
                "color": level_data['color'],
                "style": level_data['style'],
                "width": level_data['width'],
                "label": level_data['label'],
                "deleteable": True,
                "metadata": level_data.get('metadata', {})
            })

        return api_levels
