# Model Routing Benchmarks

Performance benchmarks for OpenAI model routing optimization.

## Quick Start

Run benchmarks with default models (gpt-4o-mini, gpt-4o):

```bash
cd backend
python scripts/benchmark_models.py
```

## Usage Examples

### Test specific models:
```bash
python scripts/benchmark_models.py --models gpt-4o-mini gpt-4o gpt-5-mini
```

### Test specific intent:
```bash
python scripts/benchmark_models.py --intent price_only
python scripts/benchmark_models.py --intent technical_analysis
```

### Custom output path:
```bash
python scripts/benchmark_models.py --output benchmarks/my_results.json
```

## Intent Types

- **price_only**: Simple price lookups (should use cheapest model)
- **technical_analysis**: Complex analysis with indicators
- **news_summary**: News aggregation and summarization
- **market_overview**: Overall market conditions
- **chart_command**: Chart control commands
- **general_query**: Open-ended investment queries

## Output

Results are saved to JSON with:
- Per-model statistics (latency, cost, success rate)
- Per-intent statistics
- Routing recommendations

## Reading Results

```python
import json

with open('benchmarks/model_benchmark.json') as f:
    report = json.load(f)

# Best model for each intent
print(report['recommended_routing'])

# Detailed model stats
print(report['model_stats'])
```

## Metrics Tracked

- **Latency**: Response time in milliseconds
- **Cost**: USD cost per query (including prompt caching)
- **Tokens**: Prompt, completion, cached token counts
- **Success Rate**: % of successful completions
- **Quality**: Correctness of tool calls (future)

## Routing Strategy

Current scoring formula (per query):
- 60% weight on latency (lower is better)
- 40% weight on cost (lower is better)
- Must succeed (failures score 0)

Best model per intent becomes routing recommendation.
