"""
Sentry Configuration for Error Monitoring and Performance Tracking

This module initializes Sentry for the GVSES Trading Dashboard backend.
It provides error tracking, performance monitoring, and request tracing.
"""

import os
import logging
from typing import Optional
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialize Sentry error tracking for the backend.
    Should be called as early as possible in the application lifecycle.
    """
    dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("SENTRY_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
    release = os.getenv("SENTRY_RELEASE", "gvses-backend@unknown")

    # Only initialize if DSN is provided
    if not dsn:
        logger.warning("Sentry DSN not configured. Error tracking disabled.")
        return

    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    # Initialize Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            logging_integration,
        ],
        # Performance Monitoring
        traces_sample_rate=0.1 if environment == "production" else 1.0,

        # Filter out expected errors
        before_send=_before_send,

        # Add custom tags
        _experiments={
            "profiles_sample_rate": 0.1 if environment == "production" else 1.0,
        },
    )

    # Set global tags
    sentry_sdk.set_tag("component", "backend")
    sentry_sdk.set_tag("framework", "fastapi")
    sentry_sdk.set_tag("runtime", "uvicorn")

    logger.info(f"✅ Sentry initialized ({environment})")


def _before_send(event, hint):
    """
    Filter and modify events before sending to Sentry.

    Args:
        event: The event dictionary
        hint: Additional context about the event

    Returns:
        The modified event or None to drop it
    """
    # Filter out expected errors
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Filter out rate limit errors (expected in production)
        if exc_type.__name__ == "RateLimitExceeded":
            event["level"] = "info"

        # Filter out expected WebSocket disconnections
        if "websocket" in str(exc_value).lower():
            event["level"] = "info"

    return event


def capture_exception(
    error: Exception,
    context: Optional[dict] = None,
    level: str = "error"
) -> None:
    """
    Capture an exception to Sentry with optional context.

    Args:
        error: The exception to capture
        context: Additional context dictionary
        level: Severity level (debug, info, warning, error, fatal)
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        scope.level = level
        sentry_sdk.capture_exception(error)


def capture_message(
    message: str,
    level: str = "info",
    context: Optional[dict] = None
) -> None:
    """
    Capture a message to Sentry with optional context.

    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context dictionary
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        scope.level = level
        sentry_sdk.capture_message(message)


def set_user(user_id: Optional[str] = None, email: Optional[str] = None) -> None:
    """
    Set user context for error tracking.

    Args:
        user_id: The user's ID
        email: The user's email address
    """
    if user_id:
        sentry_sdk.set_user({"id": user_id, "email": email})
    else:
        sentry_sdk.set_user(None)


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: Optional[dict] = None
) -> None:
    """
    Add a breadcrumb for debugging.

    Args:
        message: The breadcrumb message
        category: The breadcrumb category
        level: Severity level
        data: Additional data dictionary
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
