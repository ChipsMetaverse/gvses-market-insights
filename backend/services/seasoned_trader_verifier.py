"""
Seasoned Trader Computer Use Verifier
=====================================
Specialized Computer Use testing with G'sves trader persona.
Tests the application as a senior portfolio manager would.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .computer_use_verifier import ComputerUseVerifier, ComputerUseConfig

logger = logging.getLogger(__name__)


class SeasonedTraderVerifier(ComputerUseVerifier):
    """Extends ComputerUseVerifier with trader-specific behaviors and scenarios."""
    
    def __init__(self):
        super().__init__()
        self.trader_name = "G'sves"
        self.trading_experience = "30+ years at top investment firms"
        self.specialties = [
            "inter-day option trading",
            "swing option trading", 
            "options scalping",
            "technical analysis",
            "risk management"
        ]
    
    def _build_verification_prompt(self, scenario: Dict[str, Any]) -> str:
        """Override to always include trader persona for all scenarios."""
        steps = scenario.get("steps", [])
        
        # Always include trader persona for this specialized verifier
        persona_context = f"""You are {self.trader_name}, a senior portfolio manager with {self.trading_experience}.
Your expertise includes {', '.join(self.specialties)}.
You were trained under Warren Buffett, Paul Tudor Jones, Ray Dalio, and George Soros.

As you test this trading dashboard, approach it with your decades of experience:
- Start with "Good morning" to trigger your market brief routine
- Check pre-market movements and overnight changes systematically
- Verify technical levels (Load the Boat (LTB), Swing Trade (ST), Quick Entry (QE))
- Validate moving averages, RSI, volume trends, and Fibonacci retracements
- Assess risk-reward ratios for every potential trade
- Look for strong news catalysts and market-moving events
- Apply proper position sizing and stop-loss placement

Remember: You've seen market crashes and rallies. You know that discipline, not emotion, drives success.
A professional trader needs accurate, real-time data and reliable technical analysis tools.
"""
        
        prompt = f"""{persona_context}

Testing Scenario: {scenario['name']}

Approach this test as you would in your real trading workflow. Use your experience to identify any issues that would prevent you from making informed trading decisions.

1. Open {self.tunnel_url} in your browser
2. Wait for the app to load completely  
3. Take a screenshot labeled "initial-state.png"

Test Steps (execute as a professional trader would):
"""
        for i, step in enumerate(steps, 1):
            prompt += f"\n{i}. {step['action']}"
            if "expected" in step:
                prompt += f"\n   Expected: {step['expected']}"
            prompt += f"\n   Take screenshot: step-{i}.png"
            prompt += f"\n   As a trader, verify this meets professional standards"

        prompt += """

After completing all steps, provide your professional assessment:

1. Trading Functionality Assessment:
   - Can you execute your morning routine effectively?
   - Are the technical indicators accurate and timely?
   - Does the platform support your risk management needs?
   - Are the charts responsive and clear for quick decisions?

2. Data Quality Evaluation:
   - Is market data real-time or delayed?
   - Are price quotes accurate?
   - Do technical levels match your calculations?
   - Is news feed relevant and timely?

3. Critical Issues for Trading:
   - Any delays that would impact trade execution?
   - Missing indicators or tools you rely on?
   - UI/UX issues that slow down decision-making?
   - Data accuracy problems that could lead to losses?

4. Professional Recommendations:
   Priority fixes from a trader's perspective (Critical/High/Medium/Low)
   
5. Would you trade with this platform?
   Give your verdict as a senior portfolio manager.
