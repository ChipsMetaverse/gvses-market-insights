#!/usr/bin/env python3
"""
Computer Use Verification CLI Runner
=====================================
Standalone script to run UI verification tests using OpenAI Computer Use.

Usage:
    python run_computer_use_verification.py [options]
    
Options:
    --tunnel-url URL    Override default tunnel URL
    --scenarios NAMES   Comma-separated list of scenarios to run
    --config FILE       Path to scenarios YAML file
    --report-only ID    Just show report for existing session
    --quick             Run quick check only
"""

import asyncio
import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.computer_use_verifier import ComputerUseVerifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_scenario_result(result: dict):
    """Print formatted scenario result."""
    name = result.get("scenario", "Unknown")
    status = result.get("status", "unknown")
    
    # Determine status symbol
    if status == "completed" and not result.get("issues"):
        symbol = "✅"
        status_text = "PASSED"
    elif status == "completed":
        symbol = "⚠️"
        status_text = "ISSUES FOUND"
    elif status == "failed":
        symbol = "❌"
        status_text = "FAILED"
    else:
        symbol = "⏳"
        status_text = status.upper()
    
    print(f"\n{symbol} {name}: {status_text}")
    
    # Print issues if any
    if result.get("issues"):
        print("  Issues found:")
        for issue in result["issues"]:
            print(f"    - {issue}")
    
    # Print suggested fixes if any
    if result.get("fixes"):
        print("  Suggested fixes:")
        for fix in result["fixes"]:
            if isinstance(fix, dict):
                file = fix.get("file", "Unknown file")
                line = fix.get("line", "Unknown line")
                desc = fix.get("description", "No description")
                print(f"    - {file}:{line} - {desc}")
            else:
                print(f"    - {fix}")
    
    # Print screenshot info
    screenshots = result.get("screenshots", [])
    if screenshots:
        print(f"  Screenshots captured: {len(screenshots)}")


def print_summary(results: List[dict]):
    """Print summary of all results."""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "completed" and not r.get("issues"))
    failed = total - passed
    
    print_header("VERIFICATION SUMMARY")
    print(f"\nTotal Scenarios: {total}")
    print(f"Passed: {passed} ({(passed/total)*100:.1f}%)" if total > 0 else "Passed: 0")
    print(f"Failed: {failed}")
    
    # List critical issues
    critical_issues = []
    for result in results:
        for issue in result.get("issues", []):
            if isinstance(issue, dict) and issue.get("priority") == "Critical":
                critical_issues.append(issue)
    
    if critical_issues:
        print("\n⚠️  CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"  - {issue.get('description', issue)}")


async def run_verification(args):
    """Run verification scenarios."""
    print_header("COMPUTER USE VERIFICATION")
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        return 1
    
    if not os.getenv("USE_COMPUTER_USE", "").lower() == "true":
        print("⚠️  Warning: USE_COMPUTER_USE not set to 'true'")
        print("   Set USE_COMPUTER_USE=true to enable Computer Use")
        return 1
    
    tunnel_url = args.tunnel_url or os.getenv("TUNNEL_URL", "http://localhost:5174")
    print(f"\nTarget URL: {tunnel_url}")
    
    # Create verifier
    verifier = ComputerUseVerifier()
    if args.tunnel_url:
        verifier.tunnel_url = args.tunnel_url
    
    print("\n🤖 Creating verification agent...")
    
    try:
        # Run scenarios
        if args.quick:
            print("\nRunning quick verification check...")
            scenarios = [
                {
                    "name": "Quick Company Info Check",
                    "steps": [
                        {"action": "Query 'What is PLTR?'", "expected": "Company description"}
                    ]
                },
                {
                    "name": "Quick Chart Sync Check",
                    "steps": [
                        {"action": "Query 'Show MSFT'", "expected": "Chart shows MSFT"}
                    ]
                }
            ]
            results = []
            for scenario in scenarios:
                result = await verifier.run_scenario(scenario)
                results.append(result)
                print_scenario_result(result)
        
        elif args.scenarios:
            # Run specific scenarios
            scenario_names = [s.strip() for s in args.scenarios.split(",")]
            print(f"\nRunning scenarios: {', '.join(scenario_names)}")
            
            results = []
            for name in scenario_names:
                scenario = {"name": name, "steps": []}  # Would load from config
                result = await verifier.run_scenario(scenario)
                results.append(result)
                print_scenario_result(result)
        
        else:
            # Run all scenarios
            print("\nRunning all verification scenarios...")
            
            config_file = args.config or str(Path(__file__).parent.parent / "config" / "computer_use_scenarios.yaml")
            
            if Path(config_file).exists():
                results = await verifier.run_all_scenarios(config_file)
            else:
                print(f"⚠️  Config file not found: {config_file}")
                print("   Using default scenarios...")
                results = await verifier.run_all_scenarios()
            
            # Print results as they complete
            for result in results:
                print_scenario_result(result)
        
        # Print summary
        print_summary(results)
        
        # Save report location
        report_dir = Path(__file__).parent.parent / "verification_reports"
        print(f"\n📁 Full reports saved to: {report_dir}")
        
        # Return exit code based on results
        all_passed = all(
            r.get("status") == "completed" and not r.get("issues") 
            for r in results
        )
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return 1


async def show_report(session_id: str):
    """Show report for an existing session."""
    print_header(f"REPORT FOR SESSION {session_id}")
    
    # Look for report file
    report_dir = Path(__file__).parent.parent / "verification_reports"
    report_files = list(report_dir.glob(f"*{session_id}*.json"))
    
    if not report_files:
        print(f"❌ No report found for session {session_id}")
        return 1
    
    # Load and display report
    with open(report_files[0], 'r') as f:
        report = json.load(f)
    
    print(f"\nScenario: {report.get('scenario')}")
    print(f"Status: {report.get('status')}")
    print(f"Timestamp: {report.get('timestamp')}")
    
    if report.get("issues"):
        print("\nIssues Found:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    
    if report.get("fixes"):
        print("\nSuggested Fixes:")
        for fix in report["fixes"]:
            print(f"  - {fix}")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Computer Use verification for the trading app",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--tunnel-url",
        help="Override default tunnel URL (e.g., https://abc.ngrok.io)"
    )
    
    parser.add_argument(
        "--scenarios",
        help="Comma-separated list of scenarios to run"
    )
    
    parser.add_argument(
        "--config",
        help="Path to scenarios YAML file"
    )
    
    parser.add_argument(
        "--report-only",
        help="Just show report for existing session ID"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick verification check only"
    )
    
    args = parser.parse_args()
    
    # Handle report-only mode
    if args.report_only:
        return asyncio.run(show_report(args.report_only))
    
    # Run verification
    return asyncio.run(run_verification(args))


if __name__ == "__main__":
    sys.exit(main())