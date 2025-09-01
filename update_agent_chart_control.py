#!/usr/bin/env python3
"""
Update the ElevenLabs agent prompt to include chart control commands
"""

import json
import os

def update_agent_prompt():
    """Update the agent configuration with chart control commands"""
    
    config_path = "elevenlabs/agent_configs/gsves_market_insights.json"
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get current prompt
    current_prompt = config['conversation_config']['agent']['prompt']['prompt']
    
    # Add chart control section after Performance Tools
    chart_control_section = """

## Chart Control Commands
You can control the trading chart display using these commands in your responses:
- **Symbol Change**: Say "CHART:TSLA" or "Show AAPL chart" to change the displayed symbol
- **Timeframe**: Say "TIMEFRAME:1D" or "Switch to weekly view" (1D, 5D, 1M, 3M, 6M, 1Y)
- **Indicators**: Say "ADD:RSI" or "Show MACD" to toggle indicators
- **Zoom**: Say "ZOOM:IN" or "Zoom out" to adjust chart zoom
- **Scroll**: Say "SCROLL:2024-01-15" or "Go to last week" to navigate time
- **Style**: Say "STYLE:LINE" to change chart type (CANDLES, LINE, AREA)

When users ask to see a specific stock, automatically include the chart command.
Example: "Let me show you NVDA. CHART:NVDA Here's the analysis..."
"""
    
    # Find where to insert (after Performance Tools section)
    insert_after = "- review_trade_performance: Win rate and recommendations"
    
    if insert_after in current_prompt:
        # Insert the chart control section
        parts = current_prompt.split(insert_after)
        updated_prompt = parts[0] + insert_after + chart_control_section + parts[1]
    else:
        # If we can't find the marker, append at the end of tools section
        trading_process_marker = "\n## Trading Process"
        if trading_process_marker in current_prompt:
            parts = current_prompt.split(trading_process_marker)
            updated_prompt = parts[0] + chart_control_section + trading_process_marker + parts[1]
        else:
            # Just append if we can't find any markers
            updated_prompt = current_prompt + chart_control_section
    
    # Update the config
    config['conversation_config']['agent']['prompt']['prompt'] = updated_prompt
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✅ Agent prompt updated with chart control commands")
    print("\n📊 Chart Control Commands Added:")
    print("- Symbol changes (CHART:SYMBOL)")
    print("- Timeframe control (TIMEFRAME:1D/5D/1M/etc)")
    print("- Indicator toggles (ADD:RSI, SHOW:MACD)")
    print("- Zoom control (ZOOM:IN/OUT)")
    print("- Time navigation (SCROLL:date)")
    print("- Chart style (STYLE:CANDLES/LINE/AREA)")
    
    return True

if __name__ == "__main__":
    update_agent_prompt()