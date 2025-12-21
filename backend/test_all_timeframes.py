#!/usr/bin/env python3
"""
Quick test script for all 12 timeframes after Phase 1 fixes
"""
import requests
import time

INTERVALS = ['1m', '5m', '15m', '30m', '1H', '2H', '4H', '1d', '1Y', '2Y', '3Y', 'MAX']
BASE_URL = 'http://localhost:8000'

print("Testing all 12 timeframes with Phase 1 fixes...")
print("=" * 60)

results = []
for interval in INTERVALS:
    try:
        response = requests.get(
            f"{BASE_URL}/api/pattern-detection",
            params={'symbol': 'TSLA', 'interval': interval},
            timeout=30
        )
        data = response.json()
        trendlines_count = len(data.get('trendlines', []))
        status = '✅ PASS' if trendlines_count >= 4 else ('⚠️ LOW' if trendlines_count > 0 else '❌ FAIL')
        results.append({
            'interval': interval,
            'count': trendlines_count,
            'status': status
        })
        print(f"{interval:>4} | {trendlines_count} trendlines | {status}")
    except Exception as e:
        results.append({
            'interval': interval,
            'count': 0,
            'status': f'❌ ERROR: {str(e)}'
        })
        print(f"{interval:>4} | ERROR: {str(e)}")
    time.sleep(0.5)

print("=" * 60)
print("\nSummary:")
passing = sum(1 for r in results if r['count'] >= 4)
low = sum(1 for r in results if 0 < r['count'] < 4)
failing = sum(1 for r in results if r['count'] == 0)
print(f"✅ PASS (4+ trendlines): {passing}/12")
print(f"⚠️ LOW (1-3 trendlines): {low}/12")
print(f"❌ FAIL (0 trendlines): {failing}/12")
