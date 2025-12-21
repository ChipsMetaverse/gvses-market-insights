#!/usr/bin/env python3
"""
Test script to verify Chart Analysis Panel MCP data parsing fixes.
Tests the news loading functionality specifically to ensure our fixes work.
"""

import asyncio
import json
from datetime import datetime

async def test_chart_analysis_panel():
    """Test the Chart Analysis Panel to verify MCP data parsing fixes"""
    
    print("🚀 Starting Chart Analysis Panel Test")
    print("=" * 60)
    
    # Navigate to the frontend
    frontend_url = "http://localhost:5175"
    print(f"📱 Navigating to frontend: {frontend_url}")
    
    try:
        # Use MCP Playwright tools
        from claude_code import mcp__playwright__browser_navigate, mcp__playwright__browser_wait_for, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_snapshot, mcp__playwright__browser_evaluate
        
        await mcp__playwright__browser_navigate(url=frontend_url)
        print("✅ Successfully navigated to frontend")
        
        # Wait a bit for initial page load
        await mcp__playwright__browser_wait_for(time=3)
        
        # Take initial screenshot
        initial_screenshot = f"chart_analysis_initial_{int(datetime.now().timestamp())}.png"
        await mcp__playwright__browser_take_screenshot(filename=initial_screenshot)
        print(f"📸 Initial screenshot: {initial_screenshot}")
        
        # Get page snapshot to identify elements
        snapshot = await mcp__playwright__browser_snapshot()
        print("📋 Page snapshot captured")
        
        # Look for Chart Analysis Panel section
        chart_analysis_visible = await browser_evaluate(
            function="""() => {
                const analysisSection = document.querySelector('[class*="chart-analysis"], [class*="analysis"], .analysis-section, [data-testid="chart-analysis"]');
                if (analysisSection) {
                    return {
                        found: true,
                        visible: analysisSection.offsetHeight > 0,
                        className: analysisSection.className,
                        innerHTML: analysisSection.innerHTML.substring(0, 500)
                    };
                }
                
                // Also check for news-related sections
                const newsSection = document.querySelector('[class*="news"], .news-section, [data-testid="news"]');
                if (newsSection) {
                    return {
                        found: true,
                        visible: newsSection.offsetHeight > 0,
                        className: newsSection.className,
                        innerHTML: newsSection.innerHTML.substring(0, 500),
                        type: 'news'
                    };
                }
                
                return {found: false};
            }"""
        )
        
        print(f"🔍 Chart Analysis Panel Status: {json.dumps(chart_analysis_visible, indent=2)}")
        
        # Wait for data to load
        print("⏳ Waiting for market data to load...")
        await browser_wait_for(time=5)
        
        # Check if news articles are actually loading
        news_status = await browser_evaluate(
            function="""() => {
                // Look for various news-related selectors
                const selectors = [
                    '[class*="news-item"]',
                    '[class*="article"]', 
                    '.news-feed',
                    '[data-testid="news-item"]',
                    '.chart-analysis .news',
                    '.analysis-panel .news'
                ];
                
                let results = {
                    totalArticles: 0,
                    articles: [],
                    loadingIndicators: 0,
                    errorMessages: 0
                };
                
                selectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el.textContent.trim().length > 10) {
                            results.totalArticles++;
                            results.articles.push({
                                selector: selector,
                                content: el.textContent.substring(0, 200),
                                hasLinks: el.querySelectorAll('a').length > 0
                            });
                        }
                    });
                });
                
                // Check for loading states
                document.querySelectorAll('[class*="loading"], [class*="spinner"], .loading').forEach(() => {
                    results.loadingIndicators++;
                });
                
                // Check for error messages
                document.querySelectorAll('[class*="error"], .error-message').forEach(el => {
                    if (el.textContent.includes('error') || el.textContent.includes('failed')) {
                        results.errorMessages++;
                    }
                });
                
                return results;
            }"""
        )
        
        print(f"📰 News Status: {json.dumps(news_status, indent=2)}")
        
        # Try to click on a stock to trigger chart analysis
        print("📊 Attempting to trigger chart analysis...")
        
        # Look for stock cards or ticker symbols to click
        stock_click_result = await browser_evaluate(
            function="""() => {
                // Look for clickable stock elements
                const stockElements = document.querySelectorAll('[class*="stock"], [class*="ticker"], [data-symbol]');
                for (let el of stockElements) {
                    if (el.textContent.includes('TSLA') || el.textContent.includes('AAPL') || el.textContent.includes('NVDA')) {
                        el.click();
                        return {
                            clicked: true,
                            element: el.textContent.substring(0, 100),
                            symbol: el.textContent.match(/[A-Z]{2,5}/)?.[0]
                        };
                    }
                }
                return {clicked: false};
            }"""
        )
        
        print(f"🖱️ Stock Click Result: {json.dumps(stock_click_result, indent=2)}")
        
        # Wait for chart analysis to update after click
        if stock_click_result.get('clicked'):
            print("⏳ Waiting for chart analysis to update...")
            await browser_wait_for(time=3)
        
        # Check news loading again after potential symbol change
        final_news_status = await browser_evaluate(
            function="""() => {
                const results = {
                    newsArticles: [],
                    hasContent: false,
                    loadingStates: [],
                    errorStates: []
                };
                
                // More comprehensive news detection
                const newsSelectors = [
                    '[class*="news"]',
                    '[class*="article"]',
                    '[class*="feed"]',
                    '.chart-analysis',
                    '.analysis-panel'
                ];
                
                newsSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        const content = el.textContent.trim();
                        if (content.length > 50) {
                            results.newsArticles.push({
                                selector: selector,
                                contentLength: content.length,
                                preview: content.substring(0, 300),
                                hasTimestamp: /\\d{1,2}[:\\/]\\d{1,2}|ago|AM|PM/i.test(content),
                                hasSource: /Reuters|Bloomberg|CNBC|Yahoo|AP/i.test(content)
                            });
                            results.hasContent = true;
                        }
                        
                        // Check for loading states
                        if (content.includes('Loading') || el.querySelector('.spinner, [class*="loading"]')) {
                            results.loadingStates.push(content.substring(0, 100));
                        }
                        
                        // Check for error states
                        if (content.includes('Error') || content.includes('Failed') || content.includes('Unable to load')) {
                            results.errorStates.push(content.substring(0, 100));
                        }
                    });
                });
                
                // Check for empty states
                const emptyIndicators = document.querySelectorAll('[class*="empty"], [class*="no-data"], .placeholder');
                results.emptyStates = Array.from(emptyIndicators).map(el => el.textContent.substring(0, 100));
                
                return results;
            }"""
        )
        
        print(f"📈 Final News Analysis: {json.dumps(final_news_status, indent=2)}")
        
        # Take final screenshot
        final_screenshot = f"chart_analysis_final_{int(datetime.now().timestamp())}.png"
        await browser_take_screenshot(filename=final_screenshot)
        print(f"📸 Final screenshot: {final_screenshot}")
        
        # Test different stock symbols to ensure consistency
        print("🔄 Testing different symbols...")
        symbols_to_test = ['AAPL', 'NVDA', 'SPY']
        
        for symbol in symbols_to_test:
            symbol_result = await browser_evaluate(
                function=f"""() => {{
                    // Try to find and click a {symbol} element
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {{
                        if (el.textContent.includes('{symbol}') && el.offsetHeight > 0) {{
                            el.click();
                            return {{success: true, found: el.textContent.substring(0, 100)}};
                        }}
                    }}
                    return {{success: false}};
                }}"""
            )
            
            if symbol_result.get('success'):
                print(f"✅ Successfully clicked {symbol}")
                await browser_wait_for(time=2)
                
                # Check if news updates for this symbol
                symbol_news = await browser_evaluate(
                    function="""() => {
                        const newsContent = document.querySelector('.chart-analysis, .analysis-panel, [class*="news"]');
                        if (newsContent) {
                            return {
                                hasNews: newsContent.textContent.length > 100,
                                contentPreview: newsContent.textContent.substring(0, 200)
                            };
                        }
                        return {hasNews: false};
                    }"""
                )
                print(f"📰 {symbol} News Status: {json.dumps(symbol_news, indent=2)}")
            else:
                print(f"❌ Could not find clickable {symbol} element")
        
        # Final comprehensive check
        print("\n🔍 FINAL COMPREHENSIVE ANALYSIS")
        print("=" * 40)
        
        comprehensive_check = await browser_evaluate(
            function="""() => {
                return {
                    // Page structure
                    hasChartAnalysis: !!document.querySelector('[class*="chart"], [class*="analysis"]'),
                    hasNewsSection: !!document.querySelector('[class*="news"], [class*="feed"]'),
                    
                    // Content status  
                    totalTextContent: document.body.textContent.length,
                    hasMarketData: document.body.textContent.includes('$') || document.body.textContent.includes('%'),
                    hasTimestamps: /\\d{1,2}[:\\/]\\d{1,2}|ago|AM|PM/i.test(document.body.textContent),
                    
                    // Error indicators
                    hasErrors: document.body.textContent.includes('Error') || document.body.textContent.includes('Failed'),
                    hasLoadingStates: document.body.textContent.includes('Loading...') || !!document.querySelector('[class*="loading"]'),
                    
                    // News source indicators
                    hasCNBC: document.body.textContent.includes('CNBC'),
                    hasYahoo: document.body.textContent.includes('Yahoo'),
                    hasReuters: document.body.textContent.includes('Reuters'),
                    
                    // MCP specific checks
                    hasMCPData: document.body.textContent.includes('data_source') || document.body.textContent.includes('mcp'),
                    
                    // Console errors
                    consoleErrors: window.console ? 'Available' : 'Not Available'
                };
            }"""
        )
        
        print(f"📊 Comprehensive Analysis:")
        for key, value in comprehensive_check.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
        
        # Generate summary report
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "Chart Analysis Panel MCP Fix Verification",
            "frontend_url": frontend_url,
            "screenshots": [initial_screenshot, final_screenshot],
            "chart_analysis_status": chart_analysis_visible,
            "news_loading_status": news_status,
            "final_news_status": final_news_status,
            "stock_interaction": stock_click_result,
            "comprehensive_check": comprehensive_check,
            "success_indicators": {
                "has_news_content": final_news_status.get('hasContent', False),
                "news_article_count": len(final_news_status.get('newsArticles', [])),
                "no_error_states": len(final_news_status.get('errorStates', [])) == 0,
                "has_market_data": comprehensive_check.get('hasMarketData', False),
                "has_news_sources": any([
                    comprehensive_check.get('hasCNBC', False),
                    comprehensive_check.get('hasYahoo', False),
                    comprehensive_check.get('hasReuters', False)
                ])
            }
        }
        
        # Save detailed report
        report_filename = f"chart_analysis_test_report_{int(datetime.now().timestamp())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Detailed report saved: {report_filename}")
        
        # Print summary
        print("\n🎯 TEST SUMMARY")
        print("=" * 30)
        success_count = sum(1 for v in report['success_indicators'].values() if v)
        total_indicators = len(report['success_indicators'])
        
        print(f"✅ Success Indicators: {success_count}/{total_indicators}")
        for indicator, status in report['success_indicators'].items():
            emoji = "✅" if status else "❌"
            print(f"  {emoji} {indicator.replace('_', ' ').title()}: {status}")
        
        if success_count >= total_indicators * 0.8:  # 80% success threshold
            print("\n🎉 CHART ANALYSIS PANEL TEST: PASSED")
            print("The MCP data parsing fixes appear to be working!")
        else:
            print("\n⚠️ CHART ANALYSIS PANEL TEST: NEEDS ATTENTION")
            print("Some issues detected. Check the detailed report.")
            
        return report
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        error_screenshot = f"chart_analysis_error_{int(datetime.now().timestamp())}.png"
        try:
            await browser_take_screenshot(filename=error_screenshot)
            print(f"📸 Error screenshot: {error_screenshot}")
        except:
            pass
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🧪 Chart Analysis Panel MCP Fix Test")
    print("Testing news loading and data parsing improvements")
    print("=" * 60)
    
    result = asyncio.run(test_chart_analysis_panel())
    print(f"\n📋 Test completed with result: {json.dumps(result.get('success_indicators', {}), indent=2)}")