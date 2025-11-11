"""
Event model for ForexFactory calendar events.
"""

from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    """
    Structured representation of a ForexFactory calendar event.

    Attributes
    ----------
    id : str
        Unique identifier for the event.
    title : str
        Event title/name (e.g., "Non-Farm Payrolls").
    currency : str
        Currency code affected by the event (e.g., "USD", "EUR").
    impact : int
        Impact level: 1 (Low), 2 (Medium), 3 (High).
    datetime : str
        Event datetime in ISO 8601 UTC format.
    forecast : Optional[str]
        Forecasted value for the economic indicator.
    previous : Optional[str]
        Previous value of the economic indicator.
    actual : Optional[str]
        Actual value after the event occurs.
    """

    id: str
    title: str
    currency: str
    impact: int  # 1=low, 2=medium, 3=high
    datetime: str  # ISO 8601 UTC format
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None
