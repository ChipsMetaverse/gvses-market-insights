"""
Request Context Utilities
==========================
Utilities for request ID generation and context propagation for distributed tracing.

Phase 3: Observability Infrastructure - Request ID Propagation
"""

import uuid
from contextvars import ContextVar
from typing import Optional
import logging

# Thread-safe context variable for request ID
_request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """
    Generate a new UUID for request tracking.

    Returns:
        str: UUID in format 'req_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    """
    return f"req_{uuid.uuid4()}"


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set the request ID for the current context.
    If no request ID provided, generates a new one.

    Args:
        request_id: Optional request ID to use

    Returns:
        str: The request ID that was set
    """
    if not request_id:
        request_id = generate_request_id()

    _request_id_ctx.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from context.

    Returns:
        Optional[str]: Request ID if set, None otherwise
    """
    return _request_id_ctx.get()


def clear_request_id() -> None:
    """Clear the request ID from context."""
    _request_id_ctx.set(None)


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds request_id to log records.

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(RequestIDFilter())
        logger.addHandler(handler)
    """

    def filter(self, record):
        """Add request_id to the log record."""
        record.request_id = get_request_id() or 'no-request-id'
        return True


def configure_request_id_logging():
    """
    Configure logging to include request IDs.
    Call this once during application startup.
    """
    # Add filter to root logger
    root_logger = logging.getLogger()

    # Check if filter already exists
    for handler in root_logger.handlers:
        if not any(isinstance(f, RequestIDFilter) for f in handler.filters):
            handler.addFilter(RequestIDFilter())

    logger.info("Request ID logging configured")
