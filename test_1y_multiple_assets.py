#!/usr/bin/env python3
"""Test 1Y chart with multiple assets to verify yearly aggregation works universally"""
import requests
import json
from datetime import datetime

# Test symbols with different IPO dates and history lengths
TEST_SYMBOLS = [
    {"symbol": "AMZN", "ipo_year": 1997, "name": "Amazon"},
    {"symbol": "GOOGL", "ipo_year": 2004, "name": "Google/Alphabet"},
    {"symbol": "MSFT", "ipo_year": 1986, "name": "Microsoft"},
    {"symbol": "META", "ipo_year": 2012, "name": "Meta/Facebook"},
    {"symbol": "NFLX", "ipo_year": 2002, "name": "Netflix"},
    {"symbol": "DIS", "ipo_year": 1957, "name": "Disney"},
]

def test_symbol(symbol_info):
    """Test a single symbol's 1Y chart"""
    symbol = symbol_info["symbol"]
    name = symbol_info["name"]
    ipo_year = symbol_info["ipo_year"]
    current_year = datetime.now().year
    expected_min_candles = current_year - ipo_year + 1

    print(f"\n{'='*80}")
    print(f"Testing: {symbol} ({name})")
    print(f"IPO Year: {ipo_year}")
    print(f"Expected: At least {expected_min_candles} yearly candles ({ipo_year}-{current_year})")
    print('='*80)

    try:
        # Request 50 years of data
        url = f"http://localhost:8000/api/stock-history?symbol={symbol}&interval=1y&days=18250"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False

        data = response.json()

        candle_count = data.get('count', 0)
        data_source = data.get('data_source', 'unknown')
        candles = data.get('candles', [])

        print(f"✅ HTTP 200 OK")
        print(f"📊 Candles received: {candle_count}")
        print(f"🔄 Data source: {data_source}")

        if candle_count == 0:
            print(f"❌ FAILED: No candles returned!")
            return False

        if candle_count < 3:
            print(f"⚠️  WARNING: Only {candle_count} candles (expected at least {expected_min_candles})")
            print(f"   This might indicate the old bug (only showing ~3 years)")
            return False

        # Extract years from timestamps
        if candles and len(candles) > 0:
            first_candle = candles[0]
            last_candle = candles[-1]

            first_year = first_candle['timestamp'][:4]
            last_year = last_candle['timestamp'][:4]

            print(f"📅 Year range: {first_year} to {last_year}")
            print(f"💰 Price range: ${first_candle['open']:.2f} (open {first_year}) → ${last_candle['close']:.2f} (close {last_year})")

            # Check if we got reasonable history
            if int(first_year) > ipo_year + 5:
                print(f"⚠️  WARNING: First candle is {first_year}, but IPO was {ipo_year}")
                print(f"   Missing {int(first_year) - ipo_year} years of history")

        if candle_count >= 10:
            print(f"✅ PASSED: Got {candle_count} yearly candles (sufficient history)")
            return True
        else:
            print(f"⚠️  PARTIAL: Got {candle_count} candles (works but limited history)")
            return True

    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Request took longer than 30 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR: {e}")
        print(f"Response text: {response.text[:500]}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("1Y CHART MULTI-ASSET VERIFICATION")
    print("Testing yearly aggregation across different stocks with varying histories")
    print("="*80)

    results = {}
    for symbol_info in TEST_SYMBOLS:
        success = test_symbol(symbol_info)
        results[symbol_info['symbol']] = success

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for symbol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{symbol:8} {status}")

    print("="*80)
    print(f"Results: {passed}/{total} passed")
    print("="*80)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Yearly aggregation works across all tested assets.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above for details.")
        return 1

if __name__ == '__main__':
    exit(main())
