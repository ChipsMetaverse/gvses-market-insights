# Market MCP Server - Usage Examples

## 📊 Quick Start Examples

These examples show how to use the Market MCP Server tools in Claude Desktop.

### Stock Market Examples

#### Get a Simple Stock Quote
```
Get the current price of Apple stock
```

#### Get Detailed Stock Information
```
Give me detailed fundamentals for Microsoft including PE ratio, market cap, and financial metrics
```

#### Track Multiple Stocks
```
Show me current prices for AAPL, GOOGL, MSFT, AMZN, and TSLA with their daily changes
```

#### Historical Data
```
Show me Tesla's price history for the last 3 months with weekly intervals
```

#### Options Trading
```
Get the options chain for SPY expiring next month
```

#### Streaming Prices
```
Stream real-time prices for AAPL, MSFT, and GOOGL for the next 60 seconds
```

### Cryptocurrency Examples

#### Get Crypto Prices
```
What's the current price of Bitcoin, Ethereum, and Solana?
```

#### Top Cryptocurrencies
```
Show me the top 20 cryptocurrencies by market cap with their 24-hour changes
```

#### DeFi Protocols
```
Get DeFi data for Uniswap including TVL and chain distribution
```

#### Stream Crypto Prices
```
Stream Bitcoin and Ethereum prices for 30 seconds
```

### Technical Analysis Examples

#### Calculate Indicators
```
Calculate RSI, MACD, and Bollinger Bands for SPY
```

#### Support and Resistance
```
Find support and resistance levels for TSLA based on the last 3 months
```

#### Multiple Indicators
```
Give me a complete technical analysis for NVDA including RSI, MACD, Bollinger Bands, SMA, and EMA
```

### Market Overview Examples

#### Complete Market Snapshot
```
Give me a complete market overview including indices, bonds, and commodities
```

#### Market Movers
```
Show me today's top gainers and losers in the stock market
```

#### Sector Performance
```
How are different market sectors performing today?
```

#### Fear & Greed Index
```
What's the current market Fear & Greed Index and what does it mean?
```

### News and Analysis Examples

#### Latest News
```
Get the latest market news
```

#### Filtered News
```
Get cryptocurrency news from the last 24 hours
```

#### Streaming News
```
Stream market news with keywords "Fed" and "inflation" for the next 2 minutes
```

#### Analyst Ratings
```
What are the analyst ratings and price targets for Amazon?
```

#### Insider Trading
```
Show insider trading activity for Meta in the last 30 days
```

### Portfolio Management Examples

#### Create a Watchlist
```
Create a watchlist called "Tech Giants" with AAPL, GOOGL, MSFT, AMZN, META, and NVDA
```

#### Track Portfolio Performance
```
Track my portfolio: 100 shares of AAPL bought at $150, 50 shares of TSLA at $200, 200 shares of MSFT at $300
```

#### Calculate Correlations
```
Calculate the correlation between SPY, QQQ, and DIA over the last 6 months
```

### Economic Data Examples

#### Treasury Yields
```
Show me current US Treasury yields and analyze the yield curve
```

#### Commodities
```
Get current prices for gold, silver, oil, and natural gas
```

#### Forex Rates
```
Show me forex rates for EUR, GBP, JPY, and CHF against USD
```

#### Economic Calendar
```
Show upcoming economic events for the next 7 days
```

### Alert Examples

#### Set Price Alerts
```
Set an alert when Apple goes above $200
Set an alert when Bitcoin drops below $40,000
```

#### Monitor Alerts
```
Stream my active price alerts for the next 2 minutes
```

## 🔥 Advanced Combinations

### Complete Stock Analysis
```
Give me a complete analysis of NVDA including:
1. Current quote with pre/post market data
2. Technical indicators (RSI, MACD, Bollinger Bands)
3. Support and resistance levels
4. Recent analyst ratings
5. Latest news about the company
```

### Market Dashboard
```
Create a market dashboard showing:
1. Major indices (S&P 500, NASDAQ, DOW, VIX)
2. Top 5 gainers and losers
3. Sector performance
4. Fear & Greed Index
5. Latest market news
```

### Crypto Portfolio Analysis
```
Analyze these cryptocurrencies: Bitcoin, Ethereum, Binance Coin, Cardano, and Solana
Include current prices, 24h changes, market caps, and correlation analysis
```

### Options Strategy Analysis
```
For SPY:
1. Get current price and technical indicators
2. Show options chain for next month
3. Identify support and resistance levels
4. Calculate implied volatility
```

### Economic Overview
```
Give me a complete economic overview:
1. Treasury yields and yield curve analysis
2. Commodity prices (gold, oil)
3. Major forex rates
4. Upcoming economic events
5. Current Fear & Greed Index
```

## 📈 Streaming Examples

### Multi-Asset Streaming
```
Stream the following for 2 minutes:
- Stock prices: AAPL, TSLA, SPY
- Crypto prices: Bitcoin, Ethereum
- Market news with keyword "earnings"
```

### Real-Time Market Monitor
```
Create a real-time monitor for the next 3 minutes showing:
- S&P 500 and VIX updates
- Top movers updates
- Breaking news alerts
```

## 💡 Tips for Best Results

1. **Be Specific**: Include ticker symbols when asking about specific stocks
2. **Set Time Frames**: Specify periods for historical data (1d, 1w, 1mo, 3mo, 1y)
3. **Combine Tools**: Ask for multiple analyses in one request
4. **Use Proper Symbols**: 
   - Stocks: AAPL, MSFT, GOOGL
   - ETFs: SPY, QQQ, DIA
   - Crypto: bitcoin, ethereum (lowercase for CoinGecko)
   - Indices: ^GSPC (S&P 500), ^IXIC (NASDAQ), ^DJI (DOW)
5. **Streaming Duration**: Keep streaming under 5 minutes for best performance

## 🎯 Common Workflows

### Morning Market Check
```
Good morning! Give me:
1. Pre-market futures
2. Yesterday's market summary
3. Today's economic events
4. Top pre-market movers
5. Latest market news
```

### End of Day Analysis
```
Market close analysis:
1. How did major indices perform today?
2. What were the top gainers and losers?
3. Which sectors led and lagged?
4. Any significant after-hours movements?
5. Tomorrow's earnings calendar
```

### Weekly Portfolio Review
```
Weekly portfolio review for my holdings:
[List your stocks]
Include:
1. Week's performance for each
2. Technical indicators status
3. Any analyst rating changes
4. Relevant news for each holding
5. Correlation analysis
```

## 🚀 Pro Tips

- **Rate Limits**: The server caches data for 60 seconds to avoid rate limits
- **Free Tiers**: Most features work without API keys using free tiers
- **Data Delay**: Free tier data may be delayed 15-20 minutes
- **Batch Requests**: Combine multiple queries for efficiency
- **Error Handling**: If a symbol fails, the server continues with others
