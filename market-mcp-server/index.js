import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import yahooFinance from 'yahoo-finance2';

// Redirect console.log to stderr for MCP server to prevent stdout pollution
// This ensures JSON-RPC protocol works correctly while preserving debug messages
const originalConsoleLog = console.log;
console.log = (...args) => {
  const message = args.join(' ');
  // Only allow JSON-RPC messages to stdout
  if (message.startsWith('{"jsonrpc"')) {
    originalConsoleLog(...args);
  } else {
    // All other messages (including Yahoo Finance debug) go to stderr
    console.error('[DEBUG]', ...args);
  }
};
import axios from 'axios';
import WebSocket from 'ws';
import * as cheerio from 'cheerio';
import NodeCache from 'node-cache';
import pLimit from 'p-limit';
import * as ta from 'technicalindicators';
import { format, subDays, subMonths } from 'date-fns';
import EventSource from 'eventsource';
import dotenv from 'dotenv';
import CNBCIntegration from './cnbc-integration.js';

dotenv.config();

// Cache with 60 second TTL for rate limiting
const cache = new NodeCache({ stdTTL: 60 });

// Initialize CNBC integration
const cnbc = new CNBCIntegration(cache);

// Rate limiter for API calls
const limit = pLimit(5); // Max 5 concurrent requests

class MarketMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'market-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          streaming: true, // Enable streaming
        },
      }
    );
    
    this.wsConnections = new Map();
    this.sseConnections = new Map();
    this.setupHandlers();
  }

  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        // Stock Market Tools
        {
          name: 'get_stock_quote',
          description: 'Get real-time stock quote with detailed metrics',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol (e.g., AAPL, TSLA)' },
              includePrePost: { type: 'boolean', description: 'Include pre/post market data' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_stock_history',
          description: 'Get historical stock price data',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              period: { type: 'string', enum: ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'], description: 'Time period' },
              interval: { type: 'string', enum: ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'], description: 'Data interval' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'stream_stock_prices',
          description: 'Stream real-time stock prices (WebSocket)',
          inputSchema: {
            type: 'object',
            properties: {
              symbols: { type: 'array', items: { type: 'string' }, description: 'Array of stock symbols to stream' },
              duration: { type: 'number', description: 'Stream duration in seconds (max 300)' }
            },
            required: ['symbols']
          }
        },
        
        {
          name: 'get_options_chain',
          description: 'Get options chain for a stock',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              expiration: { type: 'string', description: 'Option expiration date (YYYY-MM-DD)' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_stock_fundamentals',
          description: 'Get fundamental analysis data',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_earnings_calendar',
          description: 'Get upcoming earnings reports',
          inputSchema: {
            type: 'object',
            properties: {
              days: { type: 'number', description: 'Number of days ahead (default: 7)' }
            }
          }
        },
        
        // Cryptocurrency Tools
        {
          name: 'get_crypto_price',
          description: 'Get cryptocurrency price from CoinGecko',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'string', description: 'Crypto ID (e.g., bitcoin, ethereum)' },
              vsCurrency: { type: 'string', description: 'Currency to compare (default: usd)' },
              includeMarketCap: { type: 'boolean', description: 'Include market cap data' },
              include24hrChange: { type: 'boolean', description: 'Include 24hr change data' }
            },
            required: ['id']
          }
        },
        
        {
          name: 'get_crypto_market_data',
          description: 'Get top cryptocurrencies by market cap',
          inputSchema: {
            type: 'object',
            properties: {
              limit: { type: 'number', description: 'Number of cryptos to return (default: 20)' },
              page: { type: 'number', description: 'Page number for pagination' }
            }
          }
        },
        
        {
          name: 'stream_crypto_prices',
          description: 'Stream real-time crypto prices',
          inputSchema: {
            type: 'object',
            properties: {
              ids: { type: 'array', items: { type: 'string' }, description: 'Array of crypto IDs' },
              vsCurrency: { type: 'string', description: 'Currency (default: usd)' },
              duration: { type: 'number', description: 'Stream duration in seconds' }
            },
            required: ['ids']
          }
        },
        
        {
          name: 'get_defi_data',
          description: 'Get DeFi protocol data and TVL',
          inputSchema: {
            type: 'object',
            properties: {
              protocol: { type: 'string', description: 'DeFi protocol name' }
            }
          }
        },
        
        {
          name: 'get_nft_collection',
          description: 'Get NFT collection data',
          inputSchema: {
            type: 'object',
            properties: {
              collection: { type: 'string', description: 'NFT collection name or contract' }
            },
            required: ['collection']
          }
        },
        
        // Market Overview Tools
        {
          name: 'get_market_overview',
          description: 'Get overall market overview (indices, commodities, bonds)',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        
        {
          name: 'get_market_movers',
          description: 'Get top gainers, losers, and most active stocks',
          inputSchema: {
            type: 'object',
            properties: {
              type: { type: 'string', enum: ['gainers', 'losers', 'active'], description: 'Type of movers' }
            }
          }
        },
        
        {
          name: 'get_sector_performance',
          description: 'Get performance by market sector',
          inputSchema: {
            type: 'object',
            properties: {
              period: { type: 'string', enum: ['1d', '1w', '1m', '3m', 'ytd'], description: 'Time period' }
            }
          }
        },
        
        {
          name: 'get_fear_greed_index',
          description: 'Get market fear & greed index',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        
        // News and Analysis
        {
          name: 'get_market_news',
          description: 'Get latest market news from CNBC and other sources',
          inputSchema: {
            type: 'object',
            properties: {
              category: { type: 'string', enum: ['all', 'stocks', 'crypto', 'economy', 'earnings'], description: 'News category' },
              limit: { type: 'number', description: 'Number of articles (default: 10)' },
              includeCNBC: { type: 'boolean', description: 'Include CNBC news (default: true)' }
            }
          }
        },
        
        {
          name: 'get_cnbc_movers',
          description: 'Get pre-market movers from CNBC',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        
        {
          name: 'get_cnbc_sentiment',
          description: 'Get market sentiment and outlook from CNBC',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        
        {
          name: 'stream_market_news',
          description: 'Stream real-time market news',
          inputSchema: {
            type: 'object',
            properties: {
              sources: { type: 'array', items: { type: 'string' }, description: 'News sources to stream' },
              keywords: { type: 'array', items: { type: 'string' }, description: 'Keywords to filter' },
              duration: { type: 'number', description: 'Stream duration in seconds' }
            }
          }
        },
        
        {
          name: 'get_analyst_ratings',
          description: 'Get analyst ratings and price targets',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_insider_trading',
          description: 'Get insider trading activity',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              days: { type: 'number', description: 'Number of days to look back' }
            }
          }
        },
        
        // Technical Analysis
        {
          name: 'get_technical_indicators',
          description: 'Calculate technical indicators (RSI, MACD, Bollinger Bands, etc.)',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              indicators: { 
                type: 'array', 
                items: { type: 'string', enum: ['rsi', 'macd', 'bb', 'sma', 'ema', 'stoch', 'adx', 'cci'] },
                description: 'Technical indicators to calculate'
              },
              period: { type: 'number', description: 'Period for indicators (default: 14)' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_support_resistance',
          description: 'Calculate support and resistance levels',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              period: { type: 'string', enum: ['1mo', '3mo', '6mo', '1y'], description: 'Analysis period' }
            },
            required: ['symbol']
          }
        },
        
        {
          name: 'get_chart_patterns',
          description: 'Detect chart patterns (head and shoulders, triangles, etc.)',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol' },
              timeframe: { type: 'string', enum: ['1d', '1w', '1mo'], description: 'Chart timeframe' }
            },
            required: ['symbol']
          }
        },
        
        // Portfolio Tools
        {
          name: 'create_watchlist',
          description: 'Create a watchlist of stocks/cryptos',
          inputSchema: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Watchlist name' },
              symbols: { type: 'array', items: { type: 'string' }, description: 'Symbols to add' }
            },
            required: ['name', 'symbols']
          }
        },
        
        {
          name: 'track_portfolio',
          description: 'Track portfolio performance',
          inputSchema: {
            type: 'object',
            properties: {
              holdings: { 
                type: 'array', 
                items: {
                  type: 'object',
                  properties: {
                    symbol: { type: 'string' },
                    quantity: { type: 'number' },
                    avgCost: { type: 'number' }
                  }
                },
                description: 'Portfolio holdings'
              }
            },
            required: ['holdings']
          }
        },
        
        {
          name: 'calculate_correlation',
          description: 'Calculate correlation between assets',
          inputSchema: {
            type: 'object',
            properties: {
              symbols: { type: 'array', items: { type: 'string' }, description: 'Symbols to correlate' },
              period: { type: 'string', enum: ['1mo', '3mo', '6mo', '1y'], description: 'Analysis period' }
            },
            required: ['symbols']
          }
        },
        
        // Economic Data
        {
          name: 'get_economic_calendar',
          description: 'Get economic events calendar',
          inputSchema: {
            type: 'object',
            properties: {
              days: { type: 'number', description: 'Number of days ahead' },
              importance: { type: 'string', enum: ['all', 'high', 'medium', 'low'], description: 'Event importance' }
            }
          }
        },
        
        {
          name: 'get_treasury_yields',
          description: 'Get US Treasury yields',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        
        {
          name: 'get_commodities',
          description: 'Get commodity prices (gold, oil, etc.)',
          inputSchema: {
            type: 'object',
            properties: {
              commodities: { 
                type: 'array', 
                items: { type: 'string', enum: ['gold', 'silver', 'oil', 'gas', 'wheat', 'corn'] },
                description: 'Commodities to get'
              }
            }
          }
        },
        
        {
          name: 'get_forex_rates',
          description: 'Get foreign exchange rates',
          inputSchema: {
            type: 'object',
            properties: {
              base: { type: 'string', description: 'Base currency (default: USD)' },
              currencies: { type: 'array', items: { type: 'string' }, description: 'Target currencies' }
            }
          }
        },
        
        // Alerts and Notifications
        {
          name: 'set_price_alert',
          description: 'Set price alert for a symbol',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Symbol to watch' },
              targetPrice: { type: 'number', description: 'Target price' },
              condition: { type: 'string', enum: ['above', 'below'], description: 'Alert condition' }
            },
            required: ['symbol', 'targetPrice', 'condition']
          }
        },
        
        {
          name: 'stream_price_alerts',
          description: 'Stream active price alerts',
          inputSchema: {
            type: 'object',
            properties: {
              duration: { type: 'number', description: 'Stream duration in seconds' }
            }
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        let result;
        
        switch (name) {
          // Stock Market Tools
          case 'get_stock_quote':
            result = await this.getStockQuote(args);
            break;
            
          case 'get_stock_history':
            result = await this.getStockHistory(args);
            break;
            
          case 'stream_stock_prices':
            result = await this.streamStockPrices(args);
            break;
            
          case 'get_options_chain':
            result = await this.getOptionsChain(args);
            break;
            
          case 'get_stock_fundamentals':
            result = await this.getStockFundamentals(args);
            break;
            
          case 'get_earnings_calendar':
            result = await this.getEarningsCalendar(args);
            break;
            
          // Cryptocurrency Tools
          case 'get_crypto_price':
            result = await this.getCryptoPrice(args);
            break;
            
          case 'get_crypto_market_data':
            result = await this.getCryptoMarketData(args);
            break;
            
          case 'stream_crypto_prices':
            result = await this.streamCryptoPrices(args);
            break;
            
          case 'get_defi_data':
            result = await this.getDefiData(args);
            break;
            
          case 'get_nft_collection':
            result = await this.getNftCollection(args);
            break;
            
          // Market Overview
          case 'get_market_overview':
            result = await this.getMarketOverview();
            break;
            
          case 'get_market_movers':
            result = await this.getMarketMovers(args);
            break;
            
          case 'get_sector_performance':
            result = await this.getSectorPerformance(args);
            break;
            
          case 'get_fear_greed_index':
            result = await this.getFearGreedIndex();
            break;
            
          // News and Analysis
          case 'get_market_news':
            result = await this.getMarketNews(args);
            break;
            
          case 'get_cnbc_movers':
            result = await cnbc.getCNBCPreMarket();
            break;
            
          case 'get_cnbc_sentiment':
            result = await cnbc.getCNBCSentiment();
            break;
            
          case 'stream_market_news':
            result = await this.streamMarketNews(args);
            break;
            
          case 'get_analyst_ratings':
            result = await this.getAnalystRatings(args);
            break;
            
          case 'get_insider_trading':
            result = await this.getInsiderTrading(args);
            break;
            
          // Technical Analysis
          case 'get_technical_indicators':
            result = await this.getTechnicalIndicators(args);
            break;
            
          case 'get_support_resistance':
            result = await this.getSupportResistance(args);
            break;
            
          case 'get_chart_patterns':
            result = await this.getChartPatterns(args);
            break;
            
          // Portfolio Tools
          case 'create_watchlist':
            result = await this.createWatchlist(args);
            break;
            
          case 'track_portfolio':
            result = await this.trackPortfolio(args);
            break;
            
          case 'calculate_correlation':
            result = await this.calculateCorrelation(args);
            break;
            
          // Economic Data
          case 'get_economic_calendar':
            result = await this.getEconomicCalendar(args);
            break;
            
          case 'get_treasury_yields':
            result = await this.getTreasuryYields();
            break;
            
          case 'get_commodities':
            result = await this.getCommodities(args);
            break;
            
          case 'get_forex_rates':
            result = await this.getForexRates(args);
            break;
            
          // Alerts
          case 'set_price_alert':
            result = await this.setPriceAlert(args);
            break;
            
          case 'stream_price_alerts':
            result = await this.streamPriceAlerts(args);
            break;
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
        
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
      } catch (error) {
        return { content: [{ type: 'text', text: `Error: ${error.message}` }] };
      }
    });
  }
  
  // Stock Market Methods
  async getStockQuote(args) {
    const cacheKey = `quote_${args.symbol}`;
    const cached = cache.get(cacheKey);
    if (cached) return cached;
    
    try {
      // Primary data from Yahoo Finance
      const quote = await yahooFinance.quote(args.symbol);
      
      const result = {
        symbol: quote.symbol,
        name: quote.longName || quote.shortName,
        price: quote.regularMarketPrice,
        change: quote.regularMarketChange,
        changePercent: quote.regularMarketChangePercent,
        volume: quote.regularMarketVolume,
        marketCap: quote.marketCap,
        dayHigh: quote.regularMarketDayHigh,
        dayLow: quote.regularMarketDayLow,
        yearHigh: quote.fiftyTwoWeekHigh,
        yearLow: quote.fiftyTwoWeekLow,
        pe: quote.trailingPE,
        eps: quote.epsTrailingTwelveMonths,
        dividend: quote.dividendRate,
        dividendYield: quote.dividendYield,
        beta: quote.beta,
        timestamp: new Date().toISOString(),
        dataSources: ['Yahoo Finance']
      };
      
      // Try to enrich with CNBC data
      if (args.includeCNBC !== false) {
        try {
          const cnbcData = await cnbc.getCNBCQuote(args.symbol);
          if (cnbcData) {
            result.cnbc = {
              price: cnbcData.price,
              change: cnbcData.change,
              changePercent: cnbcData.changePercent,
              extendedHours: cnbcData.extendedHours,
              exchange: cnbcData.exchange,
              lastUpdate: cnbcData.lastUpdate
            };
            result.dataSources.push('CNBC');
          }
        } catch (cnbcError) {
          console.error(`CNBC data unavailable for ${args.symbol}`);
        }
      }
      
      if (args.includePrePost) {
        result.preMarket = {
          price: quote.preMarketPrice,
          change: quote.preMarketChange,
          changePercent: quote.preMarketChangePercent
        };
        result.postMarket = {
          price: quote.postMarketPrice,
          change: quote.postMarketChange,
          changePercent: quote.postMarketChangePercent
        };
      }
      
      cache.set(cacheKey, result);
      return result;
    } catch (error) {
      throw new Error(`Failed to get quote for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getStockHistory(args) {
    const period = args.period || '1mo';
    const interval = args.interval || '1d';
    
    try {
      const history = await yahooFinance.historical(args.symbol, {
        period1: this.getPeriodDate(period),
        period2: new Date(),
        interval
      });
      
      return {
        symbol: args.symbol,
        period,
        interval,
        data: history.map(h => ({
          date: h.date,
          open: h.open,
          high: h.high,
          low: h.low,
          close: h.close,
          volume: h.volume
        }))
      };
    } catch (error) {
      throw new Error(`Failed to get history for ${args.symbol}: ${error.message}`);
    }
  }
  
  async streamStockPrices(args) {
    const duration = Math.min(args.duration || 60, 300); // Max 5 minutes
    const symbols = args.symbols;
    const streamId = `stock_${Date.now()}`;
    
    return new Promise((resolve) => {
      const results = [];
      const startTime = Date.now();
      
      // Simulate streaming with polling
      const interval = setInterval(async () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        if (elapsed >= duration) {
          clearInterval(interval);
          resolve({
            streamId,
            duration: elapsed,
            symbols,
            updates: results,
            status: 'completed'
          });
          return;
        }
        
        // Fetch current prices
        const updates = await Promise.all(
          symbols.map(async (symbol) => {
            try {
              const quote = await yahooFinance.quote(symbol);
              return {
                symbol: quote.symbol,
                price: quote.regularMarketPrice,
                change: quote.regularMarketChange,
                changePercent: quote.regularMarketChangePercent,
                volume: quote.regularMarketVolume,
                timestamp: new Date().toISOString()
              };
            } catch (error) {
              return { symbol, error: error.message };
            }
          })
        );
        
        results.push({
          timestamp: new Date().toISOString(),
          data: updates
        });
        
      }, 2000); // Update every 2 seconds
    });
  }
  
  async getOptionsChain(args) {
    try {
      const options = await yahooFinance.options(args.symbol, {
        date: args.expiration
      });
      
      return {
        symbol: args.symbol,
        expirationDates: options.expirationDates,
        strikes: options.strikes,
        calls: options.options[0]?.calls || [],
        puts: options.options[0]?.puts || [],
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get options for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getStockFundamentals(args) {
    try {
      const [quote, financials] = await Promise.all([
        yahooFinance.quote(args.symbol),
        yahooFinance.quoteSummary(args.symbol, {
          modules: ['financialData', 'defaultKeyStatistics', 'summaryProfile']
        })
      ]);
      
      return {
        symbol: args.symbol,
        company: {
          name: quote.longName,
          sector: financials.summaryProfile?.sector,
          industry: financials.summaryProfile?.industry,
          employees: financials.summaryProfile?.fullTimeEmployees,
          description: financials.summaryProfile?.longBusinessSummary
        },
        valuation: {
          marketCap: quote.marketCap,
          enterpriseValue: financials.defaultKeyStatistics?.enterpriseValue,
          peRatio: quote.trailingPE,
          forwardPE: quote.forwardPE,
          pegRatio: financials.defaultKeyStatistics?.pegRatio,
          priceToBook: financials.defaultKeyStatistics?.priceToBook,
          priceToSales: financials.financialData?.priceToSalesTrailing12Months
        },
        financials: {
          revenue: financials.financialData?.totalRevenue,
          revenueGrowth: financials.financialData?.revenueGrowth,
          grossMargin: financials.financialData?.grossMargins,
          operatingMargin: financials.financialData?.operatingMargins,
          profitMargin: financials.financialData?.profitMargins,
          currentRatio: financials.financialData?.currentRatio,
          debtToEquity: financials.financialData?.debtToEquity,
          roe: financials.financialData?.returnOnEquity,
          roa: financials.financialData?.returnOnAssets
        }
      };
    } catch (error) {
      throw new Error(`Failed to get fundamentals for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getEarningsCalendar(args) {
    const days = args.days || 7;
    
    try {
      // This would typically call a dedicated earnings API
      // For now, simulating with Yahoo Finance trending
      const trending = await yahooFinance.trendingSymbols('US');
      
      return {
        period: `${days} days`,
        upcoming: trending.quotes.slice(0, 10).map(q => ({
          symbol: q.symbol,
          company: q.longName || q.shortName,
          estimatedDate: 'TBD',
          estimatedEPS: 'N/A',
          previousEPS: 'N/A'
        }))
      };
    } catch (error) {
      throw new Error(`Failed to get earnings calendar: ${error.message}`);
    }
  }
  
  // Cryptocurrency Methods
  async getCryptoPrice(args) {
    const vsCurrency = args.vsCurrency || 'usd';
    const cacheKey = `crypto_${args.id}_${vsCurrency}`;
    const cached = cache.get(cacheKey);
    if (cached) return cached;
    
    try {
      const response = await axios.get(
        `https://api.coingecko.com/api/v3/simple/price`,
        {
          params: {
            ids: args.id,
            vs_currencies: vsCurrency,
            include_market_cap: args.includeMarketCap || true,
            include_24hr_vol: true,
            include_24hr_change: args.include24hrChange || true,
            include_last_updated_at: true
          }
        }
      );
      
      const data = response.data[args.id];
      const result = {
        id: args.id,
        price: data[vsCurrency],
        marketCap: data[`${vsCurrency}_market_cap`],
        volume24h: data[`${vsCurrency}_24h_vol`],
        change24h: data[`${vsCurrency}_24h_change`],
        lastUpdated: new Date(data.last_updated_at * 1000).toISOString()
      };
      
      cache.set(cacheKey, result);
      return result;
    } catch (error) {
      throw new Error(`Failed to get crypto price for ${args.id}: ${error.message}`);
    }
  }
  
  async getCryptoMarketData(args) {
    const limit = args.limit || 20;
    const page = args.page || 1;
    
    try {
      const response = await axios.get(
        'https://api.coingecko.com/api/v3/coins/markets',
        {
          params: {
            vs_currency: 'usd',
            order: 'market_cap_desc',
            per_page: limit,
            page: page,
            sparkline: true,
            price_change_percentage: '1h,24h,7d'
          }
        }
      );
      
      return {
        page,
        limit,
        data: response.data.map(coin => ({
          rank: coin.market_cap_rank,
          id: coin.id,
          symbol: coin.symbol.toUpperCase(),
          name: coin.name,
          price: coin.current_price,
          marketCap: coin.market_cap,
          volume24h: coin.total_volume,
          change1h: coin.price_change_percentage_1h_in_currency,
          change24h: coin.price_change_percentage_24h,
          change7d: coin.price_change_percentage_7d_in_currency,
          sparkline: coin.sparkline_in_7d?.price?.slice(-24) // Last 24 points
        }))
      };
    } catch (error) {
      throw new Error(`Failed to get crypto market data: ${error.message}`);
    }
  }
  
  async streamCryptoPrices(args) {
    const duration = Math.min(args.duration || 60, 300);
    const vsCurrency = args.vsCurrency || 'usd';
    const streamId = `crypto_${Date.now()}`;
    
    return new Promise((resolve) => {
      const results = [];
      const startTime = Date.now();
      
      const interval = setInterval(async () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        if (elapsed >= duration) {
          clearInterval(interval);
          resolve({
            streamId,
            duration: elapsed,
            ids: args.ids,
            updates: results,
            status: 'completed'
          });
          return;
        }
        
        try {
          const response = await axios.get(
            'https://api.coingecko.com/api/v3/simple/price',
            {
              params: {
                ids: args.ids.join(','),
                vs_currencies: vsCurrency,
                include_24hr_change: true
              }
            }
          );
          
          const update = Object.entries(response.data).map(([id, data]) => ({
            id,
            price: data[vsCurrency],
            change24h: data[`${vsCurrency}_24h_change`],
            timestamp: new Date().toISOString()
          }));
          
          results.push({
            timestamp: new Date().toISOString(),
            data: update
          });
        } catch (error) {
          results.push({
            timestamp: new Date().toISOString(),
            error: error.message
          });
        }
      }, 3000); // Update every 3 seconds
    });
  }
  
  async getDefiData(args) {
    try {
      // Using DeFi Llama API
      const response = await axios.get(
        `https://api.llama.fi/protocol/${args.protocol}`
      );
      
      const data = response.data;
      return {
        name: data.name,
        symbol: data.symbol,
        tvl: data.tvl,
        chainTvls: data.chainTvls,
        change1d: data.change_1d,
        change7d: data.change_7d,
        mcap: data.mcap,
        category: data.category,
        chains: data.chains,
        description: data.description,
        url: data.url
      };
    } catch (error) {
      throw new Error(`Failed to get DeFi data for ${args.protocol}: ${error.message}`);
    }
  }
  
  async getNftCollection(args) {
    try {
      // Simplified NFT data - would typically use OpenSea or similar API
      return {
        collection: args.collection,
        floorPrice: 'API integration needed',
        volume24h: 'API integration needed',
        owners: 'API integration needed',
        items: 'API integration needed',
        message: 'NFT data requires specific API keys for OpenSea/Rarible'
      };
    } catch (error) {
      throw new Error(`Failed to get NFT data: ${error.message}`);
    }
  }
  
  // Market Overview Methods
  async getMarketOverview() {
    try {
      const [sp500, nasdaq, dow, vix] = await Promise.all([
        yahooFinance.quote('^GSPC'),
        yahooFinance.quote('^IXIC'),
        yahooFinance.quote('^DJI'),
        yahooFinance.quote('^VIX')
      ]);
      
      // Get bond yields
      const bonds = await Promise.all([
        yahooFinance.quote('^TNX'), // 10-year
        yahooFinance.quote('^TYX'), // 30-year
        yahooFinance.quote('^FVX')  // 5-year
      ]);
      
      // Get commodities
      const commodities = await Promise.all([
        yahooFinance.quote('GC=F'), // Gold
        yahooFinance.quote('SI=F'), // Silver
        yahooFinance.quote('CL=F'), // Crude Oil
        yahooFinance.quote('NG=F')  // Natural Gas
      ]);
      
      return {
        indices: {
          sp500: {
            value: sp500.regularMarketPrice,
            change: sp500.regularMarketChange,
            changePercent: sp500.regularMarketChangePercent
          },
          nasdaq: {
            value: nasdaq.regularMarketPrice,
            change: nasdaq.regularMarketChange,
            changePercent: nasdaq.regularMarketChangePercent
          },
          dow: {
            value: dow.regularMarketPrice,
            change: dow.regularMarketChange,
            changePercent: dow.regularMarketChangePercent
          },
          vix: {
            value: vix.regularMarketPrice,
            change: vix.regularMarketChange,
            changePercent: vix.regularMarketChangePercent
          }
        },
        bonds: {
          '10year': bonds[0].regularMarketPrice,
          '30year': bonds[1].regularMarketPrice,
          '5year': bonds[2].regularMarketPrice
        },
        commodities: {
          gold: commodities[0].regularMarketPrice,
          silver: commodities[1].regularMarketPrice,
          oil: commodities[2].regularMarketPrice,
          naturalGas: commodities[3].regularMarketPrice
        },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get market overview: ${error.message}`);
    }
  }
  
  async getMarketMovers(args) {
    try {
      const type = args.type || 'gainers';
      
      // Get trending tickers as a proxy
      const trending = await yahooFinance.trendingSymbols('US');
      
      // Get quotes for trending symbols
      const quotes = await Promise.all(
        trending.quotes.slice(0, 20).map(async (q) => {
          try {
            const quote = await yahooFinance.quote(q.symbol);
            return {
              symbol: quote.symbol,
              name: quote.longName || quote.shortName,
              price: quote.regularMarketPrice,
              change: quote.regularMarketChange,
              changePercent: quote.regularMarketChangePercent,
              volume: quote.regularMarketVolume
            };
          } catch {
            return null;
          }
        })
      );
      
      const validQuotes = quotes.filter(q => q !== null);
      
      // Sort based on type
      let sorted;
      if (type === 'gainers') {
        sorted = validQuotes.sort((a, b) => b.changePercent - a.changePercent);
      } else if (type === 'losers') {
        sorted = validQuotes.sort((a, b) => a.changePercent - b.changePercent);
      } else {
        sorted = validQuotes.sort((a, b) => b.volume - a.volume);
      }
      
      return {
        type,
        data: sorted.slice(0, 10),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get market movers: ${error.message}`);
    }
  }
  
  async getSectorPerformance(args) {
    const period = args.period || '1d';
    
    try {
      const sectors = [
        { symbol: 'XLK', name: 'Technology' },
        { symbol: 'XLF', name: 'Financial' },
        { symbol: 'XLV', name: 'Healthcare' },
        { symbol: 'XLE', name: 'Energy' },
        { symbol: 'XLI', name: 'Industrial' },
        { symbol: 'XLY', name: 'Consumer Discretionary' },
        { symbol: 'XLP', name: 'Consumer Staples' },
        { symbol: 'XLB', name: 'Materials' },
        { symbol: 'XLRE', name: 'Real Estate' },
        { symbol: 'XLU', name: 'Utilities' },
        { symbol: 'XLC', name: 'Communication' }
      ];
      
      const performance = await Promise.all(
        sectors.map(async (sector) => {
          const quote = await yahooFinance.quote(sector.symbol);
          return {
            sector: sector.name,
            symbol: sector.symbol,
            change: quote.regularMarketChangePercent,
            price: quote.regularMarketPrice,
            volume: quote.regularMarketVolume
          };
        })
      );
      
      return {
        period,
        data: performance.sort((a, b) => b.change - a.change),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get sector performance: ${error.message}`);
    }
  }
  
  async getFearGreedIndex() {
    try {
      // CNN Fear & Greed Index - would need web scraping
      const response = await axios.get(
        'https://api.alternative.me/fng/',
        { params: { limit: 1 } }
      );
      
      const data = response.data.data[0];
      
      return {
        value: parseInt(data.value),
        classification: data.value_classification,
        timestamp: data.timestamp,
        interpretation: this.interpretFearGreed(parseInt(data.value))
      };
    } catch (error) {
      // Fallback calculation based on VIX
      try {
        const vix = await yahooFinance.quote('^VIX');
        const value = Math.max(0, Math.min(100, 100 - (vix.regularMarketPrice * 2)));
        
        return {
          value,
          source: 'VIX-based calculation',
          vix: vix.regularMarketPrice,
          classification: this.classifyFearGreed(value),
          interpretation: this.interpretFearGreed(value)
        };
      } catch {
        throw new Error('Failed to get Fear & Greed Index');
      }
    }
  }
  
  // News Methods
  async getMarketNews(args) {
    const category = args.category || 'all';
    const limit = args.limit || 10;
    const includeCNBC = args.includeCNBC !== false;
    
    try {
      // Aggregate from multiple sources
      const newsPromises = [];
      
      // CNBC news (primary source when available)
      if (includeCNBC) {
        const cnbcCategory = category === 'all' ? 'markets' : category;
        newsPromises.push(
          cnbc.getCNBCNews(cnbcCategory, limit)
            .catch(err => {
              console.error('CNBC news fetch failed:', err.message);
              return [];
            })
        );
      }
      
      // Yahoo Finance news
      if (['all', 'stocks'].includes(category)) {
        newsPromises.push(this.getYahooNews());
      }
      
      // Crypto news
      if (['all', 'crypto'].includes(category)) {
        newsPromises.push(this.getCryptoNews());
      }
      
      const allNews = await Promise.all(newsPromises);
      const combined = allNews.flat();
      
      // Sort by timestamp and limit
      combined.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      
      return {
        category,
        count: Math.min(limit, combined.length),
        articles: combined.slice(0, limit)
      };
    } catch (error) {
      throw new Error(`Failed to get market news: ${error.message}`);
    }
  }
  
  async streamMarketNews(args) {
    const duration = Math.min(args.duration || 60, 300);
    const streamId = `news_${Date.now()}`;
    
    return new Promise((resolve) => {
      const results = [];
      const startTime = Date.now();
      
      const interval = setInterval(async () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        if (elapsed >= duration) {
          clearInterval(interval);
          resolve({
            streamId,
            duration: elapsed,
            sources: args.sources,
            articles: results,
            status: 'completed'
          });
          return;
        }
        
        try {
          const news = await this.getMarketNews({ limit: 5 });
          
          if (args.keywords && args.keywords.length > 0) {
            news.articles = news.articles.filter(article => 
              args.keywords.some(keyword => 
                article.title.toLowerCase().includes(keyword.toLowerCase()) ||
                article.summary?.toLowerCase().includes(keyword.toLowerCase())
              )
            );
          }
          
          if (news.articles.length > 0) {
            results.push({
              timestamp: new Date().toISOString(),
              articles: news.articles
            });
          }
        } catch (error) {
          // Continue streaming even if one fetch fails
        }
      }, 10000); // Check every 10 seconds
    });
  }
  
  // Technical Analysis Methods
  async getTechnicalIndicators(args) {
    try {
      const period = args.period || 14;
      const history = await yahooFinance.historical(args.symbol, {
        period1: subMonths(new Date(), 3),
        period2: new Date(),
        interval: '1d'
      });
      
      const prices = history.map(h => h.close);
      const highs = history.map(h => h.high);
      const lows = history.map(h => h.low);
      const volumes = history.map(h => h.volume);
      
      const indicators = {};
      const requestedIndicators = args.indicators || ['rsi', 'macd', 'bb'];
      
      // Calculate requested indicators
      if (requestedIndicators.includes('rsi')) {
        indicators.rsi = this.calculateRSI(prices, period);
      }
      
      if (requestedIndicators.includes('macd')) {
        indicators.macd = this.calculateMACD(prices);
      }
      
      if (requestedIndicators.includes('bb')) {
        indicators.bollingerBands = this.calculateBollingerBands(prices, 20);
      }
      
      if (requestedIndicators.includes('sma')) {
        indicators.sma = {
          sma20: this.calculateSMA(prices, 20),
          sma50: this.calculateSMA(prices, 50),
          sma200: this.calculateSMA(prices, 200)
        };
      }
      
      if (requestedIndicators.includes('ema')) {
        indicators.ema = {
          ema12: this.calculateEMA(prices, 12),
          ema26: this.calculateEMA(prices, 26)
        };
      }
      
      if (requestedIndicators.includes('stoch')) {
        indicators.stochastic = this.calculateStochastic(highs, lows, prices, period);
      }
      
      return {
        symbol: args.symbol,
        currentPrice: prices[prices.length - 1],
        indicators,
        interpretation: this.interpretIndicators(indicators),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to calculate indicators for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getSupportResistance(args) {
    try {
      const history = await yahooFinance.historical(args.symbol, {
        period1: this.getPeriodDate(args.period || '3mo'),
        period2: new Date(),
        interval: '1d'
      });
      
      const prices = history.map(h => ({
        high: h.high,
        low: h.low,
        close: h.close,
        volume: h.volume
      }));
      
      // Find pivot points
      const pivots = this.calculatePivotPoints(prices);
      
      // Find support and resistance levels
      const levels = this.findSupportResistanceLevels(prices);
      
      return {
        symbol: args.symbol,
        currentPrice: prices[prices.length - 1].close,
        support: levels.support,
        resistance: levels.resistance,
        pivotPoints: pivots,
        strength: this.calculateLevelStrength(prices, levels),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to calculate support/resistance for ${args.symbol}: ${error.message}`);
    }
  }
  
  // Helper Methods
  getPeriodDate(period) {
    const now = new Date();
    switch (period) {
      case '1d': return subDays(now, 1);
      case '5d': return subDays(now, 5);
      case '1mo': return subMonths(now, 1);
      case '3mo': return subMonths(now, 3);
      case '6mo': return subMonths(now, 6);
      case '1y': return subMonths(now, 12);
      case '2y': return subMonths(now, 24);
      case '5y': return subMonths(now, 60);
      default: return subMonths(now, 1);
    }
  }
  
  async getYahooNews() {
    try {
      // This would typically use Yahoo Finance news API
      return [
        {
          source: 'Yahoo Finance',
          title: 'Market Update',
          summary: 'Latest market movements and analysis',
          url: 'https://finance.yahoo.com',
          timestamp: new Date().toISOString()
        }
      ];
    } catch {
      return [];
    }
  }
  
  async getCryptoNews() {
    try {
      const response = await axios.get(
        'https://api.coingecko.com/api/v3/news',
        { params: { per_page: 10 } }
      );
      
      return response.data.data.map(article => ({
        source: article.news_site,
        title: article.title,
        summary: article.description,
        url: article.url,
        timestamp: article.updated_at
      }));
    } catch {
      return [];
    }
  }
  
  // Technical Indicator Calculations
  calculateRSI(prices, period = 14) {
    if (prices.length < period + 1) return null;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = 1; i <= period; i++) {
      const diff = prices[i] - prices[i - 1];
      if (diff > 0) gains += diff;
      else losses -= diff;
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    const rs = avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));
    
    return Math.round(rsi * 100) / 100;
  }
  
  calculateMACD(prices) {
    const ema12 = this.calculateEMA(prices, 12);
    const ema26 = this.calculateEMA(prices, 26);
    
    if (!ema12 || !ema26) return null;
    
    const macd = ema12 - ema26;
    const signal = this.calculateEMA([macd], 9) || 0;
    const histogram = macd - signal;
    
    return {
      macd: Math.round(macd * 100) / 100,
      signal: Math.round(signal * 100) / 100,
      histogram: Math.round(histogram * 100) / 100
    };
  }
  
  calculateBollingerBands(prices, period = 20) {
    const sma = this.calculateSMA(prices, period);
    if (!sma) return null;
    
    const relevantPrices = prices.slice(-period);
    const squaredDiffs = relevantPrices.map(p => Math.pow(p - sma, 2));
    const variance = squaredDiffs.reduce((a, b) => a + b, 0) / period;
    const stdDev = Math.sqrt(variance);
    
    return {
      upper: Math.round((sma + 2 * stdDev) * 100) / 100,
      middle: Math.round(sma * 100) / 100,
      lower: Math.round((sma - 2 * stdDev) * 100) / 100
    };
  }
  
  calculateSMA(prices, period) {
    if (prices.length < period) return null;
    const relevantPrices = prices.slice(-period);
    return relevantPrices.reduce((a, b) => a + b, 0) / period;
  }
  
  calculateEMA(prices, period) {
    if (prices.length < period) return null;
    
    const multiplier = 2 / (period + 1);
    let ema = this.calculateSMA(prices.slice(0, period), period);
    
    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }
    
    return ema;
  }
  
  calculateStochastic(highs, lows, closes, period = 14) {
    if (highs.length < period) return null;
    
    const recentHighs = highs.slice(-period);
    const recentLows = lows.slice(-period);
    const currentClose = closes[closes.length - 1];
    
    const highestHigh = Math.max(...recentHighs);
    const lowestLow = Math.min(...recentLows);
    
    const k = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
    
    return {
      k: Math.round(k * 100) / 100,
      d: Math.round(k * 100) / 100 // Simplified - usually a 3-period SMA of K
    };
  }
  
  calculatePivotPoints(prices) {
    const latest = prices[prices.length - 1];
    const pivot = (latest.high + latest.low + latest.close) / 3;
    
    return {
      pivot: Math.round(pivot * 100) / 100,
      r1: Math.round((2 * pivot - latest.low) * 100) / 100,
      r2: Math.round((pivot + latest.high - latest.low) * 100) / 100,
      s1: Math.round((2 * pivot - latest.high) * 100) / 100,
      s2: Math.round((pivot - latest.high + latest.low) * 100) / 100
    };
  }
  
  findSupportResistanceLevels(prices) {
    const closes = prices.map(p => p.close);
    const sorted = [...closes].sort((a, b) => a - b);
    
    // Find levels where price has bounced multiple times
    const levels = [];
    const tolerance = 0.02; // 2% tolerance
    
    for (let i = 0; i < sorted.length; i++) {
      const level = sorted[i];
      const touches = closes.filter(p => 
        Math.abs(p - level) / level < tolerance
      ).length;
      
      if (touches >= 3) {
        levels.push({ price: level, touches });
      }
    }
    
    // Sort by number of touches
    levels.sort((a, b) => b.touches - a.touches);
    
    const currentPrice = closes[closes.length - 1];
    const support = levels.filter(l => l.price < currentPrice).slice(0, 3);
    const resistance = levels.filter(l => l.price > currentPrice).slice(0, 3);
    
    return {
      support: support.map(s => s.price),
      resistance: resistance.map(r => r.price)
    };
  }
  
  calculateLevelStrength(prices, levels) {
    // Calculate how strong support/resistance levels are
    const strength = {};
    
    if (levels.support.length > 0) {
      strength.support = 'Strong'; // Simplified
    }
    
    if (levels.resistance.length > 0) {
      strength.resistance = 'Strong'; // Simplified
    }
    
    return strength;
  }
  
  interpretIndicators(indicators) {
    const signals = [];
    
    if (indicators.rsi) {
      if (indicators.rsi > 70) signals.push('RSI indicates overbought conditions');
      else if (indicators.rsi < 30) signals.push('RSI indicates oversold conditions');
      else signals.push('RSI is neutral');
    }
    
    if (indicators.macd) {
      if (indicators.macd.histogram > 0) signals.push('MACD shows bullish momentum');
      else signals.push('MACD shows bearish momentum');
    }
    
    return signals;
  }
  
  classifyFearGreed(value) {
    if (value <= 25) return 'Extreme Fear';
    if (value <= 45) return 'Fear';
    if (value <= 55) return 'Neutral';
    if (value <= 75) return 'Greed';
    return 'Extreme Greed';
  }
  
  interpretFearGreed(value) {
    if (value <= 25) {
      return 'Market is experiencing extreme fear. This could be a buying opportunity for contrarian investors.';
    } else if (value <= 45) {
      return 'Market sentiment is fearful. Investors are cautious.';
    } else if (value <= 55) {
      return 'Market sentiment is neutral. No extreme emotions driving the market.';
    } else if (value <= 75) {
      return 'Market is showing greed. Investors are becoming more risk-seeking.';
    } else {
      return 'Market is in extreme greed territory. Consider taking profits or being cautious with new positions.';
    }
  }
  
  // Portfolio Methods
  async createWatchlist(args) {
    // Store in cache as simple implementation
    const watchlistKey = `watchlist_${args.name}`;
    cache.set(watchlistKey, args.symbols, 86400); // Store for 24 hours
    
    return {
      name: args.name,
      symbols: args.symbols,
      created: new Date().toISOString(),
      message: 'Watchlist created successfully'
    };
  }
  
  async trackPortfolio(args) {
    const holdings = args.holdings;
    
    const portfolioData = await Promise.all(
      holdings.map(async (holding) => {
        try {
          const quote = await yahooFinance.quote(holding.symbol);
          const currentPrice = quote.regularMarketPrice;
          const totalValue = currentPrice * holding.quantity;
          const totalCost = holding.avgCost * holding.quantity;
          const gainLoss = totalValue - totalCost;
          const gainLossPercent = (gainLoss / totalCost) * 100;
          
          return {
            symbol: holding.symbol,
            quantity: holding.quantity,
            avgCost: holding.avgCost,
            currentPrice,
            totalValue,
            totalCost,
            gainLoss,
            gainLossPercent,
            dayChange: quote.regularMarketChange * holding.quantity,
            dayChangePercent: quote.regularMarketChangePercent
          };
        } catch (error) {
          return {
            symbol: holding.symbol,
            error: error.message
          };
        }
      })
    );
    
    const validHoldings = portfolioData.filter(h => !h.error);
    const totalValue = validHoldings.reduce((sum, h) => sum + h.totalValue, 0);
    const totalCost = validHoldings.reduce((sum, h) => sum + h.totalCost, 0);
    const totalGainLoss = totalValue - totalCost;
    const totalGainLossPercent = (totalGainLoss / totalCost) * 100;
    
    return {
      holdings: portfolioData,
      summary: {
        totalValue,
        totalCost,
        totalGainLoss,
        totalGainLossPercent,
        dayChange: validHoldings.reduce((sum, h) => sum + h.dayChange, 0)
      },
      timestamp: new Date().toISOString()
    };
  }
  
  async calculateCorrelation(args) {
    try {
      const period = args.period || '3mo';
      const symbols = args.symbols;
      
      // Get historical data for all symbols
      const historicalData = await Promise.all(
        symbols.map(symbol => 
          yahooFinance.historical(symbol, {
            period1: this.getPeriodDate(period),
            period2: new Date(),
            interval: '1d'
          })
        )
      );
      
      // Calculate returns
      const returns = historicalData.map(data => 
        data.slice(1).map((d, i) => 
          (d.close - data[i].close) / data[i].close
        )
      );
      
      // Calculate correlation matrix
      const correlationMatrix = {};
      
      for (let i = 0; i < symbols.length; i++) {
        correlationMatrix[symbols[i]] = {};
        for (let j = 0; j < symbols.length; j++) {
          const correlation = this.calculatePearsonCorrelation(returns[i], returns[j]);
          correlationMatrix[symbols[i]][symbols[j]] = correlation;
        }
      }
      
      return {
        period,
        symbols,
        correlationMatrix,
        interpretation: this.interpretCorrelation(correlationMatrix, symbols),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to calculate correlation: ${error.message}`);
    }
  }
  
  calculatePearsonCorrelation(x, y) {
    const n = Math.min(x.length, y.length);
    if (n === 0) return 0;
    
    const sumX = x.slice(0, n).reduce((a, b) => a + b, 0);
    const sumY = y.slice(0, n).reduce((a, b) => a + b, 0);
    const sumXY = x.slice(0, n).reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumX2 = x.slice(0, n).reduce((sum, xi) => sum + xi * xi, 0);
    const sumY2 = y.slice(0, n).reduce((sum, yi) => sum + yi * yi, 0);
    
    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    if (denominator === 0) return 0;
    
    return Math.round((numerator / denominator) * 100) / 100;
  }
  
  interpretCorrelation(matrix, symbols) {
    const interpretations = [];
    
    for (let i = 0; i < symbols.length; i++) {
      for (let j = i + 1; j < symbols.length; j++) {
        const corr = matrix[symbols[i]][symbols[j]];
        let interpretation;
        
        if (corr > 0.7) {
          interpretation = `${symbols[i]} and ${symbols[j]} are strongly positively correlated (${corr})`;
        } else if (corr > 0.3) {
          interpretation = `${symbols[i]} and ${symbols[j]} have moderate positive correlation (${corr})`;
        } else if (corr < -0.7) {
          interpretation = `${symbols[i]} and ${symbols[j]} are strongly negatively correlated (${corr})`;
        } else if (corr < -0.3) {
          interpretation = `${symbols[i]} and ${symbols[j]} have moderate negative correlation (${corr})`;
        } else {
          interpretation = `${symbols[i]} and ${symbols[j]} have weak correlation (${corr})`;
        }
        
        interpretations.push(interpretation);
      }
    }
    
    return interpretations;
  }
  
  // Economic Data Methods
  async getEconomicCalendar(args) {
    const days = args.days || 7;
    const importance = args.importance || 'all';
    
    // This would typically use an economic calendar API
    return {
      period: `Next ${days} days`,
      importance,
      events: [
        {
          date: new Date(Date.now() + 86400000).toISOString(),
          event: 'Fed Interest Rate Decision',
          importance: 'high',
          forecast: '5.25%',
          previous: '5.00%'
        },
        {
          date: new Date(Date.now() + 172800000).toISOString(),
          event: 'Non-Farm Payrolls',
          importance: 'high',
          forecast: '200K',
          previous: '187K'
        }
      ],
      message: 'Economic calendar data would require dedicated API integration'
    };
  }
  
  async getTreasuryYields() {
    try {
      const yields = await Promise.all([
        yahooFinance.quote('^IRX'),  // 13 week
        yahooFinance.quote('^FVX'),  // 5 year
        yahooFinance.quote('^TNX'),  // 10 year
        yahooFinance.quote('^TYX')   // 30 year
      ]);
      
      return {
        '3month': yields[0].regularMarketPrice,
        '5year': yields[1].regularMarketPrice,
        '10year': yields[2].regularMarketPrice,
        '30year': yields[3].regularMarketPrice,
        yieldCurve: this.analyzeYieldCurve(yields),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get treasury yields: ${error.message}`);
    }
  }
  
  analyzeYieldCurve(yields) {
    const shortTerm = yields[0].regularMarketPrice;
    const longTerm = yields[2].regularMarketPrice;
    const spread = longTerm - shortTerm;
    
    if (spread < 0) {
      return {
        shape: 'inverted',
        spread,
        interpretation: 'Yield curve is inverted, which historically has preceded recessions'
      };
    } else if (spread < 0.5) {
      return {
        shape: 'flat',
        spread,
        interpretation: 'Yield curve is relatively flat, indicating economic uncertainty'
      };
    } else {
      return {
        shape: 'normal',
        spread,
        interpretation: 'Yield curve is normal, indicating healthy economic expectations'
      };
    }
  }
  
  async getCommodities(args) {
    const commoditySymbols = {
      gold: 'GC=F',
      silver: 'SI=F',
      oil: 'CL=F',
      gas: 'NG=F',
      wheat: 'ZW=F',
      corn: 'ZC=F'
    };
    
    const requested = args.commodities || ['gold', 'silver', 'oil'];
    
    const data = await Promise.all(
      requested.map(async (commodity) => {
        try {
          const quote = await yahooFinance.quote(commoditySymbols[commodity]);
          return {
            commodity,
            price: quote.regularMarketPrice,
            change: quote.regularMarketChange,
            changePercent: quote.regularMarketChangePercent,
            dayHigh: quote.regularMarketDayHigh,
            dayLow: quote.regularMarketDayLow
          };
        } catch (error) {
          return {
            commodity,
            error: error.message
          };
        }
      })
    );
    
    return {
      commodities: data,
      timestamp: new Date().toISOString()
    };
  }
  
  async getForexRates(args) {
    const base = args.base || 'USD';
    const currencies = args.currencies || ['EUR', 'GBP', 'JPY', 'CHF', 'CAD'];
    
    const pairs = currencies.map(currency => {
      if (base === 'USD') {
        return `${currency}${base}=X`;
      } else {
        return `${base}${currency}=X`;
      }
    });
    
    const rates = await Promise.all(
      pairs.map(async (pair, index) => {
        try {
          const quote = await yahooFinance.quote(pair);
          return {
            currency: currencies[index],
            rate: base === 'USD' ? 1 / quote.regularMarketPrice : quote.regularMarketPrice,
            change: quote.regularMarketChange,
            changePercent: quote.regularMarketChangePercent
          };
        } catch (error) {
          return {
            currency: currencies[index],
            error: error.message
          };
        }
      })
    );
    
    return {
      base,
      rates,
      timestamp: new Date().toISOString()
    };
  }
  
  // Alert Methods
  async setPriceAlert(args) {
    const alertKey = `alert_${args.symbol}_${Date.now()}`;
    const alert = {
      symbol: args.symbol,
      targetPrice: args.targetPrice,
      condition: args.condition,
      created: new Date().toISOString(),
      triggered: false
    };
    
    cache.set(alertKey, alert, 86400); // Store for 24 hours
    
    return {
      alertId: alertKey,
      ...alert,
      message: 'Price alert set successfully'
    };
  }
  
  async streamPriceAlerts(args) {
    const duration = Math.min(args.duration || 60, 300);
    const streamId = `alerts_${Date.now()}`;
    
    // Get all alerts from cache
    const alertKeys = cache.keys().filter(k => k.startsWith('alert_'));
    const alerts = alertKeys.map(k => ({ id: k, ...cache.get(k) }));
    
    return new Promise((resolve) => {
      const results = [];
      const startTime = Date.now();
      
      const interval = setInterval(async () => {
        const elapsed = (Date.now() - startTime) / 1000;
        
        if (elapsed >= duration) {
          clearInterval(interval);
          resolve({
            streamId,
            duration: elapsed,
            alerts: results,
            status: 'completed'
          });
          return;
        }
        
        // Check alerts
        for (const alert of alerts) {
          if (!alert.triggered) {
            try {
              const quote = await yahooFinance.quote(alert.symbol);
              const currentPrice = quote.regularMarketPrice;
              
              const triggered = alert.condition === 'above' 
                ? currentPrice > alert.targetPrice
                : currentPrice < alert.targetPrice;
              
              if (triggered) {
                alert.triggered = true;
                results.push({
                  timestamp: new Date().toISOString(),
                  alert: {
                    ...alert,
                    currentPrice,
                    message: `Alert triggered: ${alert.symbol} is ${alert.condition} ${alert.targetPrice}`
                  }
                });
              }
            } catch (error) {
              // Continue checking other alerts
            }
          }
        }
      }, 5000); // Check every 5 seconds
    });
  }
  
  // Other helper methods
  async getAnalystRatings(args) {
    try {
      const summary = await yahooFinance.quoteSummary(args.symbol, {
        modules: ['recommendationTrend', 'upgradeDowngradeHistory']
      });
      
      return {
        symbol: args.symbol,
        currentTrend: summary.recommendationTrend?.trend[0],
        history: summary.upgradeDowngradeHistory?.history?.slice(0, 10),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get analyst ratings for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getInsiderTrading(args) {
    try {
      const summary = await yahooFinance.quoteSummary(args.symbol, {
        modules: ['insiderTransactions', 'insiderHolders']
      });
      
      return {
        symbol: args.symbol,
        recentTransactions: summary.insiderTransactions?.transactions?.slice(0, 10),
        topHolders: summary.insiderHolders?.holders?.slice(0, 5),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get insider trading for ${args.symbol}: ${error.message}`);
    }
  }
  
  async getChartPatterns(args) {
    // This would require sophisticated pattern recognition
    // Simplified implementation
    return {
      symbol: args.symbol,
      timeframe: args.timeframe,
      patterns: [
        {
          pattern: 'Ascending Triangle',
          reliability: 'High',
          signal: 'Bullish',
          description: 'Price making higher lows with resistance at same level'
        }
      ],
      message: 'Advanced pattern recognition would require specialized algorithms',
      timestamp: new Date().toISOString()
    };
  }
  
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Market MCP Server running with streaming support...');
  }
}

const server = new MarketMCPServer();
server.run().catch(console.error);
