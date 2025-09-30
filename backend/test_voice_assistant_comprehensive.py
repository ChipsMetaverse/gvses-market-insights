#!/usr/bin/env python3
"""
Comprehensive Voice Assistant Test for New Traders
Tests real interactions with the Voice Assistant and audits responses
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time


class VoiceAssistantTester:
    """Test Voice Assistant responses from a new trader's perspective."""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_tests": 0,
                "successful_responses": 0,
                "failed_responses": 0,
                "accuracy_scores": []
            }
        }
        
        # Comprehensive test questions
        self.test_questions = [
            # Price inquiries
            {
                "question": "What is the current price of TSLA?",
                "expected_keywords": ["TSLA", "price", "$", "440"],
                "category": "price",
                "wait_time": 8
            },
            {
                "question": "How much is Apple stock?",
                "expected_keywords": ["AAPL", "Apple", "$", "255"],
                "category": "price",
                "wait_time": 8
            },
            
            # Technical analysis
            {
                "question": "Show me the technical levels for TSLA",
                "expected_keywords": ["support", "resistance", "level", "$"],
                "category": "technical",
                "wait_time": 10
            },
            {
                "question": "What are TSLA's support and resistance?",
                "expected_keywords": ["support", "resistance", "TSLA", "$"],
                "category": "technical",
                "wait_time": 10
            },
            
            # Pattern detection
            {
                "question": "Are there any patterns in TSLA?",
                "expected_keywords": ["pattern", "TSLA"],
                "category": "patterns",
                "wait_time": 10
            },
            {
                "question": "Show me ML patterns for TSLA",
                "expected_keywords": ["pattern", "TSLA", "ML", "detected"],
                "category": "patterns",
                "wait_time": 12
            },
            
            # News and updates
            {
                "question": "What's the latest news on Tesla?",
                "expected_keywords": ["Tesla", "TSLA", "news"],
                "category": "news",
                "wait_time": 10
            },
            {
                "question": "Any market updates today?",
                "expected_keywords": ["market", "today", "update"],
                "category": "news",
                "wait_time": 10
            },
            
            # Trading recommendations
            {
                "question": "Should I buy TSLA now?",
                "expected_keywords": ["TSLA", "buy", "sell", "recommendation"],
                "category": "strategy",
                "wait_time": 12
            },
            {
                "question": "Is TSLA a good investment?",
                "expected_keywords": ["TSLA", "investment", "analysis"],
                "category": "strategy",
                "wait_time": 12
            },
            
            # Comparisons
            {
                "question": "Compare TSLA and NVDA",
                "expected_keywords": ["TSLA", "NVDA", "compare"],
                "category": "comparison",
                "wait_time": 12
            },
            {
                "question": "Which is better TSLA or AAPL?",
                "expected_keywords": ["TSLA", "AAPL", "better", "compare"],
                "category": "comparison",
                "wait_time": 12
            },
            
            # Educational
            {
                "question": "What does BTD mean?",
                "expected_keywords": ["BTD", "Buy", "Dip"],
                "category": "educational",
                "wait_time": 8
            },
            {
                "question": "Explain bullish patterns",
                "expected_keywords": ["bullish", "pattern", "upward"],
                "category": "educational",
                "wait_time": 10
            },
            
            # Risk management
            {
                "question": "What's a good stop loss for TSLA?",
                "expected_keywords": ["stop", "loss", "TSLA", "risk"],
                "category": "risk",
                "wait_time": 10
            },
            {
                "question": "How volatile is TSLA?",
                "expected_keywords": ["TSLA", "volatile", "volatility"],
                "category": "risk",
                "wait_time": 10
            }
        ]
    
    async def run_test(self):
        """Run the comprehensive Voice Assistant test."""
        
        print("=" * 80)
        print("🤖 COMPREHENSIVE VOICE ASSISTANT TEST - NEW TRADER PERSPECTIVE")
        print("=" * 80)
        print(f"Testing {len(self.test_questions)} different scenarios")
        print("Categories: Price, Technical, Patterns, News, Strategy, Comparison, Education, Risk")
        print("=" * 80)
        
        async with async_playwright() as p:
            # Setup browser
            print("\n1️⃣ Setting up browser...")
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=500
            )
            
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Navigate to app
            print("2️⃣ Loading trading application...")
            await page.goto("http://localhost:5174")
            await page.wait_for_timeout(8000)  # Ensure app is fully loaded
            
            # Take initial screenshot
            await page.screenshot(path="voice_test_initial.png")
            print("   ✅ Application loaded")
            
            # Test each question
            print("\n3️⃣ Starting Voice Assistant tests...\n")
            
            for idx, test_case in enumerate(self.test_questions, 1):
                print(f"{'='*60}")
                print(f"Test {idx}/{len(self.test_questions)}: {test_case['category'].upper()}")
                print(f"Question: {test_case['question']}")
                
                test_result = {
                    "test_number": idx,
                    "category": test_case["category"],
                    "question": test_case["question"],
                    "expected_keywords": test_case["expected_keywords"],
                    "response": "",
                    "found_keywords": [],
                    "missing_keywords": [],
                    "accuracy_score": 0,
                    "passed": False,
                    "issues": []
                }
                
                try:
                    # Find and clear input field
                    input_field = await page.wait_for_selector(
                        'input[placeholder*="message"], textarea, input[type="text"]',
                        timeout=5000
                    )
                    
                    # Clear existing text
                    await input_field.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Delete")
                    
                    # Type the question
                    await input_field.type(test_case["question"])
                    
                    # Submit
                    await page.keyboard.press("Enter")
                    print(f"   ⏳ Waiting {test_case['wait_time']}s for response...")
                    
                    # Wait for response
                    await page.wait_for_timeout(test_case["wait_time"] * 1000)
                    
                    # Capture response (try multiple selectors)
                    response_text = ""
                    selectors = [
                        '.voice-message:last-child',
                        '.message:last-child',
                        'div[class*="message"]:last-child',
                        '.assistant-response:last-child',
                        '.chat-message:last-child'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                text = await element.inner_text()
                                if text and len(text) > 10 and text != test_case["question"]:
                                    response_text = text
                                    break
                        except:
                            continue
                    
                    # If no response found, try getting all recent text
                    if not response_text:
                        # Get the entire voice assistant panel text
                        voice_panel = await page.query_selector('.voice-assistant, #voice-assistant, div[class*="voice"]')
                        if voice_panel:
                            panel_text = await voice_panel.inner_text()
                            # Extract the response (last substantial text block)
                            lines = panel_text.split('\n')
                            for line in reversed(lines):
                                if len(line) > 20 and line != test_case["question"]:
                                    response_text = line
                                    break
                    
                    test_result["response"] = response_text
                    
                    # Audit the response
                    if response_text:
                        print(f"   💬 Response received: {response_text[:100]}...")
                        
                        # Check for expected keywords
                        response_lower = response_text.lower()
                        for keyword in test_case["expected_keywords"]:
                            if keyword.lower() in response_lower:
                                test_result["found_keywords"].append(keyword)
                            else:
                                test_result["missing_keywords"].append(keyword)
                        
                        # Calculate accuracy
                        if test_case["expected_keywords"]:
                            test_result["accuracy_score"] = len(test_result["found_keywords"]) / len(test_case["expected_keywords"])
                        
                        # Determine pass/fail
                        test_result["passed"] = test_result["accuracy_score"] >= 0.5
                        
                        # Report findings
                        if test_result["found_keywords"]:
                            print(f"   ✅ Found keywords: {', '.join(test_result['found_keywords'])}")
                        if test_result["missing_keywords"]:
                            print(f"   ⚠️ Missing keywords: {', '.join(test_result['missing_keywords'])}")
                        
                        print(f"   📊 Accuracy: {test_result['accuracy_score']*100:.1f}%")
                        
                        if test_result["passed"]:
                            print(f"   ✅ TEST PASSED")
                            self.test_results["summary"]["successful_responses"] += 1
                        else:
                            print(f"   ❌ TEST FAILED")
                            self.test_results["summary"]["failed_responses"] += 1
                            test_result["issues"].append("Insufficient keyword matches")
                    else:
                        print(f"   ❌ No response captured")
                        test_result["issues"].append("No response received")
                        self.test_results["summary"]["failed_responses"] += 1
                    
                    # Take screenshot after each test
                    screenshot_name = f"voice_test_{idx}_{test_case['category']}.png"
                    await page.screenshot(path=screenshot_name)
                    
                except Exception as e:
                    print(f"   ❌ Test error: {e}")
                    test_result["issues"].append(f"Error: {str(e)}")
                    self.test_results["summary"]["failed_responses"] += 1
                
                # Add to results
                self.test_results["tests"].append(test_result)
                self.test_results["summary"]["accuracy_scores"].append(test_result["accuracy_score"])
                
                # Brief pause between tests
                await page.wait_for_timeout(2000)
            
            # Calculate final statistics
            self.test_results["summary"]["total_tests"] = len(self.test_questions)
            if self.test_results["summary"]["accuracy_scores"]:
                avg_accuracy = sum(self.test_results["summary"]["accuracy_scores"]) / len(self.test_results["summary"]["accuracy_scores"])
                self.test_results["summary"]["average_accuracy"] = avg_accuracy
            else:
                self.test_results["summary"]["average_accuracy"] = 0
            
            # Generate report
            self.generate_report()
            
            # Final screenshot
            await page.screenshot(path="voice_test_final.png", full_page=True)
            
            print("\n⏸️ Browser will remain open for 15 seconds for inspection...")
            await page.wait_for_timeout(15000)
            
            await browser.close()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        
        print("\n" + "=" * 80)
        print("📊 VOICE ASSISTANT TEST REPORT")
        print("=" * 80)
        
        summary = self.test_results["summary"]
        
        # Overall statistics
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['successful_responses']} ({summary['successful_responses']/summary['total_tests']*100:.1f}%)")
        print(f"   Failed: {summary['failed_responses']} ({summary['failed_responses']/summary['total_tests']*100:.1f}%)")
        print(f"   Average Accuracy: {summary.get('average_accuracy', 0)*100:.1f}%")
        
        # Category performance
        print(f"\n📊 CATEGORY BREAKDOWN:")
        categories = {}
        for test in self.test_results["tests"]:
            cat = test["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "accuracy": []}
            
            if test["passed"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
            categories[cat]["accuracy"].append(test["accuracy_score"])
        
        for cat, data in categories.items():
            total = data["passed"] + data["failed"]
            avg_acc = sum(data["accuracy"]) / len(data["accuracy"]) if data["accuracy"] else 0
            status = "✅" if avg_acc >= 0.7 else "⚠️" if avg_acc >= 0.5 else "❌"
            print(f"   {status} {cat.upper()}: {avg_acc*100:.1f}% accuracy ({data['passed']}/{total} passed)")
        
        # Critical issues
        print(f"\n⚠️ ISSUES FOUND:")
        issue_count = {}
        for test in self.test_results["tests"]:
            for issue in test["issues"]:
                issue_count[issue] = issue_count.get(issue, 0) + 1
        
        if issue_count:
            for issue, count in sorted(issue_count.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {issue}: {count} occurrences")
        else:
            print("   None - All tests completed without errors")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        avg_acc = summary.get('average_accuracy', 0)
        if avg_acc >= 0.8:
            print("   ✅ Excellent: Voice Assistant performing very well")
            print("   - Consider adding more advanced features")
        elif avg_acc >= 0.6:
            print("   ⚠️ Good: Voice Assistant working but needs improvements")
            print("   - Review failed tests for specific issues")
            print("   - Enhance response accuracy for missing keywords")
        else:
            print("   ❌ Needs Improvement: Voice Assistant requires significant work")
            print("   - Many responses missing expected information")
            print("   - Review AI prompt engineering")
            print("   - Consider enhancing the backend response generation")
        
        # Save detailed report
        report_file = f"voice_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        # Create markdown summary
        self.create_markdown_report()
    
    def create_markdown_report(self):
        """Create a markdown report for easy reading."""
        
        report = f"""# Voice Assistant Test Report

**Date:** {self.test_results['timestamp']}
**Average Accuracy:** {self.test_results['summary'].get('average_accuracy', 0)*100:.1f}%
**Success Rate:** {self.test_results['summary']['successful_responses']}/{self.test_results['summary']['total_tests']}

## Test Results

"""
        
        for test in self.test_results["tests"]:
            status = "✅ PASSED" if test["passed"] else "❌ FAILED"
            report += f"""
### Test {test['test_number']}: {test['question']}
- **Category:** {test['category']}
- **Status:** {status}
- **Accuracy:** {test['accuracy_score']*100:.1f}%
- **Expected:** {', '.join(test['expected_keywords'])}
- **Found:** {', '.join(test['found_keywords']) if test['found_keywords'] else 'None'}
- **Missing:** {', '.join(test['missing_keywords']) if test['missing_keywords'] else 'None'}
- **Response Preview:** {test['response'][:200] if test['response'] else 'No response captured'}

"""
        
        markdown_file = f"voice_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(markdown_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Markdown summary saved: {markdown_file}")


async def main():
    """Run the Voice Assistant test."""
    
    print("\n🚀 Starting Comprehensive Voice Assistant Test")
    print("   This simulates a real new trader interacting with the app")
    print("   Each response will be audited for accuracy\n")
    
    tester = VoiceAssistantTester()
    await tester.run_test()
    
    print("\n✅ TEST SUITE COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())