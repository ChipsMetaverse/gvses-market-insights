#!/usr/bin/env python3
"""
Unit tests for trading level calculations.
Tests the logic for BTD, Buy Low, SE, and Retest levels.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_technical_analysis import AdvancedTechnicalAnalysis
import numpy as np

def test_flat_price_history():
    """Test level calculations with flat price history."""
    print("\n" + "=" * 70)
    print("TEST: Flat Price History")
    print("=" * 70)
    
    # Create flat price history
    prices = [100.0] * 200
    volumes = [1000000] * 200
    current_price = 100.0
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volumes, current_price
    )
    
    print(f"Current Price: ${current_price}")
    print(f"BTD Level: ${levels['btd_level']} (expected ~92)")
    print(f"Buy Low Level: ${levels['buy_low_level']} (expected ~96)")
    print(f"Retest Level: ${levels['retest_level']} (expected ~98)")
    print(f"Sell High Level: ${levels['se_level']} (expected ~102)")
    
    # Assertions for flat history
    assert 91 < levels['btd_level'] < 93, f"BTD should be ~92 for flat history, got {levels['btd_level']}"
    assert 95 < levels['buy_low_level'] < 97, f"Buy Low should be ~96 for flat history, got {levels['buy_low_level']}"
    assert 97 < levels['retest_level'] < 99, f"Retest should be ~98 for flat history, got {levels['retest_level']}"
    assert 101 < levels['se_level'] < 104, f"Sell High should be ~102-103 for flat history, got {levels['se_level']}"
    
    # Verify correct ordering
    assert levels['btd_level'] < levels['buy_low_level'], "BTD should be below Buy Low"
    assert levels['buy_low_level'] < levels['retest_level'], "Buy Low should be below Retest"
    assert levels['retest_level'] < current_price, "Retest should be below current price"
    assert current_price < levels['se_level'], "Sell High should be above current price"
    
    print("✅ All assertions passed for flat price history")
    return True

def test_uptrend_history():
    """Test level calculations with uptrending price history."""
    print("\n" + "=" * 70)
    print("TEST: Uptrend Price History")
    print("=" * 70)
    
    # Create uptrending price history (80 to 120)
    prices = list(np.linspace(80, 120, 200))
    volumes = [1000000] * 200
    current_price = 120.0
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volumes, current_price
    )
    
    print(f"Current Price: ${current_price}")
    print(f"BTD Level: ${levels['btd_level']}")
    print(f"Buy Low Level: ${levels['buy_low_level']}")
    print(f"Retest Level: ${levels['retest_level']}")
    print(f"Sell High Level: ${levels['se_level']}")
    print(f"MA 200: ${levels['ma_200']}")
    print(f"MA 50: ${levels['ma_50']}")
    print(f"MA 20: ${levels['ma_20']}")
    
    # In uptrend, moving averages should be below current price
    assert levels['ma_200'] < current_price, "MA200 should be below current in uptrend"
    assert levels['ma_50'] < current_price, "MA50 should be below current in uptrend"
    
    # Verify correct ordering
    assert levels['btd_level'] < levels['buy_low_level'], "BTD should be below Buy Low"
    assert levels['buy_low_level'] < levels['retest_level'], "Buy Low should be below Retest"
    assert levels['retest_level'] < current_price, "Retest should be below current price"
    assert current_price < levels['se_level'], "Sell High should be above current price"
    
    print("✅ All assertions passed for uptrend history")
    return True

def test_downtrend_history():
    """Test level calculations with downtrending price history."""
    print("\n" + "=" * 70)
    print("TEST: Downtrend Price History")
    print("=" * 70)
    
    # Create downtrending price history (120 to 80)
    prices = list(np.linspace(120, 80, 200))
    volumes = [1000000] * 200
    current_price = 80.0
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volumes, current_price
    )
    
    print(f"Current Price: ${current_price}")
    print(f"BTD Level: ${levels['btd_level']}")
    print(f"Buy Low Level: ${levels['buy_low_level']}")
    print(f"Retest Level: ${levels['retest_level']}")
    print(f"Sell High Level: ${levels['se_level']}")
    print(f"MA 200: ${levels['ma_200']}")
    print(f"MA 50: ${levels['ma_50']}")
    print(f"MA 20: ${levels['ma_20']}")
    
    # In downtrend, moving averages should be above current price
    assert levels['ma_200'] > current_price, "MA200 should be above current in downtrend"
    assert levels['ma_50'] > current_price, "MA50 should be above current in downtrend"
    
    # Verify correct ordering still holds
    assert levels['btd_level'] < levels['buy_low_level'], "BTD should be below Buy Low"
    assert levels['buy_low_level'] < current_price, "Buy Low should be below current"
    # Retest might be above current in downtrend
    assert current_price < levels['se_level'], "Sell High should be above current price"
    
    print("✅ All assertions passed for downtrend history")
    return True

def test_volatile_history():
    """Test level calculations with volatile price history."""
    print("\n" + "=" * 70)
    print("TEST: Volatile Price History")
    print("=" * 70)
    
    # Create volatile price history
    np.random.seed(42)
    base = 100
    prices = [base + np.random.randn() * 10 for _ in range(200)]
    volumes = [1000000 + np.random.randint(-500000, 500000) for _ in range(200)]
    current_price = prices[-1]
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volumes, current_price
    )
    
    print(f"Current Price: ${current_price:.2f}")
    print(f"BTD Level: ${levels['btd_level']}")
    print(f"Buy Low Level: ${levels['buy_low_level']}")
    print(f"Retest Level: ${levels['retest_level']}")
    print(f"Sell High Level: ${levels['se_level']}")
    print(f"Recent High: ${levels['recent_high']}")
    print(f"Recent Low: ${levels['recent_low']}")
    
    # Basic sanity checks
    assert levels['btd_level'] > 0, "BTD level should be positive"
    assert levels['buy_low_level'] > 0, "Buy Low level should be positive"
    assert levels['retest_level'] > 0, "Retest level should be positive"
    assert levels['se_level'] > 0, "Sell High level should be positive"
    
    # Verify Fibonacci levels were calculated
    assert 'fib_levels' in levels, "Should have Fibonacci levels"
    assert levels['fib_levels'], "Fibonacci levels should not be empty"
    
    # Verify volume profile was calculated
    assert 'volume_profile' in levels, "Should have volume profile"
    
    print("✅ All assertions passed for volatile history")
    return True

def test_insufficient_data():
    """Test fallback logic with insufficient data."""
    print("\n" + "=" * 70)
    print("TEST: Insufficient Data (Fallback)")
    print("=" * 70)
    
    # Create insufficient price history (only 30 candles)
    prices = [100.0] * 30
    volumes = [1000000] * 30
    current_price = 100.0
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volumes, current_price
    )
    
    print(f"Current Price: ${current_price}")
    print(f"BTD Level: ${levels['btd_level']} (fallback: ~92)")
    print(f"Buy Low Level: ${levels['buy_low_level']} (fallback: ~96)")
    print(f"Retest Level: ${levels['retest_level']} (fallback: ~98)")
    print(f"Sell High Level: ${levels['se_level']} (fallback: ~103)")
    
    # Should use simple fallback calculations
    assert abs(levels['btd_level'] - current_price * 0.92) < 0.01, "Should use 8% fallback for BTD"
    assert abs(levels['buy_low_level'] - current_price * 0.96) < 0.01, "Should use 4% fallback for Buy Low"
    assert abs(levels['retest_level'] - current_price * 0.98) < 0.01, "Should use 2% fallback for Retest"
    assert abs(levels['se_level'] - current_price * 1.03) < 0.01, "Should use 3% fallback for Sell High"
    
    print("✅ All assertions passed for insufficient data")
    return True

def run_all_tests():
    """Run all unit tests."""
    print("\n" + "=" * 70)
    print("RUNNING TRADING LEVEL CALCULATION TESTS")
    print("=" * 70)
    
    tests = [
        ("Flat History", test_flat_price_history),
        ("Uptrend", test_uptrend_history),
        ("Downtrend", test_downtrend_history),
        ("Volatile", test_volatile_history),
        ("Insufficient Data", test_insufficient_data)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    else:
        print("🎉 All tests passed!")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)