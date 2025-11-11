"""
Retry Utilities
Exponential backoff retry logic for resilient API calls

Phase 3: Observability & Resilience - Retry Patterns
"""

import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from openai import (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)

logger = logging.getLogger(__name__)

# Exceptions that should trigger retries
RETRIABLE_EXCEPTIONS = (
    RateLimitError,  # 429 - Rate limit exceeded
    APIConnectionError,  # Network errors
    APITimeoutError,  # Timeout errors
    InternalServerError,  # 500+ Server errors
)

def create_openai_retry_decorator(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
):
    """
    Create a retry decorator for OpenAI API calls

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time in seconds (default: 1)
        max_wait: Maximum wait time in seconds (default: 10)

    Returns:
        Retry decorator configured for OpenAI errors

    Usage:
        @create_openai_retry_decorator()
        async def call_openai():
            return await client.chat.completions.create(...)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(RETRIABLE_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )

# Default retry decorator for OpenAI calls
# 3 attempts with exponential backoff: 1s, 2s, 4s
openai_retry = create_openai_retry_decorator(
    max_attempts=3,
    min_wait=1,
    max_wait=4,
)

# Aggressive retry for critical operations
# 5 attempts with longer backoff
openai_retry_aggressive = create_openai_retry_decorator(
    max_attempts=5,
    min_wait=1,
    max_wait=10,
)

# Quick retry for lightweight operations
# 2 attempts with minimal wait
openai_retry_quick = create_openai_retry_decorator(
    max_attempts=2,
    min_wait=0.5,
    max_wait=2,
)
