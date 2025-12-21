#!/usr/bin/env python3
"""
Test Key Levels Across All Timeframes

Cycles through all available timeframes and verifies that all 5 key levels
(BL, SH, BTD, PDH, PDL) display correctly for each interval.
"""

import requests
import time
import json
from typing import Dict, List, Any

# API endpoint
BASE_URL = "http://localhost:8000"
SYMBOL = "TSLA"

# All timeframes to test
TIMEFRAMES = [
    "1m",   # 1 minute
    "5m",   # 5 minutes
    "15m",  # 15 minutes
    "30m",  # 30 minutes
    "1h",   # 1 hour (aliased as 1H in UI)
    "2h",   # 2 hours (aliased as 2H in UI)
    "4h",   # 4 hours (aliased as 4H in UI)
    "1d",   # 1 day
    "1wk",  # 1 week
    "1mo"   # 1 month
]

# Expected key level labels
EXPECTED_LEVELS = ["BL", "SH", "BTD (200 SMA)", "PDH", "PDL"]

def test_timeframe(interval: str) -> Dict[str, Any]:
    """Test pattern detection for a single timeframe."""
    print(f"\n{'='*80}")
    print(f"Testing Interval: {interval.upper()}")
    print(f"{'='*80}")

    url = f"{BASE_URL}/api/pattern-detection"
    params = {
        "symbol": SYMBOL,
        "interval": interval
    }

    try:
        print(f"⏳ Fetching pattern detection data...")
        start_time = time.time()
        response = requests.get(url, params=params, timeout=30)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return {
                "interval": interval,
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": elapsed
            }

        data = response.json()
        key_levels = data.get("key_levels", [])

        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"📊 Key Levels Found: {len(key_levels)}")

        # Extract level labels and details
        levels_by_label = {}
        for level in key_levels:
            label = level.get("label", "Unknown")
            price = level.get("price", 0)
            color = level.get("color", "")
            style = level.get("style", "")

            levels_by_label[label] = {
                "price": price,
                "color": color,
                "style": style
            }

            print(f"  • {label}: ${price:.2f} (color: {color}, style: {style})")

        # Check which expected levels are present
        missing_levels = []
        present_levels = []

        for expected in EXPECTED_LEVELS:
            if expected in levels_by_label:
                present_levels.append(expected)
            else:
                missing_levels.append(expected)

        # Summary
        all_present = len(missing_levels) == 0
        if all_present:
            print(f"\n✅ All 5 key levels present!")
        else:
            print(f"\n⚠️ Missing {len(missing_levels)} level(s): {', '.join(missing_levels)}")

        return {
            "interval": interval,
            "success": all_present,
            "total_levels": len(key_levels),
            "present_levels": present_levels,
            "missing_levels": missing_levels,
            "levels_data": levels_by_label,
            "response_time": elapsed
        }

    except requests.Timeout:
        print(f"❌ Request timeout after 30 seconds")
        return {
            "interval": interval,
            "success": False,
            "error": "Timeout",
            "response_time": 30.0
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "interval": interval,
            "success": False,
            "error": str(e),
            "response_time": 0
        }

def main():
    """Run tests for all timeframes and generate summary report."""
    print(f"\n{'#'*80}")
    print(f"# KEY LEVELS VERIFICATION ACROSS ALL TIMEFRAMES")
    print(f"# Symbol: {SYMBOL}")
    print(f"# Expected Levels: {', '.join(EXPECTED_LEVELS)}")
    print(f"{'#'*80}")

    results = []

    for interval in TIMEFRAMES:
        result = test_timeframe(interval)
        results.append(result)

        # Small delay between requests to avoid overwhelming the server
        time.sleep(1)

    # Generate summary report
    print(f"\n\n{'='*80}")
    print(f"SUMMARY REPORT")
    print(f"{'='*80}\n")

    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    print(f"Total Timeframes Tested: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"\nAverage Response Time: {sum(r.get('response_time', 0) for r in results) / len(results):.2f}s")

    if failed:
        print(f"\n⚠️ Failed Timeframes:")
        for r in failed:
            interval = r.get("interval", "Unknown")
            error = r.get("error", "Missing levels")
            missing = r.get("missing_levels", [])
            print(f"  • {interval.upper()}: {error}")
            if missing:
                print(f"    Missing: {', '.join(missing)}")

    if successful:
        print(f"\n✅ Successful Timeframes:")
        for r in successful:
            interval = r.get("interval", "Unknown")
            total = r.get("total_levels", 0)
            response_time = r.get("response_time", 0)
            print(f"  • {interval.upper()}: {total} levels ({response_time:.2f}s)")

    # Detailed level comparison across timeframes
    print(f"\n\n{'='*80}")
    print(f"LEVEL PRICES BY TIMEFRAME")
    print(f"{'='*80}\n")

    # Create table
    print(f"{'Interval':<10}", end="")
    for level in EXPECTED_LEVELS:
        print(f"{level:<18}", end="")
    print()
    print("-" * 100)

    for result in results:
        if result.get("success"):
            interval = result.get("interval", "Unknown")
            levels_data = result.get("levels_data", {})

            print(f"{interval.upper():<10}", end="")
            for level in EXPECTED_LEVELS:
                if level in levels_data:
                    price = levels_data[level].get("price", 0)
                    print(f"${price:<16.2f}", end="")
                else:
                    print(f"{'N/A':<18}", end="")
            print()

    # Final verdict
    print(f"\n\n{'='*80}")
    if len(failed) == 0:
        print("🎉 VERIFICATION COMPLETE: All timeframes displaying 5 key levels correctly!")
    else:
        print(f"⚠️ VERIFICATION INCOMPLETE: {len(failed)} timeframe(s) need attention")
    print(f"{'='*80}\n")

    # Save detailed results to JSON
    output_file = "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/timeframe_verification_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "symbol": SYMBOL,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
            "summary": {
                "total_tested": len(results),
                "successful": len(successful),
                "failed": len(failed)
            }
        }, f, indent=2)

    print(f"📄 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
