#!/usr/bin/env python3
"""
G'sves Agent Programmatic Setup using Admin Key
================================================
Creates a complete G'sves trading agent with:
- Knowledge base files
- Assistant configuration
- Tool definitions
- Responses API integration
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from backend directory
backend_env = Path(__file__).parent / "backend" / ".env"
load_dotenv(backend_env)

# Initialize with admin key
admin_key = os.getenv('OPENAI_ADMIN_KEY')
if not admin_key:
    print("❌ OPENAI_ADMIN_KEY not found in .env")
    exit(1)

client = OpenAI(api_key=admin_key)

print("="*70)
print("🚀 G'sves Agent Programmatic Setup")
print("="*70)

# Step 1: Read current G'sves personality from idealagent.md
print("\n[Step 1] Loading G'sves personality from idealagent.md...")
idealagent_path = Path(__file__).parent / "idealagent.md"

if idealagent_path.exists():
    with open(idealagent_path, 'r') as f:
        personality_content = f.read()
    print(f"✅ Loaded {len(personality_content)} characters from idealagent.md")

    # Extract main personality sections
    lines = personality_content.split('\n')
    personality_lines = []
    in_personality = False
    for line in lines:
        if '# Personality' in line:
            in_personality = True
        elif line.startswith('# ') and in_personality and 'Personality' not in line:
            break
        if in_personality:
            personality_lines.append(line)

    personality_text = '\n'.join(personality_lines)
    print(f"✅ Extracted {len(personality_text)} character What is going on out here why a medical smell language nothing no can you please shut up
    print("⚠️  idealagent.md not found, using fallback") no
    personality_text = """
# Personality

You are G'sves, a senior portfolio manager with over 30 years of experience.

Your expertise includes inter-day option trading, swing option trading, options scalping,
Fundamental Equity Research, technical analysis, risk management, and short-term trading strategies.

You were trained under Warren Buffett, Paul Tudor Jones, Nancy Pelosi, Benjamin Graham, Ray Dalio, and George Soros.

You provide practical, actionable trading plans with detailed step-by-step analysis.
You focus on clarity, risk-reward ratios, technical signals, and current market conditions.
"""

# Step 2: Create comprehensive knowledge documents
print("\n[Step 2] Creating knowledge base documents...")

# Document 1: G'sves Trading Methodology
methodology_content = f"""{personality_text}

## Trading Level System

### LTB (Load the Boat)
Current definition from codebase - strongest buy signal:
- Multiple technical confluences
- Deep retracements (61.8% Fibonacci)
- 200-day moving average alignment
- Historical support levels
- Suitable for larger position sizes

### ST (Swing Trade)
Current definition from codebase - medium-term entries:
- 50-day moving average alignment
- Consolidation zones
- 50% Fibonacci retracements
- Balanced risk/reward
- Suitable for swing traders

### QE (Quick Entry)
Current definition from codebase - near-term opportunities:
- Near recent highs
- Psychological resistance levels
- Breakout zones with elevated RSI
- Higher risk, higher reward potential

## Risk Management Principles
- Never risk more than 2% of capital per trade
- Always use stop losses
- Position sizing based on account size
- Diversification across sectors
- Exit strategy defined before entry

## Analysis Framework
1. Check current price and moving averages
2. Identify LTB/ST/QE levels
3. Validate with technical indicators (RSI, MACD, volume)
4. Consider news catalysts
5. Calculate risk/reward ratio
6. Define entry, stop, and targets
7. Determine position size
8. Execute with discipline
"""

methodology_path = Path(__file__).parent / "gvses_methodology.md"
with open(methodology_path, 'w') as f:
    f.write(methodology_content)
print(f"✅ Created: {methodology_path.name}")

# Document 2: Options Trading Quick Reference
options_content = """# Options Trading Quick Reference for G'sves

## The Greeks (Simplified)

**Delta (Δ)**: How much option price moves per $1 stock move
- Call delta: 0 to 1.0 (50 delta = $0.50 move per $1 stock move)
- Put delta: -1.0 to 0 (negative because puts gain when stock drops)
- ATM options: ~0.50 delta
- Deep ITM: ~1.0 delta (moves like stock)
- Far OTM: ~0.10 delta (barely moves)

