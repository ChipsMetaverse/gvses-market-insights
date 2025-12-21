"""
Bar Aggregation Service - Aggregate OHLC bars into larger timeframes

Supports aggregating smaller intervals into larger ones:
- Monthly bars → Yearly bars (12 months → 1 year)

For proper OHLC aggregation:
- Open: First bar's open price
- High: Highest high across all bars
- Low: Lowest low across all bars
- Close: Last bar's close price
- Volume: Sum of all volumes
"""

import logging
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class BarAggregator:
    """Aggregates OHLC bars into larger timeframes."""

    @staticmethod
    def aggregate_to_yearly(monthly_bars: List[Dict]) -> List[Dict]:
        """
        Aggregate monthly bars into yearly bars.

        Args:
            monthly_bars: List of monthly OHLC bars with 'timestamp' field

        Returns:
            List of yearly OHLC bars (one per calendar year)

        Example:
            Input: 24 monthly bars (2023-01 through 2024-12)
            Output: 2 yearly bars (2023, 2024)
        """
        if not monthly_bars:
            return []

        # Group bars by year
        bars_by_year = defaultdict(list)

        for bar in monthly_bars:
            # Parse timestamp to get year
            timestamp_str = bar.get('timestamp', '')
            if not timestamp_str:
                continue

            try:
                # Handle both ISO format and datetime objects
                if isinstance(timestamp_str, str):
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    dt = timestamp_str

                year = dt.year
                bars_by_year[year].append(bar)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse timestamp {timestamp_str}: {e}")
                continue

        # Aggregate each year's bars into one yearly bar
        yearly_bars = []

        for year in sorted(bars_by_year.keys()):
            year_bars = bars_by_year[year]

            if not year_bars:
                continue

            # Sort by timestamp to ensure correct order
            year_bars.sort(key=lambda x: x.get('timestamp', ''))

            yearly_bar = {
                'timestamp': year_bars[0]['timestamp'],  # January (first month)
                'open': year_bars[0]['open'],             # January open
                'close': year_bars[-1]['close'],          # December close (last month)
                'high': max(bar['high'] for bar in year_bars),
                'low': min(bar['low'] for bar in year_bars),
                'volume': sum(bar.get('volume', 0) for bar in year_bars),
            }

            # Preserve optional fields if they exist (handle None values)
            if 'trade_count' in year_bars[0]:
                # Filter out None values before summing
                trade_counts = [bar.get('trade_count') for bar in year_bars if bar.get('trade_count') is not None]
                yearly_bar['trade_count'] = sum(trade_counts) if trade_counts else None

            if 'vwap' in year_bars[0]:
                # VWAP for the year = weighted average of monthly VWAPs (skip None values)
                total_volume = yearly_bar['volume']
                if total_volume > 0:
                    weighted_vwap = sum(
                        bar.get('vwap', 0) * bar.get('volume', 0)
                        for bar in year_bars
                        if bar.get('vwap') is not None
                    )
                    yearly_bar['vwap'] = weighted_vwap / total_volume if weighted_vwap > 0 else None

            yearly_bars.append(yearly_bar)

            logger.debug(
                f"Aggregated {len(year_bars)} monthly bars for {year} → "
                f"O: {yearly_bar['open']:.2f}, "
                f"H: {yearly_bar['high']:.2f}, "
                f"L: {yearly_bar['low']:.2f}, "
                f"C: {yearly_bar['close']:.2f}"
            )

        logger.info(
            f"Aggregated {len(monthly_bars)} monthly bars → "
            f"{len(yearly_bars)} yearly bars"
        )

        return yearly_bars


def get_bar_aggregator() -> BarAggregator:
    """Get singleton instance of BarAggregator."""
    return BarAggregator()
