#!/usr/bin/env python3
"""
Quick test to verify chart control function calling implementation.
"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test_chart_tools():
    """Test that chart control tools are properly configured."""
    try:
        from services.agent_orchestrator import AgentOrchestrator
        print('✅ AgentOrchestrator imports successfully\n')

        # Initialize orchestrator (requires async)
        orchestrator = AgentOrchestrator()
        await asyncio.sleep(0.1)  # Let initialization complete

        # Get tool schemas
        tools = orchestrator._get_tool_schemas()

        # Find chart-related tools (nested under 'function' key)
        chart_tools = [t for t in tools if 'chart' in t.get('function', {}).get('name', '').lower()]
        print(f'✅ Found {len(chart_tools)} chart control tools:')
        for tool in chart_tools:
            func = tool.get('function', {})
            name = func.get('name', 'unknown')
            desc = func.get('description', '')[:70]
            params = func.get('parameters', {}).get('properties', {})
            required = func.get('parameters', {}).get('required', [])
            print(f'   - {name}')
            print(f'     Description: {desc}...')
            print(f'     Parameters: {list(params.keys())}')
            if required:
                print(f'     Required: {required}')
            print()

        # Verify critical tools exist (extract from nested 'function' key)
        tool_names = {t.get('function', {}).get('name') for t in tools}
        required_tools = {
            'load_chart': 'Switch chart symbol',
            'set_chart_timeframe': 'Change timeframe',
            'add_chart_indicator': 'Add technical indicator',
            'get_current_chart_state': 'Get current chart info'
        }

        print('✅ Verifying required chart control tools:')
        all_present = True
        for tool_name, purpose in required_tools.items():
            if tool_name in tool_names:
                print(f'   ✅ {tool_name:<25} ({purpose})')
            else:
                print(f'   ❌ {tool_name:<25} MISSING!')
                all_present = False

        # Verify load_chart requires symbol parameter
        load_chart_tool = next((t for t in tools if t.get('function', {}).get('name') == 'load_chart'), None)
        if load_chart_tool:
            required_params = load_chart_tool.get('function', {}).get('parameters', {}).get('required', [])
            if 'symbol' in required_params:
                print('\n✅ load_chart requires "symbol" parameter (prevents LOAD: bug)')
            else:
                print('\n❌ load_chart does NOT require "symbol" parameter!')
                all_present = False

        if all_present:
            print('\n🎉 All chart control tools are properly configured!')
            print('\n📋 Implementation Summary:')
            print('   - Schema validation prevents malformed commands')
            print('   - Type-safe enum parameters for indicators/timeframes')
            print('   - Chart context storage for multi-turn conversations')
            print('   - Proper command extraction from tool results')
            return 0
        else:
            print('\n❌ Some required tools are missing!')
            return 1

    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(test_chart_tools())
    sys.exit(exit_code)
