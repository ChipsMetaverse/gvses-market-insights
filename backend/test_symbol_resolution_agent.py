#!/usr/bin/env python3
"""
Test script for Symbol Resolution Agent using OpenAI Agents SDK
"""

import os
import sys
import asyncio
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openai_agents_basic():
    """Test basic OpenAI Agents SDK functionality"""
    print("🧪 Testing OpenAI Agents SDK Basic Functionality...")
    
    try:
        # Test basic agent creation
        from agents import Agent, Runner
        
        # Create a simple test agent
        test_agent = Agent(
            name='Test Agent',
            instructions='You are a test agent. Respond with "Hello, I am working!"',
            model='gpt-3.5-turbo'
        )
        
        print("✅ Agent creation successful")
        
        # Create runner
        runner = Runner()
        print("✅ Runner creation successful")
        
        # Test agent execution (basic)
        result = await runner.run(test_agent, "Say hello")
        print(f"✅ Agent execution successful: {result.final_output[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Agents SDK test failed: {e}")
        return False

async def test_function_tools():
    """Test function tools with OpenAI Agents"""
    print("\n🔧 Testing Function Tools...")
    
    try:
        from agents import Agent, Runner, function_tool
        
        @function_tool
        def get_greeting(name: str) -> str:
            """Get a greeting for a person."""
            return f"Hello, {name}! Nice to meet you."
        
        # Create agent with tools
        tool_agent = Agent(
            name='Tool Test Agent',
            instructions='Use the get_greeting tool to greet users.',
            model='gpt-3.5-turbo',
            tools=[get_greeting]
        )
        
        runner = Runner()
        result = await runner.run(tool_agent, "Greet Alice")
        
        print(f"✅ Function tool test successful: {result.final_output[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Function tools test failed: {e}")
        return False

async def test_symbol_resolution_agent():
    """Test the Symbol Resolution Agent"""
    print("\n🎯 Testing Symbol Resolution Agent...")
    
    try:
        from services.symbol_resolution_agent import get_symbol_resolution_agent
        
        # Get the agent instance
        symbol_agent = await get_symbol_resolution_agent()
        print("✅ Symbol Resolution Agent created successfully")
        
        # Test resolution workflow  
        test_cases = ["google", "microsoft", "MSFT"]
        
        for query in test_cases:
            print(f"\n🔍 Testing query: '{query}'")
            result = await symbol_agent.resolve_symbol(query)
            print(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Symbol Resolution Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_static_mapping_tool():
    """Test the static mapping tool directly"""
    print("\n🗺️ Testing Static Mapping Tool...")
    
    try:
        from services.symbol_resolution_agent import STATIC_COMPANY_MAPPINGS
        
        # Test static mapping logic directly
        def check_mapping(company_name: str) -> dict:
            company_lower = company_name.lower().strip()
            if company_lower in STATIC_COMPANY_MAPPINGS:
                ticker = STATIC_COMPANY_MAPPINGS[company_lower]
                asset_type = 'crypto' if ticker.endswith('-USD') else 'stock'
                return {
                    "found": True,
                    "symbol": ticker,
                    "company_name": company_name.title(),
                    "asset_type": asset_type,
                    "source": "static_mapping",
                    "priority": "high"
                }
            return {
                "found": False,
                "reason": f"No static mapping found for '{company_name}'"
            }
        
        # Test direct mapping usage
        result1 = check_mapping("google")
        print(f"   'google' → {result1}")
        
        result2 = check_mapping("microsoft")  
        print(f"   'microsoft' → {result2}")
        
        result3 = check_mapping("unknown_company")
        print(f"   'unknown_company' → {result3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Static mapping tool test failed: {e}")
        return False

async def test_alpaca_search_tool():
    """Test the Alpaca search tool"""
    print("\n🔍 Testing Alpaca Search Tool...")
    
    try:
        from services.market_service_factory import MarketServiceFactory
        
        # Test Alpaca search logic directly
        async def test_search(query: str, limit: int = 5) -> dict:
            try:
                service = MarketServiceFactory.get_service()
                if not service:
                    return {
                        "found": False,
                        "error": "Market service not available"
                    }
                
                # Search via Alpaca API
                results = await service.search_assets(query, limit)
                
                if not results:
                    return {
                        "found": False,
                        "reason": f"No symbols found for '{query}'"
                    }
                
                # Return first result for testing
                best_match = results[0]
                return {
                    "found": True,
                    "symbol": best_match.get('symbol'),
                    "company_name": best_match.get('name'),
                    "asset_type": "stock",
                    "source": "alpaca_api",
                    "priority": "medium",
                    "total_results": len(results)
                }
                
            except Exception as e:
                return {
                    "found": False,
                    "error": str(e)
                }
        
        # Test Alpaca search
        result = await test_search("google", 5)
        print(f"   'google' search → {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alpaca search tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting OpenAI Agents SDK and Symbol Resolution Agent Tests\n")
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
    
    results = []
    
    # Run tests
    results.append(await test_openai_agents_basic())
    results.append(await test_function_tools())
    results.append(await test_static_mapping_tool())
    results.append(await test_alpaca_search_tool())
    results.append(await test_symbol_resolution_agent())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI Agents SDK is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())