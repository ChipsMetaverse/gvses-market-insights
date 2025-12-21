"""
Test candlestick interval validation
Verifies that each timeframe returns candles with correct time deltas
"""
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def test_interval_validation():
    """Test each timeframe interval for correct candlestick spacing"""

    # Expected deltas in seconds for each timeframe
    expected_deltas = {
        '1m': 60,        # 1 minute
        '5m': 300,       # 5 minutes
        '15m': 900,      # 15 minutes
        '30m': 1800,     # 30 minutes
        '1H': 3600,      # 1 hour
        '2H': 7200,      # 2 hours
        '4H': 14400,     # 4 hours
        '1D': 86400,     # 1 day
    }

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Track API responses
        api_responses = {}

        async def handle_response(response):
            """Capture stock-history API responses"""
            url = response.url
            # Look for stock-history endpoint specifically
            if 'stock-history' in url.lower():
                try:
                    print(f"DEBUG: Intercepted stock-history URL: {url}")
                    data = await response.json()

                    # Extract interval from URL
                    if 'interval=' in url:
                        interval = url.split('interval=')[1].split('&')[0]
                        api_responses[interval] = data
                        candles_count = len(data.get('candles', [])) if isinstance(data, dict) else 'unknown'
                        print(f"✓ Captured {interval} response with {candles_count} candles")
                except Exception as e:
                    print(f"Error capturing response from {url}: {e}")

        page.on('response', handle_response)

        # Navigate to demo page
        print("\nNavigating to http://localhost:5174/demo...")
        await page.goto('http://localhost:5174/demo', wait_until='networkidle')

        # Wait for chart to load
        await page.wait_for_selector('.tv-lightweight-charts', timeout=10000)
        print("✓ Chart loaded")

        # Remove onboarding overlay using JavaScript
        try:
            print("Removing onboarding overlay...")
            await page.evaluate("""
                // Remove overlay
                const overlay = document.querySelector('.onboarding-overlay');
                if (overlay) overlay.remove();

                // Remove tooltip
                const tooltip = document.querySelector('.onboarding-tooltip');
                if (tooltip) tooltip.remove();

                console.log('Onboarding elements removed');
            """)
            await asyncio.sleep(0.5)
            print("✓ Onboarding overlay removed")
        except Exception as e:
            print(f"Error removing onboarding: {e}")

        # Test each timeframe
        for timeframe, expected_delta in expected_deltas.items():
            print(f"\n{'='*60}")
            print(f"Testing {timeframe} interval...")
            print(f"{'='*60}")

            # Clear previous response
            api_responses.clear()

            # Click timeframe button
            button_selector = f'button:has-text("{timeframe}")'
            try:
                await page.click(button_selector, timeout=5000)
                print(f"✓ Clicked {timeframe} button")
            except Exception as e:
                print(f"❌ Failed to click {timeframe} button: {e}")
                results.append({
                    'interval': timeframe,
                    'expected_delta': expected_delta,
                    'actual_delta': 'N/A',
                    'status': '❌ BUTTON NOT FOUND'
                })
                continue

            # Wait for API response
            await asyncio.sleep(3)

            # Check if we got response for this timeframe
            if timeframe not in api_responses:
                print(f"❌ No API response captured for {timeframe}")
                print(f"DEBUG: Available responses: {list(api_responses.keys())}")
                results.append({
                    'interval': timeframe,
                    'expected_delta': expected_delta,
                    'actual_delta': 'N/A',
                    'status': '❌ NO API RESPONSE'
                })
                continue

            # Analyze timestamps
            data = api_responses[timeframe]
            bars = data.get('candles', data.get('bars', []))

            if len(bars) < 2:
                print(f"❌ Not enough bars ({len(bars)}) to validate")
                results.append({
                    'interval': timeframe,
                    'expected_delta': expected_delta,
                    'actual_delta': 'N/A',
                    'status': f'❌ INSUFFICIENT DATA ({len(bars)} bars)'
                })
                continue

            # Calculate time deltas between consecutive candles
            deltas = []
            print(f"\nAnalyzing first 5 candles:")
            for i in range(min(5, len(bars) - 1)):
                bar1 = bars[i]
                bar2 = bars[i + 1]

                # Parse timestamps (assuming Unix timestamps in seconds)
                ts1 = bar1.get('timestamp') or bar1.get('time') or bar1.get('t')
                ts2 = bar2.get('timestamp') or bar2.get('time') or bar2.get('t')

                if ts1 is None or ts2 is None:
                    print(f"❌ Missing timestamps in bars")
                    continue

                # Convert to datetime for display
                dt1 = datetime.fromtimestamp(ts1)
                dt2 = datetime.fromtimestamp(ts2)

                # Calculate delta in seconds
                delta_seconds = abs(ts2 - ts1)
                deltas.append(delta_seconds)

                print(f"  Bar {i}: {dt1.strftime('%Y-%m-%d %H:%M:%S')} → {dt2.strftime('%Y-%m-%d %H:%M:%S')} = {delta_seconds}s")

            if not deltas:
                print(f"❌ Could not calculate any deltas")
                results.append({
                    'interval': timeframe,
                    'expected_delta': expected_delta,
                    'actual_delta': 'N/A',
                    'status': '❌ NO DELTAS CALCULATED'
                })
                continue

            # Get average delta (to handle weekend gaps for daily data)
            avg_delta = sum(deltas) / len(deltas)

            # For daily data, we need to account for weekends
            # Accept deltas within ±20% tolerance for intraday, ±50% for daily (weekends)
            if timeframe == '1D':
                tolerance = 0.5  # 50% tolerance for daily (weekends)
                min_acceptable = expected_delta * (1 - tolerance)
                max_acceptable = expected_delta * (1 + tolerance) * 3  # Up to 3 days for weekend
            else:
                tolerance = 0.2  # 20% tolerance for intraday
                min_acceptable = expected_delta * (1 - tolerance)
                max_acceptable = expected_delta * (1 + tolerance)

            # Check if delta matches expected
            is_correct = min_acceptable <= avg_delta <= max_acceptable

            status = '✅ CORRECT' if is_correct else '❌ INCORRECT'
            print(f"\n{status}")
            print(f"Expected delta: {expected_delta}s ({expected_delta/60:.1f}min)")
            print(f"Average delta: {avg_delta:.0f}s ({avg_delta/60:.1f}min)")
            print(f"Acceptable range: {min_acceptable:.0f}s - {max_acceptable:.0f}s")

            results.append({
                'interval': timeframe,
                'expected_delta': f"{expected_delta}s ({expected_delta/60:.1f}min)" if expected_delta < 3600 else f"{expected_delta}s ({expected_delta/3600:.1f}h)",
                'actual_delta': f"{avg_delta:.0f}s ({avg_delta/60:.1f}min)" if avg_delta < 3600 else f"{avg_delta:.0f}s ({avg_delta/3600:.1f}h)",
                'status': status,
                'sample_deltas': [f"{d}s" for d in deltas[:3]]
            })

        await browser.close()

    # Print final results table
    print("\n" + "="*100)
    print("CANDLESTICK INTERVAL VALIDATION RESULTS")
    print("="*100)
    print(f"{'Interval':<10} {'Expected Delta':<20} {'Actual Delta':<20} {'Sample Deltas':<30} {'Status':<15}")
    print("-"*100)

    for result in results:
        print(f"{result['interval']:<10} {result['expected_delta']:<20} {result['actual_delta']:<20} {', '.join(result.get('sample_deltas', ['N/A'])):<30} {result['status']:<15}")

    print("="*100)

    # Summary
    correct_count = sum(1 for r in results if '✅' in r['status'])
    total_count = len(results)
    print(f"\nSummary: {correct_count}/{total_count} intervals validated correctly")

    if correct_count == total_count:
        print("✅ ALL INTERVALS CORRECT - Candlesticks match selected timeframes!")
    else:
        print("❌ SOME INTERVALS INCORRECT - Backend may not be providing correct interval data!")

    return results

if __name__ == '__main__':
    asyncio.run(test_interval_validation())
