#!/usr/bin/env python3
"""
Debug Script: Chart Command Generation and Agent Response Issues

This script helps debug:
1. Why charts don't switch when querying different symbols
2. Why "What is PLTR" gives trading info instead of company info
3. Chart command generation and execution flow
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_chart_commands.log')
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def test_query(session: aiohttp.ClientSession, query: str) -> Dict[str, Any]:
    """Test a single query and analyze the response."""
    logger.info(f"\n{'='*60}")
    logger.info(f"TESTING QUERY: {query}")
    logger.info(f"{'='*60}")
    
    try:
        # Make the request
        async with session.post(
            f"{BASE_URL}/api/agent/orchestrate",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Log the full response
            logger.debug(f"Full Response: {json.dumps(data, indent=2)[:500]}...")
            
            # Analyze key components
            analysis = {
                "query": query,
                "has_text": bool(data.get("text")),
                "text_preview": (data.get("text", "")[:100] + "...") if data.get("text") else "No text",
                "chart_commands": data.get("chart_commands", []),
                "chart_commands_in_data": data.get("data", {}).get("chart_commands", []),
                "tools_used": data.get("tools_used", []),
                "intent": data.get("intent", "unknown"),
                "model": data.get("model", "unknown"),
                "cached": data.get("cached", False)
            }
            
            # Check if symbol is mentioned in response but chart command missing
            response_text = data.get("text", "").upper()
            detected_symbols = []
            for symbol in ["PLTR", "TSLA", "AAPL", "NVDA", "MSFT"]:
                if symbol in response_text:
                    detected_symbols.append(symbol)
            
            analysis["symbols_in_text"] = detected_symbols
            
            # Check for chart command generation
            has_load_command = any(
                cmd.startswith("LOAD:") 
                for cmd in analysis["chart_commands"] + analysis["chart_commands_in_data"]
            )
            analysis["has_load_command"] = has_load_command
            
            # Log analysis
            logger.info(f"Analysis Results:")
            for key, value in analysis.items():
                logger.info(f"  {key}: {value}")
            
            # Warnings
            if detected_symbols and not has_load_command:
                logger.warning(f"⚠️ Symbol(s) {detected_symbols} mentioned but NO chart LOAD command!")
            
            if not analysis["chart_commands"] and not analysis["chart_commands_in_data"]:
                logger.warning(f"⚠️ No chart commands generated at all!")
            
            return analysis
            
    except Exception as e:
        logger.error(f"Error testing query: {e}")
        return {"error": str(e)}

async def test_diagnostics(session: aiohttp.ClientSession):
    """Get diagnostics information."""
    try:
        async with session.get(f"{BASE_URL}/api/agent/diag") as response:
            response.raise_for_status()
            data = await response.json()
            
            # Extract relevant diagnostics
            orch_diag = data.get("orchestrator", {})
            last_diag = orch_diag.get("last_diag", {})
            
            logger.info(f"\nDiagnostics:")
            logger.info(f"  Model: {orch_diag.get('model')}")
            logger.info(f"  Last Query Path: {last_diag.get('path')}")
            logger.info(f"  Last Query Intent: {last_diag.get('intent')}")
            logger.info(f"  Last Tools Used: {last_diag.get('tools_used')}")
            logger.info(f"  Last Duration: {last_diag.get('durations', {}).get('total')}s")
            
            return last_diag
    except Exception as e:
        logger.error(f"Error getting diagnostics: {e}")
        return {}

async def main():
    """Run comprehensive debugging tests."""
    
    # Test queries that should trigger chart changes
    test_queries = [
        # Basic symbol queries
        "What is PLTR?",
        "PLTR",
        "Show PLTR",
        "Tell me about PLTR",
        
        # Chart-specific queries
        "Show PLTR chart",
        "Display NVDA chart",
        "Load TSLA chart",
        
        # Price queries
        "PLTR price",
        "What is PLTR trading at?",
        "How much is PLTR?",
        
        # Technical analysis
        "PLTR technical analysis",
        "Show support and resistance for PLTR",
        
        # Mixed queries
        "What is PLTR and show me the chart",
        "Tell me about Palantir and its price",
    ]
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Test health
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                health = await response.json()
                logger.info(f"Backend Health: {health.get('status')}")
        except Exception as e:
            logger.error(f"Backend not reachable: {e}")
            return
        
        # Run all test queries
        results = []
        for query in test_queries:
            result = await test_query(session, query)
            results.append(result)
            
            # Get diagnostics after each query
            await test_diagnostics(session)
            
            # Small delay between queries
            await asyncio.sleep(0.5)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*60}")
        
        # Count issues
        no_chart_cmd = sum(1 for r in results if not r.get("has_load_command"))
        symbol_mismatch = sum(1 for r in results if r.get("symbols_in_text") and not r.get("has_load_command"))
        
        logger.info(f"Total queries tested: {len(results)}")
        logger.info(f"Queries missing chart commands: {no_chart_cmd}")
        logger.info(f"Queries with symbol but no chart switch: {symbol_mismatch}")
        
        # Detailed summary
        logger.info(f"\nDetailed Results:")
        for r in results:
            status = "✅" if r.get("has_load_command") else "❌"
            logger.info(f"{status} {r.get('query', 'Unknown')}")
            if r.get("chart_commands"):
                logger.info(f"   Commands: {r['chart_commands']}")
            if r.get("symbols_in_text"):
                logger.info(f"   Symbols mentioned: {r['symbols_in_text']}")
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_count": len(results),
            "issues_found": {
                "no_chart_commands": no_chart_cmd,
                "symbol_without_chart_switch": symbol_mismatch
            },
            "detailed_results": results
        }
        
        # Save report
        with open("chart_command_debug_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\nReport saved to chart_command_debug_report.json")
        logger.info(f"Log saved to debug_chart_commands.log")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)