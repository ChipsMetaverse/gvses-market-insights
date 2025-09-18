#!/usr/bin/env python3
"""
Test suite for Pattern Detection
Validates pattern detection accuracy using known fixtures
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pattern_detection import PatternDetector


def load_fixture(fixture_name: str) -> dict:
    """Load a test fixture from the fixtures directory"""
    fixture_path = Path(__file__).parent / "fixtures" / f"{fixture_name}.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)


def test_bullish_engulfing():
    """Test detection of bullish engulfing pattern"""
    print("\n🧪 Testing Bullish Engulfing Detection")
    print("=" * 50)
    
    fixture = load_fixture("bullish_engulfing")
    detector = PatternDetector(fixture["candles"])
    results = detector.detect_all_patterns()
    
    # Check if bullish engulfing was detected
    detected_types = [p["type"] for p in results["detected"]]
    
    if "bullish_engulfing" in detected_types:
        pattern = next(p for p in results["detected"] if p["type"] == "bullish_engulfing")
        print(f"✅ Bullish Engulfing detected at candle {pattern['start_candle']}-{pattern['end_candle']}")
        print(f"   Confidence: {pattern['confidence']}%")
        print(f"   Description: {pattern['description']}")
        
        # Validate it's at the expected position (index 7)
        if pattern['end_candle'] == 7:
            print("✅ Pattern found at expected position")
        else:
            print(f"⚠️  Pattern at unexpected position: {pattern['end_candle']} (expected 7)")
        
        # Check confidence is high (should be >75%)
        if pattern['confidence'] >= 75:
            print(f"✅ Confidence level appropriate: {pattern['confidence']}%")
        else:
            print(f"⚠️  Low confidence: {pattern['confidence']}%")
    else:
        print("❌ Bullish Engulfing not detected")
        print(f"   Detected patterns: {detected_types}")
    
    return "bullish_engulfing" in detected_types


def test_doji():
    """Test detection of doji pattern"""
    print("\n🧪 Testing Doji Detection")
    print("=" * 50)
    
    fixture = load_fixture("doji_pattern")
    detector = PatternDetector(fixture["candles"])
    results = detector.detect_all_patterns()
    
    # Check if doji was detected
    doji_patterns = [p for p in results["detected"] if p["type"] == "doji"]
    
    if doji_patterns:
        print(f"✅ {len(doji_patterns)} Doji pattern(s) detected")
        
        # Check for the perfect doji at index 4
        perfect_doji = next((p for p in doji_patterns if p['start_candle'] == 4), None)
        if perfect_doji:
            print(f"✅ Perfect Doji found at index 4")
            print(f"   Confidence: {perfect_doji['confidence']}%")
            
            if perfect_doji['confidence'] >= 90:
                print("✅ High confidence for perfect doji")
            else:
                print(f"⚠️  Lower than expected confidence: {perfect_doji['confidence']}%")
        else:
            print("⚠️  Perfect doji at index 4 not detected")
            print(f"   Doji indices: {[p['start_candle'] for p in doji_patterns]}")
    else:
        print("❌ No Doji patterns detected")
    
    return len(doji_patterns) > 0


def test_support_breakout():
    """Test detection of support levels and breakout"""
    print("\n🧪 Testing Support/Resistance and Breakout Detection")
    print("=" * 50)
    
    fixture = load_fixture("support_breakout")
    detector = PatternDetector(fixture["candles"])
    results = detector.detect_all_patterns()
    
    # Check support levels
    support_levels = results.get("active_levels", {}).get("support", [])
    resistance_levels = results.get("active_levels", {}).get("resistance", [])
    
    print(f"Support levels: {support_levels}")
    print(f"Resistance levels: {resistance_levels}")
    
    # Check if 95 is identified as support (±1%)
    has_95_support = any(94.5 <= s <= 95.5 for s in support_levels)
    if has_95_support:
        print("✅ Support level around $95 detected")
    else:
        print("⚠️  Support at $95 not detected")
    
    # Check for breakout pattern
    breakout_patterns = [p for p in results["detected"] if "breakout" in p["type"]]
    
    if breakout_patterns:
        print(f"✅ {len(breakout_patterns)} Breakout pattern(s) detected")
        for breakout in breakout_patterns:
            print(f"   - {breakout['description']}")
            print(f"     Confidence: {breakout['confidence']}%")
    else:
        print("⚠️  No breakout patterns detected")
        
    # Check for support bounce patterns
    bounce_patterns = [p for p in results["detected"] if "support_bounce" in p["type"]]
    if bounce_patterns:
        print(f"✅ {len(bounce_patterns)} Support bounce(s) detected")
    
    return has_95_support or len(breakout_patterns) > 0


def test_agent_explanation():
    """Test that agent explanation is generated"""
    print("\n🧪 Testing Agent Explanation Generation")
    print("=" * 50)
    
    fixture = load_fixture("bullish_engulfing")
    detector = PatternDetector(fixture["candles"])
    results = detector.detect_all_patterns()
    
    if "agent_explanation" in results:
        print("✅ Agent explanation generated:")
        print(f'   "{results["agent_explanation"]}"')
        
        # Check if explanation mentions key elements
        explanation = results["agent_explanation"].lower()
        has_pattern_mention = any(word in explanation for word in ["engulfing", "doji", "pattern"])
        has_level_mention = "support" in explanation or "resistance" in explanation
        
        if has_pattern_mention or has_level_mention:
            print("✅ Explanation includes relevant technical terms")
        else:
            print("⚠️  Explanation might be too generic")
    else:
        print("❌ No agent explanation generated")
    
    return "agent_explanation" in results


def run_all_tests():
    """Run all pattern detection tests"""
    print("\n" + "=" * 60)
    print("🚀 PATTERN DETECTION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Bullish Engulfing", test_bullish_engulfing),
        ("Doji Pattern", test_doji),
        ("Support/Breakout", test_support_breakout),
        ("Agent Explanation", test_agent_explanation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Pattern detection is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)