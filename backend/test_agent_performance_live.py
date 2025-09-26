#!/usr/bin/env python3
"""
Live Performance & Diagnostics Test for Agent

Scenarios:
- Price-only
- Technical analysis
- News query
- Complex multi-tool

Outputs:
- Console summary with end-to-end durations and /api/agent/diag per-phase metrics
- Optional HTML report written to backend/performance_report.html
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional

import aiohttp

BASE_URL = os.environ.get("AGENT_BASE_URL", "http://localhost:8000")


def fmt_ms(seconds: float) -> str:
    return f"{int(seconds * 1000)} ms"


async def fetch_json(session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Any:
    async with session.request(method.upper(), url, **kwargs) as resp:
        resp.raise_for_status()
        return await resp.json()


async def post_orchestrate(session: aiohttp.ClientSession, query: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    data = await fetch_json(
        session,
        "POST",
        f"{BASE_URL}/api/agent/orchestrate",
        json={"query": query, "stream": False},
        headers={"Content-Type": "application/json"},
    )
    t1 = time.perf_counter()
    data["_latency_s"] = t1 - t0
    return data


async def get_diag(session: aiohttp.ClientSession) -> Dict[str, Any]:
    try:
        return await fetch_json(session, "GET", f"{BASE_URL}/api/agent/diag")
    except Exception:
        return {}


def extract_chart_checks(resp: Dict[str, Any]) -> Dict[str, Any]:
    cmds = resp.get("chart_commands") or (resp.get("data") or {}).get("chart_commands") or []
    if not isinstance(cmds, list):
        cmds = []
    return {
        "has_chart": any(c.startswith("CHART:") for c in cmds),
        "has_support": any(c.startswith("SUPPORT:") for c in cmds),
        "has_resistance": any(c.startswith("RESISTANCE:") for c in cmds),
        "has_fib": any(c.startswith("FIBONACCI:") for c in cmds),
        "has_trendline": any(c.startswith("TRENDLINE:") for c in cmds),
        "timeframes": [c.split(":")[1] for c in cmds if c.startswith("TIMEFRAME:")],
        "commands": cmds,
    }


async def run_scenarios() -> List[Dict[str, Any]]:
    scenarios = [
        {"name": "price", "query": "Get AAPL price", "target": "<4s"},
        {"name": "technical", "query": "Show technical analysis for NVDA with support, resistance, fibonacci, trendline", "target": "6–9s"},
        {"name": "news", "query": "What are the latest news headlines for TSLA?", "target": "5–8s"},
        {"name": "complex", "query": "For MSFT give me price, a quick analysis, and if any notable news or catalysts", "target": "<12s"},
    ]

    results: List[Dict[str, Any]] = []
    timeout = aiohttp.ClientTimeout(total=90)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Health check
        try:
            health = await fetch_json(session, "GET", f"{BASE_URL}/api/agent/health")
            print("Health:", health)
        except Exception as e:
            print("Backend not reachable:", e)
            return []

        for sc in scenarios:
            try:
                print(f"\n=== Scenario: {sc['name']} ===")
                resp = await post_orchestrate(session, sc["query"])
                diag = await get_diag(session)
                checks = extract_chart_checks(resp)
                result = {
                    "scenario": sc["name"],
                    "query": sc["query"],
                    "latency_s": resp.get("_latency_s"),
                    "text_len": len(resp.get("text", "")),
                    "tools_used": resp.get("tools_used", []),
                    "diag": diag.get("orchestrator", {}).get("last_diag"),
                    "chart_checks": checks,
                    "target": sc["target"],
                }
                print(f"Latency: {fmt_ms(result['latency_s'])}")
                if result["diag"]:
                    print("Per-phase:", result["diag"].get("durations"))
                if checks["commands"]:
                    print("chart_commands:", checks["commands"][:10], ("..." if len(checks["commands"])>10 else ""))
                results.append(result)
            except Exception as e:
                print(f"Scenario '{sc['name']}' failed:", e)
    return results


def write_html_report(results: List[Dict[str, Any]], path: str) -> None:
    rows = []
    for r in results:
        d = r.get("diag") or {}
        dur = d.get("durations") or {}
        tf = ", ".join((r.get("chart_checks") or {}).get("timeframes", [])[:8])
        rows.append(f"""
        <tr>
          <td>{r['scenario']}</td>
          <td>{r['target']}</td>
          <td>{r['query']}</td>
          <td>{int((r['latency_s'] or 0)*1000)}</td>
          <td>{dur.get('llm1','')}</td>
          <td>{dur.get('tools','')}</td>
          <td>{dur.get('summarization','') or dur.get('llm2','')}</td>
          <td>{dur.get('total','')}</td>
          <td>{'✔' if (r.get('chart_checks') or {}).get('has_support') else ''}</td>
          <td>{'✔' if (r.get('chart_checks') or {}).get('has_resistance') else ''}</td>
          <td>{'✔' if (r.get('chart_checks') or {}).get('has_fib') else ''}</td>
          <td>{'✔' if (r.get('chart_checks') or {}).get('has_trendline') else ''}</td>
          <td title="First 8 TFs">{tf}</td>
        </tr>
        """)

    html = f"""
    <html><head><meta charset='utf-8'><title>Agent Performance Report</title>
    <style>
      body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 16px; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; }}
      th {{ background: #f5f5f5; text-align: left; }}
      caption {{ text-align: left; font-weight: bold; margin-bottom: 8px; }}
    </style>
    </head><body>
      <h2>Agent Performance Report</h2>
      <p>Base URL: {BASE_URL}</p>
      <table>
        <caption>Latency and Diagnostics</caption>
        <thead>
          <tr>
            <th>Scenario</th><th>Target</th><th>Query</th><th>Latency (ms)</th>
            <th>LLM#1</th><th>Tools</th><th>Summ/LLM#2</th><th>Total</th>
            <th>Sup</th><th>Res</th><th>Fib</th><th>Trend</th><th>Timeframes</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </body></html>
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


async def main() -> int:
    results = await run_scenarios()
    if not results:
        return 1
    out_path = os.path.join(os.path.dirname(__file__), "performance_report.html")
    write_html_report(results, out_path)
    print(f"\nReport written to {out_path}")
    return 0


if __name__ == "__main__":
    try:
        rc = asyncio.run(main())
    except KeyboardInterrupt:
        rc = 130
    sys.exit(rc)

