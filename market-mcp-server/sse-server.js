#!/usr/bin/env node

/**
 * MCP SSE Server for OpenAI Agent Builder Integration
 * ===================================================
 * 
 * This server implements the SSE (Server-Sent Events) transport that OpenAI Agent Builder expects.
 * Fixed version based on official MCP SDK documentation.
 * 
 * Usage: node sse-server-fixed.js [port]
 * Default port: 3001
 */

import { createServer } from 'node:http';
import { URL } from 'node:url';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import yahooFinance from 'yahoo-finance2';
import axios from 'axios';
import * as cheerio from 'cheerio';
import NodeCache from 'node-cache';
import pLimit from 'p-limit';
import * as ta from 'technicalindicators';
import { format, subDays, subMonths } from 'date-fns';
import dotenv from 'dotenv';
import CNBCIntegration from './cnbc-integration.js';

dotenv.config();

// Cache with 60 second TTL for rate limiting
const cache = new NodeCache({ stdTTL: 60 });

// Initialize CNBC integration
const cnbc = new CNBCIntegration(cache);

// Rate limiter for API calls
const limit = pLimit(5); // Max 5 concurrent requests

/**
 * Market MCP Server with SSE Transport
 */
class MarketMCPSSEServer {
  constructor() {
    this.server = new Server(
      {
        name: 'market-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Store transports by sessionId for SSE connections (per official docs)
    this.transports = {};

    this.setupToolHandlers();
    this.setupListToolsHandler();
  }

  setupListToolsHandler() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        // Stock Data Tools
        {
          name: 'get_stock_quote',
          description: 'Get real-time stock quote with detailed metrics',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Stock ticker symbol (e.g., AAPL, TSLA)'
              },
              includePrePost: {
                type: 'boolean',
                description: 'Include pre/post market data'
              }
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
              symbol: {
                type: 'string',
                description: 'Stock ticker symbol'
              },
              period: {
                type: 'string',
                enum: ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
                description: 'Time period'
              },
              interval: {
                type: 'string',
                enum: ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'],
                description: 'Data interval'
              }
            },
            required: ['symbol']
          }
        },
        {
          name: 'get_market_overview',
          description: 'Get overall market overview (indices, commodities, bonds)',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        {
          name: 'get_market_news',
          description: 'Get latest market news from CNBC and other sources',
          inputSchema: {
            type: 'object',
            properties: {
              category: {
                type: 'string',
                enum: ['all', 'stocks', 'crypto', 'economy', 'earnings'],
                description: 'News category'
              },
              limit: {
                type: 'number',
                description: 'Number of articles (default: 10)'
              },
              includeCNBC: {
                type: 'boolean',
                description: 'Include CNBC news (default: true)'
              }
            }
          }
        },

        // Chart Control Tools for Agent Builder
        {
          name: 'change_chart_symbol',
          description: 'Change the symbol displayed on the trading chart',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock ticker symbol to display (e.g., AAPL, TSLA)' }
            },
            required: ['symbol']
          }
        },

        {
          name: 'set_chart_timeframe',
          description: 'Set the timeframe for chart data display',
          inputSchema: {
            type: 'object',
            properties: {
              timeframe: { 
                type: 'string', 
                enum: ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'],
                description: 'Chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)' 
              }
            },
            required: ['timeframe']
          }
        },

        {
          name: 'toggle_chart_indicator',
          description: 'Toggle technical indicators on/off on the chart',
          inputSchema: {
            type: 'object',
            properties: {
              indicator: { 
                type: 'string',
                enum: ['sma', 'ema', 'bollinger', 'rsi', 'macd', 'volume'],
                description: 'Technical indicator to toggle'
              },
              enabled: { type: 'boolean', description: 'Whether to show or hide the indicator' },
              period: { type: 'number', description: 'Period for the indicator (optional, default varies by indicator)' }
            },
            required: ['indicator', 'enabled']
          }
        },

        {
          name: 'capture_chart_snapshot',
          description: 'Capture a screenshot of the current chart state',
          inputSchema: {
            type: 'object',
            properties: {
              width: { type: 'number', description: 'Screenshot width in pixels (default: 1200)' },
              height: { type: 'number', description: 'Screenshot height in pixels (default: 800)' },
              format: { type: 'string', enum: ['png', 'jpeg'], description: 'Image format (default: png)' }
            }
          }
        }
        // Simplified chart control tools for Agent Builder - keeping it focused
      ]
    }));
  }

  setupToolHandlers() {
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_stock_quote':
            return await this.getStockQuote(args);
          
          case 'get_stock_history':
            return await this.getStockHistory(args);
            
          case 'get_market_overview':
            return await this.getMarketOverview(args);
            
          case 'get_market_news':
            return await this.getMarketNews(args);

          // Chart Control Tools
          case 'change_chart_symbol':
            return await this.changeChartSymbol(args);

          case 'set_chart_timeframe':
            return await this.setChartTimeframe(args);

          case 'toggle_chart_indicator':
            return await this.toggleChartIndicator(args);

          case 'capture_chart_snapshot':
            return await this.captureChartSnapshot(args);
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${name}: ${error.message}`
            }
          ]
        };
      }
    });
  }

  async getStockQuote(args) {
    const { symbol, includePrePost = false } = args;
    
    try {
      const quote = await yahooFinance.quote(symbol);
      
      const result = {
        symbol: quote.symbol,
        price: quote.regularMarketPrice || quote.price,
        currency: quote.currency,
        change: quote.regularMarketChange,
        changePercent: quote.regularMarketChangePercent,
        marketCap: quote.marketCap,
        volume: quote.regularMarketVolume,
        previousClose: quote.regularMarketPreviousClose,
        open: quote.regularMarketOpen,
        dayLow: quote.regularMarketDayLow,
        dayHigh: quote.regularMarketDayHigh,
        fiftyTwoWeekLow: quote.fiftyTwoWeekLow,
        fiftyTwoWeekHigh: quote.fiftyTwoWeekHigh,
        timestamp: new Date().toISOString()
      };

      if (includePrePost) {
        result.preMarketPrice = quote.preMarketPrice;
        result.preMarketChange = quote.preMarketChange;
        result.preMarketChangePercent = quote.preMarketChangePercent;
        result.postMarketPrice = quote.postMarketPrice;
        result.postMarketChange = quote.postMarketChange;
        result.postMarketChangePercent = quote.postMarketChangePercent;
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to get stock quote for ${symbol}: ${error.message}`);
    }
  }

  async getStockHistory(args) {
    const { symbol, period = '1y', interval = '1d' } = args;
    
    try {
      const historical = await yahooFinance.historical(symbol, {
        period1: this.getPeriodStart(period),
        period2: new Date(),
        interval: interval
      });

      const result = {
        symbol,
        period,
        interval,
        data: historical.slice(-100).map(item => ({
          date: item.date.toISOString().split('T')[0],
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume
        })),
        count: historical.length
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to get stock history for ${symbol}: ${error.message}`);
    }
  }

  async getMarketOverview() {
    try {
      // Get major indices
      const indices = await Promise.all([
        yahooFinance.quote('^GSPC'), // S&P 500
        yahooFinance.quote('^DJI'),  // Dow Jones
        yahooFinance.quote('^IXIC')  // NASDAQ
      ]);

      const result = {
        indices: indices.map(index => ({
          symbol: index.symbol,
          name: index.longName || index.shortName,
          price: index.regularMarketPrice,
          change: index.regularMarketChange,
          changePercent: index.regularMarketChangePercent
        })),
        timestamp: new Date().toISOString()
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to get market overview: ${error.message}`);
    }
  }

  async getMarketNews(args) {
    const { category = 'all', limit = 5, includeCNBC = true } = args;
    
    try {
      let news = [];
      
      // Try CNBC first
      if (includeCNBC) {
        try {
          const cnbcNews = await cnbc.getCNBCNews(category, limit);
          news = news.concat(cnbcNews.slice(0, limit));
        } catch (error) {
          console.log('CNBC fallback triggered:', error.message);
        }
      }

      // If CNBC failed or returned no news, use Yahoo Finance RSS fallback
      if (news.length === 0) {
        try {
          const yahooNews = await this.getYahooFinanceNews(category, limit);
          news = yahooNews;
        } catch (error) {
          console.log('Yahoo Finance fallback failed:', error.message);
          // Return minimal default if all sources fail
          news = [{
            source: 'Market Update',
            title: 'Market data available - check latest prices and charts',
            summary: 'Real-time market data and analysis available through our tools',
            url: 'https://finance.yahoo.com',
            publishedAt: new Date().toISOString()
          }];
        }
      }

      const result = {
        articles: news.map(article => ({
          title: article.title,
          summary: article.description || article.summary,
          source: article.source || 'CNBC',
          publishedAt: article.publishedAt || article.published_at || article.publishedAt,
          url: article.url || article.link
        })),
        count: news.length,
        category,
        timestamp: new Date().toISOString()
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to get market news: ${error.message}`);
    }
  }

  // Yahoo Finance RSS fallback
  async getYahooFinanceNews(category, limit) {
    const rssUrls = {
      'all': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
      'stocks': 'https://feeds.finance.yahoo.com/rss/2.0/headline', 
      'economy': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
      'earnings': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
      'crypto': 'https://feeds.finance.yahoo.com/rss/2.0/headline'
    };

    const url = rssUrls[category] || rssUrls['all'];
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
        'Accept': 'application/rss+xml, application/xml, text/xml'
      },
      timeout: 10000
    });

    // Parse RSS/XML
    const $ = cheerio.load(response.data, { xmlMode: true });
    const articles = [];

    $('item').each((i, item) => {
      if (articles.length >= limit) return false;
      
      const $item = $(item);
      const title = $item.find('title').text().trim();
      const link = $item.find('link').text().trim();
      const description = $item.find('description').text().trim();
      const pubDate = $item.find('pubDate').text().trim();

      if (title && link) {
        articles.push({
          source: 'Yahoo Finance',
          title: title,
          summary: description || title,
          url: link,
          publishedAt: pubDate ? new Date(pubDate).toISOString() : new Date().toISOString()
        });
      }
    });

    return articles;
  }

  getPeriodStart(period) {
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
      case 'max': return new Date('1970-01-01');
      default: return subMonths(now, 12);
    }
  }

  // Chart Control Methods for Agent Builder
  async changeChartSymbol(args) {
    const { symbol } = args;
    
    try {
      // Call the headless chart service to change symbol
      const backendUrl = process.env.BACKEND_URL || 'https://gvses-ai-market-assistant.fly.dev';
      const response = await fetch(`${backendUrl}/api/chart/change-symbol`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: symbol.toUpperCase() })
      });
      
      if (!response.ok) {
        throw new Error(`Chart service error: ${response.statusText}`);
      }
      
      const result = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'change_symbol',
            symbol: symbol.toUpperCase(),
            status: 'success',
            message: `Chart symbol changed to ${symbol.toUpperCase()}`,
            timestamp: new Date().toISOString(),
            ...result
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'change_symbol',
            symbol: symbol.toUpperCase(),
            status: 'error',
            message: `Failed to change chart symbol: ${error.message}`,
            timestamp: new Date().toISOString()
          }, null, 2)
        }]
      };
    }
  }

  async setChartTimeframe(args) {
    const { timeframe } = args;
    
    try {
      const backendUrl = process.env.BACKEND_URL || 'https://gvses-ai-market-assistant.fly.dev';
      const response = await fetch(`${backendUrl}/api/chart/set-timeframe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timeframe })
      });
      
      if (!response.ok) {
        throw new Error(`Chart service error: ${response.statusText}`);
      }
      
      const result = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'set_timeframe',
            timeframe,
            status: 'success',
            message: `Chart timeframe set to ${timeframe}`,
            timestamp: new Date().toISOString(),
            ...result
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'set_timeframe',
            timeframe,
            status: 'error',
            message: `Failed to set chart timeframe: ${error.message}`,
            timestamp: new Date().toISOString()
          }, null, 2)
        }]
      };
    }
  }

  async toggleChartIndicator(args) {
    const { indicator, enabled, period } = args;
    
    try {
      const backendUrl = process.env.BACKEND_URL || 'https://gvses-ai-market-assistant.fly.dev';
      const response = await fetch(`${backendUrl}/api/chart/toggle-indicator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indicator, enabled, period })
      });
      
      if (!response.ok) {
        throw new Error(`Chart service error: ${response.statusText}`);
      }
      
      const result = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'toggle_indicator',
            indicator,
            enabled,
            period,
            status: 'success',
            message: `${indicator.toUpperCase()} indicator ${enabled ? 'enabled' : 'disabled'}`,
            timestamp: new Date().toISOString(),
            ...result
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'toggle_indicator',
            indicator,
            enabled,
            status: 'error',
            message: `Failed to toggle indicator: ${error.message}`,
            timestamp: new Date().toISOString()
          }, null, 2)
        }]
      };
    }
  }

  async captureChartSnapshot(args) {
    const { width = 1200, height = 800, format = 'png' } = args;
    
    try {
      const backendUrl = process.env.BACKEND_URL || 'https://gvses-ai-market-assistant.fly.dev';
      const response = await fetch(`${backendUrl}/api/chart/capture-snapshot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ include_data: args.include_data || false })
      });
      
      if (!response.ok) {
        throw new Error(`Chart service error: ${response.statusText}`);
      }
      
      const result = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'capture_snapshot',
            dimensions: { width, height },
            format,
            status: 'success',
            message: 'Chart snapshot captured successfully',
            timestamp: new Date().toISOString(),
            ...result
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            action: 'capture_snapshot',
            status: 'error',
            message: `Failed to capture chart snapshot: ${error.message}`,
            timestamp: new Date().toISOString()
          }, null, 2)
        }]
      };
    }
  }

  /**
   * Create HTTP server with SSE support
   * Based on official MCP SDK backwards compatibility example
   */
  createHTTPServer(port = 3001) {
    const server = createServer(async (req, res) => {
      const url = new URL(req.url, `http://${req.headers.host}`);
      
      // CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
      }

      // Legacy SSE endpoint for older clients (Agent Builder)
      if (url.pathname === '/sse' && req.method === 'GET') {
        const timestamp = new Date().toISOString();
        const userAgent = req.headers['user-agent'] || 'unknown';
        const origin = req.headers.origin || 'no-origin';
        const acceptHeader = req.headers.accept || 'no-accept';
        
        console.log(`[${timestamp}] === SSE CONNECTION ATTEMPT ===`);
        console.log(`[${timestamp}] User-Agent: ${userAgent}`);
        console.log(`[${timestamp}] Origin: ${origin}`);
        console.log(`[${timestamp}] Accept: ${acceptHeader}`);
        console.log(`[${timestamp}] URL: ${req.url}`);
        console.log(`[${timestamp}] Headers:`, JSON.stringify(req.headers, null, 2));
        
        // Create SSE transport for legacy clients (per official docs)
        const transport = new SSEServerTransport('/messages', res);
        this.transports[transport.sessionId] = transport;
        
        console.log(`[${timestamp}] Created transport with sessionId: ${transport.sessionId}`);

        res.on('close', () => {
          delete this.transports[transport.sessionId];
          console.log('SSE connection closed, sessionId:', transport.sessionId);
        });

        try {
          await this.server.connect(transport);
          console.log('SSE connection established, sessionId:', transport.sessionId);
        } catch (error) {
          console.error('SSE connection error:', error);
          res.writeHead(500);
          res.end('SSE connection failed');
        }
        
      } else if (url.pathname === '/messages' && req.method === 'POST') {
        // Legacy message endpoint for older clients (per official docs)
        const timestamp = new Date().toISOString();
        const sessionId = url.searchParams.get('sessionId');
        const transport = this.transports[sessionId];

        console.log(`[${timestamp}] === MESSAGE REQUEST ===`);
        console.log(`[${timestamp}] SessionId: ${sessionId}`);
        console.log(`[${timestamp}] Available sessions: ${Object.keys(this.transports).join(', ')}`);
        console.log(`[${timestamp}] Transport exists: ${!!transport}`);

        if (!transport) {
          console.error(`[${timestamp}] No transport found for sessionId: ${sessionId}`);
          console.error(`[${timestamp}] Available transports:`, Object.keys(this.transports));
          res.writeHead(400);
          res.end('No transport found for sessionId');
          return;
        }

        console.log(`[${timestamp}] Handling POST message for sessionId: ${sessionId}`);

        try {
          await transport.handlePostMessage(req, res);
        } catch (error) {
          console.error('Message handling error:', error);
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            jsonrpc: "2.0",
            error: {
              code: -32603,
              message: `Internal error: ${error.message}`
            },
            id: null
          }));
        }
        
      } else if (url.pathname === '/health' && req.method === 'GET') {
        // Health check endpoint
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy', transport: 'sse' }));
        
      } else {
        // 404 for other paths
        res.writeHead(404);
        res.end('Not Found');
      }
    });

    server.listen(port, () => {
      console.log(`🚀 MCP SSE Server running on port ${port}`);
      console.log(`📡 SSE endpoint: http://localhost:${port}/sse`);
      console.log(`🔗 For OpenAI Agent Builder, use: http://localhost:${port}/sse`);
    });

    return server;
  }
}

// Start the server
const port = process.argv[2] ? parseInt(process.argv[2]) : 3001;
const mcpServer = new MarketMCPSSEServer();
mcpServer.createHTTPServer(port);