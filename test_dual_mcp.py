#!/usr/bin/env python3
"""
Test script for dual MCP server setup
Tests both market-mcp-server (Yahoo Finance) and alpaca-mcp-server (Alpaca Markets)
"""

import asyncio
import httpx
import json
import os


async def test_dual_mcp():
    """Test the dual MCP server setup via API endpoints."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Dual MCP Server Setup\n" + "=" * 50)
        
        # Test 1: Enhanced market data (auto source)
        print("\n1. Testing enhanced market data (auto source)...")
        try:
            response = await client.get(f"{base_url}/api/enhanced/market-data", params={
                "symbol": "AAPL",
                "source": "auto"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Market data retrieved from: {data.get('source', 'unknown')}")
                if 'data' in data:
                    print(f"   Symbol: {data['data'].get('symbol', 'N/A')}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Compare data sources
        print("\n2. Comparing data sources for TSLA...")
        try:
            response = await client.get(f"{base_url}/api/enhanced/compare-sources", params={
                "symbol": "TSLA"
            })
            if response.status_code == 200:
                data = response.json()
                sources = data.get('sources', {})
                print(f"✅ Data sources available: {list(sources.keys())}")
                
                # Show price from each source
                for source, source_data in sources.items():
                    if source == 'yahoo' and isinstance(source_data, dict):
                        price = source_data.get('regularMarketPrice', 'N/A')
                        print(f"   Yahoo Finance price: ${price}")
                    elif source == 'alpaca' and isinstance(source_data, dict):
                        if 'latest_trade' in source_data:
                            price = source_data['latest_trade'].get('price', 'N/A')
                            print(f"   Alpaca price: ${price}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Alpaca account info
        print("\n3. Testing Alpaca account info...")
        try:
            response = await client.get(f"{base_url}/api/enhanced/alpaca-account")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Alpaca account status: {data.get('status', 'unknown')}")
                print(f"   Buying power: ${data.get('buying_power', 0):,.2f}")
                print(f"   Portfolio value: ${data.get('portfolio_value', 0):,.2f}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 4: Market status
        print("\n4. Testing market status...")
        try:
            response = await client.get(f"{base_url}/api/enhanced/market-status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Market open: {data.get('is_open', False)}")
                print(f"   Source: {data.get('source', 'unknown')}")
                if 'next_open' in data:
                    print(f"   Next open: {data['next_open']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 5: Historical data
        print("\n5. Testing historical data retrieval...")
        try:
            response = await client.get(f"{base_url}/api/enhanced/historical-data", params={
                "symbol": "GOOGL",
                "days": 7,
                "source": "auto"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Historical data from: {data.get('source', 'unknown')}")
                if 'data' in data and 'bars' in data['data']:
                    bars = data['data']['bars']
                    print(f"   Number of bars: {len(bars)}")
                    if bars:
                        first_bar = bars[0]
                        print(f"   First bar date: {first_bar.get('timestamp', 'N/A')}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 6: Original endpoints still work
        print("\n6. Testing backward compatibility...")
        try:
            response = await client.get(f"{base_url}/api/stock-price", params={
                "symbol": "MSFT"
            })
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Original /api/stock-price endpoint works")
                print(f"   Price: ${data.get('price', 'N/A')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("Dual MCP Server Test Complete!")


async def main():
    """Main entry point."""
    print("Starting dual MCP server test...")
    print("Make sure the backend server is running on localhost:8000")
    print()
    
    # Wait a moment for user to see the message
    await asyncio.sleep(2)
    
    try:
        await test_dual_mcp()
    except Exception as e:
        print(f"Test failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())