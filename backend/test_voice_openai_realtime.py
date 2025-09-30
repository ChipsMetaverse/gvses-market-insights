#!/usr/bin/env python3
"""
Voice Assistant Test for OpenAI Realtime API
Tests real interactions with the Voice Assistant and audits responses
Fixed for OpenAI Realtime API architecture
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time


class VoiceAssistantOpenAITester:
    """Test Voice Assistant with OpenAI Realtime API from a new trader's perspective."""
    
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
        
        # Test questions for a new trader
        self.test_questions = [
            # Price inquiries
            {
                "question": "What is the current price of TSLA?",
                "expected_keywords": ["TSLA", "price", "$"],
                "category": "price",
                "wait_time": 10
            },
            {
                "question": "How much is Apple stock?",
                "expected_keywords": ["AAPL", "Apple", "$"],
                "category": "price",
                "wait_time": 10
            },
            
            # Technical analysis
            {
                "question": "Show me the technical levels for TSLA",
                "expected_keywords": ["support", "resistance", "level"],
                "category": "technical",
                "wait_time": 12
            },
            
            # Pattern detection
            {
                "question": "Are there any patterns in TSLA?",
                "expected_keywords": ["pattern", "TSLA"],
                "category": "patterns",
                "wait_time": 12
            },
            
            # News
            {
                "question": "What's the latest news on Tesla?",
                "expected_keywords": ["Tesla", "TSLA", "news"],
                "category": "news",
                "wait_time": 12
            },
            
            # Trading recommendations
            {
                "question": "Should I buy TSLA now?",
                "expected_keywords": ["TSLA", "analysis"],
                "category": "strategy",
                "wait_time": 15
            },
            
            # Comparisons
            {
                "question": "Compare TSLA and NVDA",
                "expected_keywords": ["TSLA", "NVDA"],
                "category": "comparison",
                "wait_time": 15
            },
            
            # Educational
            {
                "question": "What does BTD mean?",
                "expected_keywords": ["BTD", "Buy", "Dip"],
                "category": "educational",
                "wait_time": 10
            },
            
            # Risk management
            {
                "question": "What's a good stop loss for TSLA?",
                "expected_keywords": ["stop", "loss", "TSLA"],
                "category": "risk",
                "wait_time": 12
            }
        ]
    
    async def run_test(self):
        """Run the Voice Assistant test with OpenAI Realtime API."""
        
        print("=" * 80)
        print("🤖 VOICE ASSISTANT TEST - OPENAI REALTIME API")
        print("=" * 80)
        print(f"Testing {len(self.test_questions)} scenarios")
        print("Categories: Price, Technical, Patterns, News, Strategy, Comparison, Education, Risk")
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
            await page.wait_for_timeout(5000)  # Wait for app to load
            
            # Take initial screenshot
            await page.screenshot(path="openai_test_initial.png")
            print("   ✅ Application loaded")
            
            # Connect Voice Assistant
            print("\n3️⃣ Connecting Voice Assistant...")
            
            # Click the voice FAB button
            try:
                voice_button = await page.wait_for_selector(
                    '.voice-fab',
                    timeout=5000
                )
                await voice_button.click()
                print("   ✅ Clicked voice button")
                
                # Wait for connection (look for active state)
                await page.wait_for_selector(
                    '.voice-fab.active',
                    timeout=10000
                )
                print("   ✅ Voice Assistant connected")
                
            except Exception as e:
                print(f"   ❌ Failed to connect Voice Assistant: {e}")
                await browser.close()
                return
            
            # Wait for WebSocket connection to stabilize
            await page.wait_for_timeout(3000)
            
            # Test each question
            print("\n4️⃣ Starting Voice Assistant tests...\n")
            
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
                    # Find the input field in the voice conversation section
                    input_selector = '.voice-conversation-section input[type="text"], .voice-conversation-section textarea'
                    input_field = await page.wait_for_selector(
                        input_selector,
                        timeout=5000
                    )
                    
                    # Clear and type the question
                    await input_field.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Delete")
                    await input_field.type(test_case["question"])
                    
                    # Submit
                    await page.keyboard.press("Enter")
                    print(f"   ⏳ Waiting {test_case['wait_time']}s for response...")
                    
                    # Wait for response
                    await page.wait_for_timeout(test_case["wait_time"] * 1000)
                    
                    # Capture response from voice conversation section
                    response_text = ""
                    
                    # Try to get the last message in the conversation
                    try:
                        # Get all messages in the voice conversation
                        messages = await page.query_selector_all('.voice-conversation-section .message')
                        if messages:
                            # Get the last assistant message
                            for message in reversed(messages):
                                role = await message.get_attribute('data-role')
                                if role == 'assistant':
                                    response_text = await message.inner_text()
                                    break
                        
                        # Fallback: try to get any text from conversation section
                        if not response_text:
                            conversation_section = await page.query_selector('.voice-conversation-section')
                            if conversation_section:
                                full_text = await conversation_section.inner_text()
                                # Extract response after the question
                                lines = full_text.split('\n')
                                question_found = False
                                for line in lines:
                                    if test_case["question"] in line:
                                        question_found = True
                                    elif question_found and line.strip():
                                        response_text = line.strip()
                                        break
                    except Exception as e:
                        print(f"   ⚠️ Error capturing response: {e}")
                    
                    test_result["response"] = response_text
                    
                    # Audit the response
                    if response_text:
                        print(f"   💬 Response: {response_text[:150]}...")
                        
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
                    screenshot_name = f"openai_test_{idx}_{test_case['category']}.png"
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
            await page.screenshot(path="openai_test_final.png", full_page=True)
            
            print("\n⏸️ Browser will remain open for 10 seconds for inspection...")
            await page.wait_for_timeout(10000)
            
            await browser.close()
    
    def generate_report(self):
        """Generate test report."""
        
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
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        avg_acc = summary.get('average_accuracy', 0)
        if avg_acc >= 0.8:
            print("   ✅ Excellent: Voice Assistant performing very well")
        elif avg_acc >= 0.6:
            print("   ⚠️ Good: Voice Assistant working but needs improvements")
            print("   - Review failed tests for specific issues")
        else:
            print("   ❌ Needs Improvement: Voice Assistant requires significant work")
            print("   - Many responses missing expected information")
        
        # Save detailed report
        report_file = f"openai_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")


async def main():
    """Run the Voice Assistant test."""
    
    print("\n🚀 Starting Voice Assistant Test (OpenAI Realtime API)")
    print("   Testing from a new trader's perspective")
    print("   Each response will be audited for accuracy\n")
    
    tester = VoiceAssistantOpenAITester()
    await tester.run_test()
    
    print("\n✅ TEST SUITE COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())