"""
        
        return prompt
    
    def get_trader_scenarios(self) -> List[Dict[str, Any]]:
        """Return trader-specific test scenarios."""
        return [
            {
                "name": "G'sves Morning Routine",
                "description": "Complete morning workflow as senior portfolio manager",
                "steps": [
                    {"action": "Start with 'Good morning' greeting", "expected": "Market brief with overnight movers"},
                    {"action": "Check SPY, QQQ, and DIA pre-market levels", "expected": "See index futures and pre-market changes"},
                    {"action": "Review your watchlist stocks", "expected": "Quick scan of key positions"},
                    {"action": "Ask 'Show me the biggest movers'", "expected": "Top gainers and losers display"},
                    {"action": "Check VIX levels for market sentiment", "expected": "Volatility index displayed"},
                    {"action": "Ask for economic calendar events", "expected": "Today's key economic releases"}
                ],
            },
            {
                "name": "LTB Entry Point Analysis",
                "description": "Find Load the Boat entry points using technical confluence",
                "steps": [
                    {"action": "Ask 'What stocks are near LTB levels?'", "expected": "List of stocks near strong support"},
                    {"action": "Pick one stock and ask for detailed LTB analysis", "expected": "200-day MA alignment, 61.8% Fibonacci"},
                    {"action": "Verify the chart shows these levels", "expected": "Visual confirmation on chart"},
                    {"action": "Ask for volume analysis at these levels", "expected": "Volume profile and accumulation zones"},
                    {"action": "Calculate position size for $100k portfolio", "expected": "Proper 2% risk calculation"},
                    {"action": "Set stop-loss below LTB level", "expected": "Risk management parameters defined"}
                ],
            },
            {
                "name": "Options Strategy Setup",
                "description": "Weekly options trade setup with full Greeks analysis",
                "steps": [
                    {"action": "Ask 'Suggest weekly options for high IV stocks'", "expected": "Stocks with elevated implied volatility"},
                    {"action": "Select TSLA and ask for options chain", "expected": "Strike prices with Greeks displayed"},
                    {"action": "Ask for Delta-neutral strategy", "expected": "Balanced options positions suggested"},
                    {"action": "Check Theta decay impact", "expected": "Time decay analysis for weeklies"},
                    {"action": "Verify IV percentile", "expected": "Current IV vs historical range"},
                    {"action": "Calculate max profit/loss scenarios", "expected": "Risk graph or P&L calculations"}
                ],
            },
            {
                "name": "Swing Trade Setup Validation",
                "description": "Identify and validate swing trade opportunities",
                "steps": [
                    {"action": "Ask 'Show me stocks at ST levels'", "expected": "Stocks near 50-day MA or consolidation"},
                    {"action": "Pick NVDA and ask for swing trade setup", "expected": "Entry, target, stop defined"},
                    {"action": "Verify RSI is not overbought", "expected": "RSI below 70, ideally 40-60"},
                    {"action": "Check for bullish divergence", "expected": "Price vs momentum divergence analysis"},
                    {"action": "Ask for 3-day expected move", "expected": "ATR-based price projection"},
                    {"action": "Confirm risk/reward is at least 2:1", "expected": "Clear R:R calculation displayed"}
                ],
            },
            {
                "name": "News Catalyst Trading",
                "description": "Trade setup based on breaking news",
                "steps": [
                    {"action": "Ask 'What stocks have earnings today?'", "expected": "List of companies reporting"},
                    {"action": "Check for any FDA approvals or M&A news", "expected": "Market-moving catalysts identified"},
                    {"action": "Select a stock with positive catalyst", "expected": "Stock with bullish news selected"},
                    {"action": "Ask for pre-market volume analysis", "expected": "Unusual volume detection"},
                    {"action": "Check if stock is gapping up", "expected": "Gap analysis and fill probability"},
                    {"action": "Define gap-and-go trade setup", "expected": "Clear entry above opening range high"}
                ],
            },
            {
                "name": "Risk Management Validation",
                "description": "Ensure platform supports professional risk management",
                "steps": [
                    {"action": "Ask 'Calculate position size for 2% risk on AAPL'", "expected": "Proper position sizing math"},
                    {"action": "Set multiple alerts at key levels", "expected": "Price alerts at support/resistance"},
                    {"action": "Ask for correlation analysis with SPY", "expected": "Beta and correlation metrics"},
                    {"action": "Check max drawdown for current positions", "expected": "Portfolio risk metrics"},
                    {"action": "Verify trailing stop functionality", "expected": "Dynamic stop-loss capability"},
                    {"action": "Ask for Kelly Criterion suggestion", "expected": "Optimal position sizing calculation"}
                ],
            },
            {
                "name": "Multi-Timeframe Confluence Check",
                "description": "Validate signals across multiple timeframes",
                "steps": [
                    {"action": "Show daily chart for SPY", "expected": "Daily timeframe with clear trends"},
                    {"action": "Switch to 4-hour chart", "expected": "Intermediate timeframe analysis"},
                    {"action": "Switch to 15-minute for entry timing", "expected": "Precision entry timeframe"},
                    {"action": "Verify support levels align across timeframes", "expected": "Confluence of levels confirmed"},
                    {"action": "Check if moving averages stack bullishly", "expected": "MA alignment verification"},
                    {"action": "Ask 'Is this a valid breakout?'", "expected": "Multi-timeframe breakout confirmation"}
                ],
            },
            {
                "name": "End of Day Review",
                "description": "Professional trader's EOD routine",
                "steps": [
                    {"action": "Ask 'Show me today's P&L'", "expected": "Daily performance summary"},
                    {"action": "Review trades executed today", "expected": "Trade log with entries/exits"},
                    {"action": "Ask 'What mistakes did I make?'", "expected": "Trade analysis and improvements"},
                    {"action": "Check tomorrow's economic calendar", "expected": "Upcoming catalysts identified"},
                    {"action": "Set alerts for overnight levels", "expected": "Key levels monitored"},
                    {"action": "Ask for tomorrow's watchlist", "expected": "Next day preparation complete"}
                ],
            }
        ]
    
    async def run_morning_routine(self) -> Dict[str, Any]:
        """Run G'sves complete morning routine test."""
        morning_scenario = self.get_trader_scenarios()[0]  # G'sves Morning Routine
        logger.info(f"Starting {self.trader_name}'s morning routine verification")
        return await self.run_scenario(morning_scenario)
    
    async def run_trading_day_simulation(self) -> List[Dict[str, Any]]:
        """Run a full trading day simulation from morning to EOD."""
        trading_day_scenarios = [
            self.get_trader_scenarios()[0],  # Morning Routine
            self.get_trader_scenarios()[1],  # LTB Analysis
            self.get_trader_scenarios()[3],  # Swing Trade Setup
            self.get_trader_scenarios()[4],  # News Catalyst
            self.get_trader_scenarios()[7],  # End of Day Review
        ]
        
        results = []
        logger.info(f"Starting full trading day simulation for {self.trader_name}")
        
        for scenario in trading_day_scenarios:
            logger.info(f"Executing: {scenario['name']}")
            result = await self.run_scenario(scenario)
            results.append(result)
            # Brief pause between scenarios
            import asyncio
            await asyncio.sleep(3)
        
        # Generate trading day summary
        summary = self._generate_trading_day_summary(results)
        await self._save_summary(summary)
        
        return results
    
    def _generate_trading_day_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary from a trader's perspective."""
        total_scenarios = len(results)
        successful = sum(1 for r in results if r.get("status") == "completed" and not r.get("issues"))
        
        # Categorize issues by trading impact
        critical_for_trading = []
        high_impact = []
        medium_impact = []
        low_impact = []
        
        for result in results:
            for issue in result.get("issues", []):
                issue_text = str(issue)
                if any(keyword in issue_text.lower() for keyword in ["data", "price", "quote", "real-time", "delay"]):
                    critical_for_trading.append(issue)
                elif any(keyword in issue_text.lower() for keyword in ["chart", "indicator", "technical", "analysis"]):
                    high_impact.append(issue)
                elif any(keyword in issue_text.lower() for keyword in ["ui", "display", "visual"]):
                    medium_impact.append(issue)
                else:
                    low_impact.append(issue)
        
        return {
            "trader": self.trader_name,
            "experience": self.trading_experience,
            "test_date": datetime.now().isoformat(),
            "scenarios_run": total_scenarios,
            "successful_scenarios": successful,
            "success_rate": f"{(successful/total_scenarios)*100:.1f}%" if total_scenarios > 0 else "0%",
            "trading_impact_assessment": {
                "critical_for_trading": len(critical_for_trading),
                "high_impact": len(high_impact),
                "medium_impact": len(medium_impact),
                "low_impact": len(low_impact),
                "details": {
                    "critical_issues": critical_for_trading[:3],  # Top 3 critical issues
                    "high_priority_fixes": high_impact[:3]
                }
            },
            "platform_readiness": {
                "can_trade": len(critical_for_trading) == 0,
                "recommendation": "Ready for professional trading" if len(critical_for_trading) == 0 else "Fix critical issues before trading",
                "confidence_level": "High" if successful >= total_scenarios * 0.8 else "Medium" if successful >= total_scenarios * 0.5 else "Low"
            },
            "trader_verdict": self._get_trader_verdict(successful, total_scenarios, critical_for_trading)
        }
    
    def _get_trader_verdict(self, successful: int, total: int, critical_issues: List) -> str:
        """Get G'sves professional verdict on the platform."""
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        if critical_issues:
            return f"As {self.trader_name}, I cannot recommend this platform for professional trading until critical data and execution issues are resolved. My {self.trading_experience} tells me these issues could lead to significant losses."
        elif success_rate >= 90:
            return f"This platform meets my professional standards. After {self.trading_experience}, I can confidently execute my strategies here. The tools are reliable and data is accurate."
        elif success_rate >= 70:
            return f"The platform shows promise but needs refinement. With {self.trading_experience}, I've seen better but also worse. It's usable for swing trading but needs improvements for day trading."
        else:
            return f"This platform is not ready for professional trading. In my {self.trading_experience}, I've learned that unreliable tools lead to poor decisions. Significant improvements needed."


def get_seasoned_trader_verifier() -> SeasonedTraderVerifier:
    """Get or create the singleton SeasonedTraderVerifier instance."""
    return SeasonedTraderVerifier()