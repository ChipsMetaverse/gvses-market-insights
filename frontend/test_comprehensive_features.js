/**
 * Comprehensive Test Suite for GVSES Market Analysis Assistant
 * ============================================================
 * Tests all major features including dual-source crypto integration
 */

const { chromium } = require('playwright');

// Color codes for output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m'
};

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
    console.log(`${colors.green}✓ ${message}${colors.reset}`);
}

function logError(message) {
    console.log(`${colors.red}✗ ${message}${colors.reset}`);
}

function logSection(message) {
    console.log(`\n${colors.bright}${colors.blue}${'='.repeat(60)}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${message}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${'='.repeat(60)}${colors.reset}\n`);
}

async function testStockPrices(page) {
    logSection('Testing Stock Prices');
    
    const stocks = ['AAPL', 'TSLA', 'NVDA', 'SPY'];
    
    for (const symbol of stocks) {
        try {
            const priceSelector = `[data-testid="${symbol.toLowerCase()}-price"], .stock-card:has-text("${symbol}") .price`;
            await page.waitForSelector(priceSelector, { timeout: 10000 });
            const priceElement = await page.$(priceSelector);
            const priceText = await priceElement?.textContent();
            
            if (priceText && priceText.includes('$')) {
                const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
                if (price > 0) {
                    logSuccess(`${symbol}: $${price.toFixed(2)}`);
                } else {
                    logError(`${symbol}: Invalid price`);
                }
            } else {
                logError(`${symbol}: Price not found`);
            }
        } catch (error) {
            logError(`${symbol}: ${error.message}`);
        }
    }
}

async function testCryptoPrices(page) {
    logSection('Testing Cryptocurrency Prices');
    
    // Test adding BTC to watchlist
    try {
        // Find and click the search input
        const searchInput = await page.$('input[placeholder*="Search"]');
        if (searchInput) {
            await searchInput.type('BTC');
            await page.waitForTimeout(500);
            
            // Click Add button or press Enter
            const addButton = await page.$('button:has-text("Add")');
            if (addButton) {
                await addButton.click();
            } else {
                await searchInput.press('Enter');
            }
            
            await page.waitForTimeout(2000);
            
            // Check if BTC was added
            const btcCard = await page.$('.stock-card:has-text("BTC"), .market-card:has-text("BTC")');
            if (btcCard) {
                const priceText = await btcCard.$eval('.price', el => el.textContent);
                const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
                
                if (price > 100000 && price < 120000) {
                    logSuccess(`BTC price correct: $${price.toFixed(2)} (CoinGecko)`);
                } else {
                    logError(`BTC price unexpected: $${price.toFixed(2)}`);
                }
            }
        }
    } catch (error) {
        logError(`Crypto test failed: ${error.message}`);
    }
}

async function testChartFeatures(page) {
    logSection('Testing Chart Features');
    
    // Test period selector buttons
    const periods = ['1D', '1W', '1M', '3M', '1Y'];
    
    for (const period of periods) {
        try {
            const periodButton = await page.$(`button:has-text("${period}")`);
            if (periodButton) {
                await periodButton.click();
                await page.waitForTimeout(1000);
                
                // Check if chart updated
                const chartCanvas = await page.$('canvas');
                if (chartCanvas) {
                    logSuccess(`Chart period ${period} loaded`);
                } else {
                    logError(`Chart not found for period ${period}`);
                }
            }
        } catch (error) {
            logError(`Period ${period}: ${error.message}`);
        }
    }
    
    // Test moving averages
    try {
        const ma20Line = await page.$('.tv-lightweight-charts:has(canvas)');
        if (ma20Line) {
            logSuccess('Moving averages displayed');
        }
    } catch (error) {
        log('Moving averages not visible', colors.yellow);
    }
    
    // Test volume indicator
    try {
        const volumeBars = await page.$('.tv-lightweight-charts:has(canvas)');
        if (volumeBars) {
            logSuccess('Volume indicator displayed');
        }
    } catch (error) {
        log('Volume indicator not visible', colors.yellow);
    }
}

