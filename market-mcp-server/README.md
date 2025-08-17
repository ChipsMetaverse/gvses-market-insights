# Market MCP Server

A comprehensive Model Context Protocol (MCP) server for real-time market data with streaming capabilities. Access stock quotes, cryptocurrency prices, market news, technical analysis, and more from Yahoo Finance, CoinGecko, and other sources.

## 🚀 Features

### 📈 Stock Market Tools
- **Real-time Quotes**: Get detailed stock quotes with pre/post market data
- **Historical Data**: Access price history with customizable periods
- **Streaming Prices**: Real-time WebSocket streaming for multiple symbols
- **Options Chain**: View options data with strikes and expiration dates
- **Fundamentals**: Company financials, valuation metrics, and key statistics
- **Earnings Calendar**: Upcoming earnings reports and estimates

### 🪙 Cryptocurrency Tools
- **Live Prices**: Real-time crypto prices from CoinGecko
- **Market Data**: Top cryptocurrencies by market cap
- **Streaming Updates**: Stream crypto prices with customizable intervals
- **DeFi Analytics**: Protocol TVL and DeFi metrics
- **NFT Collections**: Basic NFT collection data

### 📊 Market Overview
- **Market Indices**: S&P 500, NASDAQ, DOW, VIX tracking
- **Market Movers**: Top gainers, losers, and most active stocks
- **Sector Performance**: Track performance across market sectors
- **Fear & Greed Index**: Market sentiment indicator

### 📰 News & Analysis
- **Market News**: Aggregated news from multiple sources
- **Streaming News**: Real-time news updates with keyword filtering
- **Analyst Ratings**: Price targets and recommendations
- **Insider Trading**: Track insider transactions

### 📉 Technical Analysis
- **Technical Indicators**: RSI, MACD, Bollinger Bands, SMA, EMA, Stochastic
- **Support & Resistance**: Calculate key price levels
- **Chart Patterns**: Detect common trading patterns
- **Pivot Points**: Calculate daily pivot levels

### 💼 Portfolio Tools
- **Watchlists**: Create and manage stock watchlists
- **Portfolio Tracking**: Track holdings performance and P&L
- **Correlation Analysis**: Calculate asset correlations

### 💵 Economic Data
- **Economic Calendar**: Upcoming economic events
- **Treasury Yields**: US Treasury bond yields and yield curve
- **Commodities**: Gold, Silver, Oil, Gas prices
- **Forex Rates**: Foreign exchange rates

### 🔔 Alerts
- **Price Alerts**: Set price target alerts
- **Stream Alerts**: Monitor active alerts in real-time

## 📦 Installation

### 1. Clone and Install

```bash
cd /Users/MarcoPolo/workspace/market-mcp-server
npm install
```

### 2. Configure Environment (Optional)

While the server works without API keys using free tiers, you can add optional API keys for enhanced features:

```bash
cp .env.example .env
```

Edit `.env` and add any API keys you have:

```env
# Optional - for enhanced features
ALPHAVANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
```

### 3. Configure Claude Desktop

Add to your Claude Desktop configuration:

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

### 4. Restart Claude Desktop

The market tools will be available immediately!

## 🎯 Usage Examples

### Stock Market Queries

```
Get the current price of Apple stock

Show me Tesla's price history for the last month

Stream real-time prices for AAPL, MSFT, and GOOGL for 30 seconds

What are the support and resistance levels for SPY?

Calculate RSI and MACD indicators for NVDA

Show me the options chain for AMZN expiring next month
```

### Cryptocurrency Queries

```
What's the current price of Bitcoin and Ethereum?

Show me the top 10 cryptocurrencies by market cap

Stream Bitcoin and Ethereum prices for 1 minute

Get DeFi protocol data for Uniswap
```

### Market Overview

```
Give me a complete market overview

Show me today's top gainers and losers

How are different sectors performing today?

What's the current Fear & Greed Index?
```

