"""
TimePeriod enum for calendar date range selection.
"""

from datetime import datetime
from enum import Enum


class TimePeriod(Enum):
    """
    Predefined time periods for ForexFactory calendar queries.

    Use CUSTOM with explicit start_date and end_date for custom ranges.
    """

    TODAY = "today"
    TOMORROW = "tomorrow"
    THIS_WEEK = "this_week"
    NEXT_WEEK = "next_week"
    THIS_MONTH = "this_month"
    NEXT_MONTH = "next_month"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"

    @staticmethod
    def from_text(text: str) -> "TimePeriod":
        """
        Parse a text string into a TimePeriod enum value.

        Parameters
        ----------
        text : str
            Text representation (e.g., "today", "next week", "next_week").

        Returns
        -------
        TimePeriod
            The corresponding enum value.

        Raises
        ------
        ValueError
            If the text doesn't match any valid TimePeriod.
        """
        if text is None:
            raise ValueError("Input text cannot be None")

        # Normalize: lowercase, replace spaces with underscores
        text = text.strip().lower().replace(" ", "_")

        mapping = {
            "today": TimePeriod.TODAY,
            "tomorrow": TimePeriod.TOMORROW,
            "this_week": TimePeriod.THIS_WEEK,
            "next_week": TimePeriod.NEXT_WEEK,
            "this_month": TimePeriod.THIS_MONTH,
            "next_month": TimePeriod.NEXT_MONTH,
            "yesterday": TimePeriod.YESTERDAY,
            "last_week": TimePeriod.LAST_WEEK,
            "last_month": TimePeriod.LAST_MONTH,
            "custom": TimePeriod.CUSTOM,
        }

        if text not in mapping:
            valid_options = ", ".join(mapping.keys())
            raise ValueError(f"Invalid text for TimePeriod: '{text}'. Valid options: {valid_options}")

        return mapping[text]

    @staticmethod
    def to_text(enum_value: "TimePeriod") -> str:
        """Convert TimePeriod to human-readable text."""
        mapping = {
            TimePeriod.TODAY: "Today",
            TimePeriod.TOMORROW: "Tomorrow",
            TimePeriod.THIS_WEEK: "This Week",
            TimePeriod.NEXT_WEEK: "Next Week",
            TimePeriod.THIS_MONTH: "This Month",
            TimePeriod.NEXT_MONTH: "Next Month",
            TimePeriod.YESTERDAY: "Yesterday",
            TimePeriod.LAST_WEEK: "Last Week",
            TimePeriod.LAST_MONTH: "Last Month",
            TimePeriod.CUSTOM: "Custom",
        }

        if enum_value not in mapping:
            raise ValueError(f"Invalid TimePeriod value: '{enum_value}'")

        return mapping[enum_value]

    @staticmethod
    def to_href(value: "TimePeriod") -> str:
        """
        Convert TimePeriod to ForexFactory URL path.

        Parameters
        ----------
        value : TimePeriod
            The time period enum value.

        Returns
        -------
        str
            URL path for ForexFactory calendar (e.g., "/calendar?day=today").
        """
        if isinstance(value, str):
            value = TimePeriod.from_text(value)

        if not isinstance(value, TimePeriod):
            raise ValueError(f"Invalid TimePeriod value: '{value}'")

        href_mapping = {
            TimePeriod.TODAY: "/calendar?day=today",
            TimePeriod.TOMORROW: "/calendar?day=tomorrow",
            TimePeriod.YESTERDAY: "/calendar?day=yesterday",
            TimePeriod.THIS_WEEK: "/calendar?week=this",
            TimePeriod.NEXT_WEEK: "/calendar?week=next",
            TimePeriod.LAST_WEEK: "/calendar?week=last",
            TimePeriod.THIS_MONTH: "/calendar?month=this",
            TimePeriod.NEXT_MONTH: "/calendar?month=next",
            TimePeriod.LAST_MONTH: "/calendar?month=last",
            TimePeriod.CUSTOM: "/calendar?range=",
        }

        return href_mapping[value]

    @staticmethod
    def validate_date_format(date_text: str) -> str:
        """
        Validate that a date string matches YYYY-MM-DD format.

        Parameters
        ----------
        date_text : str
            Date string to validate.

        Returns
        -------
        str
            The validated date string.

        Raises
        ------
        ValueError
            If the date format is invalid.
        """
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Incorrect date format, should be YYYY-MM-DD: '{date_text}'"
            )
        return date_text
