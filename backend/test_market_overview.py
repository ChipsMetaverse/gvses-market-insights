#!/usr/bin/env python3
"""
Test script for the new market overview endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

# API base URL - adjust if running on different port
BASE_URL = "http://localhost:8000"


async def test_market_overview():
    """Test the /api/market-overview endpoint."""
    
    print("\n" + "="*60)
    print("Testing Market Overview Endpoint")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Make request to market overview endpoint
            print(f"\n📊 Fetching market overview from {BASE_URL}/api/market-overview...")
            
            start_time = datetime.now()
            response = await client.get(f"{BASE_URL}/api/market-overview")
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Response received in {elapsed:.2f} seconds")
            print(f"📝 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check data source
                data_source = data.get("data_source", "unknown")
                print(f"\n🔧 Data Source: {data_source}")
                
                # Display indices
                indices = data.get("indices", {})
                if indices:
                    print("\n📈 Market Indices:")
                    print("-" * 40)
                    for index_name, index_data in indices.items():
                        value = index_data.get("value", 0)
                        change = index_data.get("change", 0)
                        change_pct = index_data.get("change_percent", 0)
                        
                        # Format change with color
                        if change >= 0:
                            change_str = f"+{change:.2f} ({change_pct:+.2f}%)"
                            emoji = "🟢"
                        else:
                            change_str = f"{change:.2f} ({change_pct:.2f}%)"
                            emoji = "🔴"
                        
                        print(f"{emoji} {index_name.upper():8} ${value:,.2f}  {change_str}")
                else:
                    print("\n⚠️ No indices data found")
                
                # Display movers if available
                movers = data.get("movers", {})
                if movers:
                    print("\n📊 Market Movers:")
                    print("-" * 40)
                    
                    # Show gainers
                    gainers = movers.get("gainers", [])
                    if gainers:
                        print("Top Gainers:")
                        for i, gainer in enumerate(gainers[:3], 1):
                            symbol = gainer.get("symbol", "N/A")
                            change_pct = gainer.get("change_percent", 0)
                            print(f"  {i}. {symbol:6} +{change_pct:.2f}%")
                    
                    # Show losers  
                    losers = movers.get("losers", [])
                    if losers:
                        print("\nTop Losers:")
                        for i, loser in enumerate(losers[:3], 1):
                            symbol = loser.get("symbol", "N/A")
                            change_pct = loser.get("change_percent", 0)
                            print(f"  {i}. {symbol:6} {change_pct:.2f}%")
                
                # Check for errors
                if "error" in data:
                    print(f"\n⚠️ Error in response: {data['error']}")
                
                # Display timestamp
                timestamp = data.get("timestamp", "N/A")
                print(f"\n⏰ Timestamp: {timestamp}")
                
                # Performance assessment
                print("\n" + "="*40)
                print("Performance Assessment:")
                if data_source == "alpaca" and elapsed < 1.0:
                    print("✅ EXCELLENT: Sub-second response using Alpaca")
                elif data_source == "yahoo_mcp" and elapsed < 15:
                    print("✅ GOOD: MCP fallback working as expected")
                else:
                    print(f"⚠️ SLOW: Response took {elapsed:.2f}s")
                
            else:
                print(f"\n❌ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except httpx.TimeoutException:
            print("\n❌ Request timed out after 30 seconds")
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Run all tests."""
    print("\n🚀 Starting Market Overview Tests")
    print("="*60)
    
    # Test the market overview endpoint
    await test_market_overview()
    
    print("\n✅ Tests completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())