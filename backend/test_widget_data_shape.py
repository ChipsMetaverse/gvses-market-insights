#!/usr/bin/env python3
"""
Data Shape Validation Test for GVSES Stock Card Widget
Tests that backend tool output matches widget template expectations
"""

import asyncio
import json
from services.market_service_factory import MarketServiceFactory
from pprint import pprint

async def test_comprehensive_data_shape():
    """Test the data structure returned by comprehensive stock data endpoint"""
    print("=" * 80)
    print("GVSES Widget Data Shape Validation Test")
    print("=" * 80)

    service = MarketServiceFactory.get_service()

    # Test with AAPL as reference
    test_symbol = "AAPL"
    print(f"\nTesting with symbol: {test_symbol}")
    print("-" * 80)

    try:
        data = await service.get_comprehensive_stock_data(test_symbol)

        print("\n📊 FULL DATA STRUCTURE:")
        print(json.dumps(data, indent=2, default=str))

        # Validate critical widget fields
        print("\n" + "=" * 80)
        print("🔍 WIDGET TEMPLATE FIELD VALIDATION")
        print("=" * 80)

        validations = []

        # Check company and symbol
        validations.append(("company", data.get("company"), "string", "Company Inc"))
        validations.append(("symbol", data.get("symbol"), "string", "AAPL"))

        # Check price fields
        if "price" in data:
            price = data["price"]
            validations.append(("price.current", price.get("current"), "number", 150.25))
            validations.append(("price.change", price.get("change"), "number", 1.23))
            validations.append(("price.changePercent", price.get("changePercent"), "number", 0.82))
            validations.append(("price.previousClose", price.get("previousClose"), "number", 149.02))
        else:
            print("⚠️  WARNING: 'price' object missing from data")

        # Check technical levels (critical - must be SH/BL/BTD)
        if "technical" in data:
            tech = data["technical"]
            validations.append(("technical.position", tech.get("position"), "string", "Bullish"))
            validations.append(("technical.color", tech.get("color"), "string", "success"))

            if "levels" in tech:
                levels = tech["levels"]
                # Widget expects: sh, bl, now, btd (with $ formatting)
                validations.append(("technical.levels.sh", levels.get("sh"), "string", "$130.00"))
                validations.append(("technical.levels.bl", levels.get("bl"), "string", "$126.00"))
                validations.append(("technical.levels.now", levels.get("now"), "string", "$123.45"))
                validations.append(("technical.levels.btd", levels.get("btd"), "string", "$118.00"))
            else:
                print("⚠️  WARNING: 'technical.levels' object missing from data")
        else:
            print("⚠️  WARNING: 'technical' object missing from data")

        # Check stats
        if "stats" in data:
            stats = data["stats"]
            validations.append(("stats.open", stats.get("open"), "string", "$121.00"))
            validations.append(("stats.volume", stats.get("volume"), "string", "12.3M"))
            validations.append(("stats.marketCap", stats.get("marketCap"), "string", "$55.4B"))
            validations.append(("stats.dayLow", stats.get("dayLow"), "string", "$120.50"))
            validations.append(("stats.dayHigh", stats.get("dayHigh"), "string", "$124.00"))
            validations.append(("stats.yearLow", stats.get("yearLow"), "string", "$88.34"))
            validations.append(("stats.yearHigh", stats.get("yearHigh"), "string", "$130.22"))
            validations.append(("stats.eps", stats.get("eps"), "string", "$4.12"))
            validations.append(("stats.peRatio", stats.get("peRatio"), "string", "29.9"))
        else:
            print("⚠️  WARNING: 'stats' object missing from data")

        # Check chart data structure
        if "chart" in data:
            chart = data["chart"]
            if isinstance(chart, dict):
                validations.append(("chart.data", chart.get("data"), "array", []))
                if "data" in chart and isinstance(chart["data"], list) and len(chart["data"]) > 0:
                    sample_point = chart["data"][0]
                    print(f"\n📈 Chart Data Sample Point: {json.dumps(sample_point, indent=2, default=str)}")
            else:
                validations.append(("chart", chart, "object/array", "Unexpected structure"))
        else:
            print("⚠️  WARNING: 'chart' data missing")

        # Check news array
        if "news" in data:
            news = data["news"]
            if isinstance(news, list):
                validations.append(("news", news, "array", f"{len(news)} articles"))
                if len(news) > 0:
                    sample_news = news[0]
                    print(f"\n📰 News Sample Item: {json.dumps(sample_news, indent=2, default=str)}")
                    # Check required news fields
                    validations.append(("news[0].title", sample_news.get("title"), "string", "Sample headline"))
                    validations.append(("news[0].source", sample_news.get("source"), "string", "Reuters"))
                    validations.append(("news[0].time", sample_news.get("time"), "string", "2h"))
                    validations.append(("news[0].url", sample_news.get("url"), "string", "https://..."))
            else:
                validations.append(("news", news, "array", f"Wrong type: {type(news)}"))
        else:
            print("⚠️  WARNING: 'news' array missing from data")

        # Check patterns
        if "patterns" in data:
            patterns = data["patterns"]
            if isinstance(patterns, list):
                validations.append(("patterns", patterns, "array", f"{len(patterns)} patterns"))
                if len(patterns) > 0:
                    sample_pattern = patterns[0]
                    print(f"\n🔍 Pattern Sample: {json.dumps(sample_pattern, indent=2, default=str)}")
            else:
                validations.append(("patterns", patterns, "array", f"Wrong type: {type(patterns)}"))
        else:
            print("⚠️  WARNING: 'patterns' array missing from data")

        # Check events
        if "events" in data:
            events = data["events"]
            if isinstance(events, list):
                validations.append(("events", events, "array", f"{len(events)} events"))
                if len(events) > 0:
                    sample_event = events[0]
                    print(f"\n📅 Event Sample: {json.dumps(sample_event, indent=2, default=str)}")
            else:
                validations.append(("events", events, "array", f"Wrong type: {type(events)}"))
        else:
            print("⚠️  WARNING: 'events' array missing from data")

        # Print validation results
        print("\n" + "=" * 80)
        print("✅ FIELD VALIDATION RESULTS")
        print("=" * 80)

        issues = []
        for field_path, actual_value, expected_type, example in validations:
            status = "✅" if actual_value is not None else "❌"

            # Check type matching
            if actual_value is not None:
                actual_type = type(actual_value).__name__
                if expected_type == "string" and not isinstance(actual_value, str):
                    status = "⚠️"
                    issues.append(f"{field_path}: Expected {expected_type}, got {actual_type} ({actual_value})")
                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    status = "⚠️"
                    issues.append(f"{field_path}: Expected {expected_type}, got {actual_type} ({actual_value})")
                elif expected_type == "array" and not isinstance(actual_value, list):
                    status = "⚠️"
                    issues.append(f"{field_path}: Expected {expected_type}, got {actual_type}")
            else:
                issues.append(f"{field_path}: MISSING (expected {expected_type})")

            print(f"{status} {field_path}: {actual_value} (expected: {expected_type}, example: {example})")

        # Summary
        print("\n" + "=" * 80)
        print("📋 VALIDATION SUMMARY")
        print("=" * 80)

        if issues:
            print(f"\n⚠️  {len(issues)} ISSUES FOUND:\n")
            for issue in issues:
                print(f"   • {issue}")
            print("\n🔧 TRANSFORM REQUIRED: Tool output needs reshaping to match widget template expectations")
        else:
            print("\n✅ ALL FIELDS VALID: Tool output matches widget template expectations")
            print("✅ NO TRANSFORM NEEDED: Direct data binding should work")

        # Check critical formatting
        print("\n" + "=" * 80)
        print("💰 FORMATTING VALIDATION (Critical for Widget Display)")
        print("=" * 80)

        formatting_issues = []

        # Technical levels must have $ prefix
        if "technical" in data and "levels" in data["technical"]:
            levels = data["technical"]["levels"]
            for key in ["sh", "bl", "btd", "now"]:
                if key in levels:
                    val = levels[key]
                    if isinstance(val, (int, float)):
                        formatting_issues.append(f"technical.levels.{key}: Raw number {val}, needs $ formatting (e.g., '${val:.2f}')")
                    elif isinstance(val, str) and not val.startswith("$"):
                        formatting_issues.append(f"technical.levels.{key}: String without $ prefix: '{val}'")

        # Stats should be formatted with units
        if "stats" in data:
            stats = data["stats"]
            # Volume should have M/B suffix
            if "volume" in stats and isinstance(stats["volume"], (int, float)):
                formatting_issues.append(f"stats.volume: Raw number {stats['volume']}, needs formatting (e.g., '47.4M')")
            # Market cap should have T/B/M suffix
            if "marketCap" in stats and isinstance(stats["marketCap"], (int, float)):
                formatting_issues.append(f"stats.marketCap: Raw number {stats['marketCap']}, needs formatting (e.g., '$55.4B')")

        if formatting_issues:
            print("\n⚠️  FORMATTING ISSUES DETECTED:\n")
            for issue in formatting_issues:
                print(f"   • {issue}")
            print("\n🔧 RECOMMENDATION: Add number formatting in backend before sending to widget")
        else:
            print("\n✅ ALL FORMATTING CORRECT: Values already formatted with $ and units")

        return data

    except Exception as e:
        print(f"\n❌ ERROR during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_edge_cases():
    """Test error scenarios"""
    print("\n\n" + "=" * 80)
    print("🧪 EDGE CASE TESTING")
    print("=" * 80)

    service = MarketServiceFactory.get_service()

    test_cases = [
        ("Invalid Symbol", "XYZ123ABC", "Should return error or empty data"),
        ("Obscure Ticker", "HMNY", "Might have limited data/news"),
    ]

    for test_name, symbol, expectation in test_cases:
        print(f"\n🔬 Test: {test_name} ({symbol})")
        print(f"   Expectation: {expectation}")
        print("-" * 80)

        try:
            data = await service.get_comprehensive_stock_data(symbol)
            if data:
                print(f"   ✅ Returned data (keys: {list(data.keys())})")
                if "price" in data and data["price"].get("current") == 0:
                    print("   ⚠️  Price is 0 - likely invalid symbol")
            else:
                print("   ⚠️  Returned None/empty")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 Starting Widget Data Shape Validation Tests\n")

    # Run tests
    asyncio.run(test_comprehensive_data_shape())
    asyncio.run(test_edge_cases())

    print("\n" + "=" * 80)
    print("✅ Test Suite Complete")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Review validation results above")
    print("2. If Transform needed, create Transform node in Agent Builder")
    print("3. If formatting issues, update backend formatting functions")
    print("4. Re-run test after fixes to verify")
    print("=" * 80)
