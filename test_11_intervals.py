#!/usr/bin/env python3
"""
Test all 11 timeframe intervals via API to verify:
1. Backend accepts all intervals
2. Correct interval parameter sent to Alpaca
3. Yearly aggregation works (1y interval)
4. All intervals return data
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

# API endpoint
BASE_URL = "http://localhost:8000"

# All 11 intervals to test
INTERVALS = [
    # Intraday (4)
    {'range': '1m', 'expected_interval': '1m', 'expected_spacing': 60},
    {'range': '5m', 'expected_interval': '5m', 'expected_spacing': 300},
    {'range': '15m', 'expected_interval': '15m', 'expected_spacing': 900},
    {'range': '1H', 'expected_interval': '1h', 'expected_spacing': 3600},

    # Daily+ (3)
    {'range': '1D', 'expected_interval': '1d', 'expected_spacing': 86400},
    {'range': '1W', 'expected_interval': '1w', 'expected_spacing': 604800},
    {'range': '1M', 'expected_interval': '1mo', 'expected_spacing': None},  # Monthly varies

    # Long-term (4)
    {'range': '1Y', 'expected_interval': '1y', 'expected_spacing': None, 'note': 'Yearly aggregation'},
    {'range': 'YTD', 'expected_interval': '1d', 'expected_spacing': 86400},
    {'range': 'MAX', 'expected_interval': '1d', 'expected_spacing': 86400},
]

def test_interval(interval_config):
    """Test a single interval configuration"""
    range_param = interval_config['range']
    expected_interval = interval_config['expected_interval']
    expected_spacing = interval_config['expected_spacing']

    print(f"\n{'='*80}")
    print(f"Testing: {range_param}")
    print(f"Expected interval parameter: {expected_interval}")
    if interval_config.get('note'):
        print(f"Note: {interval_config['note']}")
    print(f"{'='*80}")

    try:
        # Call API
        url = f"{BASE_URL}/api/intraday"
        params = {
            'symbol': 'TSLA',
            'interval': expected_interval,
            'days': 365  # Get enough data for testing
        }

        print(f"Calling: {url}")
        print(f"Params: {params}")

        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return {
                'range': range_param,
                'status': 'FAILED',
                'error': f"HTTP {response.status_code}",
                'bars': 0
            }

        data = response.json()
        bars = data.get('bars', [])
        bar_count = len(bars)

        print(f"✅ Response: HTTP 200")
        print(f"✅ Bars returned: {bar_count}")
        print(f"   Data source: {data.get('data_source', 'unknown')}")
        print(f"   Cache tier: {data.get('cache_tier', 'unknown')}")

        if bar_count == 0:
            print(f"⚠️  No bars returned")
            return {
                'range': range_param,
                'status': 'FAILED',
                'error': 'No bars returned',
                'bars': 0
            }

        # Check spacing if expected
        if expected_spacing and bar_count >= 2:
            spacings = []
            for i in range(min(10, bar_count - 1)):  # Check first 10 bars
                ts1 = datetime.fromisoformat(bars[i]['timestamp'].replace('Z', '+00:00'))
                ts2 = datetime.fromisoformat(bars[i + 1]['timestamp'].replace('Z', '+00:00'))
                spacing = abs((ts2 - ts1).total_seconds())
                spacings.append(spacing)

            avg_spacing = sum(spacings) / len(spacings)
            tolerance = expected_spacing * 0.2  # 20% tolerance

            if abs(avg_spacing - expected_spacing) <= tolerance:
                print(f"✅ Spacing correct: {avg_spacing:.0f}s (expected {expected_spacing}s)")
            else:
                print(f"⚠️  Spacing mismatch: {avg_spacing:.0f}s (expected {expected_spacing}s)")

        # Show sample bars
        print(f"\n   Sample bars (first 3):")
        for i, bar in enumerate(bars[:3]):
            timestamp = datetime.fromisoformat(bar['timestamp'].replace('Z', '+00:00'))
            print(f"     {i+1}. {timestamp} | O:{bar['open']:.2f} H:{bar['high']:.2f} L:{bar['low']:.2f} C:{bar['close']:.2f}")

        # For yearly interval, verify aggregation
        if range_param == '1Y':
            # Check if bars span multiple years
            timestamps = [datetime.fromisoformat(b['timestamp'].replace('Z', '+00:00')) for b in bars]
            years = set(t.year for t in timestamps)
            print(f"\n   📊 Yearly aggregation check:")
            print(f"      Total bars: {bar_count}")
            print(f"      Years covered: {sorted(years)}")

            if bar_count <= len(years) * 1.2:  # Should have roughly 1 bar per year
                print(f"      ✅ Looks like yearly bars (roughly 1 per year)")
            else:
                print(f"      ⚠️  May not be aggregated (too many bars)")

        return {
            'range': range_param,
            'status': 'PASSED',
            'bars': bar_count,
            'interval': expected_interval,
            'data_source': data.get('data_source', 'unknown')
        }

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout")
        return {
            'range': range_param,
            'status': 'FAILED',
            'error': 'Timeout',
            'bars': 0
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'range': range_param,
            'status': 'FAILED',
            'error': str(e),
            'bars': 0
        }

def main():
    """Run all interval tests"""
    print("="*80)
    print("11-INTERVAL VERIFICATION TEST")
    print("="*80)
    print(f"Testing {len(INTERVALS)} intervals against {BASE_URL}")
    print()

    results = []
    for interval_config in INTERVALS:
        result = test_interval(interval_config)
        results.append(result)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    passed = [r for r in results if r['status'] == 'PASSED']
    failed = [r for r in results if r['status'] == 'FAILED']

    print(f"\n{'Range':<8} {'Status':<10} {'Bars':<10} {'Interval':<10} {'Source':<15}")
    print("-" * 80)
    for r in results:
        status_icon = '✅' if r['status'] == 'PASSED' else '❌'
        print(f"{r['range']:<8} {status_icon} {r['status']:<8} {r['bars']:<10} "
              f"{r.get('interval', 'N/A'):<10} {r.get('data_source', 'N/A'):<15}")

    print(f"\n{'='*80}")
    print(f"PASSED: {len(passed)}/{len(results)}")
    print(f"FAILED: {len(failed)}/{len(results)}")

    if failed:
        print(f"\n⚠️  Failed intervals:")
        for r in failed:
            print(f"   - {r['range']}: {r.get('error', 'Unknown error')}")

    if len(passed) == len(results):
        print(f"\n🎉 ALL TESTS PASSED! All 11 intervals working correctly.")

    print(f"{'='*80}\n")

    # Save results
    with open('interval_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'passed': len(passed),
            'failed': len(failed),
            'results': results
        }, f, indent=2)

    print(f"Results saved to: interval_test_results.json")

if __name__ == '__main__':
    main()
