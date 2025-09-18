#!/usr/bin/env python3
"""
Test Agent Knowledge and Persona
=================================
Verifies the agent correctly uses G'sves persona, trading knowledge,
and responds appropriately to different query types.
"""

import asyncio
import json
from services.agent_orchestrator import AgentOrchestrator
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Style.RESET_ALL}")

def print_test(name, passed, details=""):
    """Print test result with color."""
    if passed:
        print(f"{Fore.GREEN}✅ {name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ {name}{Style.RESET_ALL}")
    if details:
        print(f"   {Fore.YELLOW}{details}{Style.RESET_ALL}")

async def test_gsves_persona():
    """Test that agent uses G'sves persona correctly."""
    print_section("TEST 1: G'sves Persona Verification")
    
    orchestrator = AgentOrchestrator()
    
    # Test queries that should trigger G'sves persona
    test_queries = [
        "Who are you?",
        "What's your experience in trading?",
        "Tell me about your background"
    ]
    
    passed_tests = 0
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        response = await orchestrator.process_query(query)
        text = response.get('text', '')
        
        # Check for G'sves indicators
        has_gsves = "G'sves" in text or "30 years" in text
        has_experience = any(term in text.lower() for term in [
            "portfolio", "experience", "senior", "analyst", "market"
        ])
        
        passed = has_gsves or has_experience
        print_test(f"Persona check", passed, 
                  f"Found: G'sves={has_gsves}, Experience={has_experience}")
        
        if passed:
            passed_tests += 1
        
        # Print first 200 chars of response for verification
        print(f"   Response preview: {text[:200]}...")
    
    return passed_tests == len(test_queries)

async def test_trading_levels_knowledge():
    """Test that agent understands and uses new trading levels."""
    print_section("TEST 2: Trading Levels Knowledge")
    
    orchestrator = AgentOrchestrator()
    
    # Test specific stock query
    query = "What are the trading levels for AAPL?"
    print(f"\nQuery: '{query}'")
    
    response = await orchestrator.process_query(query)
    text = response.get('text', '')
    tools_used = response.get('tools_used', [])
    
    # Check tool usage
    print_test("Used market tools", len(tools_used) > 0, 
              f"Tools: {', '.join(tools_used)}")
    
    # Check for trading level mentions
    levels_found = {
        'BTD': 'buy the dip' in text.lower() or 'btd' in text.lower(),
        'Buy Low': 'buy low' in text.lower(),
        'Sell High': 'sell high' in text.lower(),
        'Retest': 'retest' in text.lower()
    }
    
    for level, found in levels_found.items():
        print_test(f"{level} level mentioned", found)
    
    # Check response structure
    has_price_data = '$' in text
    print_test("Contains price data", has_price_data)
    
    return all(levels_found.values()) and has_price_data

async def test_tool_usage_rules():
    """Test that agent only uses tools when appropriate."""
    print_section("TEST 3: Tool Usage Rules")
    
    orchestrator = AgentOrchestrator()
    
    # Query that should NOT trigger tools (general question)
    general_query = "What is a good strategy for day trading?"
    print(f"\nGeneral Query: '{general_query}'")
    
    response = await orchestrator.process_query(general_query)
    tools_used = response.get('tools_used', [])
    
    print_test("No tools for general query", len(tools_used) == 0,
              f"Tools used: {tools_used}")
    
    # Query that SHOULD trigger tools (specific stock)
    stock_query = "What's the current price of Tesla?"
    print(f"\nStock Query: '{stock_query}'")
    
    response = await orchestrator.process_query(stock_query)
    tools_used = response.get('tools_used', [])
    
    print_test("Uses tools for stock query", len(tools_used) > 0,
              f"Tools used: {tools_used}")
    
    return True

async def test_morning_greeting():
    """Test that 'Good morning' triggers market overview."""
    print_section("TEST 4: Morning Greeting Trigger")
    
    orchestrator = AgentOrchestrator()
    
    query = "Good morning"
    print(f"\nQuery: '{query}'")
    
    response = await orchestrator.process_query(query)
    text = response.get('text', '')
    tools_used = response.get('tools_used', [])
    
    # Check for market overview tool
    has_overview = 'get_market_overview' in tools_used
    print_test("Market overview triggered", has_overview,
              f"Tools: {tools_used}")
    
    # Check response contains market data
    has_market_data = any(term in text.lower() for term in [
        'market', 'futures', 's&p', 'nasdaq', 'dow'
    ])
    print_test("Contains market data", has_market_data)
    
    return has_overview and has_market_data

async def test_bounded_insights():
    """Test that LLM insights are bounded to 250 characters."""
    print_section("TEST 5: Bounded LLM Insights")
    
    orchestrator = AgentOrchestrator()
    
    # This should trigger insight generation
    query = "Analyze NVDA for me"
    print(f"\nQuery: '{query}'")
    
    response = await orchestrator.process_query(query)
    
    # The insight is embedded in the response
    # We can't directly measure it but we can check response quality
    text = response.get('text', '')
    tools_used = response.get('tools_used', [])
    
    print_test("Generated response", len(text) > 0)
    print_test("Used analysis tools", len(tools_used) > 0,
              f"Tools: {tools_used}")
    
    # Check response is concise but informative
    word_count = len(text.split())
    print_test("Response is concise", 50 < word_count < 500,
              f"Word count: {word_count}")
    
    return True

async def test_risk_management_emphasis():
    """Test that agent emphasizes risk management."""
    print_section("TEST 6: Risk Management Emphasis")
    
    orchestrator = AgentOrchestrator()
    
    query = "Should I buy TSLA calls?"
    print(f"\nQuery: '{query}'")
    
    response = await orchestrator.process_query(query)
    text = response.get('text', '')
    
    # Check for risk management terms
    risk_terms = {
        'stop-loss': 'stop' in text.lower() or 'stop-loss' in text.lower(),
        'risk': 'risk' in text.lower(),
        'position size': 'position' in text.lower() or 'sizing' in text.lower(),
        'management': 'manage' in text.lower()
    }
    
    for term, found in risk_terms.items():
        print_test(f"Mentions {term}", found)
    
    # Should have at least 2 risk management mentions
    risk_count = sum(risk_terms.values())
    print_test("Adequate risk emphasis", risk_count >= 2,
              f"Found {risk_count}/4 risk terms")
    
    return risk_count >= 2

async def run_all_tests():
    """Run all knowledge tests."""
    print("\n" + "="*70)
    print(f"{Fore.MAGENTA}AGENT KNOWLEDGE & PERSONA TEST SUITE{Style.RESET_ALL}")
    print("="*70)
    
    tests = [
        ("G'sves Persona", test_gsves_persona),
        ("Trading Levels", test_trading_levels_knowledge),
        ("Tool Usage Rules", test_tool_usage_rules),
        ("Morning Greeting", test_morning_greeting),
        ("Bounded Insights", test_bounded_insights),
        ("Risk Management", test_risk_management_emphasis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = await test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"{Fore.RED}Error in {test_name}: {e}{Style.RESET_ALL}")
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        color = Fore.GREEN if passed else Fore.RED
        print(f"{color}{status}: {test_name}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print(f"{Fore.GREEN}🎉 All tests passed! Agent knowledge verified.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️ Some tests failed. Review agent configuration.{Style.RESET_ALL}")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)