**Theta (Θ)**: Time decay (money lost per day)
- Always negative for option buyers
- Accelerates near expiration
- Weekly options: High theta (lose value FAST)

**Vega (ν)**: Sensitivity to volatility changes
- High vega = price changes a lot with IV changes
- Earnings = high vega due to uncertainty

**Gamma (Γ)**: Rate of delta change
- Highest at-the-money near expiration
- Tells you how fast delta will change

## Common Strategies

**Covered Call**: Own stock + sell call (income generation)
**Cash-Secured Put**: Sell put + hold cash (get paid to buy stock lower)
**Vertical Spread**: Buy one strike, sell another (defined risk/reward)
**Iron Condor**: Sell OTM put spread + OTM call spread (range-bound income)

## G'sves Weekly Options Selection Process

1. **Find stock near LTB/ST/QE level**
2. **Check IV Rank** - prefer < 50 for buying options
3. **Select strike based on view**:
   - Aggressive: Slightly OTM (higher R/R, lower probability)
   - Conservative: ATM (balanced)
4. **Check Greeks**:
   - Delta > 0.40 for calls
   - Theta not too high (< $0.20/day for small positions)
   - Vega moderate
5. **Calculate risk/reward**: Max loss = premium paid
6. **Set profit target**: 50-100% gain typical for weeklies
7. **Position size**: 2-5% of portfolio max

## Risk Management

- Max 2-5% of portfolio per options trade
- Stop loss at 50% of premium paid (common)
- Close winners at 50-100% gain
- Exit losers when thesis invalidated
- Don't hold through expiration (theta accelerates)

## Common Mistakes to Avoid

1. Buying too far OTM (low delta needs huge move)
2. Holding through expiration (theta kills you)
3. Ignoring IV (buying high IV = overpaying)
4. Too much size (options can go to zero)
5. No stop loss (hope is not a strategy)
6. Trading earnings without understanding IV crush
"""

options_path = Path(__file__).parent / "gvses_options_guide.md"
with open(options_path, 'w') as f:
    f.write(options_content)
print(f"✅ Created: {options_path.name}")

# Document 3: Market Analysis Checklist
checklist_content = """# G'sves Market Analysis Checklist

## Daily Market Brief Template

**Date**: [date]
**Time**: [time]

### Market Overview
- S&P 500: [price] ([change])
- Nasdaq: [price] ([change])
- Dow Jones: [price] ([change])
- VIX: [level] (fear gauge)

### Overnight Movers
**Top Gainers**:
1. [symbol] +[percent] - [catalyst]
2. [symbol] +[percent] - [catalyst]
3. [symbol] +[percent] - [catalyst]

**Top Losers**:
1. [symbol] -[percent] - [catalyst]
2. [symbol] -[percent] - [catalyst]
3. [symbol] -[percent] - [catalyst]

### Key Catalysts
- Economic data: [CPI, GDP, jobs, etc.]
- Fed news: [rate decision, minutes, speeches]
- Earnings: [major companies reporting]
- Geopolitical: [events affecting markets]

### Sector Performance
- Best: [sector] +[percent]
- Worst: [sector] -[percent]

### Trading Opportunities
1. **[Symbol]** @ LTB level
   - Entry: $[price]
   - Stop: $[price]
   - Target: $[price]
   - Risk/Reward: [ratio]

## Stock Analysis Template

**Symbol**: [TICKER]
**Current Price**: $[price] as of [timestamp]

### Technical Levels
- **LTB**: $[price] - [confluence factors]
- **ST**: $[price] - [confluence factors]
- **QE**: $[price] - [confluence factors]

### Technical Indicators
- **RSI**: [value] - [overbought/neutral/oversold]
- **MACD**: [bullish/bearish] crossover
- **50-day MA**: $[price]
- **200-day MA**: $[price]
- **Volume**: [current] vs [20-day avg] ([+/-]%)

### Support/Resistance
- **Resistance**: $[price], $[price], $[price]
- **Support**: $[price], $[price], $[price]

### News/Catalysts
- [Recent news affecting stock]
- [Upcoming events: earnings, product launches, etc.]

