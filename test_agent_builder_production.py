import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import httpx
from playwright.async_api import async_playwright


@dataclass
class EndpointResult:
    name: str
    url: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)


class AgentBuilderProductionTest:
    def __init__(self) -> None:
        self.base_url = "https://gvses-market-insights.fly.dev"
        self.frontend_url = self.base_url
        self.session_endpoint = f"{self.base_url}/api/chatkit/session"
        self.chart_endpoints = {
            "change_symbol": f"{self.base_url}/api/chart/change-symbol",
            "set_timeframe": f"{self.base_url}/api/chart/set-timeframe",
            "toggle_indicator": f"{self.base_url}/api/chart/toggle-indicator",
            "capture_snapshot": f"{self.base_url}/api/chart/capture-snapshot",
        }
        self.test_output_dir = Path("production_test_artifacts")
        self.test_output_dir.mkdir(exist_ok=True)
        self.api_results: List[EndpointResult] = []

    async def validate_frontend(self) -> Dict[str, Any]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()
            metrics: Dict[str, Any] = {"url": self.frontend_url}

            try:
                start = time.perf_counter()
                await page.goto(self.frontend_url, wait_until="networkidle", timeout=45000)
                metrics["load_time_s"] = round(time.perf_counter() - start, 2)

                selectors = [
                    "text=GVSES",  # App title visible in production
                    "text=Chart Control",  # Correct tab name in production
                    ".trading-chart",  # Chart container class
                    "canvas",  # Chart canvas element
                ]

                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=8000)
                        metrics.setdefault("selectors_found", []).append(selector)
                    except Exception:
                        metrics.setdefault("selectors_missing", []).append(selector)

                screenshot_path = self.test_output_dir / "production_dashboard.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                metrics["screenshot"] = str(screenshot_path)
            finally:
                await context.close()
                await browser.close()

        return metrics

    async def validate_api(self) -> List[EndpointResult]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "workflow_id": "wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736",
                "user_id": "production-test-user",
            }

            try:
                response = await client.post(self.session_endpoint, json=payload)
                status = "success" if response.status_code == 200 else "failure"
                details = {"status_code": response.status_code, "body": response.text[:500]}
            except Exception as exc:
                status = "error"
                details = {"error": str(exc)}

            self.api_results.append(
                EndpointResult(name="chatkit_session", url=self.session_endpoint, status=status, details=details)
            )

            for name, url in self.chart_endpoints.items():
                sample_payload: Dict[str, Any]
                if name == "change_symbol":
                    sample_payload = {"symbol": "TSLA"}
                elif name == "set_timeframe":
                    sample_payload = {"timeframe": "1h"}
                elif name == "toggle_indicator":
                    sample_payload = {"indicator": "ema", "enabled": True, "period": 21}
                else:
                    sample_payload = {"include_data": False}

                try:
                    response = await client.post(url, json=sample_payload)
                    status = "success" if response.status_code == 200 else "failure"
                    details = {"status_code": response.status_code, "body": response.text[:500]}
                except Exception as exc:
                    status = "error"
                    details = {"error": str(exc)}

                self.api_results.append(
                    EndpointResult(name=name, url=url, status=status, details=details)
                )

        return self.api_results

    async def run_workflow_simulation(self) -> Dict[str, Any]:
        workflow_report: Dict[str, Any] = {
            "session_endpoint": self.session_endpoint,
            "chart_endpoints": list(self.chart_endpoints.keys()),
            "status": "pending",
        }

        try:
            session_result = next((r for r in self.api_results if r.name == "chatkit_session"), None)
            chart_results = [r for r in self.api_results if r.name != "chatkit_session"]

            success = session_result and session_result.status == "success"
            success = success and all(r.status == "success" for r in chart_results)

            workflow_report["status"] = "success" if success else "incomplete"
            workflow_report["details"] = {
                "session": session_result.details if session_result else {},
                "chart": [{"name": r.name, "status": r.status, "details": r.details} for r in chart_results],
            }
        except Exception as exc:
            workflow_report["status"] = "error"
            workflow_report["details"] = {"error": str(exc)}

        return workflow_report

    async def run(self) -> Dict[str, Any]:
        frontend_metrics = await self.validate_frontend()
        await self.validate_api()
        workflow_report = await self.run_workflow_simulation()

        summary = {
            "frontend": frontend_metrics,
            "api": [result.__dict__ for result in self.api_results],
            "workflow": workflow_report,
            "timestamp": time.time(),
        }

        report_path = self.test_output_dir / "production_test_report.json"
        report_path.write_text(json.dumps(summary, indent=2))

        return summary


async def main() -> None:
    tester = AgentBuilderProductionTest()
    results = await tester.run()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
