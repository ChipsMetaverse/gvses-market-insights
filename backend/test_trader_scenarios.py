#!/usr/bin/env python3
"""
Test Trading Dashboard as G'sves - Senior Portfolio Manager
===========================================================
Uses Computer Use to test the application from a professional trader's perspective.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.seasoned_trader_verifier import SeasonedTraderVerifier
from dotenv import load_dotenv

load_dotenv()


async def test_morning_routine():
    """Test G'sves morning routine."""
    print("=" * 60)
    print("Testing G'sves Morning Routine")
    print("=" * 60)
    
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False  # Watch G'sves work
    verifier.cfg.slow_mo_ms = 500
    
    result = await verifier.run_morning_routine()
    
    print("\n📊 Morning Routine Results:")
    print(f"Status: {result['status']}")
    print(f"Steps completed: {len(result.get('steps', []))}")
    
    if result['status'] == 'completed':
        print("✅ G'sves successfully completed morning routine")
    else:
        print(f"❌ Issues encountered: {result.get('error', 'Check details')}")
    
    return result


async def test_ltb_analysis():
    """Test Load the Boat (LTB) level analysis."""
    print("\n" + "=" * 60)
    print("Testing LTB Entry Point Analysis")
    print("=" * 60)
    
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    # Get LTB scenario
    ltb_scenario = verifier.get_trader_scenarios()[1]
    result = await verifier.run_scenario(ltb_scenario)
    
    print("\n📈 LTB Analysis Results:")
    print(f"Status: {result['status']}")
    
    if result.get('steps'):
        for step in result['steps']:
            if step.get('type') == 'action':
                action = step.get('action', {})
                print(f"  - Executed: {action.get('type', 'unknown')} action")
    
    return result


async def test_options_strategy():
    """Test options trading strategy setup."""
    print("\n" + "=" * 60)
    print("Testing Options Strategy Setup")
    print("=" * 60)
    
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    # Get options scenario
    options_scenario = verifier.get_trader_scenarios()[2]
    result = await verifier.run_scenario(options_scenario)
    
    print("\n🎯 Options Strategy Results:")
    print(f"Status: {result['status']}")
    print(f"Greeks analysis performed: {'Yes' if result['status'] == 'completed' else 'No'}")
    
    return result


async def test_full_trading_day():
    """Simulate a full trading day from morning to EOD."""
    print("=" * 60)
    print("FULL TRADING DAY SIMULATION")
    print(f"Trader: G'sves")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 300  # Slightly faster for full day
    
    print("\n⏰ Starting trading day simulation...")
    results = await verifier.run_trading_day_simulation()
    
    print("\n" + "=" * 60)
    print("TRADING DAY SUMMARY")
    print("=" * 60)
    
    # Display summary for each part of the day
    day_parts = ["Morning Routine", "LTB Analysis", "Swing Trade", "News Trading", "EOD Review"]
    for i, (part, result) in enumerate(zip(day_parts, results)):
        status_icon = "✅" if result['status'] == 'completed' else "❌"
        print(f"{status_icon} {part}: {result['status']}")
        if result.get('issues'):
            print(f"   Issues: {len(result['issues'])} found")
    
    # Overall assessment
    successful = sum(1 for r in results if r['status'] == 'completed')
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}%")
    print(f"✅ Successful scenarios: {successful}/{total}")
    
    # G'sves verdict
    if success_rate >= 90:
        print("\n💼 G'sves says: 'This platform is ready for professional trading!'")
    elif success_rate >= 70:
        print("\n💼 G'sves says: 'Decent platform, but needs some improvements.'")
    else:
        print("\n💼 G'sves says: 'Not ready for my trading standards. Needs work.'")
    
    return results


async def test_specific_scenario(scenario_index: int):
    """Test a specific trader scenario by index."""
    verifier = SeasonedTraderVerifier()
    verifier.tunnel_url = "http://localhost:5174"
    verifier.cfg.headless = False
    verifier.cfg.slow_mo_ms = 500
    
    scenarios = verifier.get_trader_scenarios()
    if scenario_index >= len(scenarios):
        print(f"❌ Invalid scenario index. Available: 0-{len(scenarios)-1}")
        return None
    
    scenario = scenarios[scenario_index]
    print(f"\n🎯 Testing: {scenario['name']}")
    print(f"Description: {scenario['description']}")
    
    result = await verifier.run_scenario(scenario)
    
    print(f"\nResult: {result['status']}")
    if result.get('issues'):
        print(f"Issues found: {len(result['issues'])}")
    
    return result


def list_scenarios():
    """List all available trader scenarios."""
    verifier = SeasonedTraderVerifier()
    scenarios = verifier.get_trader_scenarios()
    
    print("\n" + "=" * 60)
    print("AVAILABLE TRADER SCENARIOS")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios):
        print(f"\n{i}. {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Steps: {len(scenario['steps'])}")


async def main():
    parser = argparse.ArgumentParser(description="Test trading dashboard as G'sves")
    parser.add_argument('--morning', action='store_true', help='Test morning routine')
    parser.add_argument('--ltb', action='store_true', help='Test LTB analysis')
    parser.add_argument('--options', action='store_true', help='Test options strategy')
    parser.add_argument('--full-day', action='store_true', help='Run full trading day simulation')
    parser.add_argument('--scenario', type=int, help='Run specific scenario by index')
    parser.add_argument('--list', action='store_true', help='List all scenarios')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    # If listing scenarios, do that and exit
    if args.list:
        list_scenarios()
        return
    
    # Run appropriate test
    if args.morning:
        await test_morning_routine()
    elif args.ltb:
        await test_ltb_analysis()
    elif args.options:
        await test_options_strategy()
    elif args.full_day:
        await test_full_trading_day()
    elif args.scenario is not None:
        await test_specific_scenario(args.scenario)
    else:
        # Default: run morning routine
        print("No specific test selected. Running morning routine...")
        await test_morning_routine()
    
    print("\n✨ Testing complete!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          G'sves Trading Platform Verification           ║
║         Senior Portfolio Manager Testing Suite          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())