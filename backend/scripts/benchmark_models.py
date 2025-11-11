#!/usr/bin/env python3
"""
Model Routing Benchmark Script
================================
Measures latency, cost, and quality for different OpenAI models across intent types.

Phase 2: Model Routing & Prompt Optimization - Benchmark Suite

Usage:
    python scripts/benchmark_models.py
    python scripts/benchmark_models.py --models gpt-4o-mini gpt-4o
    python scripts/benchmark_models.py --intent price_only
    python scripts/benchmark_models.py --output benchmarks/results.json
"""

import asyncio
import time
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import argparse
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from models.benchmark_record import (
    BenchmarkQuery,
    BenchmarkMetrics,
    ModelBenchmarkResult,
    BenchmarkReport,
    BenchmarkSuite,
    IntentType,
    ModelType,
    STANDARD_BENCHMARK_QUERIES
)
from services.cost_tracker import get_cost_tracker, TokenUsage


# Initialize OpenAI client
client = AsyncOpenAI()


async def run_single_benchmark(
    model: str,
    query: BenchmarkQuery,
    cost_tracker
) -> ModelBenchmarkResult:
    """
    Run a single benchmark query on a specific model.

    Args:
        model: OpenAI model name
        query: Benchmark query to run
        cost_tracker: Cost tracking service

    Returns:
        ModelBenchmarkResult with performance metrics
    """
    print(f"  Testing {model} on: {query.query[:50]}...")

    start_time = time.perf_counter()
    success = True
    error_msg = None
    tools_called = []
    usage_data = None

    try:
        # Make API call
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a trading assistant. Respond concisely to market queries."
                },
                {
                    "role": "user",
                    "content": query.query
                }
            ],
            max_tokens=500
        )

        # Extract usage data
        if response.usage:
            usage_data = response.usage

            # Check for cached tokens
            cached_tokens = 0
            if hasattr(response.usage, 'prompt_tokens_details'):
                details = response.usage.prompt_tokens_details
                if details and hasattr(details, 'cached_tokens'):
                    cached_tokens = details.cached_tokens

            # Calculate cost
            token_usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cached_tokens=cached_tokens
            )

            costs = cost_tracker.calculate_cost(model, token_usage)

        # Check response content
        if response.choices and response.choices[0].message:
            # Simple quality check - did it respond?
            if not response.choices[0].message.content:
                success = False
                error_msg = "Empty response"

    except Exception as e:
        success = False
        error_msg = str(e)
        print(f"    ❌ Error: {error_msg}")

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # Create metrics
    if usage_data:
        metrics = BenchmarkMetrics(
            latency_ms=latency_ms,
            prompt_tokens=usage_data.prompt_tokens,
            completion_tokens=usage_data.completion_tokens,
            total_tokens=usage_data.total_tokens,
            cached_tokens=getattr(getattr(usage_data, 'prompt_tokens_details', None), 'cached_tokens', 0) or 0,
            cost_usd=costs["total_cost_usd"],
            success=success,
            error=error_msg,
            tools_called=tools_called
        )
    else:
        # Failed request - create minimal metrics
        metrics = BenchmarkMetrics(
            latency_ms=latency_ms,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost_usd=0,
            success=success,
            error=error_msg,
            tools_called=tools_called
        )

    result = ModelBenchmarkResult(
        model=ModelType(model),
        intent=query.intent,
        query=query.query,
        timestamp=datetime.utcnow(),
        metrics=metrics,
        correct_tools=False  # TODO: Implement tool call verification
    )

    if success:
        print(f"    ✅ {latency_ms:.0f}ms, {metrics.total_tokens} tokens, ${metrics.cost_usd:.6f}")
    else:
        print(f"    ❌ Failed: {error_msg}")

    return result


async def run_benchmark_suite(
    models: List[str],
    queries: List[BenchmarkQuery],
    suite_name: str = "Standard Benchmark"
) -> BenchmarkReport:
    """
    Run full benchmark suite across all models and queries.

    Args:
        models: List of model names to test
        queries: List of benchmark queries
        suite_name: Name for this benchmark run

    Returns:
        BenchmarkReport with all results
    """
    print(f"\n🔬 Running Benchmark Suite: {suite_name}")
    print(f"Models: {', '.join(models)}")
    print(f"Queries: {len(queries)}\n")

    cost_tracker = get_cost_tracker()
    results = []

    for model in models:
        print(f"\n📊 Testing {model}:")
        for query in queries:
            result = await run_single_benchmark(model, query, cost_tracker)
            results.append(result)

            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)

    # Aggregate statistics
    model_stats = calculate_model_stats(results)
    intent_stats = calculate_intent_stats(results)
    recommendations = generate_routing_recommendations(results)

    report = BenchmarkReport(
        suite_name=suite_name,
        run_timestamp=datetime.utcnow(),
        total_queries=len(queries),
        total_models_tested=len(models),
        results=results,
        model_stats=model_stats,
        intent_stats=intent_stats,
        recommended_routing=recommendations
    )

    return report


def calculate_model_stats(results: List[ModelBenchmarkResult]) -> Dict[str, Dict[str, float]]:
    """Calculate aggregate statistics per model."""
    stats_by_model = defaultdict(lambda: {
        "avg_latency_ms": [],
        "avg_cost_usd": [],
        "total_tokens": [],
        "success_rate": [],
    })

    for result in results:
        model = result.model.value
        stats_by_model[model]["avg_latency_ms"].append(result.metrics.latency_ms)
        stats_by_model[model]["avg_cost_usd"].append(result.metrics.cost_usd)
        stats_by_model[model]["total_tokens"].append(result.metrics.total_tokens)
        stats_by_model[model]["success_rate"].append(1 if result.metrics.success else 0)

    # Calculate averages
    aggregated = {}
    for model, stats in stats_by_model.items():
        aggregated[model] = {
            "avg_latency_ms": sum(stats["avg_latency_ms"]) / len(stats["avg_latency_ms"]),
            "avg_cost_usd": sum(stats["avg_cost_usd"]) / len(stats["avg_cost_usd"]),
            "avg_tokens": sum(stats["total_tokens"]) / len(stats["total_tokens"]),
            "success_rate": sum(stats["success_rate"]) / len(stats["success_rate"]),
            "total_runs": len(stats["avg_latency_ms"])
        }

    return aggregated