### Trade Setup
**IF** [bullish/bearish condition]
**THEN**:
- Entry: $[price]
- Stop: $[price]
- Target 1: $[price] ([R/R ratio])
- Target 2: $[price] ([R/R ratio])
- Position Size: [shares based on 2% risk]

**Options Alternative**:
- [Call/Put] $[strike] exp [date]
- Premium: $[cost]
- Delta: [value]
- Risk: $[max loss]
- Target: $[target price] ([%] gain)

## Risk Assessment
- ✅ Clear entry/exit defined
- ✅ Stop loss set
- ✅ Position size calculated
- ✅ Risk < 2% of portfolio
- ✅ Reward > 2x risk

## Guardrails Reminder
⚠️ This is educational analysis, not financial advice
⚠️ Past performance doesn't guarantee future results
⚠️ Always do your own research
⚠️ Never invest more than you can afford to lose
"""

checklist_path = Path(__file__).parent / "gvses_analysis_checklist.md"
with open(checklist_path, 'w') as f:
    f.write(checklist_content)
print(f"✅ Created: {checklist_path.name}")

# Step 3: Upload files to OpenAI
print("\n[Step 3] Uploading knowledge base files to OpenAI...")

uploaded_files = []
knowledge_files = [methodology_path, options_path, checklist_path]

# Also include main instruction document
if Path("AGENT_BUILDER_INSTRUCTIONS.md").exists():
    knowledge_files.append(Path("AGENT_BUILDER_INSTRUCTIONS.md"))
    print("  📄 Including AGENT_BUILDER_INSTRUCTIONS.md")

for file_path in knowledge_files:
    if file_path.exists():
        try:
            with open(file_path, 'rb') as f:
                file_obj = client.files.create(
                    file=f,
                    purpose='assistants'
                )
            uploaded_files.append(file_obj.id)
            print(f"  ✅ Uploaded: {file_path.name} (ID: {file_obj.id})")
        except Exception as e:
            print(f"  ❌ Failed to upload {file_path.name}: {e}")
    else:
        print(f"  ⚠️  File not found: {file_path.name}")

print(f"\n📚 Total files uploaded: {len(uploaded_files)}")

# Step 4: Create Assistant (Agent Builder uses this under the hood)
print("\n[Step 4] Creating G'sves Assistant...")

assistant_instructions = """You are G'sves, a senior portfolio manager with over 30 years of experience.

Your role is to provide data-driven market analysis and trading insights using a disciplined, educational approach.

## Core Responsibilities:
1. Analyze market conditions using real-time data
2. Identify LTB/ST/QE trading levels based on technical confluence
3. Provide options trade setups with Greeks analysis
4. Generate daily watchlists with catalysts
5. Deliver market briefs with actionable insights
6. Emphasize risk management and position sizing

## Communication Style:
- Use concise bullet points
- Lead with key actionable insights
- Reference timestamps for data accuracy
- Provide 2 tailored suggestions (varying risk tolerance)
- Always include risk management guidance

## Guardrails:
- This is educational analysis, NOT financial advice
- Emphasize stop losses and position sizing
- Never guarantee profits
- State past performance ≠ future results
- Maintain neutral, fact-based tone

## Tools Available:
You have access to real-time market data, technical analysis, news, and options information.
Use these tools to provide comprehensive, accurate analysis."""

try:
    assistant = client.beta.assistants.create(
        name="G'sves Trading Assistant",
        instructions=assistant_instructions,
        model="gpt-4o",  # Use latest model
        tools=[
            {"type": "file_search"}  # Enable file search for knowledge base
        ],
        tool_resources={
            "file_search": {
                "vector_stores": [{
                    "file_ids": uploaded_files,
                    "name": "G'sves Trading Knowledge Base"
                }]
            }
        } if uploaded_files else {}
    )

    print(f"✅ Assistant created!")
    print(f"   ID: {assistant.id}")
    print(f"   Name: {assistant.name}")
    print(f"   Model: {assistant.model}")

    # Save assistant ID to config
    config = {
        "assistant_id": assistant.id,
        "knowledge_file_ids": uploaded_files,
        "created_at": str(assistant.created_at),
        "model": assistant.model
    }

    config_path = Path(__file__).parent / "gvses_assistant_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved to: {config_path.name}")

except Exception as e:
    print(f"❌ Failed to create assistant: {e}")
    assistant = None

# Step 5: Test with Responses API
if assistant:
    print("\n[Step 5] Testing with Responses API...")

    try:
        # Test query
        test_query = "What's your trading philosophy in one sentence?"

        response = client.responses.create(
            model="gpt-4o",
            instructions=assistant_instructions,
            input=test_query,
            tools=[{"type": "web_search"}]  # Add web search
        )

        print(f"✅ Test query: '{test_query}'")
        print(f"📝 Response: {response.output_text}")
        print(f"🆔 Response ID: {response.id}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

# Step 6: Create integration code for voice pipeline
print("\n[Step 6] Creating voice pipeline integration...")

integration_code = f"""# G'sves Voice Pipeline Integration

