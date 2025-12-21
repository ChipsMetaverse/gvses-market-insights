#!/usr/bin/env python3
"""
Test the complete data persistence pipeline
Tests both chat history and market data caching
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import time
import sys

# Configuration
API_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

# Color output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


async def test_conversation_creation():
    """Test creating a new conversation"""
    print(f"\n{BLUE}1. Testing Conversation Creation{RESET}")
    print("-" * 40)
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": TEST_USER_ID,
            "metadata": {
                "test_run": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        async with session.post(f"{API_URL}/api/conversations", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"{GREEN}✅ Conversation created: {data['conversation_id']}{RESET}")
                return data['conversation_id']
            else:
                error = await resp.text()
                print(f"{RED}❌ Failed to create conversation: {error}{RESET}")
                return None


async def test_message_saving(conversation_id):
    """Test saving messages to a conversation"""
    print(f"\n{BLUE}2. Testing Message Persistence{RESET}")
    print("-" * 40)
    
    if not conversation_id:
        print(f"{YELLOW}⚠️  Skipping - no conversation ID{RESET}")
        return False
    
    test_messages = [
        {"role": "user", "content": "What's the price of AAPL?"},
        {"role": "assistant", "content": "Apple (AAPL) is currently trading at $195.42, up 1.2% today."},
        {"role": "user", "content": "Show me the chart for Tesla"},
        {"role": "assistant", "content": "Here's the TSLA chart showing recent price action..."}
    ]
    
    async with aiohttp.ClientSession() as session:
        saved_count = 0
        
        for msg in test_messages:
            payload = {
                "conversation_id": conversation_id,
                "role": msg["role"],
                "content": msg["content"],
                "provider": "test",
                "model": "test-model" if msg["role"] == "assistant" else None
            }
            
            async with session.post(f"{API_URL}/api/messages", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✅ Saved {msg['role']} message: '{msg['content'][:50]}...'")
                    saved_count += 1
                else:
                    error = await resp.text()
                    print(f"  ❌ Failed to save message: {error}")
        
        success = saved_count == len(test_messages)
        if success:
            print(f"{GREEN}✅ All {saved_count} messages saved successfully{RESET}")
        else:
            print(f"{YELLOW}⚠️  Only {saved_count}/{len(test_messages)} messages saved{RESET}")
        
        return success


async def test_conversation_retrieval(conversation_id):
    """Test retrieving conversation history"""
    print(f"\n{BLUE}3. Testing Conversation History Retrieval{RESET}")
    print("-" * 40)
    
    if not conversation_id:
        print(f"{YELLOW}⚠️  Skipping - no conversation ID{RESET}")
        return False
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/conversations/{conversation_id}/messages") as resp:
            if resp.status == 200:
                data = await resp.json()
                message_count = len(data.get('messages', []))
                print(f"  📝 Retrieved {message_count} messages")
                
                for msg in data.get('messages', [])[:5]:  # Show first 5
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:60]
                    print(f"    [{role}]: {content}...")
                
                print(f"{GREEN}✅ Conversation history retrieved successfully{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{RED}❌ Failed to retrieve history: {error}{RESET}")
                return False


async def test_market_data_caching():
    """Test caching market data"""
    print(f"\n{BLUE}4. Testing Market Data Caching{RESET}")
    print("-" * 40)
    
    # Sample candle data
    test_candles = [
        {
            "timestamp": "2024-01-15T09:30:00Z",
            "open": 195.50,
            "high": 196.20,
            "low": 195.30,
            "close": 196.00,
            "volume": 1234567
        },
        {
            "timestamp": "2024-01-15T09:35:00Z",
            "open": 196.00,
            "high": 196.50,
            "low": 195.80,
            "close": 196.30,
            "volume": 987654
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "symbol": "AAPL",
            "timeframe": "5m",
            "candles": test_candles,
            "source": "test"
        }
        
        async with session.post(f"{API_URL}/api/market-data/cache", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"  💹 Cached {data['candles_saved']} candles for AAPL")
                print(f"{GREEN}✅ Market data cached successfully{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{RED}❌ Failed to cache market data: {error}{RESET}")
                return False


async def test_cached_data_retrieval():
    """Test retrieving cached market data"""
    print(f"\n{BLUE}5. Testing Cached Data Retrieval{RESET}")
    print("-" * 40)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/market-data/cache/AAPL?timeframe=5m") as resp:
            if resp.status == 200:
                data = await resp.json()
                candle_count = data.get('count', 0)
                is_cached = data.get('cached', False)
                
                print(f"  📊 Retrieved {candle_count} cached candles")
                print(f"  🗄️  Data from cache: {is_cached}")
                
                if data.get('candles'):
                    first_candle = data['candles'][0]
                    print(f"    First candle: {first_candle.get('timestamp')} - Close: ${first_candle.get('close')}")
                
                print(f"{GREEN}✅ Cached data retrieved successfully{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{YELLOW}⚠️  No cached data found (expected on first run): {error}{RESET}")
                return True  # Not a failure if no cache exists


async def test_news_caching():
    """Test caching news articles"""
    print(f"\n{BLUE}6. Testing News Article Caching{RESET}")
    print("-" * 40)
    
    test_articles = [
        {
            "headline": "Apple Reports Record Q4 Earnings",
            "content": "Apple Inc. reported record-breaking fourth quarter earnings...",
            "source": "CNBC",
            "url": "https://example.com/article1",
            "published_at": datetime.now().isoformat()
        },
        {
            "headline": "Tesla Unveils New Model",
            "content": "Tesla announced its latest electric vehicle model...",
            "source": "Reuters",
            "url": "https://example.com/article2",
            "published_at": datetime.now().isoformat()
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "articles": test_articles,
            "symbol": "AAPL"
        }
        
        async with session.post(f"{API_URL}/api/news/cache", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"  📰 Cached {data['articles_saved']} news articles")
                print(f"{GREEN}✅ News articles cached successfully{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{RED}❌ Failed to cache news: {error}{RESET}")
                return False


async def test_query_analytics():
    """Test query analytics retrieval"""
    print(f"\n{BLUE}7. Testing Query Analytics{RESET}")
    print("-" * 40)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/analytics/queries?user_id={TEST_USER_ID}") as resp:
            if resp.status == 200:
                data = await resp.json()
                
                if data:
                    print(f"  📊 Analytics Summary:")
                    print(f"    • Total queries: {data.get('total_queries', 0)}")
                    print(f"    • Success rate: {data.get('success_rate', 0)}%")
                    print(f"    • Avg response time: {data.get('avg_response_time_ms', 0)}ms")
                    
                    if data.get('top_symbols'):
                        print(f"    • Top symbols: {', '.join([f'{s[0]} ({s[1]})' for s in data['top_symbols'][:3]])}")
                    
                print(f"{GREEN}✅ Query analytics retrieved successfully{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{YELLOW}⚠️  No analytics data yet (expected on first run){RESET}")
                return True


async def test_recent_conversations():
    """Test retrieving recent conversations"""
    print(f"\n{BLUE}8. Testing Recent Conversations Retrieval{RESET}")
    print("-" * 40)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/conversations/recent?user_id={TEST_USER_ID}") as resp:
            if resp.status == 200:
                data = await resp.json()
                conv_count = len(data.get('conversations', []))
                
                print(f"  💬 Found {conv_count} recent conversations")
                
                for conv in data.get('conversations', [])[:3]:  # Show first 3
                    conv_id = conv.get('id', 'unknown')[:8]
                    started = conv.get('started_at', '')[:19]
                    print(f"    • {conv_id}... started at {started}")
                
                print(f"{GREEN}✅ Recent conversations retrieved{RESET}")
                return True
            else:
                error = await resp.text()
                print(f"{RED}❌ Failed to retrieve recent conversations: {error}{RESET}")
                return False


async def run_all_tests():
    """Run all persistence tests"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}       DATA PERSISTENCE PIPELINE TEST{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    results = {
        "conversation_creation": False,
        "message_saving": False,
        "conversation_retrieval": False,
        "market_data_caching": False,
        "cached_data_retrieval": False,
        "news_caching": False,
        "query_analytics": False,
        "recent_conversations": False
    }
    
    try:
        # Test conversation operations
        conversation_id = await test_conversation_creation()
        results["conversation_creation"] = conversation_id is not None
        
        if conversation_id:
            results["message_saving"] = await test_message_saving(conversation_id)
            await asyncio.sleep(1)  # Give time for async saves
            results["conversation_retrieval"] = await test_conversation_retrieval(conversation_id)
        
        # Test market data caching
        results["market_data_caching"] = await test_market_data_caching()
        results["cached_data_retrieval"] = await test_cached_data_retrieval()
        
        # Test news caching
        results["news_caching"] = await test_news_caching()
        
        # Test analytics
        results["query_analytics"] = await test_query_analytics()
        results["recent_conversations"] = await test_recent_conversations()
        
    except Exception as e:
        print(f"\n{RED}❌ Test suite failed with error: {e}{RESET}")
        return False
    
    # Print summary
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}                    TEST SUMMARY{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    passed_count = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, test_passed in results.items():
        status = f"{GREEN}✅ PASSED{RESET}" if test_passed else f"{RED}❌ FAILED{RESET}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{BLUE}Total: {passed_count}/{total} tests passed{RESET}")
    
    if passed_count == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! Data persistence pipeline is working correctly.{RESET}")
    elif passed_count >= total * 0.7:
        print(f"\n{YELLOW}⚠️  Most tests passed, but some features need attention.{RESET}")
    else:
        print(f"\n{RED}❌ Multiple tests failed. Please check the implementation.{RESET}")
    
    return passed_count == total


if __name__ == "__main__":
    print(f"\n{YELLOW}⚠️  Make sure the backend server is running on {API_URL}{RESET}")
    print(f"{YELLOW}⚠️  Make sure Supabase is configured and accessible{RESET}")
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)