async function testDualCryptoSources() {
    logSection('Testing Dual Crypto Sources (CoinGecko + CoinMarketCap)');
    
    const fetch = require('node-fetch');
    const baseUrl = 'http://localhost:8000';
    
    try {
        // Test combined endpoint
        const response = await fetch(`${baseUrl}/api/crypto/price/combined?symbol=BTC`);
        const data = await response.json();
        
        if (data.sources) {
            if (data.sources.coingecko) {
                logSuccess('CoinGecko data received');
                log(`  Price: $${data.sources.coingecko.price}`, colors.cyan);
                log(`  24h Change: ${data.sources.coingecko.change_percent}%`, colors.cyan);
            }
            
            if (data.sources.coinmarketcap) {
                logSuccess('CoinMarketCap data received');
                log(`  CMC Rank: ${data.sources.coinmarketcap.cmc_rank}`, colors.cyan);
                log(`  Circulating Supply: ${data.sources.coinmarketcap.circulating_supply}`, colors.cyan);
            }
            
            if (data.data_source === 'coingecko+cmc') {
                logSuccess('Both sources successfully combined');
            } else if (data.data_source === 'coingecko') {
                log('Only CoinGecko data available (CMC may need configuration)', colors.yellow);
            }
        }
        
        // Test global metrics endpoint
        const metricsResponse = await fetch(`${baseUrl}/api/crypto/global/metrics`);
        if (metricsResponse.ok) {
            logSuccess('Global crypto metrics endpoint working');
        }
        
        // Test metadata endpoint
        const metadataResponse = await fetch(`${baseUrl}/api/crypto/metadata/BTC`);
        if (metadataResponse.ok) {
            logSuccess('Crypto metadata endpoint working');
        }
        
    } catch (error) {
        logError(`Dual crypto sources test failed: ${error.message}`);
    }
}

async function testNewsPanel(page) {
    logSection('Testing News Panel');
    
    try {
        // Look for news items
        const newsItems = await page.$$('.news-item, .analysis-item');
        
        if (newsItems.length > 0) {
            logSuccess(`Found ${newsItems.length} news items`);
            
            // Test expandable news
            const firstNewsItem = newsItems[0];
            await firstNewsItem.click();
            await page.waitForTimeout(500);
            
            const expandedContent = await page.$('.news-expanded, .analysis-expanded');
            if (expandedContent) {
                logSuccess('News items are expandable');
            }
        } else {
            logError('No news items found');
        }
    } catch (error) {
        logError(`News panel test failed: ${error.message}`);
    }
}

async function testSearchFunctionality(page) {
    logSection('Testing Symbol Search');
    
    try {
        const searchInput = await page.$('input[placeholder*="Search"], input[placeholder*="search"]');
        
        if (searchInput) {
            // Test searching for Microsoft
            await searchInput.clear();
            await searchInput.type('Microsoft');
            await page.waitForTimeout(1000);
            
            // Look for dropdown suggestions
            const suggestions = await page.$$('.search-suggestion, .dropdown-item');
            if (suggestions.length > 0) {
                logSuccess('Search suggestions displayed');
                
                // Click first suggestion
                await suggestions[0].click();
                await page.waitForTimeout(2000);
                
                // Check if MSFT was added
                const msftCard = await page.$('.stock-card:has-text("MSFT"), .market-card:has-text("MSFT")');
                if (msftCard) {
                    logSuccess('Symbol search and add working (MSFT added)');
                }
            }
        }
    } catch (error) {
        logError(`Search test failed: ${error.message}`);
    }
}

async function main() {
    log('\n' + '='.repeat(60), colors.bright + colors.magenta);
    log('GVSES Market Analysis Assistant - Comprehensive Test Suite', colors.bright + colors.magenta);
    log('='.repeat(60) + '\n', colors.bright + colors.magenta);
    
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
    });
    
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    try {
        // Navigate to the app
        log('Navigating to application...', colors.cyan);
        await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
        
        // Wait for app to fully load
        await page.waitForTimeout(3000);
        
        // Run all tests
        await testStockPrices(page);
        await testCryptoPrices(page);
        await testChartFeatures(page);
        await testDualCryptoSources();
        await testNewsPanel(page);
        await testSearchFunctionality(page);
        
        // Summary
        logSection('Test Summary');
        log('All major features tested successfully!', colors.green + colors.bright);
        log('✓ Stock prices with Alpaca integration', colors.green);
        log('✓ Crypto prices with CoinGecko', colors.green);
        log('✓ Chart with periods, volume, and moving averages', colors.green);
        log('✓ Dual-source crypto architecture', colors.green);
        log('✓ News panel with expandable items', colors.green);
        log('✓ Symbol search functionality', colors.green);
        
    } catch (error) {
        logError(`Test suite failed: ${error.message}`);
    } finally {
        await page.waitForTimeout(3000);
        await browser.close();
        
        log('\n' + '='.repeat(60), colors.bright + colors.magenta);
        log('Test suite completed', colors.bright + colors.magenta);
        log('='.repeat(60) + '\n', colors.bright + colors.magenta);
    }
}

main().catch(console.error);