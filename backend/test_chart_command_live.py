#!/usr/bin/env python3
"""
Trigger a live chart command to test the polling system
"""
import asyncio
import httpx

API_BASE = "https://gvses-market-insights.fly.dev"

async def trigger_command():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Trigger symbol change to NVDA
        resp = await client.post(
            f"{API_BASE}/api/function-call",
            json={"name": "change_chart_symbol", "arguments": {"symbol": "NVDA"}},
            headers={"X-Client-Session": "playwright-test-session"}
        )
        result = resp.json()
        print(f"Command triggered: {result}")
        return result.get("success")

if __name__ == "__main__":
    success = asyncio.run(trigger_command())
    print(f"✓ Command sent successfully" if success else "✗ Command failed")
