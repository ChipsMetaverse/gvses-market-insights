"""
Calendar tool for retrieving ForexFactory events via MCP.
"""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from forex_mcp.models.time_period import TimePeriod
from forex_mcp.services.ff_scraper_service import FFScraperService
from forex_mcp.utils.event_utils import extract_and_normalize_events

logger = logging.getLogger(__name__)


def register_get_calendar_tool(app: FastMCP, namespace: str) -> None:
    """
    Register the get_calendar_events tool with the MCP server.

    This tool allows clients to fetch ForexFactory calendar events for:
    - Predefined periods (today, tomorrow, this_week, next_week, etc.)
    - Custom date ranges (requires start_date and end_date)

    Parameters
    ----------
    app : FastMCP
        The FastMCP application instance.
    namespace : str
        Namespace prefix for the tool name.
    """

    @app.tool(
        name=f"{namespace}_get_calendar_events",
        description=(
            "Retrieve ForexFactory calendar events for a given time period or custom date range. "
            "Valid `time_period` values include: today, tomorrow, yesterday, "
            "this_week, next_week, last_week, this_month, next_month, last_month, custom. "
            "For custom ranges, provide start_date and end_date in YYYY-MM-DD format."
        ),
    )
    async def get_calendar_events(
        time_period: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]:
        """
        Fetch ForexFactory calendar events.

        Parameters
        ----------
        time_period : str, optional
            Named period such as today, tomorrow, yesterday, this_week,
            next_week, last_week, this_month, next_month, last_month, custom.
        start_date : str, optional
            Start date in YYYY-MM-DD format (required if time_period='custom').
        end_date : str, optional
            End date in YYYY-MM-DD format (required if time_period='custom').

        Returns
        -------
        list[dict]
            List of event dictionaries with fields: id, title, currency, impact,
            datetime, forecast, previous, actual.

        Raises
        ------
        ValueError
            If time_period is invalid or custom dates are malformed.
        """
        logger.info(
            f"Calendar request: time_period={time_period}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        # CASE 1: Named time period
        if time_period and time_period.lower() != "custom":
            try:
                # Normalize and parse the time period
                normalized = time_period.strip().lower().replace(" ", "_")
                tp = TimePeriod.from_text(normalized)
            except ValueError as e:
                valid_options = ", ".join([t.value for t in TimePeriod])
                raise ValueError(
                    f"Invalid time_period '{time_period}'. "
                    f"Valid options: {valid_options}"
                ) from e

            scraper = FFScraperService(time_period=tp)
            raw_events = await scraper.get_events()

        # CASE 2: Custom date range
        else:
            if not start_date or not end_date:
                raise ValueError(
                    "Custom time period requires both start_date and end_date in YYYY-MM-DD format"
                )

            # Validate date formats
            TimePeriod.validate_date_format(start_date)
            TimePeriod.validate_date_format(end_date)

            scraper = FFScraperService(
                time_period=TimePeriod.CUSTOM,
                custom_start_date=start_date,
                custom_end_date=end_date,
            )
            raw_events = await scraper.get_events()

        # Normalize and return as JSON-serializable dicts
        normalized = extract_and_normalize_events(raw_events)

        logger.info(f"Returning {len(normalized)} normalized events")
        return normalized