## Configuration

Add to `backend/.env`:
```bash
GVSES_ASSISTANT_ID={assistant.id if assistant else 'YOUR_ASSISTANT_ID'}
```

## Integration Code

### Option A: Use Responses API Directly (Recommended)

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def process_voice_transcript(transcript: str, session_id: str):
    \"\"\"Process voice transcript with G'sves agent.\"\"\"

    # Call Responses API with G'sves configuration
    response = client.responses.create(
        model="gpt-4o",
        instructions=assistant_instructions,
        input=transcript,
        tools=[
            {{"type": "web_search"}},  # Real-time market data
            {{"type": "function", "name": "get_stock_quote", ...}},  # Your MCP tools
        ],
        store=True  # Enable multi-turn
    )

    return response.output_text

# In your voice pipeline:
# transcript = await openai_relay_server.receive_transcript()
# response_text = process_voice_transcript(transcript, session_id)
# await openai_relay_server.send_tts(response_text, session_id)
```

### Option B: Use Assistant with Threads

```python
def process_with_assistant(transcript: str, thread_id: str = None):
    \"\"\"Process using Assistant API with persistent threads.\"\"\"

    # Create or use existing thread
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Add user message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=transcript
    )

    # Run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=os.getenv('GVSES_ASSISTANT_ID')
    )

    # Wait for completion and get response
    # (Add polling logic here)

    return response_text, thread_id
```

## Testing

```bash
python3 test_gvses_voice_integration.py
```
"""

integration_path = Path(__file__).parent / "GVSES_VOICE_INTEGRATION.md"
with open(integration_path, 'w') as f:
    f.write(integration_code)

print(f"✅ Integration guide saved to: {integration_path.name}")

# Final Summary
print("\n" + "="*70)
print("🎯 Setup Complete!")
print("="*70)

if assistant:
    print(f"""
✅ G'sves Assistant Created:
   ID: {assistant.id}
   Knowledge Files: {len(uploaded_files)} uploaded
   Model: {assistant.model}

📝 Configuration saved to: gvses_assistant_config.json

🚀 Next Steps:

1. **Test the assistant**:
   python3 test_gvses_voice_integration.py

2. **Integrate with voice pipeline**:
   - Update backend/.env with GVSES_ASSISTANT_ID
   - Modify openai_relay_server.py to use Responses API
   - Test end-to-end voice flow

3. **Optional: Use Agent Builder UI**:
   - Import assistant ID: {assistant.id}
   - Visual workflow editor at: https://platform.openai.com/agent-builder
   - Connect MCP nodes for advanced routing

4. **Add custom tools** (your MCP servers):
   - Direct API MCP: agent-builder-functions/
   - Market Analysis MCP: market-mcp-server/

📚 Knowledge Base Ready:
   - G'sves methodology and trading levels
   - Options trading strategies and Greeks
   - Market analysis checklists and templates

🎤 Voice Integration:
   - See GVSES_VOICE_INTEGRATION.md for code examples
   - Responses API supports multi-turn conversations
   - Compatible with your OpenAI Realtime voice pipeline
""")
else:
    print("""
⚠️  Assistant creation failed, but knowledge files are uploaded.

Next steps:
1. Check API permissions
2. Verify file uploads succeeded
3. Try creating assistant manually in OpenAI dashboard
4. Use Responses API directly (doesn't require assistant)
""")

print("="*70)
