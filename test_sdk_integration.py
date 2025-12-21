#!/usr/bin/env python3
"""
Test script for Agents SDK integration
"""

import asyncio
import sys
import os
sys.path.append('backend')
os.chdir('backend')

from services.agents_sdk_service import agents_sdk_service, AgentQuery

async def test_educational_query():
    """Test educational query - should be routed to direct explanation"""
    print("🎓 Testing Educational Query...")
    
    query = AgentQuery(
        query='What is a moving average in trading?',
        conversation_history=[],
        session_id='test-educational-123'
    )
    
    try:
        response = await agents_sdk_service.run_workflow(query)
        print('✅ Educational Query Test Success!')
        print(f'Intent: {response.data.get("intent", "unknown")}')
        print(f'Confidence: {response.data.get("confidence", "unknown")}')
        print(f'Model: {response.model}')
        print(f'Text Preview: {response.text[:200]}...')
        print(f'Tools Used: {response.tools_used}')
        print('-' * 80)
        return True
    except Exception as e:
        print(f'❌ Educational Query Test Failed: {str(e)}')
        print('-' * 80)
        return False

async def test_market_data_query():
    """Test market data query - should be routed to MCP tools"""
    print("📊 Testing Market Data Query...")
    
    query = AgentQuery(
        query='What is Tesla stock price?',
        conversation_history=[],
        session_id='test-market-123'
    )
    
    try:
        response = await agents_sdk_service.run_workflow(query)
        print('✅ Market Data Query Test Success!')
        print(f'Intent: {response.data.get("intent", "unknown")}')
        print(f'Confidence: {response.data.get("confidence", "unknown")}')
        print(f'Model: {response.model}')
        print(f'Text Preview: {response.text[:200]}...')
        print(f'Tools Used: {response.tools_used}')
        print(f'Chart Commands: {response.chart_commands}')
        print('-' * 80)
        return True
    except Exception as e:
        print(f'❌ Market Data Query Test Failed: {str(e)}')
        print('-' * 80)
        return False

async def test_chart_command():
    """Test chart command query - should be routed appropriately"""
    print("📈 Testing Chart Command Query...")
    
    query = AgentQuery(
        query='Switch chart to 4-hour timeframe',
        conversation_history=[],
        session_id='test-chart-123'
    )
    
    try:
        response = await agents_sdk_service.run_workflow(query)
        print('✅ Chart Command Query Test Success!')
        print(f'Intent: {response.data.get("intent", "unknown")}')
        print(f'Confidence: {response.data.get("confidence", "unknown")}')
        print(f'Model: {response.model}')
        print(f'Text Preview: {response.text[:200]}...')
        print(f'Tools Used: {response.tools_used}')
        print(f'Chart Commands: {response.chart_commands}')
        print('-' * 80)
        return True
    except Exception as e:
        print(f'❌ Chart Command Query Test Failed: {str(e)}')
        print('-' * 80)
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Agents SDK Integration Tests")
    print("=" * 80)
    
    tests = [
        test_educational_query(),
        test_market_data_query(), 
        test_chart_command()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = sum(1 for result in results if result is True)
    total_count = len(results)
    
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All tests passed! Agents SDK integration is working.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    # Cleanup
    await agents_sdk_service.cleanup()
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)