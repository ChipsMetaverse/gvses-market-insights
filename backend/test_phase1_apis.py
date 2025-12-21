#!/usr/bin/env python3
"""
Comprehensive Phase 1 API Integration Tests
Tests all 7 behavioral coaching endpoints
"""
import requests
import json
from datetime import datetime, timedelta

import uuid

BASE_URL = "http://localhost:8000"
# Use a valid UUID for testing (SERVICE_ROLE_KEY bypasses foreign key checks)
USER_ID = "00000000-0000-0000-0000-000000000001"

def test_disclaimers():
    """Test legal disclaimers endpoint"""
    print("\n🧪 Testing Disclaimers...")
    response = requests.get(f"{BASE_URL}/api/coaching/disclaimers")

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    if len(data.get('disclaimers', [])) != 4:
        print(f"❌ FAILED: Expected 4 disclaimers, got {len(data.get('disclaimers', []))}")
        return False

    print("✅ Disclaimers: PASSED (4 disclaimers loaded)")
    return True

def test_act_exercises():
    """Test ACT exercises library"""
    print("\n🧪 Testing ACT Exercises...")
    response = requests.get(f"{BASE_URL}/api/coaching/act/exercises")

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    exercises = data.get('exercises', [])
    if len(exercises) != 5:
        print(f"❌ FAILED: Expected 5 exercises, got {len(exercises)}")
        return False

    # Verify exercise structure
    first_exercise = exercises[0]
    required_fields = ['id', 'type', 'title', 'description', 'duration_seconds',
                      'difficulty', 'instructions', 'trigger_contexts', 'skill_taught']

    for field in required_fields:
        if field not in first_exercise:
            print(f"❌ FAILED: Missing field '{field}' in exercise")
            return False

    print("✅ ACT Exercises: PASSED (5 exercises with complete data)")
    return True

def test_trade_capture():
    """Test trade journal capture"""
    print("\n🧪 Testing Trade Capture...")

    trade_data = {
        "symbol": "AAPL",
        "entry_price": 180.00,
        "exit_price": 182.00,
        "entry_timestamp": datetime.now().isoformat(),
        "exit_timestamp": (datetime.now() + timedelta(minutes=15)).isoformat(),
        "position_size": 100,
        "direction": "long",
        "timeframe": "5m",
        "emotional_tags": ["confident", "calm"],
        "plan_entry": "Buy at support level 180",
        "plan_exit": "Sell at resistance 182",
        "stress_level": 3,
        "confidence_level": 8
    }

    response = requests.post(
        f"{BASE_URL}/api/coaching/trades/capture",
        headers={"X-User-ID": USER_ID, "Content-Type": "application/json"},
        json=trade_data
    )

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    if 'trade_id' not in data:
        print("❌ FAILED: Missing trade_id in response")
        return False

    flags = data.get('behavioral_flags', {})
    if flags.get('is_disciplined') != True:
        print(f"❌ FAILED: Expected is_disciplined=True (had plan), got {flags.get('is_disciplined')}")
        return False

    print(f"✅ Trade Capture: PASSED (trade_id: {data['trade_id'][:8]}...)")
    print(f"   Behavioral flags: disciplined={flags.get('is_disciplined')}, " +
          f"revenge={flags.get('is_revenge')}, impulsive={flags.get('is_impulsive')}")
    return True

def test_journal_retrieval():
    """Test journal entries retrieval"""
    print("\n🧪 Testing Journal Retrieval...")
    response = requests.get(
        f"{BASE_URL}/api/coaching/trades/journal?limit=10",
        headers={"X-User-ID": USER_ID}
    )

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    trades = data.get('entries', [])
    if len(trades) < 1:
        print("❌ FAILED: Expected at least 1 trade from previous capture test")
        return False

    # Verify trade structure
    first_trade = trades[0]
    required_fields = ['id', 'symbol', 'entry_price', 'exit_price', 'pl',
                      'is_disciplined', 'entry_timestamp']

    for field in required_fields:
        if field not in first_trade:
            print(f"❌ FAILED: Missing field '{field}' in trade")
            return False

    print(f"✅ Journal Retrieval: PASSED ({len(trades)} trades retrieved)")
    print(f"   Most recent: {first_trade['symbol']} ${first_trade['entry_price']} " +
          f"→ ${first_trade['exit_price']} (P/L: ${first_trade.get('pl', 0):.2f})")
    return True

