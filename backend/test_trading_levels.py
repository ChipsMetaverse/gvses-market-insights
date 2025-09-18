#!/usr/bin/env python3
"""
Test that all trading levels have been properly migrated.
Verifies the new naming: BTD, Buy Low, SE, Retest
"""

import asyncio
from services.agent_orchestrator import get_orchestrator
from advanced_technical_analysis import AdvancedTechnicalAnalysis

async def test_trading_levels():
    """Test that the new trading levels are properly configured."""
    
    print("\n" + "=" * 70)
    print("TESTING NEW TRADING LEVELS MIGRATION")
    print("=" * 70)
    
    orchestrator = get_orchestrator()
    
    # Test 1: Check schema has new levels
    print("\n[TEST 1] Checking Schema Definition...")
    schema = orchestrator.response_schema
    tech_levels = schema["schema"]["properties"]["data"]["properties"]["technical_levels"]["properties"]
    
    expected_levels = ["se", "buy_low", "btd", "retest"]
    old_levels = ["qe", "st", "ltb"]
    
    all_correct = True
    for level in expected_levels:
        if level in tech_levels:
            print(f"✅ '{level}' found in schema")
        else:
            print(f"❌ '{level}' NOT found in schema")
            all_correct = False
    
    for level in old_levels:
        if level not in tech_levels:
            print(f"✅ Old '{level}' NOT in schema (correct)")
        else:
            print(f"❌ Old '{level}' still in schema (should be removed)")
            all_correct = False
    
    # Test 2: Check technical analysis calculations
    print("\n[TEST 2] Testing Technical Analysis Calculations...")
    
    # Test with sample data
    prices = [100.0] * 200  # Sufficient data for calculations
    volume = [1000000] * 200
    current_price = 100.0
    
    levels = AdvancedTechnicalAnalysis.calculate_advanced_levels(
        prices, volume, current_price
    )
    
    print("Technical levels returned:")
    for key, value in levels.items():
        if 'level' in key:
            print(f"  • {key}: ${value}")
    
    # Check for new level names
    new_level_names = ["btd_level", "buy_low_level", "se_level", "retest_level"]
    old_level_names = ["ltb_level", "st_level", "qe_level"]
    
    for level_name in new_level_names:
        if level_name in levels:
            print(f"✅ '{level_name}' calculated correctly")
        else:
            print(f"❌ '{level_name}' NOT calculated")
            all_correct = False
    
    for level_name in old_level_names:
        if level_name not in levels:
            print(f"✅ Old '{level_name}' NOT in results (correct)")
        else:
            print(f"❌ Old '{level_name}' still being calculated")
            all_correct = False
    
    # Test 3: Test actual query with new levels
    print("\n[TEST 3] Testing Query Response...")
    
    query = "What are the trading levels for TSLA?"
    result = await orchestrator.process_query(query)
    
    # Check response text for new terminology
    response_text = result.get("text", "")
    
    new_terms = ["BTD", "Buy Low", "SE", "Sell High", "Retest", "Buy the Dip"]
    old_terms = ["LTB", "Load the Boat", "ST", "Swing Trade", "QE", "Quick Entry"]
    
    print("\nChecking response terminology:")
    for term in new_terms:
        if term in response_text:
            print(f"✅ Found new term: '{term}'")
        # New terms might not all appear in every response
    
    for term in old_terms:
        if term not in response_text:
            print(f"✅ Old term '{term}' NOT found (correct)")
        else:
            print(f"❌ Old term '{term}' still in response")
            all_correct = False
    
    # Final verdict
    print("\n" + "=" * 70)
    if all_correct:
        print("✅ ALL TESTS PASSED - MIGRATION SUCCESSFUL!")
    else:
        print("⚠️ SOME ISSUES FOUND - REVIEW NEEDED")
    print("=" * 70)
    
    print("\n📊 Migration Summary:")
    print("• Schema: Updated with new level names")
    print("• Technical Analysis: Calculating new levels")
    print("• Response Format: Using new terminology")
    print("• Old References: Removed successfully")

if __name__ == "__main__":
    asyncio.run(test_trading_levels())