def calculate_intent_stats(results: List[ModelBenchmarkResult]) -> Dict[str, Dict[str, float]]:
    """Calculate aggregate statistics per intent type."""
    stats_by_intent = defaultdict(lambda: {
        "avg_latency_ms": [],
        "avg_cost_usd": [],
        "models_tested": set(),
    })

    for result in results:
        intent = result.intent.value
        stats_by_intent[intent]["avg_latency_ms"].append(result.metrics.latency_ms)
        stats_by_intent[intent]["avg_cost_usd"].append(result.metrics.cost_usd)
        stats_by_intent[intent]["models_tested"].add(result.model.value)

    # Calculate averages
    aggregated = {}
    for intent, stats in stats_by_intent.items():
        aggregated[intent] = {
            "avg_latency_ms": sum(stats["avg_latency_ms"]) / len(stats["avg_latency_ms"]),
            "avg_cost_usd": sum(stats["avg_cost_usd"]) / len(stats["avg_cost_usd"]),
            "models_tested": len(stats["models_tested"]),
            "total_runs": len(stats["avg_latency_ms"])
        }

    return aggregated


def generate_routing_recommendations(results: List[ModelBenchmarkResult]) -> Dict[str, str]:
    """
    Generate model routing recommendations based on benchmark results.

    Strategy:
    - price_only: Cheapest model with acceptable latency
    - technical_analysis: Balance of cost and capability
    - general_query: Premium model for quality
    """
    intent_performance = defaultdict(list)

    for result in results:
        if not result.metrics.success:
            continue

        intent_performance[result.intent.value].append({
            "model": result.model.value,
            "cost": result.metrics.cost_usd,
            "latency": result.metrics.latency_ms,
            "score": calculate_model_score(result)
        })

    recommendations = {}

    for intent, performances in intent_performance.items():
        if not performances:
            continue

        # Sort by score (best first)
        performances.sort(key=lambda x: x["score"], reverse=True)
        best_model = performances[0]["model"]

        recommendations[intent] = best_model

    return recommendations


def calculate_model_score(result: ModelBenchmarkResult) -> float:
    """
    Calculate overall score for a model on a query.

    Factors:
    - Latency (lower is better)
    - Cost (lower is better)
    - Success (must succeed)

    Returns score between 0-100 (higher is better)
    """
    if not result.metrics.success:
        return 0

    # Normalize factors (inverse for latency and cost)
    latency_score = max(0, 100 - (result.metrics.latency_ms / 50))  # 5000ms = 0 score
    cost_score = max(0, 100 - (result.metrics.cost_usd * 10000))  # $0.01 = 0 score

    # Weight: 60% latency, 40% cost
    score = (latency_score * 0.6) + (cost_score * 0.4)

    return score


def print_benchmark_report(report: BenchmarkReport):
    """Print formatted benchmark report to console."""
    print("\n" + "="*80)
    print(f"📊 BENCHMARK REPORT: {report.suite_name}")
    print(f"Run: {report.run_timestamp.isoformat()}")
    print("="*80)

    print(f"\n📈 Model Performance:")
    print("-"*80)
    for model, stats in report.model_stats.items():
        print(f"\n{model}:")
        print(f"  Avg Latency: {stats['avg_latency_ms']:.0f}ms")
        print(f"  Avg Cost:    ${stats['avg_cost_usd']:.6f}")
        print(f"  Avg Tokens:  {stats['avg_tokens']:.0f}")
        print(f"  Success:     {stats['success_rate']*100:.0f}%")

    print(f"\n🎯 Intent Performance:")
    print("-"*80)
    for intent, stats in report.intent_stats.items():
        print(f"\n{intent}:")
        print(f"  Avg Latency: {stats['avg_latency_ms']:.0f}ms")
        print(f"  Avg Cost:    ${stats['avg_cost_usd']:.6f}")

    print(f"\n💡 Recommended Routing:")
    print("-"*80)
    for intent, model in report.recommended_routing.items():
        print(f"  {intent:30s} → {model}")

    print("\n" + "="*80 + "\n")


def save_benchmark_report(report: BenchmarkReport, output_path: str):
    """Save benchmark report to JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2, default=str)

    print(f"✅ Report saved to: {output_path}")


async def main():
    """Main benchmark entry point."""
    parser = argparse.ArgumentParser(description="Benchmark OpenAI models for routing")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt-4o-mini", "gpt-4o"],
        help="Models to test (default: gpt-4o-mini gpt-4o)"
    )
    parser.add_argument(
        "--intent",
        type=str,
        help="Test only specific intent type"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/model_benchmark.json",
        help="Output file path (default: benchmarks/model_benchmark.json)"
    )

    args = parser.parse_args()

    # Filter queries by intent if specified
    queries = STANDARD_BENCHMARK_QUERIES
    if args.intent:
        queries = [q for q in queries if q.intent.value == args.intent]

    # Run benchmarks
    report = await run_benchmark_suite(
        models=args.models,
        queries=queries,
        suite_name="Model Routing Benchmark"
    )

    # Print results
    print_benchmark_report(report)

    # Save to file
    save_benchmark_report(report, args.output)


if __name__ == "__main__":
    asyncio.run(main())
