"""
Computer Use Verification Service
=================================
Proper Computer Use integration using OpenAI Responses API (computer-use-preview)
and Playwright (Python) to execute actions and capture screenshots.
"""

import os
import json
import base64
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import yaml
from openai import AsyncOpenAI
from openai.types.responses import Response

try:
    from playwright.async_api import async_playwright, Page
except Exception:  # pragma: no cover
    async_playwright = None
    Page = Any


logger = logging.getLogger(__name__)


@dataclass
class ComputerUseConfig:
    display_width: int = 1280
    display_height: int = 800
    headless: bool = True
    slow_mo_ms: int = 0


class BrowserController:
    def __init__(self, cfg: ComputerUseConfig):
        self.cfg = cfg
        self._p = None
        self._browser = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        if async_playwright is None:
            raise RuntimeError("Playwright is not installed. Run: pip install playwright && playwright install chromium")
        self._p = await async_playwright().start()
        self._browser = await self._p.chromium.launch(headless=self.cfg.headless, slow_mo=self.cfg.slow_mo_ms)
        ctx = await self._browser.new_context(viewport={"width": self.cfg.display_width, "height": self.cfg.display_height})
        self.page = await ctx.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if self._browser:
                await self._browser.close()
        finally:
            if self._p:
                await self._p.stop()

    async def goto(self, url: str):
        assert self.page is not None
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(500)

    async def screenshot(self) -> bytes:
        assert self.page is not None
        return await self.page.screenshot(full_page=True)

    async def execute_action(self, action: Dict[str, Any]):
        assert self.page is not None
        a_type = (action.get("action") or action.get("type") or "").lower()
        x = action.get("x") or (action.get("position") or {}).get("x")
        y = action.get("y") or (action.get("position") or {}).get("y")

        if a_type in ("mousemove", "mouse_move", "move") and x is not None and y is not None:
            await self.page.mouse.move(float(x), float(y))
            return
        if a_type in ("click",):
            button = (action.get("button") or "left").lower()
            await self.page.mouse.click(float(x or 0), float(y or 0), button=button)
            return
        if a_type in ("double_click", "dblclick"):
            await self.page.mouse.dblclick(float(x or 0), float(y or 0))
            return
        if a_type in ("scroll", "wheel"):
            dx = float(action.get("delta_x", action.get("dx", 0)) or 0)
            dy = float(action.get("delta_y", action.get("dy", 0)) or 0)
            # If scroll_y is provided, use it for vertical scrolling
            scroll_y = action.get("scroll_y", 0)
            if scroll_y:
                await self.page.evaluate(f"window.scrollBy(0, {scroll_y})")
            else:
                await self.page.mouse.wheel(dx, dy)
            return
        if a_type in ("type",):
            text = action.get("text", "")
            if text:
                await self.page.keyboard.type(str(text))
            return
        if a_type in ("key", "keypress", "press"):
            key = action.get("key", "Enter")
            await self.page.keyboard.press(str(key))
            return
        if a_type in ("wait",):
            # Wait action - pause for 2 seconds
            await self.page.wait_for_timeout(2000)
            return
        if a_type in ("drag",):
            # Drag action - move from start to end position
            start_x = action.get("start_x", x)
            start_y = action.get("start_y", y)
            end_x = action.get("end_x", x)
            end_y = action.get("end_y", y)
            if start_x and start_y and end_x and end_y:
                await self.page.mouse.move(float(start_x), float(start_y))
                await self.page.mouse.down()
                await self.page.mouse.move(float(end_x), float(end_y))
                await self.page.mouse.up()
            return
        if a_type in ("screenshot",):
            # Screenshot action - already handled by the loop
            return
        # Fallback
        txt = action.get("text")
        if isinstance(txt, str) and txt:
            await self.page.keyboard.type(txt)
            return
        logger.info(f"Unhandled action schema: {action}")


