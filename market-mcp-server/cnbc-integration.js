// CNBC Integration Module for Market MCP Server
import axios from 'axios';
import * as cheerio from 'cheerio';

class CNBCIntegration {
  constructor(cache) {
    this.cache = cache;
    this.baseUrl = 'https://www.cnbc.com';
  }

  // Get CNBC quote data using multiple approaches
  async getCNBCQuote(symbol) {
    const cacheKey = `cnbc_quote_${symbol}`;
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    // Try multiple approaches
    const approaches = [
      () => this.getCNBCQuoteViaAPI(symbol),
      () => this.getCNBCQuoteViaScraping(symbol)
    ];

    for (const approach of approaches) {
      try {
        const result = await approach();
        if (result) {
          this.cache.set(cacheKey, result, 30);
          return result;
        }
      } catch (error) {
        console.error(`CNBC approach failed: ${error.message}`);
        continue;
      }
    }
    
    return null;
  }

  // Method 1: Try the API endpoint with better headers
  async getCNBCQuoteViaAPI(symbol) {
    // Try different endpoint variations
    const endpoints = [
      `https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols=${symbol}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1`,
      `https://api.cnbc.com/quote/${symbol}`,
      `https://quote.cnbc.com/quote-html-webservice/quote.htm?symbols=${symbol}&requestMethod=extended&noform=1&partnerId=2&output=json`
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(endpoint, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': `https://www.cnbc.com/quotes/${symbol}`,
            'Origin': 'https://www.cnbc.com'
          },
          timeout: 5000
        });

