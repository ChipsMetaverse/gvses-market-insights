from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx

from ..models import CalendarEvent, TimePeriod
from ..utils.event_utils import normalise_events

DEFAULT_BASE_URL = os.getenv("FF_BASE_URL", "https://nfs.faireconomy.media")
CALENDAR_ENDPOINTS: Dict[TimePeriod, str] = {
    TimePeriod.TODAY: "ff_calendar_today.json",
    TimePeriod.TOMORROW: "ff_calendar_tomorrow.json",
    TimePeriod.WEEK: "ff_calendar_thisweek.json",
    TimePeriod.NEXT_WEEK: "ff_calendar_nextweek.json",
}


@dataclass
class ForexFactoryScraper:
    """Wrapper around the ForexFactory CDN feeds with caching."""

    base_url: str = DEFAULT_BASE_URL
    cache_ttl: int = int(os.getenv("FF_CACHE_TTL", "300"))
    user_agent: str = os.getenv(
        "FF_USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    _cache: Dict[str, Tuple[float, List[CalendarEvent]]] = field(default_factory=dict)

    def _client(self) -> httpx.AsyncClient:
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        return httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=20.0)

    async def _fetch(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[CalendarEvent]:
        cache_key = self._build_cache_key(endpoint, params)
        now = time.time()
        cached = self._cache.get(cache_key)
        if cached and now - cached[0] < self.cache_ttl:
            return cached[1]

        async with self._client() as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            raw: Iterable[Dict[str, Any]] = response.json()

        events = normalise_events(raw)
        self._cache[cache_key] = (now, events)
        return events

    @staticmethod
    def _build_cache_key(endpoint: str, params: Optional[Dict[str, Any]]) -> str:
        if not params:
            return endpoint
        serialized = "&".join(
            f"{key}={value}" for key, value in sorted(params.items(), key=lambda item: item[0])
        )
        return f"{endpoint}?{serialized}"

    async def fetch_period(self, period: TimePeriod) -> List[CalendarEvent]:
        if period not in CALENDAR_ENDPOINTS:
            raise ValueError(f"Unsupported time period: {period}")

        endpoint = CALENDAR_ENDPOINTS[period]
        return await self._fetch(endpoint)

    async def fetch_custom(self, start: str, end: str) -> List[CalendarEvent]:
        return await self._fetch("ff_calendar_custom.json", params={"start": start, "end": end})

    async def get_events(
        self,
        time_period: TimePeriod = TimePeriod.TODAY,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[CalendarEvent]:
        if time_period == TimePeriod.CUSTOM:
            if not (start and end):
                raise ValueError("Custom time period requires start and end parameters")
            return await self.fetch_custom(start, end)

        return await self.fetch_period(time_period)
