#!/usr/bin/env python3
"""
Comprehensive Timeframe Aggregation Investigation

Tests all aggregated intervals to verify that candlesticks match their selected timeframes:
- 3m (should be 3-minute candles, NOT 1-minute)
- 10m (should be 10-minute candles, NOT 5-minute)
- 2H (should be 2-hour candles, NOT 1-hour)
- 3H, 4H, 6H, 12H (higher hour intervals)

For each timeframe, verifies:
1. API request shows correct interval parameter
2. Number of bars returned makes sense for the date range
3. No errors in response
4. Data quality checks
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

BASE_URL = "http://localhost:8000"
SYMBOL = "TSLA"
DAYS = 7  # 1 week of data for testing

# Define test cases with expected characteristics
TEST_CASES = [
    # Format: (interval, expected_bars_per_day_range, description)
    ("1m", (350, 400), "1-minute candles (6.5 hours * 60)"),
    ("3m", (110, 140), "3-minute aggregated candles (6.5 hours * 20)"),
    ("5m", (70, 90), "5-minute candles (6.5 hours * 12)"),
    ("10m", (35, 45), "10-minute aggregated candles (6.5 hours * 6)"),
    ("15m", (24, 30), "15-minute candles (6.5 hours * 4)"),
    ("30m", (12, 16), "30-minute candles (6.5 hours * 2)"),
    ("1H", (6, 8), "1-hour candles (6.5 hours)"),
    ("2H", (3, 4), "2-hour aggregated candles (~3 per day)"),
    ("3H", (2, 3), "3-hour aggregated candles (~2 per day)"),
    ("4H", (1, 2), "4-hour aggregated candles (~1-2 per day)"),
    ("6H", (1, 2), "6-hour aggregated candles (~1 per day)"),
    ("12H", (0, 1), "12-hour aggregated candles (~1 every 2 days)"),
    ("1D", (1, 1), "Daily candles (1 per day)"),
]

# Critical intervals that require aggregation
CRITICAL_AGGREGATED_INTERVALS = ["3m", "10m", "2H", "3H", "4H", "6H", "12H"]


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def test_interval(interval: str, expected_range: Tuple[int, int], description: str) -> Dict:
    """
    Test a single interval and return detailed results.

    Args:
        interval: Timeframe string (e.g., "3m", "2H")
        expected_range: Tuple of (min_bars, max_bars) expected per day
        description: Human-readable description

    Returns:
        Dictionary with test results
    """
    print(f"\n{Colors.BOLD}Testing: {interval} - {description}{Colors.END}")
    print(f"Expected: {expected_range[0]}-{expected_range[1]} bars per day")

    result = {
        "interval": interval,
        "description": description,
        "success": False,
        "errors": [],
        "warnings": [],
        "data": {}
    }

    try:
        # Make API request
        url = f"{BASE_URL}/api/stock-history"
        params = {
            "symbol": SYMBOL,
            "days": DAYS,
            "interval": interval
        }

        print(f"Request: GET {url}")
        print(f"Params: {json.dumps(params, indent=2)}")

        response = requests.get(url, params=params, timeout=30)

        # Check HTTP status
        if response.status_code != 200:
            result["errors"].append(f"HTTP {response.status_code}: {response.text[:200]}")
            print_error(f"HTTP {response.status_code}")
            return result

        # Parse response
        data = response.json()

        # Extract candles
        candles = data.get("candles", [])
        if not candles:
            result["errors"].append("No candles returned")
            print_error("No candles in response")
            return result

        # Store response data
        result["data"] = {
            "total_bars": len(candles),
            "returned_interval": data.get("interval"),
            "data_source": data.get("data_source"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
        }

        # Calculate bars per day
        bars_per_day = len(candles) / DAYS
        result["data"]["bars_per_day"] = round(bars_per_day, 1)

        # Verify interval matches request
        if data.get("interval") != interval:
            result["warnings"].append(
                f"Interval mismatch: requested '{interval}', got '{data.get('interval')}'"
            )
            print_warning(f"Interval mismatch: {interval} vs {data.get('interval')}")

        # Check if bar count is in expected range
        expected_total_min = expected_range[0] * DAYS
        expected_total_max = expected_range[1] * DAYS

        if expected_total_min <= len(candles) <= expected_total_max:
            result["success"] = True
            print_success(f"Total bars: {len(candles)} (expected {expected_total_min}-{expected_total_max})")
            print_success(f"Bars per day: {bars_per_day:.1f} (expected {expected_range[0]}-{expected_range[1]})")
        else:
            result["errors"].append(
                f"Bar count {len(candles)} outside expected range {expected_total_min}-{expected_total_max}"
            )
            print_error(f"Total bars: {len(candles)} (expected {expected_total_min}-{expected_total_max})")
            print_error(f"Bars per day: {bars_per_day:.1f} (expected {expected_range[0]}-{expected_range[1]})")

        # Analyze timestamp intervals (check first 10 candles)
        if len(candles) >= 2:
            time_diffs = []
            for i in range(min(10, len(candles) - 1)):
                t1 = datetime.fromisoformat(candles[i]["date"].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(candles[i + 1]["date"].replace("Z", "+00:00"))
                diff_minutes = (t2 - t1).total_seconds() / 60
                time_diffs.append(diff_minutes)

            avg_diff = sum(time_diffs) / len(time_diffs)
            result["data"]["avg_candle_spacing_minutes"] = round(avg_diff, 1)
            print_info(f"Average candle spacing: {avg_diff:.1f} minutes")

            # Verify spacing matches interval
            expected_spacing = parse_interval_to_minutes(interval)
            if expected_spacing and abs(avg_diff - expected_spacing) > expected_spacing * 0.2:  # 20% tolerance
                result["warnings"].append(
                    f"Candle spacing {avg_diff:.1f}min doesn't match interval {interval} (~{expected_spacing}min)"
                )
                print_warning(f"Spacing mismatch: {avg_diff:.1f}min vs expected {expected_spacing}min")

        # Sample first and last candles
        result["data"]["first_candle"] = candles[0]
        result["data"]["last_candle"] = candles[-1]

        print_info(f"First candle: {candles[0]['date']} (O:{candles[0]['open']}, C:{candles[0]['close']})")
        print_info(f"Last candle:  {candles[-1]['date']} (O:{candles[-1]['open']}, C:{candles[-1]['close']})")
        print_info(f"Data source: {data.get('data_source', 'unknown')}")

    except requests.exceptions.Timeout:
        result["errors"].append("Request timeout (30s)")
        print_error("Request timeout")
    except Exception as e:
        result["errors"].append(f"Exception: {str(e)}")
        print_error(f"Exception: {str(e)}")

    return result


def parse_interval_to_minutes(interval: str) -> int:
    """Convert interval string to expected minutes between candles"""
    mappings = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "10m": 10,
        "15m": 15,
        "30m": 30,
        "1H": 60,
        "2H": 120,
        "3H": 180,
        "4H": 240,
        "6H": 360,
        "12H": 720,
        "1D": 1440,
    }
    return mappings.get(interval, 0)


def main():
    """Run comprehensive timeframe aggregation investigation"""
    print_header("TIMEFRAME AGGREGATION COMPREHENSIVE INVESTIGATION")
    print(f"Testing {len(TEST_CASES)} intervals for {SYMBOL}")
    print(f"Date range: {DAYS} days")
    print(f"API Base URL: {BASE_URL}")

    # Test all intervals
    results = []
    for interval, expected_range, description in TEST_CASES:
        result = test_interval(interval, expected_range, description)
        results.append(result)

    # Summary report
    print_header("TEST SUMMARY")

    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed

    print(f"\n{Colors.BOLD}Overall Results:{Colors.END}")
    print(f"  Total tests: {len(results)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    else:
        print_success(f"Failed: 0")

    # Critical intervals analysis
    print(f"\n{Colors.BOLD}Critical Aggregated Intervals:{Colors.END}")
    critical_results = [r for r in results if r["interval"] in CRITICAL_AGGREGATED_INTERVALS]

    for result in critical_results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        color = Colors.GREEN if result["success"] else Colors.RED
        print(f"  {color}{status}{Colors.END} {result['interval']:5} - {result['description']}")

        if result["errors"]:
            for error in result["errors"]:
                print(f"    {Colors.RED}Error: {error}{Colors.END}")

        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"    {Colors.YELLOW}Warning: {warning}{Colors.END}")

    # Detailed failure analysis
    failures = [r for r in results if not r["success"]]
    if failures:
        print_header("FAILURE ANALYSIS")

        for result in failures:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed: {result['interval']} - {result['description']}{Colors.END}")
            print(f"  Errors:")
            for error in result["errors"]:
                print(f"    - {error}")
            if result["warnings"]:
                print(f"  Warnings:")
                for warning in result["warnings"]:
                    print(f"    - {warning}")

            if result["data"]:
                print(f"  Data received:")
                print(f"    Total bars: {result['data'].get('total_bars', 'N/A')}")
                print(f"    Bars/day: {result['data'].get('bars_per_day', 'N/A')}")
                print(f"    Data source: {result['data'].get('data_source', 'N/A')}")

    # Save detailed results to JSON
    report_file = "/tmp/timeframe_aggregation_report.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "symbol": SYMBOL,
            "days": DAYS,
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "results": results
        }, f, indent=2)

    print(f"\n{Colors.BOLD}Full report saved to: {report_file}{Colors.END}")

    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
