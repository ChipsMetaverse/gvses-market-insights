"""
Trendline Builder - Phase 2
Builds exactly 2 main trendlines using touch-point maximization.
Superior to linear regression for trading trendlines.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pivot_detector_mtf import PivotPoint


@dataclass
class Trendline:
    """Represents a validated trendline"""
    line_type: str  # "support" or "resistance"
    start_index: int
    end_index: int
    start_price: float
    end_price: float
    slope: float
    touches: int  # Number of pivots touching this line
    pivot_indices: List[int]  # Which pivots touch this line
    color: str
    label: str


class TrendlineBuilder:
    """
    Build exactly 2 main trendlines from filtered MTF pivots.
    Uses touch-point maximization instead of linear regression.

    Professional standard: Trendlines must touch >= 3 pivot points.
    """

    def __init__(
        self,
        touch_tolerance_percent: float = 0.005,
        min_slope_threshold: float = 0.0005  # Minimum slope to avoid horizontal lines
    ):
        """
        Args:
            touch_tolerance_percent: How close price must be to line to count as "touch"
                                    (0.005 = 0.5% tolerance)
            min_slope_threshold: Minimum absolute slope to qualify as a diagonal trendline
                                (0.0005 = 0.05% price change per bar minimum)
                                Lines with |slope| < threshold are filtered out as horizontal
        """
        self.touch_tolerance = touch_tolerance_percent
        self.min_slope_threshold = min_slope_threshold

    def build_support_line(
        self,
        pivot_lows: List[PivotPoint],
        all_lows: np.ndarray,
        min_touches: int = 3
    ) -> Optional[Trendline]:
        """
        Build support trendline (connects pivot lows).

        Strategy:
        1. Try all combinations of 2 pivot points as potential line endpoints
        2. For each line, count how many other pivots "touch" it (within tolerance)
        3. Keep line with most touches (must be >= min_touches)
        4. Ensure line doesn't violate support (doesn't cross above any lows)
        5. Phase 1 Fix: Fall back to 2-touch if 3-touch fails

        Args:
            pivot_lows: List of pivot low points
            all_lows: Full array of low prices (for validation)
            min_touches: Minimum touches required for valid trendline

        Returns:
            Trendline object or None if no valid line found
        """
        if len(pivot_lows) < 2:
            return None

        best_line = None
        max_touches = 0

        # Try all pairs of pivots as potential trendline endpoints
        for i in range(len(pivot_lows)):
            for j in range(i + 1, len(pivot_lows)):
                p1 = pivot_lows[i]
                p2 = pivot_lows[j]

                # Calculate line parameters
                slope = (p2.price - p1.price) / (p2.index - p1.index)

                # FILTER: Skip near-horizontal lines (not true trendlines)
                # Horizontal lines with many touches are key levels, not trends
                if abs(slope) < self.min_slope_threshold:
                    continue  # Skip this pair - slope too flat to be a trendline

                # Count touches for this line
                touches, touching_indices = self._count_touches(
                    p1, slope, pivot_lows, is_support=True
                )

                # Validate: support line must not cross above any price
                if not self._validate_support_line(p1, slope, all_lows, p1.index, p2.index):
                    continue

                # Keep track of best line
                if touches >= min_touches and touches > max_touches:
                    max_touches = touches

                    # CRITICAL FIX: Use first and last pivots from touching_indices,
                    # not just p1 and p2 (which are the test pair)
                    # This ensures the line spans the full extent of all touching pivots
                    touching_pivots = [pivot_lows[i] for i, piv in enumerate(pivot_lows) if piv.index in touching_indices]
                    touching_pivots.sort(key=lambda p: p.index)
                    first_pivot = touching_pivots[0]
                    last_pivot = touching_pivots[-1]

                    # Recalculate end price using the slope at the last pivot's index
                    dx = last_pivot.index - first_pivot.index
                    end_price = first_pivot.price + (slope * dx)

                    best_line = Trendline(
                        line_type="support",
                        start_index=first_pivot.index,
                        end_index=last_pivot.index,
                        start_price=first_pivot.price,
                        end_price=end_price,
                        slope=slope,
                        touches=touches,
                        pivot_indices=touching_indices,
                        color="#00bcd4",  # Cyan
                        label="Lower Trend"
                    )

        # Phase 1 Fix: If no line with min_touches found, try 2-touch fallback
        if best_line is None and min_touches > 2:
            return self.build_support_line(pivot_lows, all_lows, min_touches=2)

        return best_line

    def build_resistance_line(
        self,
        pivot_highs: List[PivotPoint],
        all_highs: np.ndarray,
        min_touches: int = 3
    ) -> Optional[Trendline]:
        """
        Build resistance trendline (connects pivot highs).

        Same strategy as support, but:
        - Connects highs instead of lows
        - Validates line doesn't cross below any highs
        - Phase 1 Fix: Fall back to 2-touch if 3-touch fails

        Args:
            pivot_highs: List of pivot high points
            all_highs: Full array of high prices (for validation)
            min_touches: Minimum touches required

        Returns:
            Trendline object or None if no valid line found
        """
        if len(pivot_highs) < 2:
            return None

        best_line = None
        max_touches = 0

        # Try all pairs of pivots
        for i in range(len(pivot_highs)):
            for j in range(i + 1, len(pivot_highs)):
                p1 = pivot_highs[i]
                p2 = pivot_highs[j]

                # Calculate line parameters
                slope = (p2.price - p1.price) / (p2.index - p1.index)

                # FILTER: Skip near-horizontal lines (not true trendlines)
                # Horizontal lines with many touches are key levels, not trends
                if abs(slope) < self.min_slope_threshold:
                    continue  # Skip this pair - slope too flat to be a trendline

                # Count touches
                touches, touching_indices = self._count_touches(
                    p1, slope, pivot_highs, is_support=False
                )

                # Validate: resistance line must not cross below any price
                if not self._validate_resistance_line(p1, slope, all_highs, p1.index, p2.index):
                    continue

                # Keep track of best line
                if touches >= min_touches and touches > max_touches:
                    max_touches = touches

                    # CRITICAL FIX: Use first and last pivots from touching_indices,
                    # not just p1 and p2 (which are the test pair)
                    # This ensures the line spans the full extent of all touching pivots
                    touching_pivots = [pivot_highs[i] for i, piv in enumerate(pivot_highs) if piv.index in touching_indices]
                    touching_pivots.sort(key=lambda p: p.index)
                    first_pivot = touching_pivots[0]
                    last_pivot = touching_pivots[-1]

                    # Recalculate end price using the slope at the last pivot's index
                    dx = last_pivot.index - first_pivot.index
                    end_price = first_pivot.price + (slope * dx)

                    best_line = Trendline(
                        line_type="resistance",
                        start_index=first_pivot.index,
                        end_index=last_pivot.index,
                        start_price=first_pivot.price,
                        end_price=end_price,
                        slope=slope,
                        touches=touches,
                        pivot_indices=touching_indices,
                        color="#e91e63",  # Pink
                        label="Upper Trend"
                    )

        # Phase 1 Fix: If no line with min_touches found, try 2-touch fallback
        if best_line is None and min_touches > 2:
            return self.build_resistance_line(pivot_highs, all_highs, min_touches=2)

        return best_line

    def _count_touches(
        self,
        start_pivot: PivotPoint,
        slope: float,
        all_pivots: List[PivotPoint],
        is_support: bool
    ) -> Tuple[int, List[int]]:
        """
        Count how many pivots "touch" a trendline.

        A pivot touches if its price is within tolerance of the line's
        projected price at that bar index.

        Args:
            start_pivot: Starting point of line
            slope: Line slope
            all_pivots: All pivots to check
            is_support: True for support lines, False for resistance

        Returns:
            Tuple of (touch_count, list of pivot indices that touch)
        """
        touches = 0
        touching_indices = []

        for pivot in all_pivots:
            # Calculate expected price on line at this pivot's index
            dx = pivot.index - start_pivot.index
            line_price = start_pivot.price + (slope * dx)

            # Calculate tolerance
            tolerance = abs(line_price * self.touch_tolerance)

            # Check if pivot touches line
            price_diff = abs(pivot.price - line_price)

            if price_diff <= tolerance:
                touches += 1
                touching_indices.append(pivot.index)

        return touches, touching_indices

    def _validate_support_line(
        self,
        start_pivot: PivotPoint,
        slope: float,
        all_lows: np.ndarray,
        start_idx: int,
        end_idx: int
    ) -> bool:
        """
        Validate that support line doesn't violate any lows.

        Support line should never cross ABOVE actual price lows.

        Args:
            start_pivot: Line start point
            slope: Line slope
            all_lows: Array of all low prices
            start_idx: Start bar index
            end_idx: End bar index

        Returns:
            True if valid, False if line crosses above prices
        """
        for i in range(start_idx, min(end_idx + 1, len(all_lows))):
            dx = i - start_pivot.index
            line_price = start_pivot.price + (slope * dx)

            # Support line must be AT OR BELOW actual lows
            # Allow tiny tolerance for floating point
            if line_price > all_lows[i] * 1.001:  # 0.1% tolerance
                return False

        return True

    def _validate_resistance_line(
        self,
        start_pivot: PivotPoint,
        slope: float,
        all_highs: np.ndarray,
        start_idx: int,
        end_idx: int
    ) -> bool:
        """
        Validate that resistance line doesn't violate any highs.

        Resistance line should never cross BELOW actual price highs.

        Args:
            start_pivot: Line start point
            slope: Line slope
            all_highs: Array of all high prices
            start_idx: Start bar index
            end_idx: End bar index

        Returns:
            True if valid, False if line crosses below prices
        """
        for i in range(start_idx, min(end_idx + 1, len(all_highs))):
            dx = i - start_pivot.index
            line_price = start_pivot.price + (slope * dx)

            # Resistance line must be AT OR ABOVE actual highs
            if line_price < all_highs[i] * 0.999:  # 0.1% tolerance
                return False

        return True

    def trendline_to_dict(
        self,
        trendline: Trendline,
        candles: List[Dict[str, Any]],
        timeframe: str = "1d",  # NEW: Timeframe for extension calculation
        extend_right_days: Optional[int] = None,  # Now optional - auto-determined from timeframe
        extend_to_chart_start: bool = True  # Extend back (limited for intraday)
    ) -> Dict[str, Any]:
        """
        Convert Trendline to API-friendly format for frontend.

        FIXED: Now uses timeframe-aware extension to prevent off-screen trendlines.
        - Intraday (1m-4H): Extends ±1-2 trading days only
        - Daily+: Extends ±30+ days as before

        Args:
            trendline: Trendline object
            candles: Candle data for timestamp mapping
            timeframe: Chart timeframe (1m, 5m, 15m, 30m, 1H, 2H, 4H, 1d, 1wk, 1mo)
            extend_right_days: Number of days to extend past last candle (None = auto)
            extend_to_chart_start: If True, extend back (limited for intraday)

        Returns:
            Dictionary with start/end time and price
        """
        # Auto-determine extension based on timeframe if not provided
        if extend_right_days is None:
            extension_map = {
                # Intraday: Extend to end of next trading day only
                "1m": 1,    # 1 day = ~6.5 hours trading
                "5m": 1,
                "15m": 1,
                "30m": 1,
                "1H": 2,    # 2 days
                "2H": 2,
                "4H": 2,
                # Daily and beyond: Current behavior (project further)
                "1d": 30,   # 30 days
                "1wk": 60,  # 60 days
                "1mo": 90   # 90 days
            }
            extend_right_days = extension_map.get(timeframe, 30)
            print(f"🔧 [TRENDLINE] timeframe={timeframe}, extend_right_days={extend_right_days}")

        # Calculate extended start (limited for intraday to prevent off-screen lines)
        if extend_to_chart_start and trendline.start_index > 0:
            # For intraday: Only extend to start of current/previous trading day
            # Don't go back weeks if dataset is large
            if timeframe in ["1m", "5m", "15m", "30m", "1H", "2H", "4H"]:
                # Limit backward extension to ~1 trading day of bars
                max_lookback_bars = 390  # ~6.5 hours for 1m bars (1 trading day)
                if timeframe == "5m":
                    max_lookback_bars = 78  # ~6.5 hours for 5m bars
                elif timeframe == "15m":
                    max_lookback_bars = 26  # ~6.5 hours for 15m bars
                elif timeframe == "30m":
                    max_lookback_bars = 13  # ~6.5 hours for 30m bars
                elif timeframe in ["1H", "2H", "4H"]:
                    max_lookback_bars = 7   # ~1 trading day for hourly bars

                # Don't extend past reasonable lookback
                lookback_limit = max(0, len(candles) - max_lookback_bars)
                first_index = max(lookback_limit, 0)
            else:
                # Daily+: Use all data as before
                first_index = 0

            dx_back = trendline.start_index - first_index
            extended_start_price = trendline.start_price - (trendline.slope * dx_back)
            extended_start_time = candles[first_index]['time']
            print(f"🔧 [TRENDLINE] Intraday backward: first_index={first_index}, lookback_bars={trendline.start_index - first_index}")
        else:
            # Use original start point
            extended_start_time = candles[trendline.start_index]['time']
            extended_start_price = trendline.start_price

        # Use actual end pivot coordinates - NO EXTENSION
        # Similar to PDH/PDL approach: just draw the pattern between actual points
        # TradingView will handle visibility when coordinates are in range
        end_candle_time = candles[trendline.end_index]['time']

        # Calculate end price from slope and pivot indices
        dx = trendline.end_index - trendline.start_index
        end_price = trendline.start_price + (trendline.slope * dx)

        extended_end_time = end_candle_time
        extended_end_price = end_price

        print(f"🔧 [TRENDLINE] Using actual pivot coordinates: start_idx={trendline.start_index}, end_idx={trendline.end_index}, no extension")

        return {
            "type": trendline.line_type,
            "start": {
                "time": extended_start_time,
                "price": extended_start_price
            },
            "end": {
                "time": extended_end_time,
                "price": extended_end_price
            },
            "color": trendline.color,
            "style": "solid",
            "width": 2,
            "label": trendline.label,
            "deleteable": True,
            "metadata": {
                "touches": trendline.touches,
                "slope": trendline.slope,
                "pivot_indices": trendline.pivot_indices
            }
        }