### News and Analysis

```
Get the latest market news

Stream market news with keywords "Fed" and "inflation"

What are the analyst ratings for Microsoft?

Show insider trading activity for META
```

### Portfolio Management

```
Create a watchlist with AAPL, TSLA, AMZN, and GOOGL

Track my portfolio: 100 shares of AAPL at $150, 50 shares of TSLA at $200

Calculate correlation between SPY, QQQ, and DIA
```

### Technical Analysis

```
Calculate technical indicators for SPY

Find support and resistance levels for Bitcoin

What are the Bollinger Bands saying about TSLA?
```

### Economic Data

```
Show me US Treasury yields

What's the current price of gold and oil?

Get forex rates for EUR, GBP, and JPY

Show upcoming economic events
```

### Alerts

```
Set an alert when AAPL goes above $200

Set an alert when Bitcoin drops below $40,000

Stream my active price alerts
```

## 🔧 Available Tools

The server provides **35+ tools** covering all aspects of market data:

### Core Market Tools
- `get_stock_quote` - Real-time stock quotes
- `get_stock_history` - Historical price data
- `stream_stock_prices` - WebSocket streaming
- `get_crypto_price` - Cryptocurrency prices
- `get_crypto_market_data` - Top crypto by market cap
- `stream_crypto_prices` - Stream crypto updates

### Analysis Tools
- `get_technical_indicators` - RSI, MACD, Bollinger Bands
- `get_support_resistance` - Key price levels
- `get_chart_patterns` - Pattern recognition
- `get_analyst_ratings` - Wall Street ratings
- `get_insider_trading` - Insider transactions

### Market Overview
- `get_market_overview` - Indices and commodities
- `get_market_movers` - Gainers/losers
- `get_sector_performance` - Sector rotation
- `get_fear_greed_index` - Sentiment indicator

### News & Data
- `get_market_news` - Latest news
- `stream_market_news` - Real-time news
- `get_economic_calendar` - Economic events
- `get_treasury_yields` - Bond yields

## ⚡ Streaming Capabilities

This server supports real-time streaming for:
- Stock prices (2-second updates)
- Cryptocurrency prices (3-second updates)
- Market news (10-second checks)
- Price alerts (5-second monitoring)

Streaming tools automatically handle:
- Rate limiting
- Error recovery
- Duration limits (max 5 minutes)
- Multiple symbol tracking

## 🔒 Rate Limiting & Caching

- Intelligent caching with 60-second TTL
- Rate limiting to prevent API abuse
- Concurrent request limiting (max 5)
- Automatic retry logic

## 🛠️ Advanced Features

### Custom Indicators
The server calculates various technical indicators locally:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA/EMA (Simple/Exponential Moving Averages)
- Stochastic Oscillator
- Pivot Points

### Correlation Analysis
- Pearson correlation calculations
- Multi-asset correlation matrices
- Historical correlation trends

### Market Sentiment
- Fear & Greed Index integration
- VIX-based calculations
- Sentiment interpretation

## 📝 Notes

- Most features work without API keys using free tiers
- Some data may have delays (15-20 minutes for free tiers)
- Streaming is simulated through polling for reliability
- NFT data requires additional API integration

## 🚦 Troubleshooting

### "Rate limit exceeded"
- The server implements caching to minimize this
- Wait 60 seconds for cache to refresh

### "Symbol not found"
- Verify the ticker symbol is correct
- Use Yahoo Finance format (e.g., "AAPL" for stocks)

### Streaming stops early
- Maximum streaming duration is 5 minutes
- Check your internet connection

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! The server is designed to be extensible:
- Add new data sources
- Implement additional indicators
- Enhance streaming capabilities

## 🔗 Data Sources

- **Yahoo Finance**: Stock quotes, options, fundamentals
- **CoinGecko**: Cryptocurrency data
- **DeFi Llama**: DeFi protocol metrics
- **Alternative.me**: Fear & Greed Index
