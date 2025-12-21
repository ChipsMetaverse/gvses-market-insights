"""
Test Prometheus Metrics Integration
====================================
Sprint 1, Day 2: Verify metrics collection works end-to-end.

Tests:
1. Metrics endpoint accessibility
2. Model routing metrics recording
3. Prompt cache metrics recording
4. Cost tracking metrics recording
5. HTTP request metrics (middleware)
"""

import asyncio
import httpx
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


async def test_metrics_endpoint():
    """Test that /metrics endpoint returns Prometheus format."""
    logger.info("\n=== Testing /metrics Endpoint ===")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/metrics", timeout=10.0)

            if response.status_code != 200:
                logger.error(f"❌ Metrics endpoint returned {response.status_code}")
                return False

            # Check for Prometheus format
            content = response.text

            # Should contain metric type declarations
            if "# HELP" not in content or "# TYPE" not in content:
                logger.error("❌ Response doesn't look like Prometheus format")
                return False

            # Check for our custom metrics
            expected_metrics = [
                "http_requests_total",
                "http_request_duration_seconds",
                "model_selections_total",
                "prompt_cache_operations_total",
                "openai_api_calls_total",
                "openai_cost_usd"
            ]

            missing_metrics = []
            for metric in expected_metrics:
                if metric not in content:
                    missing_metrics.append(metric)

            if missing_metrics:
                logger.warning(f"⚠️  Missing metrics: {missing_metrics}")
                logger.info("(This is OK if no API calls have been made yet)")
            else:
                logger.info("✅ All expected metric types found")

            logger.info(f"✅ Metrics endpoint accessible (content length: {len(content)} bytes)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to access metrics endpoint: {e}")
            return False


async def test_health_endpoint():
    """Test that server is running."""
    logger.info("\n=== Testing Server Health ===")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)

            if response.status_code != 200:
                logger.error(f"❌ Health check failed with {response.status_code}")
                return False

            data = response.json()
            logger.info(f"✅ Server healthy: {data}")
            return True

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False


async def trigger_api_call():
    """Trigger an API call to generate metrics."""
    logger.info("\n=== Triggering API Call to Generate Metrics ===")

    async with httpx.AsyncClient() as client:
        try:
            # Make a simple query to trigger model routing, caching, and cost tracking
            response = await client.post(
                f"{BASE_URL}/ask",
                json={"query": "What's the price of TSLA?"},
                timeout=30.0
            )

            if response.status_code != 200:
                logger.warning(f"⚠️  API call returned {response.status_code}")
                return False

            data = response.json()
            logger.info(f"✅ API call successful: {data.get('text', '')[:100]}...")
            return True

        except Exception as e:
            logger.error(f"❌ API call failed: {e}")
            return False


async def verify_metrics_updated():
    """Verify that metrics were updated after API call."""
    logger.info("\n=== Verifying Metrics Were Updated ===")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/metrics", timeout=10.0)
            content = response.text

            # Check for specific metric values (not just declarations)
            metrics_with_values = []

            # Model routing metrics
            if "model_selections_total{" in content:
                metrics_with_values.append("model_selections_total")

            # HTTP request metrics (should always have values from our requests)
            if "http_requests_total{" in content:
                metrics_with_values.append("http_requests_total")

            # Cache metrics (might not have values if no caching occurred)
            if "prompt_cache_operations_total{" in content:
                metrics_with_values.append("prompt_cache_operations_total")

            # Cost metrics (should have values if API call succeeded)
            if "openai_api_calls_total{" in content:
                metrics_with_values.append("openai_api_calls_total")

            logger.info(f"✅ Metrics with recorded values: {metrics_with_values}")

            if len(metrics_with_values) >= 2:  # At least HTTP and one other
                logger.info("✅ Metrics are being recorded!")
                return True
            else:
                logger.warning("⚠️  Few metrics have values (might need more API calls)")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to verify metrics: {e}")
            return False


async def run_all_tests():
    """Run all tests in sequence."""
    logger.info("=" * 60)
    logger.info("Sprint 1, Day 2: Prometheus Metrics Integration Tests")
    logger.info("=" * 60)

    results = {}

    # Test 1: Health check
    results["health"] = await test_health_endpoint()
    if not results["health"]:
        logger.error("\n❌ Server not running. Start with: uvicorn mcp_server:app --reload")
        return False

    # Test 2: Metrics endpoint
    results["metrics_endpoint"] = await test_metrics_endpoint()

    # Test 3: Trigger API call
    results["api_call"] = await trigger_api_call()

    # Test 4: Verify metrics updated
    if results["api_call"]:
        # Wait a moment for metrics to be recorded
        await asyncio.sleep(1)
        results["metrics_updated"] = await verify_metrics_updated()
    else:
        results["metrics_updated"] = False
        logger.warning("⚠️  Skipping metrics verification (API call failed)")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    all_passed = all(results.values())

    if all_passed:
        logger.info("\n🎉 All tests passed! Prometheus metrics are working.")
    else:
        logger.info("\n⚠️  Some tests failed. Check logs above for details.")

    logger.info("=" * 60)

    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        sys.exit(1)
