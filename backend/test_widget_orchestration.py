"""
Test Widget Orchestration System

Tests the WidgetOrchestrator service with various user queries to ensure
correct intent classification and widget selection.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.widget_orchestrator import (
    WidgetOrchestrator,
    WidgetType,
    QueryIntent
)


def test_orchestrator():
    """Run comprehensive tests on the widget orchestrator."""
    orchestrator = WidgetOrchestrator(default_symbol="TSLA")

    test_cases = [
        # News queries
        {
            "query": "What's the news on TSLA?",
            "expected_intent": QueryIntent.NEWS,
            "expected_widgets": [WidgetType.MARKET_NEWS],
            "expected_symbol": "TSLA"
        },
        {
            "query": "Show me the latest headlines for AAPL",
            "expected_intent": QueryIntent.NEWS,
            "expected_widgets": [WidgetType.MARKET_NEWS],
            "expected_symbol": "AAPL"
        },

        # Chart queries
        {
            "query": "Show me NVDA chart",
            "expected_intent": QueryIntent.CHART,
            "expected_widgets": [WidgetType.TRADING_CHART],
            "expected_symbol": "NVDA"
        },
        {
            "query": "Display SPY price action",
            "expected_intent": QueryIntent.CHART,
            "expected_widgets": [WidgetType.TRADING_CHART],
            "expected_symbol": "SPY"
        },

        # Pattern detection queries
        {
            "query": "Are there any head and shoulders patterns on MSFT?",
            "expected_intent": QueryIntent.PATTERNS,
            "expected_widgets": [WidgetType.PATTERN_DETECTION, WidgetType.TRADING_CHART],
            "expected_symbol": "MSFT"
        },
        {
            "query": "Show me bull flags on GOOGL",
            "expected_intent": QueryIntent.PATTERNS,
            "expected_widgets": [WidgetType.PATTERN_DETECTION, WidgetType.TRADING_CHART],
            "expected_symbol": "GOOGL"
        },

        # Technical levels queries
        {
            "query": "What are the support and resistance levels for AMZN?",
            "expected_intent": QueryIntent.TECHNICAL_LEVELS,
            "expected_widgets": [WidgetType.TECHNICAL_LEVELS, WidgetType.TRADING_CHART],
            "expected_symbol": "AMZN"
        },
        {
            "query": "Show me buy the dip levels for META",
            "expected_intent": QueryIntent.TECHNICAL_LEVELS,
            "expected_widgets": [WidgetType.TECHNICAL_LEVELS, WidgetType.TRADING_CHART],
            "expected_symbol": "META"
        },

        # Economic calendar queries
        {
            "query": "When is the next NFP?",
            "expected_intent": QueryIntent.ECONOMIC_EVENTS,
            "expected_widgets": [WidgetType.ECONOMIC_CALENDAR],
            "expected_symbol": "TSLA"  # Default symbol
        },
        {
            "query": "Show me the economic calendar for this week",
            "expected_intent": QueryIntent.ECONOMIC_EVENTS,
            "expected_widgets": [WidgetType.ECONOMIC_CALENDAR],
            "expected_symbol": "TSLA"  # Default symbol
        },

        # Comprehensive queries
        {
            "query": "Give me everything on PLTR",
            "expected_intent": QueryIntent.COMPREHENSIVE,
            "expected_widgets": [
                WidgetType.TRADING_CHART,
                WidgetType.TECHNICAL_LEVELS,
                WidgetType.PATTERN_DETECTION,
                WidgetType.MARKET_NEWS,
                WidgetType.ECONOMIC_CALENDAR
            ],
            "expected_symbol": "PLTR"
        },
        {
            "query": "Complete analysis of NFLX",
            "expected_intent": QueryIntent.COMPREHENSIVE,
            "expected_widgets": [
                WidgetType.TRADING_CHART,
                WidgetType.TECHNICAL_LEVELS,
                WidgetType.PATTERN_DETECTION,
                WidgetType.MARKET_NEWS,
                WidgetType.ECONOMIC_CALENDAR
            ],
            "expected_symbol": "NFLX"
        },

        # Unknown/default queries
        {
            "query": "Hello",
            "expected_intent": QueryIntent.UNKNOWN,
            "expected_widgets": [WidgetType.TRADING_CHART],
            "expected_symbol": "TSLA"  # Default symbol
        }
    ]

    print("=" * 80)
    print("Widget Orchestration Test Suite")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        expected_intent = test["expected_intent"]
        expected_widgets = test["expected_widgets"]
        expected_symbol = test["expected_symbol"]

        # Run classification
        result = orchestrator.classify_query(query)

        # Check results
        intent_match = result.intent == expected_intent
        symbol_match = result.symbol == expected_symbol
        widgets_match = result.widgets == expected_widgets

        # Determine pass/fail
        test_passed = intent_match and symbol_match and widgets_match

        # Print results
        status = "✅ PASS" if test_passed else "❌ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Query: \"{query}\"")
        print(f"  Symbol: {result.symbol} (expected: {expected_symbol}) {'✓' if symbol_match else '✗'}")
        print(f"  Intent: {result.intent.value} (expected: {expected_intent.value}) {'✓' if intent_match else '✗'}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Widgets: {[w.value for w in result.widgets]}")
        print(f"  Expected: {[w.value for w in expected_widgets]} {'✓' if widgets_match else '✗'}")
        print(f"  Reasoning: {result.reasoning}")
        print()

        if test_passed:
            passed += 1
        else:
            failed += 1

    # Summary
    print("=" * 80)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(test_cases)} total")
    print("=" * 80)

    return failed == 0


def test_symbol_extraction():
    """Test symbol extraction logic."""
    orchestrator = WidgetOrchestrator(default_symbol="TSLA")

    test_cases = [
        ("Show me AAPL chart", "AAPL"),
        ("What's happening with NVDA?", "NVDA"),
        ("GOOGL news please", "GOOGL"),
        ("Show me the chart", "TSLA"),  # Default
        ("Give me everything on SPY", "SPY"),
        ("MSFT and AMZN comparison", "MSFT"),  # First match
    ]

    print("=" * 80)
    print("Symbol Extraction Tests")
    print("=" * 80)
    print()

    passed = 0
    for query, expected_symbol in test_cases:
        extracted = orchestrator.extract_symbol(query)
        match = extracted == expected_symbol
        status = "✅" if match else "❌"

        print(f"{status} Query: \"{query}\"")
        print(f"   Extracted: {extracted} (expected: {expected_symbol})")
        print()

        if match:
            passed += 1

    print(f"Symbol Extraction: {passed}/{len(test_cases)} passed")
    print()


def test_intent_classification():
    """Test intent classification logic."""
    orchestrator = WidgetOrchestrator(default_symbol="TSLA")

    test_cases = [
        ("What's the news on TSLA?", QueryIntent.NEWS),
        ("Show me the chart", QueryIntent.CHART),
        ("Are there any patterns?", QueryIntent.PATTERNS),
        ("Support levels please", QueryIntent.TECHNICAL_LEVELS),
        ("When is the next CPI?", QueryIntent.ECONOMIC_EVENTS),
        ("Give me everything", QueryIntent.COMPREHENSIVE),
        ("Hello", QueryIntent.UNKNOWN),
    ]

    print("=" * 80)
    print("Intent Classification Tests")
    print("=" * 80)
    print()

    passed = 0
    for query, expected_intent in test_cases:
        intent, confidence = orchestrator.classify_intent(query)
        match = intent == expected_intent
        status = "✅" if match else "❌"

        print(f"{status} Query: \"{query}\"")
        print(f"   Intent: {intent.value} (expected: {expected_intent.value})")
        print(f"   Confidence: {confidence:.2f}")
        print()

        if match:
            passed += 1

    print(f"Intent Classification: {passed}/{len(test_cases)} passed")
    print()


if __name__ == "__main__":
    # Run all tests
    print("\n🧪 Running Widget Orchestration Test Suite\n")

    test_symbol_extraction()
    test_intent_classification()
    all_passed = test_orchestrator()

    if all_passed:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