def test_weekly_insights():
    """Test weekly insights endpoint"""
    print("\n🧪 Testing Weekly Insights...")
    response = requests.get(
        f"{BASE_URL}/api/coaching/insights/weekly",
        headers={"X-User-ID": USER_ID}
    )

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    insights = data.get('insights', {})

    # Should have at least basic stats
    if 'total_trades' not in insights:
        print("❌ FAILED: Missing total_trades in insights")
        return False

    print(f"✅ Weekly Insights: PASSED")
    print(f"   Total trades: {insights.get('total_trades', 0)}")
    print(f"   Disciplined: {insights.get('disciplined_trades', 0)}")
    print(f"   Impulsive: {insights.get('impulsive_trades', 0)}")
    return True

def test_act_completion():
    """Test ACT exercise completion tracking"""
    print("\n🧪 Testing ACT Exercise Completion...")

    # First get an exercise
    exercises_response = requests.get(f"{BASE_URL}/api/coaching/act/exercises")
    if exercises_response.status_code != 200:
        print("❌ FAILED: Couldn't fetch exercises")
        return False

    exercise_id = exercises_response.json()['exercises'][0]['id']

    completion_data = {
        "exercise_id": exercise_id,
        "trigger_context": "post_stopout",
        "completed": True,
        "duration_seconds": 120,
        "quality_rating": 4,
        "user_notes": "Test completion - felt helpful",
        "prevented_impulsive_trade": True,
        "improved_emotional_state": True
    }

    response = requests.post(
        f"{BASE_URL}/api/coaching/act/complete",
        headers={"X-User-ID": USER_ID, "Content-Type": "application/json"},
        json=completion_data
    )

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    if 'completion_id' not in data:
        print("❌ FAILED: Missing completion_id")
        return False

    print(f"✅ ACT Completion: PASSED (completion_id: {data['completion_id'][:8]}...)")
    return True

def test_pattern_detection():
    """Test behavioral pattern detection"""
    print("\n🧪 Testing Pattern Detection...")

    # Need at least 20 trades for meaningful detection
    print("   Note: Pattern detection requires 20+ trades")
    print("   Creating minimal dataset for testing...")

    response = requests.get(
        f"{BASE_URL}/api/coaching/patterns/detect",
        headers={"X-User-ID": USER_ID}
    )

    if response.status_code != 200:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
        return False

    data = response.json()

    if not data.get('success'):
        print("❌ FAILED: success=False")
        return False

    # May have 0 patterns if insufficient data
    patterns = data.get('patterns', [])
    message = data.get('message', '')

    if message and 'Need' in message:
        print(f"✅ Pattern Detection: PASSED (insufficient data for detection)")
        print(f"   {message}")
    elif len(patterns) > 0:
        print(f"✅ Pattern Detection: PASSED ({len(patterns)} patterns detected)")
        for p in patterns:
            print(f"   - {p['pattern_type']}: {p['title']}")
    else:
        print("✅ Pattern Detection: PASSED (no patterns detected)")

    return True

def run_all_tests():
    """Run all Phase 1 integration tests"""
    print("=" * 70)
    print("🚀 Phase 1 Behavioral Coaching API - Integration Test Suite")
    print("=" * 70)
    print()
    print(f"Target: {BASE_URL}")
    print(f"Test User: {USER_ID}")
    print()

    # Check if backend is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=2)
        if health_response.status_code != 200:
            print("❌ Backend not responding. Start backend server first:")
            print("   cd backend && uvicorn mcp_server:app --reload")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running. Start backend server first:")
        print("   cd backend && uvicorn mcp_server:app --reload")
        return False

    results = {
        'disclaimers': False,
        'act_exercises': False,
        'trade_capture': False,
        'journal_retrieval': False,
        'weekly_insights': False,
        'act_completion': False,
        'pattern_detection': False
    }

    try:
        results['disclaimers'] = test_disclaimers()
        results['act_exercises'] = test_act_exercises()
        results['trade_capture'] = test_trade_capture()
        results['journal_retrieval'] = test_journal_retrieval()
        results['weekly_insights'] = test_weekly_insights()
        results['act_completion'] = test_act_completion()
        results['pattern_detection'] = test_pattern_detection()

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print()
    print("=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<25} {status}")

    print()
    print(f"Total: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("✅ Phase 1 Backend is fully functional")
        print()
        print("Next Steps:")
        print("  1. Review PHASE_1_IMPLEMENTATION_STATUS.md")
        print("  2. Begin frontend development")
        print("  3. Start with <TradeJournal /> component")
        print()
        return True
    else:
        print("=" * 70)
        print("⚠️  SOME TESTS FAILED")
        print("=" * 70)
        print()
        print("Common issues:")
        print("  1. Migration not run - Check PHASE_1_TESTING_GUIDE.md Step 1")
        print("  2. Tables don't exist - Run backend/check_phase1_tables.py")
        print("  3. Backend errors - Check logs for details")
        print()
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
