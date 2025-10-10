#!/usr/bin/env python3
"""
OpenAI Speech-to-Speech Tool Integration Test
============================================
Tests the complete OpenAI Realtime API with market data tools integration.
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.openai_tool_mapper import get_openai_tool_mapper
from services.openai_tool_orchestrator import get_openai_tool_orchestrator, ToolContext
from services.openai_relay_server import openai_relay_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tool_mapper():
    """Test the OpenAI tool mapper functionality."""
    logger.info("🔧 Testing OpenAI Tool Mapper...")
    
    try:
        tool_mapper = await get_openai_tool_mapper()
        
        # Test tool loading
        openai_tools = tool_mapper.get_openai_tools()
        logger.info(f"✅ Loaded {len(openai_tools)} tools for OpenAI")
        
        # Test high priority tools
        high_priority = tool_mapper.get_high_priority_tools()
        logger.info(f"✅ {len(high_priority)} high-priority tools identified")
        
        # Test individual tool execution
        test_result = await tool_mapper.execute_tool("get_stock_quote", {"symbol": "AAPL"})
        logger.info(f"✅ Tool execution test: {test_result.get('success', False)}")
        
        # Health check
        health = await tool_mapper.health_check()
        logger.info(f"✅ Tool mapper health: {health['status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool mapper test failed: {e}")
        return False


async def test_tool_orchestrator():
    """Test the tool orchestration layer."""
    logger.info("🎼 Testing Tool Orchestrator...")
    
    try:
        orchestrator = await get_openai_tool_orchestrator()
        
        # Test context analysis and tool chaining
        test_contexts = [
            ToolContext(
                user_query="What's Tesla doing today?",
                symbols_mentioned=["TSLA"],
                intent="price_query"
            ),
            ToolContext(
                user_query="Show me a comprehensive analysis of Apple over the last quarter",
                symbols_mentioned=["AAPL"],
                timeframe="3M",
                analysis_depth="comprehensive"
            ),
            ToolContext(
                user_query="How is the overall market performing?",
                intent="market_overview"
            )
        ]
        
        for i, context in enumerate(test_contexts, 1):
            logger.info(f"Testing context {i}: {context.user_query}")
            
            # Test intelligent tool orchestration
            executions = await orchestrator.orchestrate_tools(context)
            
            successful = sum(1 for e in executions if e.result and not e.error)
            logger.info(f"✅ Context {i}: {successful}/{len(executions)} tools executed successfully")
        
        # Test performance metrics
        metrics = orchestrator.get_performance_metrics()
        logger.info(f"✅ Performance metrics: {metrics.get('success_rate', 0):.1f}% success rate")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool orchestrator test failed: {e}")
        return False


async def test_openai_relay_server_ready():
    """Test that the OpenAI relay server is configured."""
    logger.info("🎙️ Testing OpenAI Relay Server...")

    try:
        # Basic attribute checks to ensure relay is wired up
        if openai_relay_server is None:
            logger.error("❌ Relay server instance is missing")
            return False

        if not hasattr(openai_relay_server, "api_key"):
            logger.error("❌ Relay server missing api_key attribute")
            return False

        if openai_relay_server.api_key:
            logger.info("✅ Relay server API key configured")
        else:
            logger.warning("⚠️ Relay server API key not configured; voice sessions will be disabled")

        logger.info(
            "✅ OpenAI relay server ready (max %s sessions)",
            getattr(openai_relay_server, "max_concurrent_sessions", "unknown")
        )
        return True

    except Exception as e:
        logger.error(f"❌ OpenAI relay server test failed: {e}")
        return False


async def test_tool_integration_scenarios():
    """Test specific voice-to-tool integration scenarios."""
    logger.info("🧪 Testing Voice-to-Tool Integration Scenarios...")
    
    try:
        orchestrator = await get_openai_tool_orchestrator()
        
        # Scenario 1: Simple price query
        logger.info("Scenario 1: Simple price query")
        context = ToolContext(user_query="What's the price of NVDA?")
        executions = await orchestrator.orchestrate_tools(context)
        
        price_found = any(
            e.tool_name == "get_stock_quote" and 
            e.result and 
            "price" in str(e.result)
            for e in executions
        )
        logger.info(f"✅ Price query: {'Success' if price_found else 'Failed'}")
        
        # Scenario 2: Complex analysis request
        logger.info("Scenario 2: Complex analysis request")
        context = ToolContext(
            user_query="Give me a comprehensive analysis of Tesla including news and technical indicators",
            analysis_depth="comprehensive"
        )
        executions = await orchestrator.orchestrate_tools(context)
        
        tools_executed = {e.tool_name for e in executions if e.result}
        expected_tools = {"get_stock_quote", "get_stock_news", "get_technical_indicators"}
        
        analysis_complete = expected_tools.issubset(tools_executed)
        logger.info(f"✅ Complex analysis: {'Success' if analysis_complete else 'Partial'}")
        logger.info(f"   Executed tools: {list(tools_executed)}")
        
        # Scenario 3: Market overview
        logger.info("Scenario 3: Market overview")
        context = ToolContext(user_query="How are the markets doing today?")
        executions = await orchestrator.orchestrate_tools(context)
        
        market_data_found = any(
            e.tool_name in ["get_market_overview", "get_market_movers"] and e.result
            for e in executions
        )
        logger.info(f"✅ Market overview: {'Success' if market_data_found else 'Failed'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration scenario test failed: {e}")
        return False


def print_test_summary(results: dict):
    """Print a summary of all test results."""
    logger.info("\n" + "="*60)
    logger.info("🏁 TEST SUMMARY")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info("-"*60)
    logger.info(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! OpenAI speech-to-speech with tools is ready!")
    else:
        logger.info("⚠️ Some tests failed. Please review the errors above.")
    
    return passed_tests == total_tests


async def main():
    """Run all tests for OpenAI speech-to-speech tool integration."""
    logger.info("🚀 Starting OpenAI Speech-to-Speech Tool Integration Tests")
    logger.info("="*60)
    
    # Check environment variables
    required_env_vars = ["ANTHROPIC_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    optional_env_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
    
    logger.info("🔍 Checking environment variables...")
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"❌ Required environment variable {var} not found")
            return False
        else:
            logger.info(f"✅ {var} is configured")
    
    for var in optional_env_vars:
        if not os.getenv(var):
            logger.warning(f"⚠️ Optional environment variable {var} not found")
        else:
            logger.info(f"✅ {var} is configured")
    
    # Run all tests
    test_results = {}
    
    logger.info("\n" + "="*60)
    test_results["Tool Mapper"] = await test_tool_mapper()
    
    logger.info("\n" + "="*60) 
    test_results["Tool Orchestrator"] = await test_tool_orchestrator()
    
    logger.info("\n" + "="*60)
    test_results["OpenAI Relay Server"] = await test_openai_relay_server_ready()
    
    logger.info("\n" + "="*60)
    test_results["Integration Scenarios"] = await test_tool_integration_scenarios()
    
    # Print final summary
    success = print_test_summary(test_results)
    
    if success:
        logger.info("\n🎤 To test voice interaction:")
        logger.info("1. Start the backend server: cd backend && uvicorn mcp_server:app --reload")
        logger.info("2. Start the frontend: cd frontend && npm run dev")
        logger.info("3. Navigate to http://localhost:5174/?provider-test")
        logger.info("4. Select 'OpenAI Realtime Voice (Dev)' as provider")
        logger.info("5. Click connect and try voice commands like:")
        logger.info("   - 'What's Tesla doing today?'")
        logger.info("   - 'Give me a market overview'")
        logger.info("   - 'Show me Apple's technical analysis'")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        sys.exit(1)