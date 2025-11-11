"""
Cost Record Models
==================
Pydantic models for cost tracking and attribution.

Phase 3: Observability Infrastructure - Cost Tracking
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TokenUsage(BaseModel):
    """Token usage breakdown for a request."""
    prompt_tokens: int = Field(ge=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(ge=0, description="Number of tokens in the completion")
    total_tokens: int = Field(ge=0, description="Total tokens used")
    cached_tokens: int = Field(default=0, ge=0, description="Number of cached tokens (prompt caching)")


class CostTags(BaseModel):
    """Attribution tags for cost tracking."""
    endpoint: Optional[str] = Field(default=None, description="API endpoint path")
    session_id: Optional[str] = Field(default=None, description="User session ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    intent: Optional[str] = Field(default=None, description="Query intent classification")
    tools_used: List[str] = Field(default_factory=list, description="Tools executed in request")
    stream: bool = Field(default=False, description="Whether request used streaming")


class CostRecord(BaseModel):
    """Complete cost record for a single request."""
    request_id: str = Field(..., description="Unique request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    model: str = Field(..., description="OpenAI model used")
    tokens: TokenUsage = Field(..., description="Token usage breakdown")
    cost_usd: float = Field(ge=0, description="Total cost in USD")
    input_cost_usd: float = Field(default=0, ge=0, description="Input token cost")
    output_cost_usd: float = Field(default=0, ge=0, description="Output token cost")
    cached_savings_usd: float = Field(default=0, ge=0, description="Savings from cached tokens")
    tags: CostTags = Field(default_factory=CostTags, description="Attribution tags")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-01-10T12:00:00Z",
                "model": "gpt-4o-mini",
                "tokens": {
                    "prompt_tokens": 150,
                    "completion_tokens": 50,
                    "total_tokens": 200,
                    "cached_tokens": 100
                },
                "cost_usd": 0.00012,
                "input_cost_usd": 0.00003,
                "output_cost_usd": 0.00009,
                "cached_savings_usd": 0.000015,
                "tags": {
                    "endpoint": "/api/agent/orchestrate",
                    "session_id": "session_abc123",
                    "user_id": "user_456",
                    "intent": "price-only",
                    "tools_used": ["get_stock_quote"],
                    "stream": False
                }
            }
        }


class CostSummary(BaseModel):
    """Aggregated cost summary over a time period."""
    period_start: datetime
    period_end: datetime
    total_requests: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    total_cost_usd: float = Field(ge=0)
    avg_cost_per_request_usd: float = Field(ge=0)
    cost_by_model: Dict[str, float] = Field(default_factory=dict)
    cost_by_endpoint: Dict[str, float] = Field(default_factory=dict)
    cost_by_intent: Dict[str, float] = Field(default_factory=dict)
    total_cached_savings_usd: float = Field(default=0, ge=0)
    cache_hit_rate: float = Field(default=0, ge=0, le=1)


class TimeWindow(str, Enum):
    """Time window for cost aggregation."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    CUSTOM = "custom"
