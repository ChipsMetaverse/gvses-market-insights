"""
Test Alpaca data availability for paper trading account.
Checks how far back historical data goes for established stocks like NVDA.
"""

import os
from datetime import datetime, timedelta, timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Load credentials
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')

if not api_key or not secret_key:
    print("❌ Missing ALPACA_API_KEY or ALPACA_SECRET_KEY")
    exit(1)

# Initialize client
client = StockHistoricalDataClient(api_key, secret_key)
print(f"✅ Initialized Alpaca client")
print(f"   API Key: {api_key[:10]}...")
print(f"   Using paper trading endpoint")
print()

# Test different date ranges for NVDA
symbol = "NVDA"
test_cases = [
    ("5 years back", 365 * 5),
    ("10 years back", 365 * 10),
    ("15 years back", 365 * 15),
    ("20 years back", 365 * 20),
    ("Since IPO (1999)", 365 * 26),  # NVDA went public in 1999
]

for description, days_back in test_cases:
    print(f"📊 Testing: {description} ({days_back} days)")

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    try:
        # Test with IEX feed (current configuration)
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            feed='iex'  # Current feed
        )

        bars_response = client.get_stock_bars(request)

        if symbol in bars_response.data:
            bars = bars_response.data[symbol]
            if len(bars) > 0:
                first_bar = bars[0]
                last_bar = bars[-1]
                print(f"   ✅ IEX Feed: Got {len(bars)} bars")
                print(f"      First bar: {first_bar.timestamp.date()}")
                print(f"      Last bar:  {last_bar.timestamp.date()}")
                print(f"      Actual range: {(last_bar.timestamp - first_bar.timestamp).days} days")
            else:
                print(f"   ⚠️ IEX Feed: 0 bars returned")
        else:
            print(f"   ❌ IEX Feed: No data for {symbol}")

    except Exception as e:
        print(f"   ❌ IEX Feed Error: {str(e)}")

    print()

# Test SIP feed if available (requires subscription)
print("=" * 60)
print("Testing SIP feed (premium data)...")
print("=" * 60)

try:
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime(1999, 1, 1, tzinfo=timezone.utc),  # NVDA IPO date
        end=datetime.now(timezone.utc),
        feed='sip'  # Premium feed
    )

    bars_response = client.get_stock_bars(request)

    if symbol in bars_response.data:
        bars = bars_response.data[symbol]
        print(f"✅ SIP Feed: Got {len(bars)} bars")
        if len(bars) > 0:
            print(f"   First bar: {bars[0].timestamp.date()}")
            print(f"   Last bar:  {bars[-1].timestamp.date()}")
    else:
        print(f"❌ SIP Feed: No data")

except Exception as e:
    print(f"❌ SIP Feed Error: {str(e)}")
    if "subscription" in str(e).lower() or "plan" in str(e).lower():
        print("   ℹ️ SIP feed requires additional subscription ($99/month)")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("Current configuration uses IEX feed with 1900-day hardcoded cap.")
print("Paper trading accounts have same data access as free tier.")
print("For full historical data, consider:")
print("  1. Remove the 1900-day cap (let Alpaca return what it has)")
print("  2. Use Yahoo Finance MCP for pre-2020 data (as backup)")
print("  3. Upgrade to SIP feed subscription if needed ($99/month)")
