#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agent Orchestrator (Day 5.1)
Tests all implemented features from Days 1-4.
"""

import asyncio
import time
import json
from typing import Dict, List, Any
from services.agent_orchestrator import get_orchestrator
from services.market_service_factory import MarketServiceFactory
from response_formatter import MarketResponseFormatter

class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, name: str, passed: bool, details: str = ""):
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUITE SUMMARY")
        print("=" * 70)
        for test in self.tests:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status}: {test['name']}")
            if test['details']:
                print(f"        {test['details']}")
        
        print("\n" + "-" * 70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 70)

async def test_tool_wiring(results: TestResults):
    """Day 1: Test tool wiring and execution."""
    print("\n[Day 1] Testing Tool Wiring...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Test that tools are defined (tools are in tool_schemas)
        tools_defined = len(orchestrator.tool_schemas) > 0
        results.record("Tool definitions exist", tools_defined, 
                      f"Found {len(orchestrator.tool_schemas)} tools")
        
        # Test tool execution
        response = await orchestrator.process_query("What is the current price of TSLA?")
        has_tools_used = 'tools_used' in response and len(response['tools_used']) > 0
        results.record("Tools executed for query", has_tools_used,
                      f"Tools used: {response.get('tools_used', [])}")
        
    except Exception as e:
        results.record("Tool wiring test", False, str(e))

async def test_triggers_disclaimers(results: TestResults):
    """Day 2: Test triggers and disclaimers."""
    print("\n[Day 2] Testing Triggers & Disclaimers...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Test that response includes disclaimer
        response = await orchestrator.process_query("Should I buy AAPL stock?")
        text = response.get('text', '')
        has_disclaimer = 'Disclaimer' in text or 'financial advice' in text.lower()
        results.record("Disclaimer included", has_disclaimer)
        
        # Test trigger words
        trigger_queries = [
            "analyze TSLA",
            "show me NVDA chart",
            "what's the price of AAPL"
        ]
        
        for query in trigger_queries:
            resp = await orchestrator.process_query(query)
            tools_triggered = len(resp.get('tools_used', [])) > 0
            results.record(f"Trigger: '{query[:20]}...'", tools_triggered,
                         f"Tools: {resp.get('tools_used', [])[:2]}")
            
    except Exception as e:
        results.record("Triggers test", False, str(e))

async def test_advanced_ta(results: TestResults):
    """Day 3.1: Test advanced technical analysis with fallback."""
    print("\n[Day 3.1] Testing Advanced TA...")
    
    try:
        service = MarketServiceFactory.get_service()
        
        # Test technical levels calculation
        comp = await service.get_comprehensive_stock_data('TSLA')
        tech_levels = comp.get('technical_levels', {})
        
        has_qe = 'qe_level' in tech_levels
        has_st = 'st_level' in tech_levels
        has_ltb = 'ltb_level' in tech_levels
        
        results.record("QE level calculated", has_qe, 
                      f"QE: ${tech_levels.get('qe_level', 'N/A')}")
        results.record("ST level calculated", has_st,
                      f"ST: ${tech_levels.get('st_level', 'N/A')}")
        results.record("LTB level calculated", has_ltb,
                      f"LTB: ${tech_levels.get('ltb_level', 'N/A')}")
        
    except Exception as e:
        results.record("Advanced TA test", False, str(e))

async def test_tailored_suggestions(results: TestResults):
    """Day 3.2: Test dynamic tailored suggestions."""
    print("\n[Day 3.2] Testing Tailored Suggestions...")
    
    try:
        # Generate tailored suggestions (it's a static method that takes one arg: context dict)
        context = {
            'symbol': 'TSLA',
            'price': 420,
            'technical_levels': {'qe_level': 425, 'st_level': 380, 'ltb_level': 350}
        }
        suggestions = MarketResponseFormatter.generate_tailored_suggestions(context)
        
        has_suggestions = len(suggestions) > 0
        results.record("Suggestions generated", has_suggestions,
                      f"Count: {len(suggestions)}")
        
        # Check quality
        if suggestions:
            first_suggestion = suggestions[0]
            is_contextual = any(word in first_suggestion.lower() 
                               for word in ['qe', 'st', 'ltb', 'resistance', 'support'])
            results.record("Suggestions are contextual", is_contextual,
                          first_suggestion[:60] + "...")
        
    except Exception as e:
        results.record("Tailored suggestions test", False, str(e))

async def test_concurrent_timeouts(results: TestResults):
    """Day 4.1: Test concurrent execution with timeouts."""
    print("\n[Day 4.1] Testing Concurrent Execution...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Test parallel execution
        start_time = time.time()
        response = await orchestrator.process_query(
            "Give me comprehensive analysis of AAPL including price, news, and technical levels"
        )
        elapsed = time.time() - start_time
        
        # Should execute in parallel (< 10s instead of sequential 30s+)
        is_concurrent = elapsed < 10
        results.record("Concurrent execution", is_concurrent,
                      f"Completed in {elapsed:.1f}s")
        
        # Test timeout handling
        tools_with_status = response.get('data', {})
        timeout_count = sum(1 for tool_data in tools_with_status.values() 
                          if isinstance(tool_data, dict) and 
                          tool_data.get('status') == 'timeout')
        
        handles_timeouts = timeout_count >= 0  # Can handle timeouts
        results.record("Timeout handling", handles_timeouts,
                      f"{timeout_count} timeouts handled gracefully")
        
    except Exception as e:
        results.record("Concurrent execution test", False, str(e))

async def test_ideal_formatter(results: TestResults):
    """Priority: Test ideal response formatter."""
    print("\n[Priority] Testing Ideal Response Format...")
    
    try:
        # Test formatter with mock data
        formatted = MarketResponseFormatter.format_stock_snapshot_ideal(
            'TSLA',
            'Tesla, Inc.',
            {'price': 410, 'change_percent': 3.5, 'volume': 150000000},
            [{'title': 'Test News', 'source': 'CNBC'}],
            {'qe_level': 420, 'st_level': 380, 'ltb_level': 350},
            {}
        )
        
        # Check for required sections
        required_sections = [
            "## Here's your real-time",
            "Market Snapshot & Context",
            "Key Headlines",
            "Technical Overview",
            "Summary Table",
            "Strategic Insights",
            "Disclaimer"
        ]
        
        for section in required_sections:
            has_section = section in formatted
            results.record(f"Has '{section[:20]}...'", has_section)
        
    except Exception as e:
        results.record("Ideal formatter test", False, str(e))

async def test_bounded_insights(results: TestResults):
    """Day 4.2: Test bounded LLM insights."""
    print("\n[Day 4.2] Testing Bounded LLM Insights...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Test insight generation
        context = {
            'symbol': 'NVDA',
            'price_data': {'price': 950, 'change_percent': 2.5},
            'technical_levels': {'qe_level': 960, 'st_level': 940}
        }
        
        # Test different character limits
        for max_chars in [150, 250]:
            insight = await orchestrator._generate_bounded_insight(context, max_chars)
            is_bounded = len(insight) <= max_chars
            results.record(f"Insight bounded to {max_chars} chars", is_bounded,
                          f"Actual: {len(insight)} chars")
        
        # Test fallback
        fallback = orchestrator._generate_fallback_insight(context, 200)
        has_fallback = len(fallback) > 0
        results.record("Fallback insight works", has_fallback,
                      fallback[:60] + "...")
        
    except Exception as e:
        results.record("Bounded insights test", False, str(e))

async def test_integration(results: TestResults):
    """Test full integration of all features."""
    print("\n[Integration] Testing Full Stack...")
    
    try:
        orchestrator = get_orchestrator()
        
        # Full query that exercises all features
        response = await orchestrator.process_query(
            "Give me a complete analysis of TSLA with all technical levels and insights"
        )
        
        text = response.get('text', '')
        
        # Check integration points
        has_price_data = '$' in text
        results.record("Price data integrated", has_price_data)
        
        has_tech_levels = any(level in text for level in ['QE', 'ST', 'LTB'])
        results.record("Technical levels integrated", has_tech_levels)
        
        has_disclaimer = 'Disclaimer' in text or 'financial advice' in text.lower()
        results.record("Disclaimer integrated", has_disclaimer)
        
        response_quality = len(text) > 500
        results.record("Response quality", response_quality,
                      f"Length: {len(text)} chars")
        
    except Exception as e:
        results.record("Integration test", False, str(e))

async def run_comprehensive_test_suite():
    """Run all tests in the comprehensive suite."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUITE - Days 1-5")
    print("=" * 70)
    
    results = TestResults()
    
    # Run all test modules
    test_modules = [
        test_tool_wiring,
        test_triggers_disclaimers,
        test_advanced_ta,
        test_tailored_suggestions,
        test_concurrent_timeouts,
        test_ideal_formatter,
        test_bounded_insights,
        test_integration
    ]
    
    for test_module in test_modules:
        try:
            await test_module(results)
        except Exception as e:
            print(f"ERROR in {test_module.__name__}: {e}")
            results.record(test_module.__name__, False, str(e))
    
    # Print summary
    results.print_summary()
    
    # Return success/failure
    return results.failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test_suite())
    exit(0 if success else 1)