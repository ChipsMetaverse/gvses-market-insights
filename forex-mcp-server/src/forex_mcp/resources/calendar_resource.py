from __future__ import annotations

from typing import Dict, List

from fastmcp import FastMCP

from ..models import CalendarEvent, TimePeriod
from ..services import ForexFactoryScraper


def _resource_payload(period: TimePeriod, events: List[CalendarEvent]) -> Dict[str, object]:
    return {
        "time_period": period.value,
        "count": len(events),
        "events": [event.model_dump() for event in events],
    }


def register_calendar_resources(mcp: FastMCP, scraper: ForexFactoryScraper) -> None:
    """Register static ForexFactory calendar resources."""

    resource_map: Dict[TimePeriod, str] = {
        TimePeriod.TODAY: "ffcal://events/today",
        TimePeriod.TOMORROW: "ffcal://events/tomorrow",
        TimePeriod.WEEK: "ffcal://events/week",
        TimePeriod.NEXT_WEEK: "ffcal://events/next-week",
    }

    def register_period(period: TimePeriod, uri: str) -> None:
        display_period = period.value.replace('-', ' ')

        @mcp.resource(
            uri=uri,
            name=f"ForexFactory {display_period.title()} Events",
            description=f"Economic calendar events for {display_period}",
            mime_type="application/json",
            tags={"forex", "calendar", "economic"},
        )
        async def reader() -> Dict[str, object]:
            events = await scraper.get_events(period)
            return _resource_payload(period, events)

        reader  # noqa: F401 - decorator handles registration

    for period, uri in resource_map.items():
        register_period(period, uri)
