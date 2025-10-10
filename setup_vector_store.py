#!/usr/bin/env python3
"""
G'sves Vector Store Setup Script
Creates OpenAI vector store with trading knowledge for Agent Builder File Search
"""

import os
import sys
from openai import OpenAI
from pathlib import Path
import json

def main():
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Set it in backend/.env or export it:")
        print("   export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client initialized")

    # Create vector store
    print("\n📚 Creating vector store for G'sves trading knowledge...")
    vector_store = client.beta.vector_stores.create(
        name="gvses-trading-knowledge",
        description="G'sves trading methodology, technical analysis, options strategies, and market education"
    )

    print(f"✅ Vector store created: {vector_store.id}")
    print(f"   Name: {vector_store.name}")

    # Prepare files to upload
    base_path = Path(__file__).parent
    files_to_upload = []

    # 1. G'sves Methodology
    methodology_file = base_path / "AGENT_BUILDER_INSTRUCTIONS.md"
    if methodology_file.exists():
        files_to_upload.append({
            "path": methodology_file,
            "description": "G'sves personality, methodology, and trading philosophy"
        })
        print(f"   📄 Found: AGENT_BUILDER_INSTRUCTIONS.md")

    # 2. Technical Analysis Knowledge
    ta_json = base_path / "backend" / "training" / "json_docs" / "technical_analysis_for_dummies_2nd_edition.json"
    if ta_json.exists():
        # Convert JSON to markdown for better vector search
        with open(ta_json, 'r') as f:
            ta_data = json.load(f)

        # Create markdown version
        ta_md = base_path / "technical_analysis_knowledge.md"
        with open(ta_md, 'w') as f:
            f.write("# Technical Analysis for Dummies (2nd Edition)\n\n")
            for entry in ta_data:
                f.write(f"## {entry.get('topic', 'Unknown Topic')}\n\n")
                f.write(f"{entry.get('content', '')}\n\n")

        files_to_upload.append({
            "path": ta_md,
            "description": "Technical Analysis knowledge base"
        })
        print(f"   📄 Converted: technical_analysis_for_dummies_2nd_edition.json → .md")

    # 3. Hybrid Tool Strategy
    strategy_file = base_path / "HYBRID_TOOL_STRATEGY.md"
    if strategy_file.exists():
        files_to_upload.append({
            "path": strategy_file,
            "description": "Tool usage strategy for Agent Builder"
        })
        print(f"   📄 Found: HYBRID_TOOL_STRATEGY.md")

    # 4. MCP Tool Mapping
    mapping_file = base_path / "MCP_TOOL_MAPPING.md"
    if mapping_file.exists():
        files_to_upload.append({
            "path": mapping_file,
            "description": "Available tools and their capabilities"
        })
        print(f"   📄 Found: MCP_TOOL_MAPPING.md")

    # Create additional knowledge documents
    print("\n📝 Creating supplementary knowledge documents...")

    # Options Trading Guide
    options_guide = base_path / "options_trading_guide.md"
    with open(options_guide, 'w') as f:
        f.write("""# Options Trading Guide

## What are Options?

Options are contracts that give the holder the right (but not obligation) to buy or sell an underlying asset at a specified price (strike price) before or on a specific date (expiration date).

### Call Options
- **Right to BUY** at the strike price
- **Bullish strategy** - profit when stock goes up
- **Example**: AAPL $175 Call expiring Oct 17
  - If AAPL is at $180 on Oct 17, option is worth at least $5
  - If AAPL is below $175, option expires worthless

### Put Options
- **Right to SELL** at the strike price
- **Bearish strategy** - profit when stock goes down
- **Example**: TSLA $245 Put expiring Oct 17
  - If TSLA is at $230 on Oct 17, option is worth at least $15
  - If TSLA is above $245, option expires worthless

## The Greeks

### Delta (Δ)
- **Measures**: Rate of change in option price relative to stock price
- **Call Delta**: 0 to 1.0 (0 to 100 in percentage)
  - 0.50 delta = option moves $0.50 for every $1 stock move
  - Higher delta = more sensitive to stock movement
- **Put Delta**: -1.0 to 0 (always negative)
- **At-the-money**: ~0.50 delta
- **In-the-money**: Higher delta (>0.70)
- **Out-of-the-money**: Lower delta (<0.30)

### Gamma (Γ)
- **Measures**: Rate of change of delta
- **Highest**: At-the-money options near expiration
- **Use**: Tells you how fast delta will change

### Theta (Θ)
- **Measures**: Time decay (money lost per day)
- **Always negative** for option buyers
- **Accelerates**: As expiration approaches
- **Weekly options**: High theta decay (lose value fast)

### Vega (ν)
- **Measures**: Sensitivity to implied volatility
- **High vega**: Option price changes a lot with IV changes
- **Earnings plays**: High vega due to volatility uncertainty

## Implied Volatility (IV)

### What is IV?
- Market's expectation of future volatility
- **High IV**: Expensive options (market expects big moves)
- **Low IV**: Cheap options (market expects quiet trading)

### IV Rank
- Where current IV sits in its 52-week range
- **Formula**: (Current IV - 52-week Low) / (52-week High - 52-week Low)
- **High IV Rank (>50)**: Good for selling options
- **Low IV Rank (<50)**: Good for buying options

### IV Percentile
- Percentage of days in the past year when IV was lower
- **75th percentile**: IV is higher than 75% of the past year

## Common Strategies

### 1. Covered Call (Income)
- **Setup**: Own 100 shares + sell 1 call
- **Goal**: Generate income from stock you own
- **Risk**: Stock called away if it rallies above strike
- **Best**: Neutral to slightly bullish outlook

### 2. Cash-Secured Put (Income + Entry)
- **Setup**: Sell put + hold cash to buy shares if assigned
- **Goal**: Get paid to potentially buy stock at lower price
- **Risk**: Must buy stock if it drops below strike
- **Best**: Want to own stock at lower price

### 3. Vertical Spread (Directional)
- **Bull Call Spread**: Buy lower strike call + sell higher strike call
- **Bear Put Spread**: Buy higher strike put + sell lower strike put
- **Goal**: Defined risk, defined reward
- **Best**: Moderate directional move expected

### 4. Iron Condor (Neutral Income)
- **Setup**: Sell OTM call spread + sell OTM put spread
- **Goal**: Profit if stock stays range-bound
- **Risk**: Loss if stock moves too much either direction
- **Best**: Low volatility, range-bound stocks

### 5. Straddle (Volatility Play)
- **Setup**: Buy call + buy put at same strike (ATM)
- **Goal**: Profit from big move in either direction
- **Risk**: Expensive due to high vega
- **Best**: Before earnings, expecting volatility

## Risk Management for Options

### Position Sizing
- **Max per trade**: 2-5% of portfolio
- **Max total options exposure**: 20-30% of portfolio
- **Account for theta**: Weekly options lose value FAST

### Stop Losses
- **Percentage based**: -50% of premium paid is common
- **Time based**: Close if thesis doesn't play out in X days
- **Delta based**: Adjust if delta moves against you

### When to Exit
1. **Hit profit target** (50-100% gain common)
2. **Hit stop loss** (50% loss common)
3. **Thesis invalidated** (news, technicals break)
4. **Close to expiration** (last week - theta accelerates)

## G'sves Options Methodology

### Weekly Options Selection
1. **Identify stock near LTB, ST, or QE level**
2. **Check IV Rank** - prefer < 50 for buying options
3. **Select strike** based on directional view:
   - **Aggressive**: Slightly OTM (higher R/R but lower probability)
   - **Conservative**: ATM (balanced approach)
4. **Check Greeks**:
   - Delta > 0.40 for calls (decent movement potential)
   - Theta not too high (< $0.20/day for small positions)
   - Vega moderate (avoid super high IV unless earnings play)
5. **Calculate risk/reward**: Max loss = premium paid
6. **Set profit target**: 50-100% gain is reasonable for weekly

### Example Weekly Setup
**Stock**: TSLA at $245 (at ST level)
**View**: Bullish breakout above $250
**Strategy**: Buy weekly call
- **Strike**: $250 (slightly OTM)
- **Expiration**: This Friday (5 days)
- **Premium**: $3.50 per contract ($350 total)
- **Delta**: 0.45 (moves $0.45 per $1 TSLA move)
- **Theta**: -$0.15/day ($15/day decay)
- **Target**: $7.00 (100% gain)
- **Stop**: $1.75 (50% loss)
- **Max Loss**: $350

**Risk Management**:
- Only risk 2% of $10,000 portfolio = $200 max
- Buy 0.5 contracts if available, or 1 contract if <$200 risk
- Close if TSLA breaks below $242 (invalidates bullish thesis)
- Take profits if TSLA hits $255+ (50%+ gain likely)

## Common Mistakes to Avoid

1. **Buying too far OTM**: Low delta = needs huge move to profit
2. **Holding through expiration**: Theta decay accelerates
3. **Ignoring IV**: Buying high IV = overpaying
4. **Too much size**: Options can go to zero
5. **No stop loss**: Hope is not a strategy
6. **Earnings without understanding**: IV crush can kill profits

## Educational Resources

- **tastytrade**: Options education platform
- **OptionStrat**: Visualize options strategies
- **Market Chameleon**: IV data and analysis
- **Investopedia**: Options terminology

---

**Remember**: Options are LEVERAGED instruments. Great for defined-risk trades, dangerous without proper education and risk management. Start small, learn the Greeks, and always have an exit plan.
""")

    files_to_upload.append({
        "path": options_guide,
        "description": "Complete options trading guide with Greeks explained"
    })
    print(f"   ✅ Created: options_trading_guide.md")

    # Trading Psychology Guide
    psychology_guide = base_path / "trading_psychology_guide.md"
    with open(psychology_guide, 'w') as f:
        f.write("""# Trading Psychology & Risk Management

## The Trader's Mind

### Emotional Discipline
- **Fear**: Causes premature exits, missed opportunities
- **Greed**: Leads to holding too long, overleveraging
- **Hope**: Makes you hold losers, ignore stop losses
- **Revenge trading**: Trying to "get even" after losses

### Solution: Process Over Outcome
- Focus on executing your plan, not the result
- One trade doesn't define you
- Keep a trading journal to identify patterns

## Risk Management Principles

### Position Sizing
**The 2% Rule**: Never risk more than 2% of capital on any single trade

**Example**:
- $10,000 account
- 2% risk = $200 max loss per trade
- Stock at $50, stop at $48 = $2 risk per share
- Position size: $200 / $2 = 100 shares max

### Diversification
- **Max per position**: 5-10% of portfolio
- **Max per sector**: 25-30% of portfolio
- **Mix timeframes**: Some day trades, some swing trades

### Stop Losses (ALWAYS USE THEM)
- **Technical stops**: Below support, above resistance
- **Percentage stops**: 5-10% for swing trades
- **ATR stops**: 2x Average True Range below entry
- **Time stops**: Exit if thesis doesn't work in X days

## G'sves Risk Framework

### Trade Entry Checklist
- [ ] Identified clear LTB, ST, or QE level
- [ ] Confirmed with technical indicators (RSI, MA, volume)
- [ ] News catalyst or technical setup present
- [ ] Risk/reward ratio > 2:1
- [ ] Stop loss defined BEFORE entry
- [ ] Position size calculated (2% max risk)
- [ ] Documented trade thesis in journal

### Trade Management
1. **Set alerts**: Don't watch the ticker all day
2. **Honor stops**: No "just a little longer"
3. **Take partials**: Scale out at targets (50% at 1R, 50% at 2R)
4. **Trail stops**: Lock in profits as trade moves favorably
5. **Review daily**: Did I follow my plan?

### Post-Trade Review
**For Winners**:
- What did I do right?
- Was it skill or luck?
- Can I replicate this setup?

**For Losers**:
- Did I follow my plan?
- Was stop loss too tight?
- What can I learn?

## Common Psychological Traps

### Confirmation Bias
- **Trap**: Only seeing evidence that supports your view
- **Fix**: Actively look for reasons your trade is WRONG

### Loss Aversion
- **Trap**: Holding losers, cutting winners
- **Fix**: "Cut losers quickly, let winners run"

### Recency Bias
- **Trap**: Thinking recent results represent skill
- **Fix**: Track 100+ trades before judging performance

### Overtrading
- **Trap**: Trading out of boredom or to "make up" losses
- **Fix**: Set max trades per day/week

## The Winning Mindset

### What Successful Traders Do
1. **Follow their plan religiously**
2. **Accept that losses are part of trading**
3. **Focus on process, not money**
4. **Continuously learn and adapt**
5. **Keep detailed records**
6. **Take breaks after big wins/losses**

### G'sves Philosophy
> "I'd rather miss an opportunity than take a bad trade. There's always another setup tomorrow."

- **Quality over quantity**: 2-3 high-quality setups > 20 mediocre trades
- **Patience pays**: Wait for LTB/ST/QE confluence
- **Risk first, reward second**: Protect capital above all
- **Compound gains**: Small consistent wins > big home runs

## Trading Journal Template

### Pre-Trade
- **Date/Time**:
- **Symbol**:
- **Entry Price**:
- **Stop Loss**:
- **Profit Target**:
- **Position Size**:
- **Risk Amount**:
- **R/R Ratio**:
- **Thesis**: Why am I taking this trade?
- **Setup Type**: LTB / ST / QE / Other

### During Trade
- **Emotions**: How am I feeling?
- **Deviations**: Am I following my plan?
- **News**: Any unexpected developments?

### Post-Trade
- **Exit Price**:
- **Exit Reason**: Target / Stop / Time / Other
- **Actual Gain/Loss**:
- **Actual R Multiple**:
- **What I Did Right**:
- **What I Did Wrong**:
- **Lessons Learned**:

---

**Key Takeaway**: The difference between profitable and losing traders isn't intelligence or access to information—it's DISCIPLINE and RISK MANAGEMENT.
""")

    files_to_upload.append({
        "path": psychology_guide,
        "description": "Trading psychology and risk management framework"
    })
    print(f"   ✅ Created: trading_psychology_guide.md")

    # Upload files to vector store
    if not files_to_upload:
        print("\n⚠️  Warning: No files found to upload")
        print("   Vector store created but empty")
    else:
        print(f"\n📤 Uploading {len(files_to_upload)} files to vector store...")

        file_ids = []
        for file_info in files_to_upload:
            file_path = file_info["path"]
            description = file_info["description"]

            try:
                with open(file_path, "rb") as f:
                    # Upload file to OpenAI
                    file_obj = client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                    file_ids.append(file_obj.id)
                    print(f"   ✅ Uploaded: {file_path.name} ({description})")
            except Exception as e:
                print(f"   ❌ Failed to upload {file_path.name}: {e}")

        # Attach files to vector store
        if file_ids:
            print(f"\n🔗 Attaching {len(file_ids)} files to vector store...")
            try:
                batch = client.beta.vector_stores.file_batches.create(
                    vector_store_id=vector_store.id,
                    file_ids=file_ids
                )
                print(f"   ✅ Batch created: {batch.id}")
                print(f"   Status: {batch.status}")
            except Exception as e:
                print(f"   ❌ Failed to attach files: {e}")

    # Save vector store ID to config file
    config_file = base_path / "vector_store_config.json"
    config = {
        "vector_store_id": vector_store.id,
        "name": vector_store.name,
        "created_at": vector_store.created_at,
        "file_count": len(files_to_upload),
        "files": [f["path"].name for f in files_to_upload]
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to: vector_store_config.json")

    # Print summary
    print("\n" + "="*60)
    print("📊 VECTOR STORE SETUP COMPLETE")
    print("="*60)
    print(f"\n📌 Vector Store ID: {vector_store.id}")
    print(f"📌 Name: {vector_store.name}")
    print(f"📌 Files Uploaded: {len(files_to_upload)}")
    print("\n📋 Next Steps:")
    print("   1. Copy the Vector Store ID above")
    print("   2. In Agent Builder, add a 'File Search' node")
    print("   3. Configure the node:")
    print(f"      - Vector Store ID: {vector_store.id}")
    print("      - Query: {{user_message}} (dynamic)")
    print("      - Max Results: 5")
    print("      - Relevance Threshold: 0.7")
    print("\n   4. Connect File Search node to Gvses Agent for RAG")
    print("\n🎯 Usage: Agent will now have access to:")
    print("   - G'sves trading methodology")
    print("   - Technical analysis knowledge")
    print("   - Options trading strategies")
    print("   - Trading psychology & risk management")
    print("   - Tool usage documentation")
    print("\n💡 Example queries the RAG can answer:")
    print("   - 'What is a covered call?'")
    print("   - 'Explain delta and gamma'")
    print("   - 'How do I calculate LTB/ST/QE levels?'")
    print("   - 'What is IV rank?'")
    print("   - 'Trading psychology for beginners'")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
