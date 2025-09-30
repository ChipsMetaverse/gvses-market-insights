#!/usr/bin/env python3
"""
Quick New Trader Test - Simplified version for faster execution
Tests essential trader questions and audits responses
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def test_trader_experience():
    """Quick test simulating a new trader."""
    
    print("=" * 70)
    print("🧪 QUICK NEW TRADER TEST")
    print("=" * 70)
    
    # Essential trader questions
    test_questions = [
        "What is the current price of TSLA?",
        "Show me patterns for TSLA",
        "What are the support and resistance levels?",
        "What's the latest news on Tesla?",
        "Should I buy or sell TSLA?",
        "Compare TSLA and NVDA"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "questions": [],
        "screenshots": []
    }
    
    async with async_playwright() as p:
        # Launch browser
        print("\n1️⃣ Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to app
        print("2️⃣ Opening trading app...")
        await page.goto("http://localhost:5174")
        await page.wait_for_timeout(5000)
        
        # Take initial screenshot
        await page.screenshot(path="trader_test_1_initial.png")
        print("   📸 Initial state captured")
        
        # Test each question
        print("\n3️⃣ Testing trader questions...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            
            # Find message input
            input_field = await page.query_selector('input[placeholder*="message"], textarea')
            
            if input_field:
                # Clear and type question
                await input_field.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")
                await input_field.type(question)
                
                # Submit
                await page.keyboard.press("Enter")
                
                # Wait for response
                await page.wait_for_timeout(3000)
                
                # Take screenshot
                screenshot_name = f"trader_test_{i+1}_{question[:20]}.png"
                await page.screenshot(path=screenshot_name)
                print(f"      📸 Response captured")
                
                # Try to capture response text
                try:
                    # Look for voice assistant response
                    response_element = await page.query_selector('.voice-response, .message:last-child, div[class*="message"]:last-child')
                    if response_element:
                        response_text = await response_element.inner_text()
                        print(f"      💬 Response preview: {response_text[:100]}...")
                        
                        # Simple audit
                        if "TSLA" in question:
                            if "TSLA" in response_text or "Tesla" in response_text:
                                print(f"      ✅ Response mentions the stock")
                            else:
                                print(f"      ⚠️ Response doesn't mention TSLA")
                        
                        if "price" in question.lower():
                            if "$" in response_text:
                                print(f"      ✅ Price information found")
                            else:
                                print(f"      ⚠️ No price found")
                        
                        if "pattern" in question.lower():
                            if "pattern" in response_text.lower():
                                print(f"      ✅ Pattern information found")
                            else:
                                print(f"      ⚠️ No pattern information")
                        
                        results["questions"].append({
                            "question": question,
                            "response": response_text,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        print(f"      ⚠️ Could not capture response")
                        
                except Exception as e:
                    print(f"      ❌ Error capturing response: {e}")
            else:
                print(f"      ❌ Could not find input field")
                break
        
        # Final screenshot
        print("\n4️⃣ Taking final screenshot...")
        await page.screenshot(path="trader_test_final.png", full_page=True)
        print("   📸 Final state captured")
        
        # Generate summary
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        print(f"\nQuestions tested: {len(test_questions)}")
        print(f"Responses captured: {len(results['questions'])}")
        
        if results["questions"]:
            print("\n🔍 Response Analysis:")
            for q in results["questions"]:
                print(f"\n❓ {q['question']}")
                response_preview = q['response'][:150] if q['response'] else "No response"
                print(f"   → {response_preview}...")
        
        # Save results
        with open(f"trader_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved to JSON file")
        
        print("\n⏸️ Browser will remain open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()
        print("✅ Test complete!")


if __name__ == "__main__":
    print("\n🚀 Starting Quick Trader Test")
    print("   Simulating new trader questions...")
    asyncio.run(test_trader_experience())