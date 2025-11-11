"""
Event normalization utilities for converting raw ForexFactory data
into structured Event models.
"""

import logging
from datetime import datetime, timezone
from typing import Iterable

from forex_mcp.settings import get_settings

logger = logging.getLogger(__name__)


def _normalize_event(raw: dict) -> dict:
    """
    Normalize raw ForexFactory event into a consistent structure.

    Includes flexible INCLUDE_FIELDS / EXCLUDE_FIELDS support from settings.

    Fallback rules:
      - id → id / eventId
      - title → title / name / soloTitle / prefixedName
      - currency → currency / country
      - impact → impact / impactName / impactTitle
      - datetime → datetime / dateline

    Parameters
    ----------
    raw : dict
        Raw event data from ForexFactory scraper.

    Returns
    -------
    dict
        Normalized event dictionary with consistent field names.
    """
    settings = get_settings()

    # --- Step 1: Build the canonical lean model with fallbacks ---
    lean_event = {
        "id": str(raw.get("id") or raw.get("eventId") or ""),
        "title": (
            raw.get("title")
            or raw.get("name")
            or raw.get("soloTitle")
            or raw.get("prefixedName")
            or ""
        ),
        "currency": raw.get("currency") or raw.get("country") or "",
        "impact": (
            raw.get("impact") or raw.get("impactName") or raw.get("impactTitle") or ""
        ),
        "datetime": str(raw.get("datetime") or raw.get("dateline") or ""),
        "forecast": raw.get("forecast") or None,
        "previous": raw.get("previous") or None,
        "actual": raw.get("actual") or None,
    }

    # --- Step 2: Decide included fields ---
    if settings.INCLUDE_FIELDS is None:
        # Blank → default lean model
        fields_to_include = settings.default_fields
    elif settings.INCLUDE_FIELDS == ["*"]:
        # Wildcard → all fields from raw event
        fields_to_include = list(raw.keys())
    else:
        # Explicit list
        fields_to_include = settings.INCLUDE_FIELDS

    # --- Step 3: Build the event dict according to INCLUDE_FIELDS ---
    if settings.INCLUDE_FIELDS == ["*"]:
        # All raw fields (keep original event structure)
        event = {k: raw.get(k) for k in fields_to_include}
    else:
        # Lean model with fallbacks → filter down
        event = {k: lean_event.get(k) for k in fields_to_include if k in lean_event}

    # --- Add datetime enrichments if datetime included ---
    if "datetime" in event and event["datetime"]:
        try:
            ts = int(event["datetime"])
            dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
            dt_local = dt_utc.astimezone(settings.local_tz)
            event["datetime_utc"] = dt_utc.isoformat()
            event["datetime_local"] = dt_local.isoformat()
        except Exception as e:
            logger.debug(f"Failed to parse timestamp {event['datetime']}: {e}")
            # if malformed timestamp, just skip enrichments

    # --- Step 4: Apply exclusions ---
    if settings.EXCLUDE_FIELDS:
        for f in settings.EXCLUDE_FIELDS:
            event.pop(f, None)

    logger.debug(f"Normalized event (fields={list(event.keys())}): {event}")
    return event


def extract_and_normalize_events(raw_events: Iterable[dict]) -> list[dict]:
    """
    Extract all events from a list of raw 'day' blocks and normalize them.

    The ForexFactory scraper returns data grouped by days, where each day
    has an 'events' array. This function flattens the structure and
    normalizes each event.

    Parameters
    ----------
    raw_events : Iterable[dict]
        Each element should be a day block with an 'events' key containing
        a list of event dictionaries.

    Returns
    -------
    list[dict]
        A flat list of normalized event dictionaries ready for JSON serialization.
    """
    events: list[dict] = []

    for event_day in raw_events:
        try:
            day_events = event_day.get("events", [])
            events.extend(day_events)
        except Exception as e:
            logger.warning(f"Skipping malformed event_day: {e}")

    normalized_events = [_normalize_event(e) for e in events]

    logger.info(f"Extracted and normalized {len(normalized_events)} events")
    return normalized_events
