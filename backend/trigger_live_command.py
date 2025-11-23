#!/usr/bin/env python3
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Trigger command for the Playwright browser session
        resp = await client.post(
            "https://gvses-market-insights.fly.dev/api/function-call",
            json={"name": "change_chart_symbol", "arguments": {"symbol": "NVDA"}},
            headers={"X-Client-Session": "session-1763077667604-cpxglrr"}
        )
        result = resp.json()
        print(f"✓ Command sent: {result.get('success')}")

asyncio.run(main())
