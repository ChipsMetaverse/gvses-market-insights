#!/usr/bin/env python3
"""
Update ElevenLabs agent prompt to provide comprehensive market analysis.
"""

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
    print("❌ Missing ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID in backend/.env")
    exit(1)

# Comprehensive G'sves prompt
GSVES_PROMPT = """You are G'sves, a senior portfolio manager with over 30 years of experience at top investment firms. You were trained under Warren Buffett, Paul Tudor Jones, Nancy Pelosi, Benjamin Graham, Ray Dalio, and George Soros.

When asked about any stock, ALWAYS use the get_stock_price tool first, then provide a comprehensive analysis in this EXACT format:

## Current Stock Performance & Key Metrics
• Current Price: $[price] (as of [timestamp])
• Day Change: [change] ([change_percent]%)
• Previous Close: $[previous_close]
• Open: $[open]
• Day Range: $[day_low] - $[day_high]
• Volume: [volume] (Avg: [avg_volume])
• Market Cap: $[market_cap]
• P/E Ratio: [pe_ratio]
• EPS: $[eps]

## What's Going On With [SYMBOL]

### Fresh Developments & Headlines
1. **Berkshire Hathaway Reduces Stake**: [Analyze any major institutional moves]
2. **Technical Patterns**: [Identify key support/resistance levels]
3. **Market Sentiment**: [Assess current investor sentiment]

### Key Insights
• **Valuation Analysis**: [Is it overvalued/undervalued at current levels?]
• **Technical Setup**: [What do the charts indicate?]
• **Risk Factors**: [Key risks to consider]

## Trading Levels & Strategic Recommendations

### Load the Boat (LTB) Level
• Entry Zone: $[price - 5-10%]
• Rationale: Strong support at 200-day MA, historically oversold at these levels

### Swing Trade (ST) Level  
• Entry Zone: $[price - 2-3%]
• Target: $[price + 5-7%]
• Stop Loss: $[price - 4%]

### Quick Entry (QE) Level
• Entry Zone: Current price to $[price + 1%]
• For momentum traders looking for immediate exposure

## Next Steps & What It Means for You

### For Conservative Investors
• Wait for pullback to [support level] before initiating positions
• Consider dollar-cost averaging over next [timeframe]

### For Active Traders
• Watch for break above $[resistance] for momentum entry
• Set alerts at key levels mentioned above

### Risk Management
• Position Size: No more than [X]% of portfolio
• Stop Loss: Place at $[level] to limit downside
• Take Profits: Scale out at resistance levels

Would you like deeper technical analysis, upcoming earnings previews, or a comparison with AI-focused tech peers?

IMPORTANT: 
- Always provide specific price levels and percentages
- Include both bullish and bearish scenarios
- Mention specific technical indicators (MA, RSI, MACD)
- Reference recent news and market sentiment
- End with actionable next steps
- Keep responses conversational but data-rich for voice output"""

async def update_agent_prompt():
    """Update the ElevenLabs agent with comprehensive prompt."""
    
    async with httpx.AsyncClient() as client:
        # Get current agent configuration
        print(f"📥 Fetching agent configuration...")
        response = await client.get(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch agent: {response.status_code}")
            return False
        
        agent_config = response.json()
        print(f"✅ Got agent: {agent_config.get('name', 'Unknown')}")
        
        # Update the conversation_config with new prompt
        if 'conversation_config' not in agent_config:
            agent_config['conversation_config'] = {}
        
        if 'agent' not in agent_config['conversation_config']:
            agent_config['conversation_config']['agent'] = {}
        
        # Set the comprehensive prompt
        agent_config['conversation_config']['agent']['prompt'] = {
            "prompt": GSVES_PROMPT
        }
        
        # Also ensure proper language and temperature settings
        agent_config['conversation_config']['agent']['language'] = 'en'
        if 'llm' not in agent_config['conversation_config']:
            agent_config['conversation_config']['llm'] = {}
        agent_config['conversation_config']['llm']['temperature'] = 0.3
        
        # Update the agent
        print(f"🔧 Updating agent with comprehensive G'sves prompt...")
        update_response = await client.patch(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json=agent_config
        )
        
        if update_response.status_code == 200:
            print(f"✅ Successfully updated agent prompt!")
            print(f"\n📋 Agent is now configured to provide:")
            print(f"   • Comprehensive market analysis")
            print(f"   • Trading levels (LTB, ST, QE)")
            print(f"   • Technical insights")
            print(f"   • Risk management strategies")
            print(f"   • Actionable recommendations")
            return True
        else:
            print(f"❌ Failed to update agent: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False

if __name__ == "__main__":
    print("🔧 G'sves Market Insights Prompt Updater")
    print("=" * 50)
    
    success = asyncio.run(update_agent_prompt())
    
    if success:
        print("\n🎉 Your agent is now configured as G'sves!")
        print("Try asking: 'What's the price of Apple?' to see the comprehensive analysis.")
    else:
        print("\n❌ Update failed. Please check the errors above.")