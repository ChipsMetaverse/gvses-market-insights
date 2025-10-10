#!/usr/bin/env python3
"""
A/B Testing Script for Education Mode
======================================
Compares LLM vs Template responses for educational queries.

Usage:
    python test_education_ab.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

# Test queries that should be educational
TEST_QUERIES = [
    "What does buy low mean?",
    "How do I start trading stocks?",
    "What is support and resistance?",
    "Explain RSI indicator",
    "What is MACD?",
    "Show me the chart for Apple",
    "What's the difference between support and resistance?"
]

def toggle_mode(use_llm: bool) -> Dict[str, Any]:
    """Toggle education mode."""
    response = requests.post(
        f"{BASE_URL}/api/agent/test/toggle-education-mode",
        params={"enabled": use_llm}
    )
    return response.json()

def run_query(query: str) -> Dict[str, Any]:
    """Run a single query and capture metrics."""
    start = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/agent/orchestrate",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    
    latency = (time.time() - start) * 1000
    result = response.json()
    
    return {
        "query": query,
        "response": result.get("text", ""),
        "tools_used": result.get("tools_used", []),
        "model": result.get("model", "unknown"),
        "education_mode": result.get("data", {}).get("education_mode") or result.get("education_mode", "unknown"),
        "latency_ms": latency,
        "char_count": len(result.get("text", "")),
        "has_response": bool(result.get("text") and result.get("text") != "I couldn't generate a response."),
        "cached": result.get("cached", False)
    }

def run_test_suite(mode_name: str, use_llm: bool) -> List[Dict[str, Any]]:
    """Run all test queries in one mode."""
    print(f"\n{'='*60}")
    print(f"Testing {mode_name} Mode")
    print(f"{'='*60}")
    
    # Toggle to the desired mode
    toggle_result = toggle_mode(use_llm)
    print(f"Mode set to: {toggle_result.get('education_mode')}")
    time.sleep(1)  # Let orchestrator pick up change
    
    results = []
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        result = run_query(query)
        
        print(f"  ✓ Response: {result['response'][:100]}..." if result['has_response'] else f"  ✗ No response")
        print(f"  ⏱ Latency: {result['latency_ms']:.0f}ms")
        print(f"  📝 Length: {result['char_count']} chars")
        print(f"  🤖 Model: {result['model']}")
        
        results.append(result)
        time.sleep(0.5)  # Avoid rate limits
    
    return results

def compare_results(template_results: List[Dict], llm_results: List[Dict]) -> Dict[str, Any]:
    """Generate comparison metrics."""
    template_success = sum(1 for r in template_results if r['has_response'])
    llm_success = sum(1 for r in llm_results if r['has_response'])
    
    template_avg_latency = sum(r['latency_ms'] for r in template_results) / len(template_results)
    llm_avg_latency = sum(r['latency_ms'] for r in llm_results) / len(llm_results)
    
    template_avg_length = sum(r['char_count'] for r in template_results if r['has_response']) / max(template_success, 1)
    llm_avg_length = sum(r['char_count'] for r in llm_results if r['has_response']) / max(llm_success, 1)
    
    return {
        "total_queries": len(TEST_QUERIES),
        "template_mode": {
            "success_count": template_success,
            "success_rate": (template_success / len(TEST_QUERIES)) * 100,
            "avg_latency_ms": template_avg_latency,
            "avg_response_length": template_avg_length
        },
        "llm_mode": {
            "success_count": llm_success,
            "success_rate": (llm_success / len(TEST_QUERIES)) * 100,
            "avg_latency_ms": llm_avg_latency,
            "avg_response_length": llm_avg_length
        },
        "improvements": {
            "success_rate_delta": ((llm_success - template_success) / len(TEST_QUERIES)) * 100,
            "latency_increase_ms": llm_avg_latency - template_avg_latency,
            "content_richness_delta": llm_avg_length - template_avg_length
        }
    }

def save_report(template_results: List[Dict], llm_results: List[Dict], comparison: Dict[str, Any]):
    """Save detailed test report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"education_ab_test_{timestamp}.json"
    
    report = {
        "test_date": datetime.now().isoformat(),
        "test_queries": TEST_QUERIES,
        "template_results": template_results,
        "llm_results": llm_results,
        "comparison": comparison
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Full report saved to: {report_path}")
    return report_path

def print_summary(comparison: Dict[str, Any]):
    """Print comparison summary."""
    print(f"\n{'='*60}")
    print("A/B Test Summary")
    print(f"{'='*60}")
    
    print(f"\n📊 Success Rates:")
    print(f"  Templates: {comparison['template_mode']['success_count']}/{comparison['total_queries']} ({comparison['template_mode']['success_rate']:.1f}%)")
    print(f"  LLM:       {comparison['llm_mode']['success_count']}/{comparison['total_queries']} ({comparison['llm_mode']['success_rate']:.1f}%)")
    print(f"  Delta:     {comparison['improvements']['success_rate_delta']:+.1f}%")
    
    print(f"\n⏱ Latency:")
    print(f"  Templates: {comparison['template_mode']['avg_latency_ms']:.0f}ms")
    print(f"  LLM:       {comparison['llm_mode']['avg_latency_ms']:.0f}ms")
    print(f"  Delta:     {comparison['improvements']['latency_increase_ms']:+.0f}ms")
    
    print(f"\n📝 Response Quality:")
    print(f"  Templates: {comparison['template_mode']['avg_response_length']:.0f} chars avg")
    print(f"  LLM:       {comparison['llm_mode']['avg_response_length']:.0f} chars avg")
    print(f"  Delta:     {comparison['improvements']['content_richness_delta']:+.0f} chars")
    
    print(f"\n💡 Recommendation:")
    if comparison['improvements']['success_rate_delta'] > 10:
        print(f"  ✅ LLM mode significantly better - recommend switching to LLM")
    elif comparison['improvements']['success_rate_delta'] < -10:
        print(f"  ⚠️ Templates performing better - keep templates")
    else:
        print(f"  ℹ️ Similar performance - choose based on latency/cost preference")

def main():
    """Run complete A/B test."""
    print("Education Mode A/B Testing")
    print("=" * 60)
    print(f"Testing {len(TEST_QUERIES)} queries in both modes")
    
    # Run template mode first
    template_results = run_test_suite("Template", use_llm=False)
    
    # Run LLM mode
    llm_results = run_test_suite("LLM", use_llm=True)
    
    # Compare results
    comparison = compare_results(template_results, llm_results)
    
    # Print summary
    print_summary(comparison)
    
    # Save detailed report
    report_path = save_report(template_results, llm_results, comparison)
    
    print(f"\n✅ A/B test complete!")
    print(f"📄 View full report: {report_path}")

if __name__ == "__main__":
    main()

