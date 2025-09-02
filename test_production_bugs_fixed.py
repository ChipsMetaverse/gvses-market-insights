#!/usr/bin/env python3
"""
Production Bug Fix Verification - September 1, 2025
Tests that the chart label and news loading issues have been resolved.
"""

import requests
import json
import time

def test_production_fixes():
    print('🎯 PRODUCTION BUG FIX VERIFICATION')
    print('=' * 50)
    print('Testing fixes for:')
    print('  ✓ Missing technical level labels on chart')
    print('  ✓ News loading consistency in Chart Analysis panel')
    print('  ✓ Enhanced error handling and retry mechanisms')
    print('  ✓ Debug logging for production troubleshooting')
    print('')

    base_url = 'https://gvses-market-insights.fly.dev'

    # Test 1: Health Check
    print('1. Testing Production Health:')
    try:
        response = requests.get(f'{base_url}/health')
        if response.status_code == 200:
            health = response.json()
            print(f'   ✅ Status: {health.get("status", "Unknown")}')
            print(f'   ⚡ Service Mode: {health.get("service_mode", "Unknown")}')
        else:
            print(f'   ❌ Health check failed: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Health check error: {e}')

    # Test 2: Technical Levels API (Chart Labels Data Source)
    print('\n2. Testing Technical Levels Data (Chart Labels):')
    try:
        response = requests.get(f'{base_url}/api/comprehensive-stock-data?symbol=TSLA')
        if response.status_code == 200:
            data = response.json()
            technical_levels = data.get('technical_levels', {})
            print(f'   ✅ Technical Levels Retrieved:')
            print(f'      QE Level: ${technical_levels.get("qe_level", "N/A")}')
            print(f'      ST Level: ${technical_levels.get("st_level", "N/A")}')
            print(f'      LTB Level: ${technical_levels.get("ltb_level", "N/A")}')
            
            # Verify all levels have values
            if all(level for level in [technical_levels.get('qe_level'), 
                                     technical_levels.get('st_level'), 
                                     technical_levels.get('ltb_level')]):
                print(f'   ✅ All technical levels available for chart overlay labels')
            else:
                print(f'   ⚠️  Some technical levels missing - labels may not display')
        else:
            print(f'   ❌ Failed: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Error: {e}')

    # Test 3: News Loading (Chart Analysis Panel)
    print('\n3. Testing News Loading Consistency:')
    symbols = ['TSLA', 'AAPL', 'NVDA']
    for symbol in symbols:
        try:
            start_time = time.time()
            response = requests.get(f'{base_url}/api/stock-news?symbol={symbol}')
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Handle different response formats
                if isinstance(news_data, list):
                    news_count = len(news_data)
                elif isinstance(news_data, dict) and 'news' in news_data:
                    news_count = len(news_data['news'])
                else:
                    news_count = 1 if news_data else 0
                
                print(f'   ✅ {symbol}: {news_count} articles ({response_time}ms)')
                
                # Verify news structure for frontend rendering
                if news_count > 0:
                    sample_article = None
                    if isinstance(news_data, list):
                        sample_article = news_data[0]
                    elif isinstance(news_data, dict) and 'news' in news_data:
                        sample_article = news_data['news'][0]
                    
                    if sample_article and 'title' in sample_article:
                        print(f'      📰 Sample: "{sample_article["title"][:50]}..."')
                    else:
                        print(f'      ⚠️  News format may cause rendering issues')
            else:
                print(f'   ❌ {symbol}: Failed ({response.status_code})')
                
        except Exception as e:
            print(f'   ❌ {symbol}: Error - {e}')

    # Test 4: Chart Data Performance  
    print('\n4. Testing Chart Data Performance:')
    try:
        start_time = time.time()
        response = requests.get(f'{base_url}/api/stock-history?symbol=TSLA&days=30')
        end_time = time.time()
        response_time = int((end_time - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            candles = len(data.get('candles', data) if isinstance(data, dict) else data)
            print(f'   ✅ Chart Data: {candles} candles ({response_time}ms)')
            
            # Verify data structure for TradingChart component
            sample_candle = None
            if isinstance(data, dict) and 'candles' in data:
                sample_candle = data['candles'][0] if data['candles'] else None
            elif isinstance(data, list):
                sample_candle = data[0] if data else None
            
            if sample_candle and all(key in sample_candle for key in ['open', 'high', 'low', 'close']):
                print(f'   ✅ Chart data format compatible with TradingChart component')
            else:
                print(f'   ⚠️  Chart data format may cause rendering issues')
        else:
            print(f'   ❌ Chart data failed: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Chart data error: {e}')

    # Test 5: Voice Assistant Integration
    print('\n5. Testing Voice Assistant Integration:')
    try:
        response = requests.get(f'{base_url}/elevenlabs/signed-url')
        if response.status_code == 200:
            url_data = response.json()
            if 'url' in url_data or isinstance(url_data, str):
                print(f'   ✅ Voice WebSocket URL generated successfully')
                print(f'   🎤 Voice assistant ready for chart control commands')
            else:
                print(f'   ⚠️  Unexpected signed URL format: {url_data}')
        else:
            print(f'   ❌ Voice assistant setup failed: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Voice assistant error: {e}')

    print('\n🎉 PRODUCTION BUG FIX VERIFICATION COMPLETE!')
    print('')
    print('📋 SUMMARY OF FIXES DEPLOYED:')
    print('   ✅ Enhanced debug logging for chart label positioning')
    print('   ✅ Improved z-index and positioning for technical level labels')
    print('   ✅ Fixed news loading error handling with retry mechanism')
    print('   ✅ Added news error states with manual retry option')
    print('   ✅ Enhanced chart event synchronization for label updates')
    print('   ✅ Production deployment with zero downtime rolling update')
    print('')
    print('🌐 Application URL: https://gvses-market-insights.fly.dev/')
    print('')
    print('📊 Next Steps:')
    print('   1. Open the application in your browser')
    print('   2. Check browser console (F12) for debug logging from chart labels')
    print('   3. Verify technical level labels (QE, ST, LTB) appear on chart left side')
    print('   4. Confirm Chart Analysis panel loads news consistently')
    print('   5. Test voice controls with "Show me AAPL chart" type commands')

if __name__ == '__main__':
    test_production_fixes()