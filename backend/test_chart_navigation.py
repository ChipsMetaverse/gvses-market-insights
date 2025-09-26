#!/usr/bin/env python3
"""
Chart Navigation Command Tests

Validates that multi-timeframe sweeps and technical drawing commands
are present in agent responses for top-down analysis queries.
"""

import json
import os
import sys
import time
from typing import Dict, Any, List

import requests

BASE_URL = os.environ.get("AGENT_BASE_URL", "http://localhost:8000")


def post_orchestrate(query: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    r = requests.post(f"{BASE_URL}/api/agent/orchestrate", json={"query": query, "stream": False}, timeout=60)
    r.raise_for_status()
    data = r.json()
    data["_latency_s"] = time.perf_counter() - t0
    return data


def get_cmds(resp: Dict[str, Any]) -> List[str]:
    cmds = resp.get("chart_commands") or (resp.get("data") or {}).get("chart_commands") or []
    return cmds if isinstance(cmds, list) else []


def assert_contains_timeframes(cmds: List[str], required: List[str]) -> List[str]:
    present = [c.split(":")[1] for c in cmds if c.startswith("TIMEFRAME:")]
    missing = [tf for tf in required if tf not in present]
    return missing


def main() -> int:
    print("Health:")
    try:
        print(requests.get(f"{BASE_URL}/api/agent/health", timeout=10).json())
    except Exception as e:
        print("Backend not reachable:", e)
        return 1

    # 1) Top-down analysis should include macro->micro timeframes
    query = "Run a top down analysis for TSLA including monthly, weekly, daily and intraday"
    resp = post_orchestrate(query)
    cmds = get_cmds(resp)
    required_tfs = ["1M", "1W", "1D", "H8", "H6", "H4", "H3", "H2", "H1", "M30", "M15", "M5", "M1", "S10"]
    missing = assert_contains_timeframes(cmds, required_tfs)
    if missing:
        print("❌ Missing timeframes:", missing)
    else:
        print("✅ Multi-timeframe sweep present")

    # 2) Technical analysis drawings for a liquid symbol
    resp2 = post_orchestrate("Show NVDA technical analysis with support, resistance, fibonacci, and trendline")
    cmds2 = get_cmds(resp2)
    has_support = any(c.startswith("SUPPORT:") for c in cmds2)
    has_res = any(c.startswith("RESISTANCE:") for c in cmds2)
    has_fib = any(c.startswith("FIBONACCI:") for c in cmds2)
    has_tl = any(c.startswith("TRENDLINE:") for c in cmds2)
    print("Drawings:", {"support": has_support, "resistance": has_res, "fibonacci": has_fib, "trendline": has_tl})

    ok = (not missing) and has_support and has_res and has_fib and has_tl
    print(f"Latency: TSLA={int(resp['_latency_s']*1000)} ms, NVDA={int(resp2['_latency_s']*1000)} ms")
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        code = main()
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)

