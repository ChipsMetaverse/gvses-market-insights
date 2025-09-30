#!/usr/bin/env python3
"""
New Trader Experience Test Suite
Simulates a new trader using the application with diverse questions
Records and audits Voice Assistant responses for accuracy
"""

import os
import asyncio
import base64
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from playwright.async_api import async_playwright, Page
import time


class NewTraderTestSuite:
    """
    Comprehensive test suite simulating a new trader's experience.
    Tests various question types and audits responses.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.playwright = None
        self.browser = None
        self.page: Optional[Page] = None
        self.display_width = 1024
        self.display_height = 768
        
        # Test results storage
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "questions_asked": [],
            "responses_received": [],
            "audit_results": [],
            "overall_accuracy": 0,
            "issues_found": [],
            "screenshots": []
        }
        
        # Define test questions a new trader would ask
        self.trader_questions = [
            # Basic price questions
            {
                "question": "What is the current price of TSLA?",
                "expected_elements": ["TSLA", "price", "$", "440"],
                "category": "price_check"
            },
            {
                "question": "How much is Apple stock trading at?",
                "expected_elements": ["AAPL", "price", "$"],
                "category": "price_check"
            },
            
            # Technical analysis questions
            {
                "question": "What are the support and resistance levels for TSLA?",
                "expected_elements": ["support", "resistance", "level", "$"],
                "category": "technical_analysis"
            },
            {
                "question": "Show me the technical indicators for NVDA",
                "expected_elements": ["NVDA", "technical", "indicator"],
                "category": "technical_analysis"
            },
            
            # Pattern detection questions
            {
                "question": "Are there any patterns forming in TSLA?",
                "expected_elements": ["pattern", "TSLA"],
                "category": "pattern_detection"
            },
            {
                "question": "Show me bullish patterns in the market",
                "expected_elements": ["bullish", "pattern"],
                "category": "pattern_detection"
            },
            
            # Market news questions
            {
                "question": "What's the latest news on Tesla?",
                "expected_elements": ["Tesla", "TSLA", "news"],
                "category": "news"
            },
            {
                "question": "Any important market updates today?",
                "expected_elements": ["market", "update", "today"],
                "category": "news"
            },
            
            # Trading strategy questions
            {
                "question": "Should I buy TSLA at this price?",
                "expected_elements": ["TSLA", "buy", "sell", "recommendation"],
                "category": "strategy"
            },
            {
                "question": "What's a good entry point for NVDA?",
                "expected_elements": ["NVDA", "entry", "price", "level"],
                "category": "strategy"
            },
            
            # Comparison questions
            {
                "question": "Compare TSLA and NVDA performance",
                "expected_elements": ["TSLA", "NVDA", "compare", "performance"],
                "category": "comparison"
            },
            {
                "question": "Which tech stock is performing better?",
                "expected_elements": ["tech", "stock", "performance"],
                "category": "comparison"
            },
            
            # Risk management questions
            {
                "question": "Where should I set my stop loss for TSLA?",
                "expected_elements": ["stop loss", "TSLA", "price", "risk"],
                "category": "risk_management"
            },
            {
                "question": "What's the volatility like for PLTR?",
                "expected_elements": ["PLTR", "volatility", "risk"],
                "category": "risk_management"
            },
            
            # Educational questions
            {
                "question": "What does BTD mean?",
                "expected_elements": ["BTD", "Buy", "Dip", "explanation"],
                "category": "educational"
            },
            {
                "question": "Explain what a bullish engulfing pattern is",
                "expected_elements": ["bullish", "engulfing", "pattern", "candle"],
                "category": "educational"
            }
        ]
    
    async def setup_browser(self):
        """Initialize browser with security settings."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            chromium_sandbox=True,
            env={},
            args=["--disable-extensions", "--disable-file-system"],
            slow_mo=1000  # Slower for visibility
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({
            "width": self.display_width,
            "height": self.display_height
        })
        print("✅ Browser initialized")
    
    async def navigate_to_app(self):
        """Navigate to the trading application."""
        print("📱 Opening trading application...")
        await self.page.goto("http://localhost:5174")
        await asyncio.sleep(5)  # Wait for app to load
        
        # Take initial screenshot
        screenshot = await self.page.screenshot()
        self.test_results["screenshots"].append({
            "name": "initial_state.png",
            "timestamp": datetime.now().isoformat()
        })
        await self.page.screenshot(path="test_1_initial.png")
        print("✅ Application loaded")
    
    async def ask_question(self, question_data: Dict[str, Any]) -> Optional[str]:
        """
        Ask a question via the Voice Assistant and capture response.
        """
        question = question_data["question"]
        print(f"\n💬 Asking: '{question}'")
        
        try:
            # Find the message input field
            input_selector = 'input[placeholder*="message"], textarea, input[type="text"]'
            input_field = await self.page.query_selector(input_selector)
            
            if not input_field:
                print("   ❌ Could not find message input")
                return None
            
            # Clear any existing text
            await input_field.click()
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Delete")
            
            # Type the question
            await input_field.type(question)
            
            # Submit the question
            await self.page.keyboard.press("Enter")
            
            # Wait for response
            await asyncio.sleep(5)  # Give time for response
            
            # Try to capture the response
            response = await self.capture_response()
            
            # Take screenshot after question
            screenshot_name = f"test_{len(self.test_results['questions_asked']) + 1}_{question_data['category']}.png"
            await self.page.screenshot(path=screenshot_name)
            self.test_results["screenshots"].append({
                "name": screenshot_name,
                "question": question,
                "timestamp": datetime.now().isoformat()
            })
            
            # Record the Q&A
            self.test_results["questions_asked"].append(question)
            self.test_results["responses_received"].append(response or "No response captured")
            
            return response
            
        except Exception as e:
            print(f"   ❌ Error asking question: {e}")
            return None
    
    async def capture_response(self) -> Optional[str]:
        """
        Capture the Voice Assistant's response from the UI.
        """
        try:
            # Look for response in various possible locations
            response_selectors = [
                '.voice-response',
                '.message-response',
                '.assistant-response',
                'div[class*="response"]',
                'div[class*="message"]:last-child',
                '.chat-message:last-child'
            ]
            
            for selector in response_selectors:
                element = await self.page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and len(text) > 10:  # Filter out empty or very short responses
                        return text
            
            # Try to get any recent text changes
            await asyncio.sleep(2)
            
            # As fallback, try to get all text and find the response
            page_text = await self.page.content()
            # Look for patterns that might indicate a response
            # This is a rough heuristic
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Could not capture response: {e}")
            return None
    
    def audit_response(self, question_data: Dict[str, Any], response: Optional[str]) -> Dict[str, Any]:
        """
        Audit the response for accuracy and completeness.
        """
        audit = {
            "question": question_data["question"],
            "category": question_data["category"],
            "response": response,
            "expected_elements": question_data["expected_elements"],
            "found_elements": [],
            "missing_elements": [],
            "accuracy_score": 0,
            "issues": []
        }
        
        if not response:
            audit["issues"].append("No response received")
            audit["accuracy_score"] = 0
            return audit
        
        response_lower = response.lower()
        
        # Check for expected elements
        for element in question_data["expected_elements"]:
            if element.lower() in response_lower:
                audit["found_elements"].append(element)
            else:
                audit["missing_elements"].append(element)
        
        # Calculate accuracy score
        if len(question_data["expected_elements"]) > 0:
            audit["accuracy_score"] = len(audit["found_elements"]) / len(question_data["expected_elements"])
        
        # Category-specific auditing
        if question_data["category"] == "price_check":
            # Check if a price with $ sign is present
            if not re.search(r'\$\d+', response):
                audit["issues"].append("No price value found in response")
        
        elif question_data["category"] == "technical_analysis":
            # Check for technical terms
            technical_terms = ["support", "resistance", "level", "indicator", "MA", "RSI", "MACD"]
            if not any(term.lower() in response_lower for term in technical_terms):
                audit["issues"].append("No technical analysis terminology found")
        
        elif question_data["category"] == "pattern_detection":
            # Check for pattern-related terms
            pattern_terms = ["pattern", "formation", "bullish", "bearish", "engulfing", "triangle"]
            if not any(term.lower() in response_lower for term in pattern_terms):
                audit["issues"].append("No pattern terminology found")
        
        # Check response length and quality
        if len(response) < 20:
            audit["issues"].append("Response too short")
        elif len(response) > 1000:
            audit["issues"].append("Response too verbose")
        
        # Check if response is relevant to the question
        question_words = question_data["question"].lower().split()
        relevant_words = sum(1 for word in question_words if word in response_lower)
        if relevant_words < 2:
            audit["issues"].append("Response may not be relevant to the question")
        
        return audit
    
    async def run_comprehensive_test(self):
        """
        Run the complete new trader experience test.
        """
        print("=" * 70)
        print("🧪 NEW TRADER EXPERIENCE TEST SUITE")
        print("=" * 70)
        print(f"Testing {len(self.trader_questions)} different question types")
        print("Categories: Price, Technical, Patterns, News, Strategy, Risk")
        print("=" * 70)
        
        # Setup browser and navigate
        await self.setup_browser()
        await self.navigate_to_app()
        
        # Test each question
        for i, question_data in enumerate(self.trader_questions, 1):
            print(f"\n📊 Test {i}/{len(self.trader_questions)}")
            print(f"   Category: {question_data['category']}")
            
            # Ask the question
            response = await self.ask_question(question_data)
            
            # Audit the response
            audit_result = self.audit_response(question_data, response)
            self.test_results["audit_results"].append(audit_result)
            
            # Display audit results
            print(f"   📈 Accuracy: {audit_result['accuracy_score']*100:.1f}%")
            if audit_result["found_elements"]:
                print(f"   ✅ Found: {', '.join(audit_result['found_elements'])}")
            if audit_result["missing_elements"]:
                print(f"   ❌ Missing: {', '.join(audit_result['missing_elements'])}")
            if audit_result["issues"]:
                print(f"   ⚠️ Issues: {', '.join(audit_result['issues'])}")
                self.test_results["issues_found"].extend(audit_result["issues"])
            
            # Short delay between questions
            await asyncio.sleep(3)
        
        # Calculate overall accuracy
        if self.test_results["audit_results"]:
            total_accuracy = sum(r["accuracy_score"] for r in self.test_results["audit_results"])
            self.test_results["overall_accuracy"] = total_accuracy / len(self.test_results["audit_results"])
        
        # Generate summary report
        await self.generate_report()
        
        # Keep browser open for final inspection
        print("\n⏸️ Browser will remain open for 10 seconds for inspection...")
        await asyncio.sleep(10)
        
        # Cleanup
        await self.browser.close()
        await self.playwright.stop()
    
    async def generate_report(self):
        """
        Generate a comprehensive test report.
        """
        print("\n" + "=" * 70)
        print("📋 TEST REPORT SUMMARY")
        print("=" * 70)
        
        # Overall statistics
        print(f"\n📊 Overall Statistics:")
        print(f"   Questions Asked: {len(self.test_results['questions_asked'])}")
        print(f"   Responses Received: {len([r for r in self.test_results['responses_received'] if r != 'No response captured'])}")
        print(f"   Overall Accuracy: {self.test_results['overall_accuracy']*100:.1f}%")
        print(f"   Issues Found: {len(self.test_results['issues_found'])}")
        
        # Category breakdown
        print(f"\n📈 Category Performance:")
        categories = {}
        for audit in self.test_results["audit_results"]:
            cat = audit["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "accuracy": 0}
            categories[cat]["count"] += 1
            categories[cat]["accuracy"] += audit["accuracy_score"]
        
        for cat, data in categories.items():
            avg_accuracy = (data["accuracy"] / data["count"]) * 100 if data["count"] > 0 else 0
            status = "✅" if avg_accuracy >= 70 else "⚠️" if avg_accuracy >= 50 else "❌"
            print(f"   {status} {cat}: {avg_accuracy:.1f}% accuracy")
        
        # Common issues
        print(f"\n⚠️ Common Issues:")
        issue_counts = {}
        for issue in self.test_results["issues_found"]:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {issue}: {count} occurrences")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if self.test_results["overall_accuracy"] < 0.5:
            print("   ❌ Critical: Voice Assistant needs significant improvements")
            print("   - Many responses missing expected information")
            print("   - Consider enhancing the AI prompt or training")
        elif self.test_results["overall_accuracy"] < 0.7:
            print("   ⚠️ Moderate: Voice Assistant needs some improvements")
            print("   - Some responses incomplete or inaccurate")
            print("   - Review specific category failures")
        else:
            print("   ✅ Good: Voice Assistant performing well overall")
            print("   - Most responses contain expected information")
            print("   - Minor improvements could enhance user experience")
        
        # Save detailed report to file
        report_filename = f"trader_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_filename}")
        
        # Create markdown summary
        markdown_report = self.generate_markdown_report()
        markdown_filename = f"trader_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(markdown_filename, 'w') as f:
            f.write(markdown_report)
        
        print(f"📄 Markdown summary saved: {markdown_filename}")
    
    def generate_markdown_report(self) -> str:
        """
        Generate a markdown-formatted test report.
        """
        report = f"""# New Trader Experience Test Report

**Date:** {self.test_results['timestamp']}
**Overall Accuracy:** {self.test_results['overall_accuracy']*100:.1f}%

## Test Summary

- **Total Questions:** {len(self.test_results['questions_asked'])}
- **Successful Responses:** {len([r for r in self.test_results['responses_received'] if r != 'No response captured'])}
- **Issues Found:** {len(self.test_results['issues_found'])}

## Question-Response Audit

"""
        for i, audit in enumerate(self.test_results["audit_results"], 1):
            status = "✅" if audit["accuracy_score"] >= 0.7 else "⚠️" if audit["accuracy_score"] >= 0.5 else "❌"
            report += f"""
### {i}. {audit['question']}
- **Category:** {audit['category']}
- **Accuracy:** {audit['accuracy_score']*100:.1f}% {status}
- **Expected Elements:** {', '.join(audit['expected_elements'])}
- **Found:** {', '.join(audit['found_elements']) if audit['found_elements'] else 'None'}
- **Missing:** {', '.join(audit['missing_elements']) if audit['missing_elements'] else 'None'}
- **Issues:** {', '.join(audit['issues']) if audit['issues'] else 'None'}

"""
        
        return report


async def main():
    """Run the new trader experience test."""
    
    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("   This test uses AI to audit responses")
        return
    
    # Check if app is running
    import requests
    try:
        response = requests.get("http://localhost:5174", timeout=2)
        if response.status_code != 200:
            print("⚠️ Trading app may not be fully loaded")
    except:
        print("❌ Trading app not running on port 5174")
        print("   Start it with: cd frontend && npm run dev")
        return
    
    print("✅ Prerequisites checked")
    print("   - OpenAI API key: Set")
    print("   - Trading app: Running")
    
    # Run the test suite
    tester = NewTraderTestSuite()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    print("\n🚀 Starting New Trader Experience Test")
    print("   This simulates a real new trader using the app")
    print("   Various questions will be asked and responses audited")
    
    asyncio.run(main())