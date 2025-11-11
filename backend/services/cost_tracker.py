"""
Cost Tracker Service
====================
Tracks token usage and costs for OpenAI API calls with attribution.

Phase 3: Observability Infrastructure - Cost Tracking
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from models.cost_record import (
    CostRecord,
    TokenUsage,
    CostTags,
    CostSummary,
    TimeWindow
)

logger = logging.getLogger(__name__)


# OpenAI Pricing (USD per 1M tokens)
# Source: https://openai.com/api/pricing/ (as of Jan 2025)
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.150,
        "output": 0.600,
        "cached_input": 0.075  # 50% discount for cached tokens
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
        "cached_input": 1.25
    },
    "gpt-5-mini": {
        "input": 0.200,  # Estimate - update when official pricing available
        "output": 0.800,
        "cached_input": 0.100
    },
    "gpt-5": {
        "input": 3.00,  # Estimate
        "output": 12.00,
        "cached_input": 1.50
    },
    "o1-mini": {
        "input": 3.00,
        "output": 12.00,
        "cached_input": 1.50
    },
    "o1": {
        "input": 15.00,
        "output": 60.00,
        "cached_input": 7.50
    }
}


class CostTracker:
    """
    Tracks costs for OpenAI API calls.

    Features:
    - Token usage tracking
    - Cost calculation with prompt caching
    - Attribution tagging
    - In-memory storage with aggregation
    - Cost summaries by time window
    """

    def __init__(self):
        """Initialize cost tracker with in-memory storage."""
        self.cost_records: List[CostRecord] = []
        # Maintain per-request index for fast lookups
        self._records_by_request: Dict[str, List[CostRecord]] = {}
        self.max_records = 10000  # Limit memory usage
        logger.info("CostTracker initialized with in-memory storage")

    def _index_record(self, record: CostRecord) -> None:
        """Index a cost record by request ID for quick retrieval."""
        self._records_by_request.setdefault(record.request_id, []).append(record)

    def _reindex_records(self) -> None:
        """Rebuild the per-request index from the current record list."""
        indexed: Dict[str, List[CostRecord]] = {}
        for record in self.cost_records:
            indexed.setdefault(record.request_id, []).append(record)
        self._records_by_request = indexed

    def calculate_cost(
        self,
        model: str,
        usage: TokenUsage
    ) -> Dict[str, float]:
        """
        Calculate cost for token usage.

        Args:
            model: OpenAI model name
            usage: Token usage breakdown

        Returns:
            Dict with input_cost, output_cost, cached_savings, total_cost
        """
        # Get pricing for model (default to gpt-4o if unknown)
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o"])

        # Calculate costs
        input_tokens = usage.prompt_tokens - usage.cached_tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
        cached_cost = (usage.cached_tokens / 1_000_000) * pricing["cached_input"]
        cached_savings = (usage.cached_tokens / 1_000_000) * (pricing["input"] - pricing["cached_input"])

        total_cost = input_cost + output_cost + cached_cost

        return {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "cached_savings_usd": round(cached_savings, 6),
            "total_cost_usd": round(total_cost, 6)
        }

    def record_cost(
        self,
        request_id: str,
        model: str,
        usage: TokenUsage,
        tags: Optional[CostTags] = None
    ) -> CostRecord:
        """
        Record cost for a request.

        Args:
            request_id: Unique request ID
            model: OpenAI model used
            usage: Token usage
            tags: Optional attribution tags

        Returns:
            CostRecord with calculated costs
        """
        # Calculate costs
        costs = self.calculate_cost(model, usage)

        # Create cost record
        record = CostRecord(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            model=model,
            tokens=usage,
            cost_usd=costs["total_cost_usd"],
            input_cost_usd=costs["input_cost_usd"],
            output_cost_usd=costs["output_cost_usd"],
            cached_savings_usd=costs["cached_savings_usd"],
            tags=tags or CostTags()
        )

        # Store record
        self.cost_records.append(record)
        self._index_record(record)

        # Trim old records if limit exceeded
        if len(self.cost_records) > self.max_records:
            self.cost_records = self.cost_records[-self.max_records:]
            self._reindex_records()

        logger.info(
            f"Cost recorded: {costs['total_cost_usd']:.6f} USD for {usage.total_tokens} tokens",
            extra={
                "request_id": request_id,
                "model": model,
                "cost_usd": costs["total_cost_usd"],
                "tokens": usage.total_tokens
            }
        )

        return record

    # ======== Retrieval helpers for telemetry/logging ========

    def get_records_by_request(self, request_id: str) -> List[CostRecord]:
        """Return list of cost records associated with a specific request."""
        return list(self._records_by_request.get(request_id, []))

    def get_cost_summary_for_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Aggregate cost and token usage for a single request ID."""
        records = self.get_records_by_request(request_id)
        if not records:
            return None

        total_cost = 0.0
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        cached_tokens = 0

        models_used: Dict[str, int] = defaultdict(int)
        intents: Dict[str, int] = defaultdict(int)
        tools: Dict[str, int] = defaultdict(int)

        for record in records:
            total_cost += record.cost_usd
            prompt_tokens += record.tokens.prompt_tokens
            completion_tokens += record.tokens.completion_tokens
            total_tokens += record.tokens.total_tokens
            cached_tokens += record.tokens.cached_tokens
            models_used[record.model] += 1
            if record.tags.intent:
                intents[record.tags.intent] += 1
            for tool in record.tags.tools_used:
                tools[tool] += 1

        return {
            "request_id": request_id,
            "total_cost_usd": round(total_cost, 6),
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cached_tokens": cached_tokens,
            },
            "models_invoked": dict(models_used),
            "intents_invoked": dict(intents),
            "tools_invoked": dict(tools),
            "records": len(records),
        }

    def get_summary(
        self,
        window: TimeWindow = TimeWindow.DAY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> CostSummary:
        """
        Get cost summary for a time window.

        Args:
            window: Time window (hour, day, week, month)
            start_time: Optional start time (for custom window)
            end_time: Optional end time (for custom window)

        Returns:
            CostSummary with aggregated data
        """
        # Determine time range
        now = datetime.utcnow()

        if window == TimeWindow.CUSTOM:
            if not start_time or not end_time:
                raise ValueError("start_time and end_time required for custom window")
            period_start = start_time
            period_end = end_time
        elif window == TimeWindow.HOUR:
            period_start = now - timedelta(hours=1)
            period_end = now
        elif window == TimeWindow.DAY:
            period_start = now - timedelta(days=1)
            period_end = now
        elif window == TimeWindow.WEEK:
            period_start = now - timedelta(weeks=1)
            period_end = now
        elif window == TimeWindow.MONTH:
            period_start = now - timedelta(days=30)
            period_end = now
        else:
            raise ValueError(f"Unknown time window: {window}")

        # Filter records in time range
        records = [
            r for r in self.cost_records
            if period_start <= r.timestamp <= period_end
        ]

        if not records:
            return CostSummary(
                period_start=period_start,
                period_end=period_end,
                total_requests=0,
                total_tokens=0,
                total_cost_usd=0,
                avg_cost_per_request_usd=0
            )

        # Aggregate data
        total_cost = sum(r.cost_usd for r in records)
        total_tokens = sum(r.tokens.total_tokens for r in records)
        total_cached_savings = sum(r.cached_savings_usd for r in records)
        total_cached_tokens = sum(r.tokens.cached_tokens for r in records)

        # Group by dimensions
        cost_by_model = defaultdict(float)
        cost_by_endpoint = defaultdict(float)
        cost_by_intent = defaultdict(float)

        for record in records:
            cost_by_model[record.model] += record.cost_usd
            if record.tags.endpoint:
                cost_by_endpoint[record.tags.endpoint] += record.cost_usd
            if record.tags.intent:
                cost_by_intent[record.tags.intent] += record.cost_usd

        # Calculate cache hit rate
        cache_hit_rate = total_cached_tokens / total_tokens if total_tokens > 0 else 0

        return CostSummary(
            period_start=period_start,
            period_end=period_end,
            total_requests=len(records),
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 6),
            avg_cost_per_request_usd=round(total_cost / len(records), 6),
            cost_by_model=dict(cost_by_model),
            cost_by_endpoint=dict(cost_by_endpoint),
            cost_by_intent=dict(cost_by_intent),
            total_cached_savings_usd=round(total_cached_savings, 6),
            cache_hit_rate=round(cache_hit_rate, 4)
        )

    def get_recent_records(self, limit: int = 100) -> List[CostRecord]:
        """
        Get most recent cost records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent cost records
        """
        return sorted(
            self.cost_records,
            key=lambda r: r.timestamp,
            reverse=True
        )[:limit]

    def get_total_cost(self) -> float:
        """Get total cost across all recorded requests."""
        return sum(r.cost_usd for r in self.cost_records)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Dict with cost tracker statistics
        """
        if not self.cost_records:
            return {
                "total_records": 0,
                "total_cost_usd": 0,
                "total_tokens": 0,
                "models_used": []
            }

        return {
            "total_records": len(self.cost_records),
            "total_cost_usd": round(self.get_total_cost(), 6),
            "total_tokens": sum(r.tokens.total_tokens for r in self.cost_records),
            "total_cached_savings_usd": round(
                sum(r.cached_savings_usd for r in self.cost_records), 6
            ),
            "models_used": list(set(r.model for r in self.cost_records)),
            "oldest_record": min(r.timestamp for r in self.cost_records).isoformat(),
            "newest_record": max(r.timestamp for r in self.cost_records).isoformat()
        }


# Singleton instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
