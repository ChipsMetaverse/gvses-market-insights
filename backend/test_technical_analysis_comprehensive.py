#!/usr/bin/env python3
"""
Comprehensive Technical Analysis Test for Voice Assistant
Tests all technical and fundamental analysis capabilities
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time


class TechnicalAnalysisTester:
    """Test Voice Assistant's technical and fundamental analysis capabilities."""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "capabilities": {
                "drawing": False,
                "support_resistance": False,
                "fibonacci": False,
                "pattern_detection": False,
                "indicators": False,
                "fundamental": False
            },
            "summary": {
                "total_tests": 0,
                "successful": 0,
                "failed": 0
            }
        }
        
        # Comprehensive test scenarios
        self.test_scenarios = [
            # Drawing Commands
            {
                "category": "drawing",
                "subcategory": "trendline",
                "question": "Draw a trendline on TSLA from the recent low to the current price",
                "expected_commands": ["TRENDLINE:", "DRAW:"],
                "wait_time": 12,
                "verify_visual": True
            },
            {
                "category": "drawing",
                "subcategory": "horizontal_lines",
                "question": "Mark the key levels on TSLA chart",
                "expected_commands": ["SUPPORT:", "RESISTANCE:"],
                "wait_time": 12,
                "verify_visual": True
            },
            
            # Support and Resistance
            {
                "category": "support_resistance",
                "subcategory": "identify",
                "question": "Show me the support and resistance levels for TSLA",
                "expected_commands": ["SUPPORT:", "RESISTANCE:", "LEVEL"],
                "wait_time": 12,
                "verify_visual": True
            },
            {
                "category": "support_resistance",
                "subcategory": "mark_specific",
                "question": "Mark support at 430 and resistance at 460 on TSLA",
                "expected_commands": ["SUPPORT:430", "RESISTANCE:460"],
                "wait_time": 10,
                "verify_visual": True
            },
            
            # Fibonacci
            {
                "category": "fibonacci",
                "subcategory": "auto",
                "question": "Pull a Fibonacci retracement on TSLA",
                "expected_commands": ["FIBONACCI:", "0.236", "0.382", "0.618"],
                "wait_time": 12,
                "verify_visual": True
            },
            {
                "category": "fibonacci",
                "subcategory": "specific",
                "question": "Draw Fibonacci from the 52-week low to high on TSLA",
                "expected_commands": ["FIBONACCI:", "52", "week"],
                "wait_time": 15,
                "verify_visual": True
            },
            
            # Pattern Detection - Chart Patterns
            {
                "category": "patterns",
                "subcategory": "chart_patterns",
                "question": "Identify any chart patterns on TSLA",
                "expected_keywords": ["pattern", "formation", "triangle", "flag", "wedge"],
                "wait_time": 15,
                "verify_visual": False
            },
            {
                "category": "patterns",
                "subcategory": "triangles",
                "question": "Are there any triangle patterns forming on TSLA?",
                "expected_keywords": ["triangle", "ascending", "descending", "symmetrical"],
                "wait_time": 12,
                "verify_visual": False
            },
            
            # Pattern Detection - Candlestick Patterns
            {
                "category": "patterns",
                "subcategory": "candlestick",
                "question": "Show me candlestick patterns on TSLA daily chart",
                "expected_keywords": ["candlestick", "doji", "hammer", "engulfing", "star"],
                "wait_time": 12,
                "verify_visual": False
            },
            {
                "category": "patterns",
                "subcategory": "reversal",
                "question": "Are there any reversal patterns on TSLA?",
                "expected_keywords": ["reversal", "head and shoulders", "double", "bottom", "top"],
                "wait_time": 12,
                "verify_visual": False
            },
            
            # Pattern Detection - Continuation Patterns
            {
                "category": "patterns",
                "subcategory": "continuation",
                "question": "Identify continuation patterns on TSLA",
                "expected_keywords": ["continuation", "flag", "pennant", "rectangle"],
                "wait_time": 12,
                "verify_visual": False
            },
            
            # Pattern Detection - Price Action
            {
                "category": "patterns",
                "subcategory": "price_action",
                "question": "Analyze the price action on TSLA",
                "expected_keywords": ["price action", "breakout", "breakdown", "consolidation"],
                "wait_time": 12,
                "verify_visual": False
            },
            
            # Divergence Detection
            {
                "category": "patterns",
                "subcategory": "divergence",
                "question": "Check for RSI divergence on TSLA",
                "expected_keywords": ["divergence", "RSI", "bullish", "bearish"],
                "wait_time": 15,
                "verify_visual": False
            },
            
            # Indicators - Oscillators
            {
                "category": "indicators",
                "subcategory": "rsi",
                "question": "Show RSI indicator on TSLA chart",
                "expected_commands": ["INDICATOR:RSI", "RSI"],
                "wait_time": 10,
                "verify_visual": True
            },
            {
                "category": "indicators",
                "subcategory": "macd",
                "question": "Add MACD indicator to TSLA",
                "expected_commands": ["INDICATOR:MACD", "MACD"],
                "wait_time": 10,
                "verify_visual": True
            },
            {
                "category": "indicators",
                "subcategory": "stochastic",
                "question": "Display Stochastic oscillator on TSLA",
                "expected_commands": ["INDICATOR:STOCH", "Stochastic"],
                "wait_time": 10,
                "verify_visual": True
            },
            
            # Indicators - Moving Averages
            {
                "category": "indicators",
                "subcategory": "sma",
                "question": "Show 50 and 200 day moving averages on TSLA",
                "expected_commands": ["INDICATOR:SMA", "SMA:50", "SMA:200"],
                "wait_time": 10,
                "verify_visual": True
            },
            {
                "category": "indicators",
                "subcategory": "ema",
                "question": "Add 20 day EMA to TSLA chart",
                "expected_commands": ["INDICATOR:EMA", "EMA:20"],
                "wait_time": 10,
                "verify_visual": True
            },
            
            # Indicators - Volatility
            {
                "category": "indicators",
                "subcategory": "bollinger",
                "question": "Show Bollinger Bands on TSLA",
                "expected_commands": ["INDICATOR:BB", "Bollinger"],
                "wait_time": 10,
                "verify_visual": True
            },
            {
                "category": "indicators",
                "subcategory": "atr",
                "question": "What's the ATR for TSLA?",
                "expected_keywords": ["ATR", "Average True Range", "volatility"],
                "wait_time": 10,
                "verify_visual": False
            },
            
            # Volume Analysis
            {
                "category": "indicators",
                "subcategory": "volume",
                "question": "Analyze volume patterns on TSLA",
                "expected_keywords": ["volume", "accumulation", "distribution", "OBV"],
                "wait_time": 12,
                "verify_visual": False
            },
            
            # Fundamental Analysis
            {
                "category": "fundamental",
                "subcategory": "earnings",
                "question": "What's TSLA's P/E ratio and earnings?",
                "expected_keywords": ["P/E", "earnings", "EPS", "ratio"],
                "wait_time": 12,
                "verify_visual": False
            },
            {
                "category": "fundamental",
                "subcategory": "valuation",
                "question": "Analyze TSLA's valuation metrics",
                "expected_keywords": ["valuation", "P/E", "P/S", "market cap", "enterprise"],
                "wait_time": 15,
                "verify_visual": False
            },
            {
                "category": "fundamental",
                "subcategory": "financials",
                "question": "Show me TSLA's revenue and profit margins",
                "expected_keywords": ["revenue", "profit", "margin", "growth"],
                "wait_time": 15,
                "verify_visual": False
            },
            
            # Complex Analysis
            {
                "category": "complex",
                "subcategory": "full_technical",
                "question": "Do a complete technical analysis of TSLA",
                "expected_keywords": ["support", "resistance", "pattern", "indicator", "trend"],
                "wait_time": 20,
                "verify_visual": True
            },
            {
                "category": "complex",
                "subcategory": "trade_setup",
                "question": "Show me a trade setup for TSLA with entry, stop loss, and targets",
                "expected_commands": ["ENTRY:", "STOPLOSS:", "TARGET:"],
                "wait_time": 15,
                "verify_visual": True
            }
        ]
    
    async def run_test(self):
        """Run comprehensive technical analysis test."""
        
        print("=" * 80)
        print("🔬 COMPREHENSIVE TECHNICAL ANALYSIS TEST")
        print("=" * 80)
        print(f"Testing {len(self.test_scenarios)} scenarios across all capabilities")
        print("Categories: Drawing, Support/Resistance, Fibonacci, Patterns, Indicators, Fundamental")
        print("=" * 80)
        
        async with async_playwright() as p:
            # Setup browser
            print("\n1️⃣ Setting up browser...")
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=300
            )
            
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Navigate to app
            print("2️⃣ Loading trading application...")
            await page.goto("http://localhost:5174")
            await page.wait_for_timeout(5000)
            
            # Connect Voice Assistant
            print("\n3️⃣ Connecting Voice Assistant...")
            try:
                voice_button = await page.wait_for_selector('.voice-fab', timeout=5000)
                await voice_button.click()
                await page.wait_for_selector('.voice-fab.active', timeout=10000)
                print("   ✅ Voice Assistant connected")
            except Exception as e:
                print(f"   ❌ Failed to connect Voice Assistant: {e}")
                await browser.close()
                return
            
            await page.wait_for_timeout(3000)
            
            # Run each test scenario
            print("\n4️⃣ Starting technical analysis tests...\n")
            
            for idx, scenario in enumerate(self.test_scenarios, 1):
                print(f"{'='*60}")
                print(f"Test {idx}/{len(self.test_scenarios)}: {scenario['category'].upper()} - {scenario['subcategory']}")
                print(f"Question: {scenario['question']}")
                
                test_result = {
                    "test_number": idx,
                    "category": scenario["category"],
                    "subcategory": scenario["subcategory"],
                    "question": scenario["question"],
                    "response": "",
                    "chart_commands": [],
                    "passed": False,
                    "notes": []
                }
                
                try:
                    # Find and use input field
                    input_selector = '.voice-conversation-section input[type="text"], .voice-conversation-section textarea'
                    input_field = await page.wait_for_selector(input_selector, timeout=5000)
                    
                    # Clear and type question
                    await input_field.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Delete")
                    await input_field.type(scenario["question"])
                    
                    # Submit
                    await page.keyboard.press("Enter")
                    print(f"   ⏳ Waiting {scenario['wait_time']}s for response...")
                    
                    # Wait for response
                    await page.wait_for_timeout(scenario["wait_time"] * 1000)
                    
                    # Check if chart was modified (for visual verification)
                    if scenario.get("verify_visual", False):
                        # Take screenshot to verify chart changes
                        screenshot_name = f"tech_test_{idx}_{scenario['subcategory']}.png"
                        await page.screenshot(path=screenshot_name)
                        print(f"   📸 Screenshot saved: {screenshot_name}")
                        
                        # Check console for chart commands
                        console_logs = await page.evaluate("() => console.logs || []")
                        chart_commands = [log for log in console_logs if any(cmd in str(log) for cmd in ["SUPPORT:", "RESISTANCE:", "FIBONACCI:", "INDICATOR:", "DRAW:", "TRENDLINE:"])]
                        test_result["chart_commands"] = chart_commands
                        
                        if chart_commands:
                            print(f"   ✅ Chart commands executed: {len(chart_commands)}")
                            test_result["notes"].append(f"Executed {len(chart_commands)} chart commands")
                    
                    # Check for expected commands or keywords in response
                    if "expected_commands" in scenario:
                        # Check if any expected commands were executed
                        commands_found = []
                        for expected in scenario["expected_commands"]:
                            if any(expected in str(cmd) for cmd in test_result.get("chart_commands", [])):
                                commands_found.append(expected)
                        
                        if commands_found:
                            print(f"   ✅ Found commands: {', '.join(commands_found)}")
                            test_result["passed"] = True
                            test_result["notes"].append(f"Commands found: {commands_found}")
                        else:
                            print(f"   ⚠️ Expected commands not found")
                            test_result["notes"].append("Expected commands not detected")
                    
                    elif "expected_keywords" in scenario:
                        # Get response text
                        try:
                            conversation_section = await page.query_selector('.voice-conversation-section')
                            if conversation_section:
                                response_text = await conversation_section.inner_text()
                                test_result["response"] = response_text
                                
                                # Check for keywords
                                keywords_found = []
                                for keyword in scenario["expected_keywords"]:
                                    if keyword.lower() in response_text.lower():
                                        keywords_found.append(keyword)
                                
                                if keywords_found:
                                    print(f"   ✅ Found keywords: {', '.join(keywords_found)}")
                                    test_result["passed"] = True
                                    test_result["notes"].append(f"Keywords found: {keywords_found}")
                                else:
                                    print(f"   ⚠️ Expected keywords not found")
                                    test_result["notes"].append("Keywords not detected in response")
                        except Exception as e:
                            print(f"   ⚠️ Could not capture response: {e}")
                    
                    # Update capability flags
                    if test_result["passed"]:
                        self.test_results["capabilities"][scenario["category"]] = True
                        self.test_results["summary"]["successful"] += 1
                        print(f"   ✅ TEST PASSED")
                    else:
                        self.test_results["summary"]["failed"] += 1
                        print(f"   ❌ TEST FAILED")
                    
                except Exception as e:
                    print(f"   ❌ Test error: {e}")
                    test_result["notes"].append(f"Error: {str(e)}")
                    self.test_results["summary"]["failed"] += 1
                
                # Add to results
                self.test_results["tests"].append(test_result)
                
                # Brief pause between tests
                await page.wait_for_timeout(2000)
            
            # Update summary
            self.test_results["summary"]["total_tests"] = len(self.test_scenarios)
            
            # Generate report
            self.generate_report()
            
            # Final screenshot
            await page.screenshot(path="tech_test_final.png", full_page=True)
            
            print("\n⏸️ Browser will remain open for 10 seconds for inspection...")
            await page.wait_for_timeout(10000)
            
            await browser.close()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        
        print("\n" + "=" * 80)
        print("📊 TECHNICAL ANALYSIS CAPABILITY REPORT")
        print("=" * 80)
        
        # Capability Summary
        print("\n🎯 CAPABILITY ASSESSMENT:")
        capabilities = self.test_results["capabilities"]
        for capability, status in capabilities.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {capability.upper()}: {'WORKING' if status else 'NOT DETECTED'}")
        
        # Test Statistics
        summary = self.test_results["summary"]
        print(f"\n📈 TEST RESULTS:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful']} ({summary['successful']/summary['total_tests']*100:.1f}%)")
        print(f"   Failed: {summary['failed']} ({summary['failed']/summary['total_tests']*100:.1f}%)")
        
        # Category Breakdown
        print(f"\n📊 CATEGORY BREAKDOWN:")
        categories = {}
        for test in self.test_results["tests"]:
            cat = test["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "subcategories": set()}
            
            if test["passed"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
            categories[cat]["subcategories"].add(test["subcategory"])
        
        for cat, data in categories.items():
            total = data["passed"] + data["failed"]
            success_rate = (data["passed"] / total * 100) if total > 0 else 0
            status = "✅" if success_rate >= 70 else "⚠️" if success_rate >= 40 else "❌"
            print(f"   {status} {cat.upper()}: {success_rate:.1f}% success ({data['passed']}/{total} passed)")
            print(f"      Tested: {', '.join(data['subcategories'])}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        working_features = [k for k, v in capabilities.items() if v]
        missing_features = [k for k, v in capabilities.items() if not v]
        
        if len(working_features) == len(capabilities):
            print("   ✅ EXCELLENT: All technical analysis capabilities are working!")
            print("   - Voice Assistant can perform comprehensive technical analysis")
            print("   - Chart drawing and indicator overlays functioning")
            print("   - Pattern detection active")
        elif len(working_features) >= 4:
            print("   ⚠️ GOOD: Most technical analysis features are working")
            print(f"   - Working: {', '.join(working_features)}")
            print(f"   - Need attention: {', '.join(missing_features)}")
        else:
            print("   ❌ NEEDS IMPROVEMENT: Limited technical analysis capabilities")
            print(f"   - Working: {', '.join(working_features) if working_features else 'None'}")
            print(f"   - Not working: {', '.join(missing_features)}")
            print("   - Check agent tools and chart control integration")
        
        # Save detailed report
        report_file = f"tech_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        # Create markdown summary
        self.create_markdown_report()
    
    def create_markdown_report(self):
        """Create a markdown report for documentation."""
        
        report = f"""# Technical Analysis Test Report

**Date:** {self.test_results['timestamp']}

## Capability Assessment

| Capability | Status |
|------------|--------|
| Drawing | {'✅ Working' if self.test_results['capabilities']['drawing'] else '❌ Not Detected'} |
| Support/Resistance | {'✅ Working' if self.test_results['capabilities']['support_resistance'] else '❌ Not Detected'} |
| Fibonacci | {'✅ Working' if self.test_results['capabilities']['fibonacci'] else '❌ Not Detected'} |
| Pattern Detection | {'✅ Working' if self.test_results['capabilities']['patterns'] else '❌ Not Detected'} |
| Indicators | {'✅ Working' if self.test_results['capabilities']['indicators'] else '❌ Not Detected'} |
| Fundamental Analysis | {'✅ Working' if self.test_results['capabilities']['fundamental'] else '❌ Not Detected'} |

## Test Results Summary

- **Total Tests:** {self.test_results['summary']['total_tests']}
- **Successful:** {self.test_results['summary']['successful']} ({self.test_results['summary']['successful']/self.test_results['summary']['total_tests']*100:.1f}%)
- **Failed:** {self.test_results['summary']['failed']} ({self.test_results['summary']['failed']/self.test_results['summary']['total_tests']*100:.1f}%)

## Detailed Test Results

"""
        
        for test in self.test_results["tests"]:
            status = "✅ PASSED" if test["passed"] else "❌ FAILED"
            report += f"""
### Test {test['test_number']}: {test['category']} - {test['subcategory']}
- **Question:** {test['question']}
- **Status:** {status}
- **Notes:** {', '.join(test['notes']) if test['notes'] else 'N/A'}
"""
            if test.get('chart_commands'):
                report += f"- **Chart Commands:** {len(test['chart_commands'])} executed\n"
        
        markdown_file = f"tech_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(markdown_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Markdown summary saved: {markdown_file}")


async def main():
    """Run the technical analysis test."""
    
    print("\n🚀 Starting Comprehensive Technical Analysis Test")
    print("   This will test all technical and fundamental analysis capabilities")
    print("   Including drawing, indicators, patterns, and more\n")
    
    tester = TechnicalAnalysisTester()
    await tester.run_test()
    
    print("\n✅ TECHNICAL ANALYSIS TEST COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())