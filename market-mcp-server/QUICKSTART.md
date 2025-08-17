# Market MCP Server - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install
```bash
cd /Users/MarcoPolo/workspace/market-mcp-server
npm run setup
```

### Step 2: Configure Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "market": {
      "command": "node",
      "args": ["/Users/MarcoPolo/workspace/market-mcp-server/index.js"]
    }
  }
}
```

### Step 3: Restart Claude
Quit and reopen Claude Desktop.

### Step 4: Test It!
Type in Claude: **"Get the current price of Apple stock"**

## ✅ That's it! You're ready to go!

---

## 🎯 Top 10 Most Useful Commands

### 1. Quick Stock Check
```
What's TSLA trading at?
```

### 2. Crypto Prices
```
Bitcoin and Ethereum prices please
```

### 3. Market Overview
```
How's the market doing today?
```

### 4. Top Movers
```
Show me today's biggest gainers
```

### 5. Technical Analysis
```
Calculate RSI for SPY
```

### 6. Market News
```
Latest market news
```

### 7. Portfolio Tracking
```
Track: 100 AAPL @ $150, 50 TSLA @ $200
```

### 8. Real-Time Streaming
```
Stream AAPL price for 30 seconds
```

### 9. Fear & Greed
```
What's the Fear & Greed Index?
```

### 10. Multi-Stock Quote
```
Prices for AAPL, GOOGL, MSFT, AMZN
```

---

## 🛠️ Troubleshooting

### Issue: "Command not found"
**Fix:** Make sure Node.js 18+ is installed
```bash
node --version  # Should be v18 or higher
```

### Issue: "Cannot find module"
**Fix:** Install dependencies
```bash
npm install
```

### Issue: "Symbol not found"
**Fix:** Use correct ticker symbols
- Stocks: `AAPL`, `TSLA`, `MSFT`
- Crypto: `bitcoin`, `ethereum` (lowercase)
- Indices: `^GSPC`, `^IXIC`, `^DJI`

### Issue: "Rate limit exceeded"
**Fix:** Wait 60 seconds (data is cached)

---

## 📚 Learn More

- Full documentation: [README.md](README.md)
- Usage examples: [EXAMPLES.md](EXAMPLES.md)
- All 35+ tools: See README for complete list

---

## 💡 Pro Tips

1. **Combine queries**: "Get AAPL quote, RSI, and news"
2. **Use time frames**: "TSLA history for 3 months"
3. **Stream multiple**: "Stream AAPL, MSFT, GOOGL"
4. **Set alerts**: "Alert me when BTC hits $50k"
5. **Track portfolios**: Save your holdings for easy tracking

---

## 🆘 Need Help?

1. Run diagnostics: `npm test`
2. Check setup: `npm run check`
3. Reinstall: `npm run setup`
4. Check the [examples](EXAMPLES.md)

---

## 🎉 You're All Set!

Start with simple commands and explore from there. The server handles 35+ different market data tools - have fun exploring!
