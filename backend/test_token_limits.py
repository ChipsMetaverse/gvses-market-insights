#!/usr/bin/env python3
"""Test script to verify token limits are properly enforced."""

import asyncio
import httpx
import json
from services.agent_orchestrator import AgentOrchestrator

async def test_orchestrator_response():
    """Test the agent orchestrator response length (should be ~700 tokens max for user-facing)."""
    print("=" * 60)
    print("Testing Agent Orchestrator Response Token Limit")
    print("=" * 60)
    
    orchestrator = AgentOrchestrator()
    
    # Test with a query that would typically generate a long response
    query = "Give me a comprehensive analysis of Tesla including all technical indicators, moving averages, support and resistance levels, news sentiment, volume analysis, and detailed predictions"
    
    result = await orchestrator.process_query(query)
    
    response_text = result.get('text', '')
    word_count = len(response_text.split())
    char_count = len(response_text)
    estimated_tokens = char_count // 4  # Rough estimate: 1 token ≈ 4 chars
    
    print(f'\nResponse length stats:')
    print(f'  Characters: {char_count}')
    print(f'  Words: {word_count}')
    print(f'  Estimated tokens: {estimated_tokens}')
    print(f'  Tools used: {result.get("tools_used", [])}')
    
    if estimated_tokens <= 700:
        print(f'  ✅ PASS: Response is within 700 token limit')
    else:
        print(f'  ❌ FAIL: Response exceeds 700 token limit')
    
    print(f'\nFirst 300 chars of response:')
    print(f'  "{response_text[:300]}..."')
    
    return estimated_tokens

async def test_direct_claude_endpoint():
    """Test the direct Claude endpoint response length (should be ~700 tokens max)."""
    print("\n" + "=" * 60)
    print("Testing Direct Claude Endpoint Token Limit")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/ask",
                json={
                    "query": "Give me an extremely detailed analysis of Apple stock with all possible technical indicators, fundamentals, news, and predictions"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('data', {}).get('response', '')
                
                word_count = len(response_text.split())
                char_count = len(response_text)
                estimated_tokens = char_count // 4
                
                print(f'\nResponse length stats:')
                print(f'  Characters: {char_count}')
                print(f'  Words: {word_count}')
                print(f'  Estimated tokens: {estimated_tokens}')
                
                if estimated_tokens <= 700:
                    print(f'  ✅ PASS: Response is within 700 token limit')
                else:
                    print(f'  ❌ FAIL: Response exceeds 700 token limit')
                
                print(f'\nFirst 300 chars of response:')
                print(f'  "{response_text[:300]}..."')
                
                return estimated_tokens
            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error testing direct endpoint: {e}")
            return None

async def test_crypto_symbol():
    """Test that BTC is properly mapped and returns correct price."""
    print("\n" + "=" * 60)
    print("Testing BTC Crypto Symbol Mapping")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/stock-price",
                params={"symbol": "BTC"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                price = data.get('data', {}).get('price', 0)
                asset_type = data.get('data', {}).get('asset_type', '')
                
                print(f'\nBTC Price Data:')
                print(f'  Price: ${price:,.2f}')
                print(f'  Asset Type: {asset_type}')
                
                if price > 50000:  # Bitcoin should be well above $50k
                    print(f'  ✅ PASS: BTC price looks correct (Bitcoin, not ETF)')
                else:
                    print(f'  ❌ FAIL: BTC price too low (might be ETF instead of crypto)')
                
                return price
            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error testing BTC: {e}")
            return None

async def main():
    """Run all tests."""
    print("\n🧪 Testing Token Limits and Crypto Mapping\n")
    
    # Test orchestrator
    orchestrator_tokens = await test_orchestrator_response()
    
    # Test direct endpoint
    direct_tokens = await test_direct_claude_endpoint()
    
    # Test crypto mapping
    btc_price = await test_crypto_symbol()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"  Orchestrator: ~{orchestrator_tokens} tokens")
    if direct_tokens:
        print(f"  Direct Claude: ~{direct_tokens} tokens")
    if btc_price:
        print(f"  BTC Price: ${btc_price:,.2f}")
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())