        if (response.data) {
          // Try to parse different response formats
          let quote = null;
          
          if (response.data.QuoteResponse?.QuickQuoteResult?.QuickQuote) {
            quote = response.data.QuoteResponse.QuickQuoteResult.QuickQuote;
          } else if (response.data.quote) {
            quote = response.data.quote;
          } else if (response.data[0]) {
            quote = response.data[0];
          }

          if (quote) {
            return {
              source: 'CNBC',
              symbol: quote.symbol || symbol,
              name: quote.name || quote.shortName || quote.companyName,
              price: parseFloat(quote.last || quote.price || quote.regularMarketPrice || 0),
              change: parseFloat(quote.change || quote.regularMarketChange || 0),
              changePercent: parseFloat(quote.change_pct || quote.changePercent || quote.regularMarketChangePercent || 0),
              volume: parseInt(quote.volume || quote.regularMarketVolume || 0),
              exchange: quote.exchange,
              lastUpdate: quote.last_time_msec || new Date().toISOString()
            };
          }
        }
      } catch (error) {
        // Continue to next endpoint
        continue;
      }
    }
    
    throw new Error('All API endpoints failed');
  }

  // Method 2: Try scraping the quote page
  async getCNBCQuoteViaScraping(symbol) {
    const response = await axios.get(`https://www.cnbc.com/quotes/${symbol}`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
      },
      timeout: 8000
    });

    const $ = cheerio.load(response.data);
    
    // Try to extract quote data from various selectors
    const priceSelectors = [
      '.QuoteStrip-lastPrice',
      '.quote-price',
      '[data-module="QuotePrice"]',
      '.last-price'
    ];
    
    let price = null;
    for (const selector of priceSelectors) {
      const priceText = $(selector).first().text().trim();
      if (priceText) {
        price = parseFloat(priceText.replace(/[^0-9.-]/g, ''));
        if (!isNaN(price)) break;
      }
    }

    if (price) {
      // Try to get additional data
      const change = parseFloat($('.QuoteStrip-change, .quote-change').first().text().replace(/[^0-9.-]/g, '')) || 0;
      const changePercent = parseFloat($('.QuoteStrip-changePercent, .quote-change-percent').first().text().replace(/[^0-9.-]/g, '')) || 0;
      
      return {
        source: 'CNBC',
        symbol: symbol,
        name: $('h1, .symbol-name').first().text().trim() || symbol,
        price: price,
        change: change,
        changePercent: changePercent,
        lastUpdate: new Date().toISOString()
      };
    }

    throw new Error('Could not scrape quote data');
  }

  // Get CNBC market news
  async getCNBCNews(category = 'markets', limit = 10) {
    const cacheKey = `cnbc_news_${category}_${limit}`;
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    try {
      const urls = {
        markets: 'https://www.cnbc.com/markets/',
        stocks: 'https://www.cnbc.com/stocks/',
        bonds: 'https://www.cnbc.com/bonds/',
        commodities: 'https://www.cnbc.com/commodities/',
        currencies: 'https://www.cnbc.com/currencies/',
        crypto: 'https://www.cnbc.com/cryptocurrency/',
        economy: 'https://www.cnbc.com/economy/'
      };

      const url = urls[category] || urls.markets;
      
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        timeout: 8000
      });

      const $ = cheerio.load(response.data);
      const articles = [];

      // Multiple selectors for different page layouts
      const articleSelectors = [
        '.Card-titleContainer a',
        '.InternationalCard-headline a', 
        '.RiverCard-headline a',
        '.FeedCard-headline a',
        'h3 a, h2 a',
        '[data-module="ArticleCard"] a'
      ];

      for (const selector of articleSelectors) {
        $(selector).each((i, elem) => {
          if (articles.length >= limit) return false;
          
          const $link = $(elem);
          const title = $link.text().trim();
          let url = $link.attr('href');
          
          if (title && url && title.length > 10) {
            if (!url.startsWith('http')) {
              url = `https://www.cnbc.com${url}`;
            }
            
            // Avoid duplicates
            if (!articles.some(article => article.title === title)) {
              articles.push({
                source: 'CNBC',
                title,
                url,
                time: new Date().toISOString(),
                category
              });
            }
          }
        });
        
        if (articles.length >= limit) break;
      }

      this.cache.set(cacheKey, articles, 60);
      return articles;
    } catch (error) {
      console.error(`CNBC news fetch failed:`, error.message);
      return [];
    }
  }

  // Get CNBC pre-market movers (simplified)
  async getCNBCPreMarket() {
    const cacheKey = 'cnbc_premarket';
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    try {
      const response = await axios.get('https://www.cnbc.com/pre-markets/', {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        },
        timeout: 8000
      });

      const $ = cheerio.load(response.data);
      const movers = {
        gainers: [],
        losers: [],
        active: []
      };

      // Try to extract any movers data
      $('.market-movers tr, .premarket-movers tr').each((i, row) => {
        const $row = $(row);
        const symbol = $row.find('td').first().text().trim();
        const price = $row.find('td').eq(1).text().trim();
        const change = $row.find('td').eq(2).text().trim();
        
        if (symbol && symbol.match(/^[A-Z]{1,5}$/)) {
          const mover = { symbol, price, change };
          
          if (change.includes('+')) {
            movers.gainers.push(mover);
          } else if (change.includes('-')) {
            movers.losers.push(mover);
          } else {
            movers.active.push(mover);
          }
        }
      });

      this.cache.set(cacheKey, movers, 60);
      return movers;
    } catch (error) {
      console.error('CNBC pre-market fetch failed:', error.message);
      return { gainers: [], losers: [], active: [] };
    }
  }

  // Get CNBC market sentiment/analysis
  async getCNBCSentiment() {
    const cacheKey = 'cnbc_sentiment';
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;

    try {
      const response = await axios.get('https://www.cnbc.com/market-outlook/', {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        },
        timeout: 8000
      });

      const $ = cheerio.load(response.data);
      const sentiment = {
        source: 'CNBC',
        timestamp: new Date().toISOString(),
        headline: $('h1, .PageHeader-title').first().text().trim() || 'Market Outlook',
        summary: $('p').first().text().trim(),
        keyPoints: []
      };

      // Extract key points from various elements
      $('li, .highlight, .key-point').each((i, elem) => {
        const point = $(elem).text().trim();
        if (point && point.length > 20 && sentiment.keyPoints.length < 5) {
          sentiment.keyPoints.push(point);
        }
      });

      this.cache.set(cacheKey, sentiment, 300); // Cache for 5 minutes
      return sentiment;
    } catch (error) {
      console.error('CNBC sentiment fetch failed:', error.message);
      return {
        source: 'CNBC',
        timestamp: new Date().toISOString(),
        headline: 'Market Outlook',
        summary: 'Sentiment data temporarily unavailable',
        keyPoints: []
      };
    }
  }
}

export default CNBCIntegration;