class ComputerUseVerifier:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tunnel_url = os.getenv("TUNNEL_URL", "http://localhost:5174")
        self.use_computer_use = os.getenv("USE_COMPUTER_USE", "false").lower() == "true"
        self.reports_dir = Path(__file__).parent.parent / "verification_reports"
        self.reports_dir.mkdir(exist_ok=True)

        self.session_id: Optional[str] = None
        self.cfg = ComputerUseConfig(
            display_width=int(os.getenv("COMPUTER_USE_WIDTH", "1280")),
            display_height=int(os.getenv("COMPUTER_USE_HEIGHT", "800")),
            headless=os.getenv("COMPUTER_USE_HEADLESS", "true").lower() == "true",
            slow_mo_ms=int(os.getenv("COMPUTER_USE_SLOWMO_MS", "0")),
        )

    async def create_verification_agent(self) -> str:
        if not self.use_computer_use:
            raise ValueError("Computer Use is not enabled. Set USE_COMPUTER_USE=true")
        import uuid
        self.session_id = str(uuid.uuid4())
        logger.info(f"Created verification session: {self.session_id}")
        return self.session_id

    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session_id:
            await self.create_verification_agent()

        try:
            prompt = self._build_verification_prompt(scenario)
            results = {
                "scenario": scenario["name"],
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "steps": [],
                "screenshots": [],
                "issues": [],
                "fixes": []
            }

            async with BrowserController(self.cfg) as browser:
                await browser.goto(self.tunnel_url)
                # Ensure the right Voice Assistant panel input is focused to guide the model
                await self._focus_voice_input(browser)
                initial_b64 = base64.b64encode(await browser.screenshot()).decode("utf-8")

                response = await self._responses_create(prompt, initial_b64)
                response = await self._handle_required_actions(browser, response, results)

                try:
                    text = getattr(response, "output_text", None)
                    if text:
                        results["steps"].append({
                            "type": "message",
                            "content": text[:1000],
                            "timestamp": datetime.now().isoformat(),
                        })
                except Exception:
                    pass

                results["status"] = "completed"
                await self._save_report(results)
                return results

        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            return {
                "scenario": scenario["name"],
                "status": "failed",
                "error": str(e)
            }

    async def run_all_scenarios(self, scenarios_file: Optional[str] = None) -> List[Dict[str, Any]]:
        if scenarios_file:
            scenarios = self._load_scenarios(scenarios_file)
        else:
            scenarios = self._get_default_scenarios()

        results = []
        for scenario in scenarios:
            logger.info(f"Running scenario: {scenario['name']}")
            result = await self.run_scenario(scenario)
            results.append(result)
            await asyncio.sleep(2)

        summary = self._generate_summary(results)
        await self._save_summary(summary)
        return results

    def _build_verification_prompt(self, scenario: Dict[str, Any]) -> str:
        steps = scenario.get("steps", [])
        
        # Add trader persona context if scenario is trading-related
        is_trading_scenario = any(keyword in scenario.get('name', '').lower() 
                                  for keyword in ['trade', 'market', 'stock', 'option', 'technical', 'ltb', 'chart'])
        
        if is_trading_scenario:
            persona_context = """You are G'sves, a senior portfolio manager with over 30 years of experience at top investment firms.
Your expertise includes inter-day option trading, swing option trading, technical analysis, and risk management.
You were trained under Warren Buffett, Paul Tudor Jones, Ray Dalio, and George Soros.

As you test this trading dashboard, approach it as you would your morning routine:
- Check pre-market movements and overnight changes
- Verify technical levels (Load the Boat (LTB), Swing Trade (ST), Quick Entry (QE))
- Validate moving averages, RSI, volume trends, and Fibonacci retracements
- Assess risk-reward ratios for potential trades
- Look for strong news catalysts and market-moving events

Remember: A professional trader needs accurate, real-time data and reliable technical analysis tools.
"""
        else:
            persona_context = ""
        
        prompt = f"""{persona_context}Please verify the following scenario: {scenario['name']}

1. Open {self.tunnel_url} in your browser
2. Wait for the app to load completely
3. Use the RIGHT sidebar labeled "VOICE ASSISTANT". The text input is at the bottom with class "voice-text-input" and placeholder "Type a message...". Do NOT use any left-side panels.
4. Take a screenshot labeled "initial-state.png"

Test Steps:
"""
        for i, step in enumerate(steps, 1):
            prompt += f"\n{i}. {step['action']}"
            if "expected" in step:
                prompt += f"\n   Expected: {step['expected']}"
            prompt += f"\n   Take screenshot: step-{i}.png"

        prompt += """

After completing all steps:
1. Compare actual behavior with expected
2. List any issues found with specific details
3. For each issue, suggest a fix with:
   - File path (e.g., backend/services/agent_orchestrator.py)
   - Line number or function name
   - Specific code change needed

Provide a final summary with:
- Pass/Fail status for each step
- Overall test result
- Priority of issues found (Critical/High/Medium/Low)
"""
        
        # Add trader-specific evaluation criteria
        if is_trading_scenario:
            prompt += """
As a seasoned trader, also evaluate:
- Data accuracy and timeliness
- Technical indicator reliability
- Chart responsiveness and clarity
- Risk management tool effectiveness
- News feed relevance and speed
"""
        
        return prompt

    async def _focus_voice_input(self, browser: "BrowserController") -> None:
        """Focus the text input in the Voice Assistant (right panel) to provide context to the model."""
        try:
            page = browser.page
            assert page is not None
            locator = page.locator('input.voice-text-input')
            if await locator.count() == 0:
                locator = page.locator('input[placeholder*="Type a message"]')
            if await locator.count() > 0:
                await locator.first.click()
                await page.wait_for_timeout(150)
                logger.info("Focused Voice Assistant input (right panel)")
            else:
                logger.warning("Voice Assistant input not found")
        except Exception as exc:
            logger.warning(f"Failed to focus voice input: {exc}")

    async def _responses_create(self, prompt: str, initial_screenshot_b64: Optional[str]) -> Response:
        content: List[Dict[str, Any]] = [{"type": "input_text", "text": prompt}]
        if initial_screenshot_b64:
            content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{initial_screenshot_b64}",
            })
        params = {
            "model": "computer-use-preview",
            "input": [
                {"role": "user", "content": content}
            ],
            "tools": [
                {
                    "type": "computer_use_preview",
                    "display_width": self.cfg.display_width,
                    "display_height": self.cfg.display_height,
                    "environment": "browser"
                }
            ],
            "max_output_tokens": 400,
            "truncation": "auto"
        }
        responses_client = getattr(self.client, "responses", None)
        if responses_client is None:
            raise RuntimeError("OpenAI SDK version does not expose Responses API")
        return await responses_client.create(**params)

    async def _handle_required_actions(self, browser: BrowserController, response: Response, results: Dict[str, Any]) -> Response:
        """Handle Computer Use responses by executing computer_call actions."""
        responses_client = getattr(self.client, "responses", None)
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}: Checking for computer_call actions")
            
            # Check for computer_call items in the output
            computer_calls = []
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'computer_call':
                        computer_calls.append(item)
                        logger.info(f"Found computer_call: {item}")
            
            # If no computer_call actions, we're done
            if not computer_calls:
                logger.info("No more computer_call actions, completing")
                # Extract any text output for the results
                if hasattr(response, 'output'):
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'text':
                            results["steps"].append({
                                "type": "final_message",
                                "content": str(item.text) if hasattr(item, 'text') else str(item),
                                "timestamp": datetime.now().isoformat(),
                            })
                return response
            
            # Execute each computer_call individually and respond with a screenshot per call
            for call in computer_calls:
                logger.info(f"Executing computer_call: {call}")

                # Extract action dict from the call
                action_dict: Dict[str, Any] = {}
                try:
                    action = getattr(call, 'action', None)
                    if action is None and isinstance(call, dict):
                        action = call.get('action')
                    if hasattr(action, '__dict__'):
                        # Convert dataclass-like to dict
                        for k in ('type', 'x', 'y', 'text', 'key', 'scroll_y'):
                            if hasattr(action, k):
                                action_dict[k] = getattr(action, k)
                    elif isinstance(action, dict):
                        action_dict = action
                except Exception as ex:
                    logger.warning(f"Could not parse action from computer_call: {ex}")

                # Execute action
                try:
                    if action_dict:
                        logger.info(f"Executing action: {action_dict}")
                        await browser.execute_action(action_dict)
                        await browser.page.wait_for_timeout(800)
                        results["steps"].append({
                            "type": "action",
                            "action": action_dict,
                            "timestamp": datetime.now().isoformat(),
                        })
                except Exception as ex:
                    logger.warning(f"Failed to execute action {action_dict}: {ex}")
                    results["issues"].append({
                        "type": "action_error",
                        "action": action_dict,
                        "error": str(ex),
                        "timestamp": datetime.now().isoformat(),
                    })

                # Take a screenshot after this action
                shot_b64 = base64.b64encode(await browser.screenshot()).decode("utf-8")
                results["screenshots"].append({
                    "name": f"{datetime.now().strftime('%H%M%S')}_{len(results['screenshots'])}.png",
                    "timestamp": datetime.now().isoformat(),
                    "file": "embedded",
                })

                # Identify call_id and send computer_call_output for THIS call
                call_id = getattr(call, 'call_id', None)
                if call_id is None and isinstance(call, dict):
                    call_id = call.get('call_id') or call.get('id')
                logger.info(f"Sending computer_call_output for call_id: {call_id}")
                response = await responses_client.create(
                    model="computer-use-preview",
                    previous_response_id=response.id,
                    tools=[{
                        "type": "computer_use_preview",
                        "display_width": self.cfg.display_width,
                        "display_height": self.cfg.display_height,
                        "environment": "browser"
                    }],
                    input=[{
                        "call_id": call_id,
                        "type": "computer_call_output",
                        "output": {
                            "type": "computer_screenshot",
                            "image_url": f"data:image/png;base64,{shot_b64}"
                        },
                        "current_url": browser.page.url if browser.page else "unknown"
                    }],
                    truncation="auto"
                )
        
        logger.warning(f"Reached max iterations ({max_iterations})")
        return response

    def _get_default_scenarios(self) -> List[Dict[str, Any]]:
        return [
            # Original basic scenarios
            {
                "name": "Company Information Query",
                "description": "Verify that asking about a company returns company info, not just price",
                "steps": [
                    {"action": "Find the Voice Assistant panel on the RIGHT side of the screen and click the text input field at the bottom", "expected": "Input field should be focused"},
                    {"action": "Type 'What is PLTR?' in the input field and press Enter", "expected": "Response should explain Palantir Technologies is a data analytics company"},
                    {"action": "Check if the chart switched to PLTR", "expected": "Chart header should show PLTR symbol"}
                ],
            },
            {
                "name": "Chart Synchronization",
                "description": "Verify chart switches when discussing different symbols",
                "steps": [
                    {"action": "In the Voice Assistant panel (right side), type 'Show me Microsoft' and press Enter", "expected": "Chart should switch to MSFT"},
                    {"action": "Verify chart header shows MSFT", "expected": "Symbol MSFT should be visible"}
                ],
            },
            
            # Trader-specific scenarios
            {
                "name": "Trader Morning Market Brief",
                "description": "Test G'sves' morning routine - checking overnight movers and pre-market",
                "steps": [
                    {"action": "Click on the text input field in the Voice Assistant panel (right side) and type 'Good morning', then press Enter", "expected": "Should trigger market brief with biggest gainers/losers"},
                    {"action": "Verify pre-market data is shown", "expected": "Should include S&P 500 and Nasdaq overnight changes"},
                    {"action": "Check for economic catalysts mentioned", "expected": "Should highlight any major news or events"}
                ],
            },
            {
                "name": "Trading Levels Analysis (LTB, ST, QE)",
                "description": "Verify technical levels are properly identified and displayed",
                "steps": [
                    {"action": "In the Voice Assistant input (right panel), type 'Show me the LTB levels for NVDA' and press Enter", "expected": "Should display Load the Boat entry level based on 200-day MA"},
                    {"action": "Verify technical indicators on chart", "expected": "Should see moving averages and support levels"},
                    {"action": "Type 'What are the ST and QE levels?' in the Voice Assistant input and press Enter", "expected": "Should show Swing Trade and Quick Entry levels with rationale"}
                ],
            },
            {
                "name": "Options Trading Setup",
                "description": "Test options recommendation workflow as a seasoned trader would",
                "steps": [
                    {"action": "Using the Voice Assistant input (right side), type 'Suggest weekly options for TSLA' and press Enter", "expected": "Should provide strike prices and expiration dates"},
                    {"action": "Check for Greeks analysis", "expected": "Should mention IV, Delta, Theta"},
                    {"action": "Verify risk/reward ratio is provided", "expected": "Should include stop-loss and profit targets"}
                ],
            },
            {
                "name": "Technical Confluence Validation",
                "description": "Verify multiple technical indicators align properly",
                "steps": [
                    {"action": "Type 'Show me technical confluence for SPY' and submit", "expected": "Should analyze multiple indicators"},
                    {"action": "Check RSI indicator on chart", "expected": "Should display overbought/oversold levels"},
                    {"action": "Verify Fibonacci retracements", "expected": "Should show key retracement levels (38.2%, 50%, 61.8%)"},
                    {"action": "Check volume analysis", "expected": "Should correlate volume with price movements"}
                ],
            },
            {
                "name": "Risk Management Assessment",
                "description": "Test risk management features critical for professional trading",
                "steps": [
                    {"action": "Type 'What's my position size for a $10k account on AAPL?' and submit", "expected": "Should calculate proper position sizing"},
                    {"action": "Ask 'Where should I place my stop-loss?'", "expected": "Should suggest stop based on technical levels"},
                    {"action": "Verify risk/reward calculation", "expected": "Should show at least 2:1 risk/reward ratio"}
                ],
            },
            {
                "name": "News Catalyst Analysis",
                "description": "Verify news integration for trading decisions",
                "steps": [
                    {"action": "Type 'Show me stocks with strong news catalysts' and submit", "expected": "Should display stocks with recent positive news"},
                    {"action": "Click on a news item in the feed", "expected": "News should expand with full details"},
                    {"action": "Ask 'How does this news affect the stock?'", "expected": "Should provide market impact analysis"}
                ],
            },
            {
                "name": "Watchlist Management",
                "description": "Test professional watchlist features",
                "steps": [
                    {"action": "Add PLTR to the watchlist using the search box", "expected": "PLTR should appear in Market Insights panel"},
                    {"action": "Remove SPY from the watchlist", "expected": "SPY should be removed but at least one stock remains"},
                    {"action": "Type 'Generate my daily watchlist' and submit", "expected": "Should suggest stocks based on technical setups and catalysts"}
                ],
            },
            {
                "name": "Multi-Timeframe Analysis",
                "description": "Verify chart timeframe switching for swing vs day trading",
                "steps": [
                    {"action": "Type 'Show me the daily chart for QQQ' and submit", "expected": "Chart should switch to daily timeframe"},
                    {"action": "Type 'Now show the 15-minute chart' and submit", "expected": "Chart should switch to 15-minute candles"},
                    {"action": "Compare support levels between timeframes", "expected": "Should maintain consistent major support/resistance levels"}
                ],
            }
        ]

    def _load_scenarios(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)["scenarios"]
        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")
            return self._get_default_scenarios()

    async def _save_report(self, results: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_name = results["scenario"].replace(" ", "_").lower()
        report_file = self.reports_dir / f"{scenario_name}_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Report saved: {report_file}")

    async def _save_summary(self, summary: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.reports_dir / f"summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved: {summary_file}")

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "completed" and not r.get("issues"))
        failed = total - passed
        all_issues: List[Dict[str, Any]] = []
        all_fixes: List[Dict[str, Any]] = []
        for result in results:
            all_issues.extend(result.get("issues", []))
            all_fixes.extend(result.get("fixes", []))
        return {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "0%",
            "critical_issues": [i for i in all_issues if i.get("priority") == "Critical"],
            "high_priority_fixes": [f for f in all_fixes if f.get("priority") in ["Critical", "High"]],
            "scenarios": [
                {
                    "name": r["scenario"],
                    "status": r["status"],
                    "issues_count": len(r.get("issues", [])),
                    "has_screenshots": len(r.get("screenshots", [])) > 0
                }
                for r in results
            ]
        }


_verifier_instance: Optional[ComputerUseVerifier] = None

def get_verifier() -> ComputerUseVerifier:
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = ComputerUseVerifier()
    return _verifier_instance
