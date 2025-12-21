"""
Multi-Timeframe Pivot Detector
Matches Pine Script ta.pivothigh/ta.pivotlow logic
NO ATR - uses structure + MTF + spacing only
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PivotPoint:
    """Represents a detected pivot point"""
    index: int          # Bar index in array
    price: float        # Price at pivot
    is_high: bool       # True if pivot high, False if pivot low
    timestamp: int      # Unix timestamp (optional)


class MTFPivotDetector:
    """
    Multi-timeframe pivot detector matching Pine Script logic.
    Implements ta.pivothigh(left, right) and ta.pivotlow(left, right) equivalents.
    """

    def __init__(self, left_bars: int = 2, right_bars: int = 2):
        """
        Initialize pivot detector with window parameters.

        Args:
            left_bars: Number of bars to the left of pivot to check
            right_bars: Number of bars to the right of pivot to check
        """
        self.left_bars = left_bars
        self.right_bars = right_bars
        # Phase 1 Fix: Adaptive spacing will be calculated per dataset
        self.min_spacing_bars = None  # Will be calculated adaptively
        # Phase 1 Fix: Relaxed threshold for intraday timeframes
        self.min_percent_move = 0.01  # 1% minimum (down from 2.5%)

    def find_pivots_single_tf(
        self,
        high: np.ndarray,
        low: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> Tuple[List[PivotPoint], List[PivotPoint]]:
        """
        Python equivalent of Pine Script's:
        ta.pivothigh(leftBars, rightBars)
        ta.pivotlow(leftBars, rightBars)

        A pivot high at bar i means:
        - high[i] >= high[i-left_bars] ... high[i-1]
        - high[i] >= high[i+1] ... high[i+right_bars]

        A pivot low at bar i means:
        - low[i] <= low[i-left_bars] ... low[i-1]
        - low[i] <= low[i+1] ... low[i+right_bars]

        Args:
            high: Array of high prices
            low: Array of low prices
            timestamps: Optional array of timestamps

        Returns:
            Tuple of (pivot_highs, pivot_lows) as lists of PivotPoint objects
        """
        if len(high) != len(low):
            raise ValueError("High and low arrays must have same length")

        if len(high) < self.left_bars + self.right_bars + 1:
            return [], []

        pivot_highs: List[PivotPoint] = []
        pivot_lows: List[PivotPoint] = []

        # Scan for pivots
        for i in range(self.left_bars, len(high) - self.right_bars):
            # Check pivot high
            # Must be >= all bars in left window and right window
            is_pivot_high = True
            current_high = high[i]

            # Check left window
            for j in range(i - self.left_bars, i):
                if high[j] > current_high:
                    is_pivot_high = False
                    break

            # Check right window
            if is_pivot_high:
                for j in range(i + 1, i + self.right_bars + 1):
                    if high[j] > current_high:
                        is_pivot_high = False
                        break

            if is_pivot_high:
                pivot = PivotPoint(
                    index=i,
                    price=float(current_high),
                    is_high=True,
                    timestamp=int(timestamps[i]) if timestamps is not None else 0
                )
                pivot_highs.append(pivot)

            # Check pivot low
            is_pivot_low = True
            current_low = low[i]

            # Check left window
            for j in range(i - self.left_bars, i):
                if low[j] < current_low:
                    is_pivot_low = False
                    break

            # Check right window
            if is_pivot_low:
                for j in range(i + 1, i + self.right_bars + 1):
                    if low[j] < current_low:
                        is_pivot_low = False
                        break

            if is_pivot_low:
                pivot = PivotPoint(
                    index=i,
                    price=float(current_low),
                    is_high=False,
                    timestamp=int(timestamps[i]) if timestamps is not None else 0
                )
                pivot_lows.append(pivot)

        return pivot_highs, pivot_lows

    def filter_by_spacing(
        self,
        pivots: List[PivotPoint],
        min_bars: int
    ) -> List[PivotPoint]:
        """
        Filter pivots to ensure minimum bar spacing.
        If two pivots are too close, keep the more extreme one.

        Args:
            pivots: List of pivot points
            min_bars: Minimum bars between pivots

        Returns:
            Filtered list of pivots
        """
        if len(pivots) <= 1:
            return pivots

        filtered = [pivots[0]]

        for pivot in pivots[1:]:
            last_pivot = filtered[-1]
            spacing = pivot.index - last_pivot.index

            if spacing >= min_bars:
                # Sufficient spacing, keep it
                filtered.append(pivot)
            else:
                # Too close - keep the more extreme one
                if pivot.is_high:
                    # For highs, keep the higher price
                    if pivot.price > last_pivot.price:
                        filtered[-1] = pivot
                else:
                    # For lows, keep the lower price
                    if pivot.price < last_pivot.price:
                        filtered[-1] = pivot

        return filtered

    def filter_by_percent_move(
        self,
        pivots: List[PivotPoint],
        min_percent: float
    ) -> List[PivotPoint]:
        """
        Filter pivots to ensure minimum percentage price move.

        Args:
            pivots: List of pivot points
            min_percent: Minimum percent move (e.g., 0.01 for 1%)

        Returns:
            Filtered list of pivots
        """
        if len(pivots) <= 1:
            return pivots

        filtered = [pivots[0]]

        for pivot in pivots[1:]:
            last_pivot = filtered[-1]
            price_change = abs(pivot.price - last_pivot.price)
            percent_change = price_change / last_pivot.price

            if percent_change >= min_percent:
                filtered.append(pivot)

        return filtered

    def filter_by_trend_structure(
        self,
        pivot_highs: List[PivotPoint],
        pivot_lows: List[PivotPoint],
        trend_direction: str = "auto"
    ) -> Tuple[List[PivotPoint], List[PivotPoint]]:
        """
        Filter pivots based on trend structure:
        - In uptrend: Keep higher lows, filter lower lows
        - In downtrend: Keep lower highs, filter higher highs

        Args:
            pivot_highs: List of pivot high points
            pivot_lows: List of pivot low points
            trend_direction: "up", "down", or "auto"

        Returns:
            Filtered (pivot_highs, pivot_lows)
        """
        if trend_direction == "auto":
            # Simple trend detection: compare first and last prices
            if len(pivot_lows) >= 2:
                if pivot_lows[-1].price > pivot_lows[0].price:
                    trend_direction = "up"
                else:
                    trend_direction = "down"
            else:
                # Not enough data, return as-is
                return pivot_highs, pivot_lows

        filtered_lows = []
        filtered_highs = []

        if trend_direction == "up":
            # In uptrend, keep higher lows
            for pivot in pivot_lows:
                if not filtered_lows or pivot.price > filtered_lows[-1].price:
                    filtered_lows.append(pivot)
            filtered_highs = pivot_highs  # Keep all highs in uptrend

        elif trend_direction == "down":
            # In downtrend, keep lower highs
            for pivot in pivot_highs:
                if not filtered_highs or pivot.price < filtered_highs[-1].price:
                    filtered_highs.append(pivot)
            filtered_lows = pivot_lows  # Keep all lows in downtrend

        return filtered_highs, filtered_lows

    def detect_pivots_with_filters(
        self,
        high: np.ndarray,
        low: np.ndarray,
        timestamps: Optional[np.ndarray] = None,
        apply_spacing: bool = True,
        apply_percent_filter: bool = True,
        apply_trend_filter: bool = True,
        trend_direction: str = "auto"
    ) -> Tuple[List[PivotPoint], List[PivotPoint]]:
        """
        Complete pivot detection pipeline with all filters.

        Args:
            high: High prices
            low: Low prices
            timestamps: Optional timestamps
            apply_spacing: Apply minimum bar spacing filter
            apply_percent_filter: Apply minimum percent move filter
            apply_trend_filter: Apply trend structure filter
            trend_direction: "up", "down", or "auto"

        Returns:
            Filtered (pivot_highs, pivot_lows)
        """
        # Step 1: Basic pivot detection
        pivot_highs, pivot_lows = self.find_pivots_single_tf(high, low, timestamps)

        # Phase 1 Fix: Calculate adaptive spacing based on data length
        # Formula: max(3, int(0.05 * total_bars))
        # This ensures 15m (109 bars) uses spacing=5 instead of 15
        total_bars = len(high)
        adaptive_spacing = max(3, int(0.05 * total_bars))

        # Step 2: Apply spacing filter with adaptive spacing
        if apply_spacing:
            pivot_highs = self.filter_by_spacing(pivot_highs, adaptive_spacing)
            pivot_lows = self.filter_by_spacing(pivot_lows, adaptive_spacing)

        # Step 3: Apply percent move filter
        if apply_percent_filter:
            pivot_highs = self.filter_by_percent_move(pivot_highs, self.min_percent_move)
            pivot_lows = self.filter_by_percent_move(pivot_lows, self.min_percent_move)

        # Step 4: Apply trend structure filter
        if apply_trend_filter:
            pivot_highs, pivot_lows = self.filter_by_trend_structure(
                pivot_highs, pivot_lows, trend_direction
            )

        return pivot_highs, pivot_lows

    def find_htf_pivots_confirmed_ltf(
        self,
        htf_high: np.ndarray,
        htf_low: np.ndarray,
        htf_timestamps: np.ndarray,
        ltf_high: np.ndarray,
        ltf_low: np.ndarray,
        ltf_timestamps: np.ndarray
    ) -> Tuple[List[PivotPoint], List[PivotPoint]]:
        """
        Multi-timeframe pivot detection:
        1. Find pivots on HTF (4H) - establishes structural pivots
        2. Map to LTF (1H) - find exact pivot location on lower timeframe
        3. Confirm pivot still valid on LTF
        4. Phase 1 Fix: Apply adaptive filters to HTF pivots

        This matches Pine Script's request.security() + confirmation logic.

        Args:
            htf_high: Higher timeframe high prices
            htf_low: Higher timeframe low prices
            htf_timestamps: HTF timestamps
            ltf_high: Lower timeframe high prices
            ltf_low: Lower timeframe low prices
            ltf_timestamps: LTF timestamps

        Returns:
            Tuple of (confirmed_pivot_highs, confirmed_pivot_lows)
        """
        # Phase 1 Fix: Use detect_pivots_with_filters instead of find_pivots_single_tf
        # This ensures adaptive spacing and filters are applied to HTF pivots
        htf_pivot_highs, htf_pivot_lows = self.detect_pivots_with_filters(
            htf_high, htf_low, htf_timestamps,
            apply_spacing=True,
            apply_percent_filter=True,
            apply_trend_filter=False  # Keep trend filter off for MTF
        )

        # Step 2: Map HTF pivots to LTF and refine location
        confirmed_highs = []
        confirmed_lows = []

        # Map pivot highs
        for htf_pivot in htf_pivot_highs:
            # Find LTF bars within the HTF pivot's time window
            # Look for the actual high within +/- 1 HTF bar around pivot
            ltf_pivot = self._map_htf_pivot_to_ltf(
                htf_pivot,
                ltf_high,
                ltf_timestamps,
                is_high=True
            )
            if ltf_pivot:
                confirmed_highs.append(ltf_pivot)

        # Map pivot lows
        for htf_pivot in htf_pivot_lows:
            ltf_pivot = self._map_htf_pivot_to_ltf(
                htf_pivot,
                ltf_low,
                ltf_timestamps,
                is_high=False
            )
            if ltf_pivot:
                confirmed_lows.append(ltf_pivot)

        return confirmed_highs, confirmed_lows

    def _map_htf_pivot_to_ltf(
        self,
        htf_pivot: PivotPoint,
        ltf_prices: np.ndarray,
        ltf_timestamps: np.ndarray,
        is_high: bool,
        search_window_seconds: int = 14400  # 4 hours
    ) -> Optional[PivotPoint]:
        """
        Map a HTF pivot to its corresponding location on LTF.

        Strategy:
        1. Find LTF bars within time window of HTF pivot
        2. Find the extreme (high/low) within that window
        3. Verify it's actually a pivot on LTF (optional strict mode)

        Args:
            htf_pivot: Pivot detected on higher timeframe
            ltf_prices: LTF price array (high or low)
            ltf_timestamps: LTF timestamps
            is_high: True for pivot high, False for pivot low
            search_window_seconds: Time window to search (default 4H)

        Returns:
            PivotPoint on LTF, or None if not confirmed
        """
        # Find LTF bars within search window
        htf_time = htf_pivot.timestamp
        time_tolerance = search_window_seconds

        # Boolean mask for bars within window
        within_window = (
            (ltf_timestamps >= htf_time - time_tolerance) &
            (ltf_timestamps <= htf_time + time_tolerance)
        )

        if not np.any(within_window):
            return None

        # Get indices within window
        window_indices = np.where(within_window)[0]

        # Find the extreme within this window
        if is_high:
            # Find highest high in window
            local_max_idx = window_indices[np.argmax(ltf_prices[window_indices])]
            extreme_price = ltf_prices[local_max_idx]
        else:
            # Find lowest low in window
            local_min_idx = window_indices[np.argmin(ltf_prices[window_indices])]
            extreme_price = ltf_prices[local_min_idx]
            local_max_idx = local_min_idx  # Reuse variable name

        # Create confirmed LTF pivot
        return PivotPoint(
            index=int(local_max_idx),
            price=float(extreme_price),
            is_high=is_high,
            timestamp=int(ltf_timestamps[local_max_idx])
        )

    def resample_to_higher_timeframe(
        self,
        ltf_candles: List[Dict[str, Any]],
        htf_interval_seconds: int = 14400  # 4H default
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Resample LTF candle data to HTF.
        Aggregates 1H bars into 4H bars.

        Args:
            ltf_candles: List of candle dicts with time, open, high, low, close
            htf_interval_seconds: HTF interval (default 14400 = 4 hours)

        Returns:
            Tuple of (htf_high, htf_low, htf_timestamps)
        """
        if not ltf_candles:
            return np.array([]), np.array([]), np.array([])

        # Group candles by HTF intervals
        htf_groups = {}

        for candle in ltf_candles:
            timestamp = candle['time']
            # Round down to HTF interval
            htf_bucket = (timestamp // htf_interval_seconds) * htf_interval_seconds

            if htf_bucket not in htf_groups:
                htf_groups[htf_bucket] = {
                    'high': candle['high'],
                    'low': candle['low'],
                    'time': htf_bucket
                }
            else:
                # Update high/low for this HTF bar
                htf_groups[htf_bucket]['high'] = max(
                    htf_groups[htf_bucket]['high'],
                    candle['high']
                )
                htf_groups[htf_bucket]['low'] = min(
                    htf_groups[htf_bucket]['low'],
                    candle['low']
                )

        # Convert to arrays
        sorted_buckets = sorted(htf_groups.keys())
        htf_high = np.array([htf_groups[t]['high'] for t in sorted_buckets])
        htf_low = np.array([htf_groups[t]['low'] for t in sorted_buckets])
        htf_timestamps = np.array(sorted_buckets)

        return htf_high, htf_low, htf_timestamps

    def pivots_to_dict(
        self,
        pivot_highs: List[PivotPoint],
        pivot_lows: List[PivotPoint],
        actual_spacing_used: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert pivot points to API-friendly dictionary format.

        Args:
            pivot_highs: List of pivot high points
            pivot_lows: List of pivot low points
            actual_spacing_used: The actual adaptive spacing used (optional)

        Returns:
            Dictionary with pivot high and low data
        """
        return {
            'pivot_highs': [
                {
                    'index': p.index,
                    'price': p.price,
                    'timestamp': p.timestamp
                }
                for p in pivot_highs
            ],
            'pivot_lows': [
                {
                    'index': p.index,
                    'price': p.price,
                    'timestamp': p.timestamp
                }
                for p in pivot_lows
            ],
            'total_pivots': len(pivot_highs) + len(pivot_lows),
            'config': {
                'left_bars': self.left_bars,
                'right_bars': self.right_bars,
                'min_spacing_bars': actual_spacing_used or 'adaptive',
                'min_percent_move': self.min_percent_move
            }
        }
