#!/usr/bin/env node
/**
 * G'sves Direct API MCP Server
 * Provides lightweight, fast API access for Agent Builder
 *
 * Tier 1 Tools: Direct Alpaca and Yahoo Finance API calls
 * Performance: < 500ms for real-time quotes
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import { format, subDays, subMonths } from 'date-fns';
import dotenv from 'dotenv';

dotenv.config({ path: '../backend/.env' });

// Redirect console.log to stderr for MCP protocol compliance
const originalConsoleLog = console.log;
console.log = (...args) => {
  const message = args.join(' ');
  if (message.startsWith('{"jsonrpc"')) {
    originalConsoleLog(...args);
  } else {
    console.error('[DEBUG]', ...args);
  }
};

class DirectAPIMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'gvses-direct-api-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Alpaca configuration
    this.alpacaHeaders = {
      'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
      'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY
    };
    this.alpacaDataURL = 'https://data.alpaca.markets';
    this.alpacaNewsURL = 'https://data.alpaca.markets/v1beta1/news';

    this.setupHandlers();

    console.error('🚀 G\'sves Direct API MCP Server initialized');
    console.error(`   Alpaca API: ${process.env.ALPACA_API_KEY ? '✅' : '❌'}`);
  }

  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'get_realtime_quote',
          description: 'Get real-time stock quote from Alpaca Markets (< 400ms). Returns current price, bid/ask, volume, and timestamp.',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Stock ticker symbol (e.g., AAPL, TSLA, NVDA)'
              }
            },
            required: ['symbol']
          }
        },

        {
          name: 'get_historical_bars',
          description: 'Get historical price bars (OHLCV) from Alpaca Markets. Essential for calculating LTB/ST/QE levels.',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Stock ticker symbol'
              },
              days: {
                type: 'number',
                description: 'Number of days of history (default: 100 for swing trading)',
                default: 100
              },
              timeframe: {
                type: 'string',
                enum: ['1Min', '5Min', '15Min', '1Hour', '1Day'],
                description: 'Bar timeframe (default: 1Day for swing trading)',
                default: '1Day'
              }
            },
            required: ['symbol']
          }
        },

        {
          name: 'get_multiple_quotes',
          description: 'Get real-time quotes for multiple symbols in a single call. Efficient for market overview and watchlists.',
          inputSchema: {
            type: 'object',
            properties: {
              symbols: {
                type: 'array',
                items: { type: 'string' },
                description: 'Array of stock symbols (e.g., ["SPY", "QQQ", "DIA", "IWM"])'
              }
            },
            required: ['symbols']
          }
        },

        {
          name: 'get_market_news',
          description: 'Get latest market news from Alpaca (includes major financial sources). Filter by symbol or get general market news.',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Stock symbol to filter news (optional - omit for general market news)'
              },
              limit: {
                type: 'number',
                description: 'Number of articles to return (default: 10, max: 50)',
                default: 10
              }
            }
          }
        },

        {
          name: 'get_yahoo_quote_fallback',
          description: 'Fallback to Yahoo Finance if Alpaca is unavailable. Also supports crypto (e.g., BTC-USD) and international markets.',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Stock/crypto symbol (use BTC-USD format for crypto)'
              }
            },
            required: ['symbol']
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_realtime_quote':
            return await this.getRealtimeQuote(args.symbol);

          case 'get_historical_bars':
            return await this.getHistoricalBars(
              args.symbol,
              args.days || 100,
              args.timeframe || '1Day'
            );

          case 'get_multiple_quotes':
            return await this.getMultipleQuotes(args.symbols);

          case 'get_market_news':
            return await this.getMarketNews(args.symbol, args.limit || 10);

          case 'get_yahoo_quote_fallback':
            return await this.getYahooQuoteFallback(args.symbol);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        console.error(`❌ Error executing ${name}:`, error.message);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              error: error.message,
              tool: name,
              timestamp: new Date().toISOString()
            }, null, 2)
          }],
          isError: true
        };
      }
    });
  }

  async getRealtimeQuote(symbol) {
    const url = `${this.alpacaDataURL}/v2/stocks/${symbol}/quotes/latest`;

    try {
      const response = await axios.get(url, {
        headers: this.alpacaHeaders,
        timeout: 5000
      });

      const quote = response.data.quote;

      const result = {
        symbol: symbol,
        price: quote.ap || quote.bp || null,  // Ask price or bid price
        bid: quote.bp,
        ask: quote.ap,
        bidSize: quote.bs,
        askSize: quote.as,
        timestamp: quote.t,
        conditions: quote.c,
        tape: quote.z,
        source: 'alpaca',
        latency_ms: response.headers['request-duration'] || 'N/A'
      };

      console.error(`✅ Quote for ${symbol}: $${result.price}`);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error(`❌ Alpaca quote failed for ${symbol}:`, error.message);
      // Fallback to Yahoo Finance
      return await this.getYahooQuoteFallback(symbol);
    }
  }

  async getHistoricalBars(symbol, days = 100, timeframe = '1Day') {
    const end = new Date();
    const start = subDays(end, days);

    const url = `${this.alpacaDataURL}/v2/stocks/${symbol}/bars`;

    try {
      const response = await axios.get(url, {
        headers: this.alpacaHeaders,
        params: {
          start: format(start, 'yyyy-MM-dd'),
          end: format(end, 'yyyy-MM-dd'),
          timeframe: timeframe,
          limit: 10000,
          adjustment: 'split'  // Adjust for stock splits
        },
        timeout: 10000
      });

      const bars = response.data.bars || [];

      const result = {
        symbol: symbol,
        timeframe: timeframe,
        period_days: days,
        bar_count: bars.length,
        bars: bars.map(bar => ({
          timestamp: bar.t,
          open: bar.o,
          high: bar.h,
          low: bar.l,
          close: bar.c,
          volume: bar.v,
          vwap: bar.vw,
          trade_count: bar.n
        })),
        source: 'alpaca'
      };

      console.error(`✅ Retrieved ${bars.length} bars for ${symbol}`);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error(`❌ Alpaca bars failed for ${symbol}:`, error.message);
      throw error;
    }
  }

  async getMultipleQuotes(symbols) {
    const url = `${this.alpacaDataURL}/v2/stocks/quotes/latest`;

    try {
      const response = await axios.get(url, {
        headers: this.alpacaHeaders,
        params: {
          symbols: symbols.join(',')
        },
        timeout: 10000
      });

      const quotes = response.data.quotes || {};

      const result = {
        timestamp: new Date().toISOString(),
        quote_count: Object.keys(quotes).length,
        quotes: Object.entries(quotes).map(([sym, quote]) => ({
          symbol: sym,
          price: quote.ap || quote.bp,
          bid: quote.bp,
          ask: quote.ap,
          timestamp: quote.t
        })),
        source: 'alpaca'
      };

      console.error(`✅ Retrieved quotes for ${Object.keys(quotes).length} symbols`);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error(`❌ Alpaca multi-quote failed:`, error.message);
      throw error;
    }
  }

  async getMarketNews(symbol = null, limit = 10) {
    try {
      const params = { limit, sort: 'desc' };
      if (symbol) {
        params.symbols = symbol;
      }

      const response = await axios.get(this.alpacaNewsURL, {
        headers: this.alpacaHeaders,
        params,
        timeout: 10000
      });

      const news = response.data.news || [];

      const result = {
        symbol: symbol || 'market-wide',
        article_count: news.length,
        articles: news.map(article => ({
          id: article.id,
          headline: article.headline,
          author: article.author,
          created_at: article.created_at,
          updated_at: article.updated_at,
          summary: article.summary,
          url: article.url,
          symbols: article.symbols || [],
          source: article.source
        })),
        source: 'alpaca_news'
      };

      console.error(`✅ Retrieved ${news.length} news articles`);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error(`❌ Alpaca news failed:`, error.message);
      throw error;
    }
  }

  async getYahooQuoteFallback(symbol) {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`;

    try {
      const response = await axios.get(url, {
        params: {
          interval: '1d',
          range: '1d'
        },
        timeout: 5000
      });

      const data = response.data.chart.result[0];
      const meta = data.meta;
      const quote = data.indicators.quote[0];

      const result = {
        symbol: symbol,
        price: meta.regularMarketPrice,
        previousClose: meta.previousClose,
        open: quote.open[0],
        high: quote.high[0],
        low: quote.low[0],
        volume: quote.volume[0],
        timestamp: new Date(meta.regularMarketTime * 1000).toISOString(),
        currency: meta.currency,
        exchangeName: meta.exchangeName,
        source: 'yahoo_finance_fallback'
      };

      console.error(`✅ Yahoo fallback quote for ${symbol}: $${result.price}`);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error(`❌ Yahoo fallback failed for ${symbol}:`, error.message);
      throw new Error(`Both Alpaca and Yahoo Finance failed for ${symbol}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('✅ G\'sves Direct API MCP Server running on stdio');
  }
}

const server = new DirectAPIMCPServer();
server.run().catch(console.error);
