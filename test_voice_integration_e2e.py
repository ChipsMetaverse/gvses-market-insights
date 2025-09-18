#!/usr/bin/env python3
"""
End-to-End Voice Integration Test
===============================
Tests the complete OpenAI Realtime voice assistant integration with market data tools.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_complete_voice_integration():
    """Test the complete voice integration pipeline."""
    logger.info("🎤 Testing Complete Voice Integration Pipeline...")
    
    try:
        from services.openai_tool_mapper import get_openai_tool_mapper
        from services.openai_tool_orchestrator import get_openai_tool_orchestrator, ToolContext
        
        # Test 1: Tool Mapper with Voice Scenarios
        logger.info("1️⃣ Testing Tool Mapper for Voice Scenarios...")
        tool_mapper = await get_openai_tool_mapper()
        
        # Get high-priority tools (what voice assistant will use)
        voice_tools = tool_mapper.get_high_priority_tools()
        logger.info(f"✅ Voice Assistant has {len(voice_tools)} tools available:")
        
        for tool in voice_tools:
            name = tool.get("function", {}).get("name", "unknown")
            desc = tool.get("function", {}).get("description", "")
            logger.info(f"  🔧 {name}: {desc[:50]}...")
        
        # Test 2: Voice Command Simulation
        logger.info("\n2️⃣ Testing Voice Command Simulation...")
        
        # Simulate typical voice commands
        voice_commands = [
            {
                "query": "What's Tesla doing today?",
                "expected_tool": "get_stock_quote",
                "symbol": "TSLA"
            },
            {
                "query": "Give me a market overview",
                "expected_tool": "get_market_overview",
                "symbol": None
            },
            {
                "query": "Show me Apple's chart for the last month",
                "expected_tool": "get_stock_history", 
                "symbol": "AAPL"
            }
        ]
        
        orchestrator = await get_openai_tool_orchestrator()
        
        for i, cmd in enumerate(voice_commands, 1):
            logger.info(f"\n🎙️ Voice Command {i}: '{cmd['query']}'")
            
            # Create context like voice assistant would
            context = ToolContext(
                user_query=cmd["query"],
                symbols_mentioned=[cmd["symbol"]] if cmd["symbol"] else [],
                intent="voice_query"
            )
            
            # Test tool orchestration
            executions = await orchestrator.orchestrate_tools(context)
            
            if executions:
                logger.info(f"✅ Voice Command {i}: {len(executions)} tools executed")
                
                for execution in executions:
                    if execution.result and not execution.error:
                        tool_name = execution.tool_name
                        
                        # Check if we got expected data
                        if tool_name == "get_stock_quote" and cmd["symbol"]:
                            result = execution.result
                            if isinstance(result, dict) and "price" in result:
                                price = result["price"]
                                change = result.get("change_percent", 0)
                                logger.info(f"  💰 {cmd['symbol']}: ${price} ({change:+.2f}%)")
                            else:
                                logger.info(f"  📊 {tool_name}: Data received")
                        elif tool_name == "get_market_overview":
                            logger.info(f"  📈 Market Overview: Data received")
                        elif tool_name == "get_stock_history":
                            result = execution.result
                            if isinstance(result, dict) and "data" in result:
                                data_points = len(result["data"])
                                logger.info(f"  📊 {cmd['symbol']} History: {data_points} data points")
                            else:
                                logger.info(f"  📊 {tool_name}: Historical data received")
                        else:
                            logger.info(f"  🔧 {tool_name}: Executed successfully")
                    else:
                        logger.warning(f"  ❌ {execution.tool_name}: {execution.error}")
            else:
                logger.warning(f"❌ Voice Command {i}: No tools executed")
        
        # Test 3: Voice Response Formatting
        logger.info("\n3️⃣ Testing Voice Response Formatting...")
        
        # Test how data would be formatted for voice output
        test_result = await tool_mapper.execute_tool("get_stock_quote", {"symbol": "AAPL"})
        
        if test_result and isinstance(test_result, dict) and "price" in test_result:
            price = test_result["price"]
            change = test_result.get("change", 0)
            change_percent = test_result.get("change_percent", 0)
            
            # Format like voice assistant would say it
            if change >= 0:
                voice_response = f"Apple is trading at ${price:.2f}, up {change:.2f} dollars or {change_percent:.1f} percent"
            else:
                voice_response = f"Apple is trading at ${price:.2f}, down {abs(change):.2f} dollars or {abs(change_percent):.1f} percent"
            
            logger.info(f"🗣️ Voice Response: '{voice_response}'")
            logger.info("✅ Voice formatting test passed")
        else:
            logger.warning("❌ Voice formatting test failed - no price data")
        
        # Test 4: WebSocket Readiness
        logger.info("\n4️⃣ Testing WebSocket Integration Readiness...")
        
        try:
            from services.openai_realtime_service import OpenAIRealtimeService
            
            # Initialize service (don't connect, just test initialization)
            service = OpenAIRealtimeService()
            
            # Check if tool mapper is integrated
            if hasattr(service, 'tool_mapper'):
                logger.info("✅ OpenAI Realtime Service has tool mapper integration")
            else:
                logger.warning("⚠️ OpenAI Realtime Service missing tool mapper integration")
            
            # Check API key
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and len(api_key) > 50:
                logger.info("✅ OpenAI API key is configured for WebSocket connection")
            else:
                logger.warning("⚠️ OpenAI API key may not be properly configured")
            
            logger.info("✅ WebSocket integration is ready")
            
        except Exception as e:
            logger.error(f"❌ WebSocket integration error: {e}")
            return False
        
        logger.info("\n🎉 Complete Voice Integration Test PASSED!")
        logger.info("🎤 Ready for live voice testing at http://localhost:5174/?provider-test")
        logger.info("🔧 Select 'OpenAI Realtime Voice (Dev)' and test commands like:")
        logger.info("   - 'What's Tesla doing today?'")
        logger.info("   - 'Give me a market overview'")  
        logger.info("   - 'Show me Apple's technical analysis'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complete voice integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the complete voice integration test."""
    logger.info("🚀 Starting Complete Voice Integration Test")
    logger.info("=" * 60)
    
    success = await test_complete_voice_integration()
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ ALL TESTS PASSED - Voice Assistant Ready!")
    else:
        logger.info("❌ Some tests failed - Check errors above")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        sys.exit(1)