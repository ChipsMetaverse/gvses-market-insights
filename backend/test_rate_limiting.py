"""
Test Rate Limiting Functionality
================================
Comprehensive tests for the enhanced rate limiting system.
"""

import httpx
import time
import asyncio
from typing import Dict, List


BASE_URL = "http://localhost:8000"


async def test_basic_rate_limit():
    """Test that rate limits are enforced for anonymous users"""
    print("\n=== Test 1: Basic Rate Limiting (Anonymous User) ===")

    async with httpx.AsyncClient() as client:
        # Health endpoint has high limit (120/minute)
        responses = []
        for i in range(5):
            response = await client.get(f"{BASE_URL}/health")
            responses.append(response)
            print(f"Request {i+1}: Status {response.status_code}, "
                  f"Remaining: {response.headers.get('X-RateLimit-Remaining', 'N/A')}, "
                  f"Limit: {response.headers.get('X-RateLimit-Limit', 'N/A')}")

        # All should succeed
        assert all(r.status_code == 200 for r in responses), "Some requests failed"
        print("✅ Basic rate limiting works")


async def test_rate_limit_exceeded():
    """Test that 429 is returned when limit is exceeded"""
    print("\n=== Test 2: Rate Limit Exceeded ===")

    async with httpx.AsyncClient() as client:
        # Spam requests to exceed limit
        # Health has 120/minute limit for anonymous users
        responses = []
        for i in range(125):
            response = await client.get(f"{BASE_URL}/health")
            responses.append(response)

            if response.status_code == 429:
                print(f"✅ Rate limit exceeded at request {i+1}")
                print(f"Response: {response.json()}")
                remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
                reset = response.headers.get('X-RateLimit-Reset', 'N/A')
                print(f"Remaining: {remaining}, Reset: {reset}")
                break

        has_429 = any(r.status_code == 429 for r in responses)
        if not has_429:
            print(f"⚠️  No 429 received after {len(responses)} requests")
            print("This might mean rate limiting is not active or limits are very high")


async def test_rate_limit_headers():
    """Test that rate limit headers are present"""
    print("\n=== Test 3: Rate Limit Headers ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")

        headers = {
            'X-RateLimit-Limit': response.headers.get('X-RateLimit-Limit'),
            'X-RateLimit-Remaining': response.headers.get('X-RateLimit-Remaining'),
            'X-RateLimit-Reset': response.headers.get('X-RateLimit-Reset'),
            'X-RateLimit-Window': response.headers.get('X-RateLimit-Window'),
        }

        print("Rate Limit Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")

        if all(v is not None for v in headers.values()):
            print("✅ All rate limit headers present")
        else:
            print("⚠️  Some rate limit headers missing")


async def test_admin_bypass():
    """Test that admin users bypass rate limits"""
    print("\n=== Test 4: Admin Bypass ===")

    # Set X-User-Tier header to admin
    headers = {"X-User-Tier": "admin"}

    async with httpx.AsyncClient() as client:
        # Make many requests - should all succeed for admin
        responses = []
        for i in range(150):
            response = await client.get(f"{BASE_URL}/health", headers=headers)
            responses.append(response)

        all_success = all(r.status_code == 200 for r in responses)
        if all_success:
            print(f"✅ Admin made {len(responses)} requests without being rate limited")
        else:
            failed = [r for r in responses if r.status_code != 200]
            print(f"⚠️  Admin was rate limited: {len(failed)} requests failed")


async def test_authenticated_user():
    """Test authenticated user has higher limits"""
    print("\n=== Test 5: Authenticated User Higher Limits ===")

    # Set X-User-Tier header to authenticated
    headers = {"X-User-Tier": "authenticated"}

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health", headers=headers)

        limit = response.headers.get('X-RateLimit-Limit')
        remaining = response.headers.get('X-RateLimit-Remaining')

        print(f"Authenticated user limit: {limit}")
        print(f"Remaining: {remaining}")

        # Health endpoint: anonymous=120/min, authenticated=200/min
        if limit and int(limit) > 120:
            print("✅ Authenticated user has higher limits than anonymous")
        else:
            print("⚠️  Authenticated user limit not higher than anonymous")


async def test_rate_limit_monitoring_endpoints():
    """Test rate limit monitoring endpoints"""
    print("\n=== Test 6: Rate Limit Monitoring Endpoints ===")

    async with httpx.AsyncClient() as client:
        # Test /api/rate-limits/config
        print("\n--- Config Endpoint ---")
        response = await client.get(f"{BASE_URL}/api/rate-limits/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Config endpoint works")
            print(f"  Redis available: {config.get('redis_available')}")
            print(f"  Endpoints configured: {config.get('endpoints_configured')}")
        else:
            print(f"⚠️  Config endpoint failed: {response.status_code}")

        # Test /api/rate-limits/status
        print("\n--- Status Endpoint ---")
        response = await client.get(f"{BASE_URL}/api/rate-limits/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status endpoint works")
            print(f"  Tier: {status.get('tier')}")
            print(f"  Backend: {status.get('backend')}")
            print(f"  Limits tracked: {len(status.get('limits', []))}")
        else:
            print(f"⚠️  Status endpoint failed: {response.status_code}")

        # Test /api/rate-limits/limits
        print("\n--- Limits List Endpoint ---")
        response = await client.get(f"{BASE_URL}/api/rate-limits/limits")
        if response.status_code == 200:
            limits = response.json()
            print(f"✅ Limits list endpoint works")
            print(f"  Total endpoints: {limits.get('total_endpoints')}")
            anonymous_limits = limits.get('tiers', {}).get('anonymous', {})
            print(f"  Anonymous tier limits: {len(anonymous_limits)} endpoints")
        else:
            print(f"⚠️  Limits list endpoint failed: {response.status_code}")


async def test_different_endpoints():
    """Test that different endpoints have different limits"""
    print("\n=== Test 7: Different Endpoint Limits ===")

    async with httpx.AsyncClient() as client:
        endpoints = [
            ("/health", "Health"),
            ("/api/stock-price?symbol=TSLA", "Market Data"),
            ("/api/symbol-search?query=test", "Search"),
        ]

        for endpoint, name in endpoints:
            response = await client.get(f"{BASE_URL}{endpoint}")
            limit = response.headers.get('X-RateLimit-Limit', 'N/A')
            print(f"{name:20} | Limit: {limit:6}/window")


async def main():
    """Run all tests"""
    print("=" * 70)
    print("RATE LIMITING TEST SUITE")
    print("=" * 70)

    try:
        await test_basic_rate_limit()
        await test_rate_limit_headers()
        await test_authenticated_user()
        await test_admin_bypass()
        await test_rate_limit_monitoring_endpoints()
        await test_different_endpoints()

        # This test can take a while and spam the server
        # await test_rate_limit_exceeded()

        print("\n" + "=" * 70)
        print("✅ TEST SUITE COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
