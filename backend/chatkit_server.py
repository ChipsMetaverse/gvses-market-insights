"""
ChatKit Python Server Implementation
Native widget streaming for GVSES Market Analysis Assistant

This module implements the ChatKit Python Server with native widget support,
replacing the Agent Builder + custom parsing approach with native ChatKit widgets.

Architecture:
- Uses openai-chatkit Python SDK (not Agent Builder)
- Implements @function_tool decorators for market data
- Streams widgets natively with await ctx.context.stream_widget(widget)
- Integrates with existing MarketServiceFactory for data
"""

import os
from typing import Any, AsyncIterator
from datetime import datetime

from chatkit.server import ChatKitServer, ThreadStreamEvent
from chatkit.types import ThreadMetadata, UserMessageItem
from chatkit.agents import AgentContext, stream_agent_response, simple_to_agent_input
from chatkit.widgets import (
    Card,
    Text,
    Title,
    Divider,
    ListView,
    ListViewItem,
    Caption,
    Badge,
    Image,
    Row,
    Box,
)
from chatkit.store import Store
from openai_agents import Agent, function_tool, RunContextWrapper, Runner

# Import existing market data services
from services.market_service_factory import MarketServiceFactory


# Global market service instance
_market_service = None


def set_market_service(service):
    """Set the global market service instance"""
    global _market_service
    _market_service = service


def get_market_service():
    """Get the global market service instance"""
    if _market_service is None:
        return MarketServiceFactory.get_service()
    return _market_service


# =============================================================================
# IN-MEMORY STORE IMPLEMENTATION
# =============================================================================


class MemoryStore(Store[dict]):
    """
    Simple in-memory storage for ChatKit threads and items

    This implementation stores thread metadata and messages in memory.
    For production, use PostgresStore or another persistent storage.
    """

    def __init__(self):
        self._threads: dict[str, ThreadMetadata] = {}
        self._items: dict[str, list] = {}  # thread_id -> list of items
        self._counter = 0

    def generate_thread_id(self, context: dict) -> str:
        """Generate a unique thread ID"""
        self._counter += 1
        return f"thread_{self._counter}_{datetime.now().timestamp()}"

    def generate_item_id(
        self,
        item_type: str,
        thread: ThreadMetadata,
        context: dict,
    ) -> str:
        """Generate a unique item ID"""
        self._counter += 1
        return f"{item_type}_{self._counter}_{datetime.now().timestamp()}"

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        """Load thread metadata"""
        if thread_id not in self._threads:
            # Create new thread if doesn't exist
            thread = ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(),
                title=None,
                metadata={},
            )
            self._threads[thread_id] = thread
            return thread
        return self._threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        """Save thread metadata"""
        self._threads[thread.id] = thread

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ):
        """Load thread items (messages, widgets, etc.)"""
        from chatkit.types import Page

        items = self._items.get(thread_id, [])

        # Simple pagination
        if after:
            # Find the index of the 'after' item
            after_idx = next((i for i, item in enumerate(items) if item.id == after), -1)
            items = items[after_idx + 1:] if after_idx >= 0 else items

        # Apply limit
        has_more = len(items) > limit
        items = items[:limit]

        return Page(
            data=items,
            has_more=has_more,
            after=items[-1].id if items and has_more else None,
        )

    async def add_thread_item(
        self, thread_id: str, item, context: dict
    ) -> None:
        """Add an item to a thread"""
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)

    async def save_item(
        self, thread_id: str, item, context: dict
    ) -> None:
        """Save/update a thread item"""
        items = self._items.get(thread_id, [])
        # Update if exists, otherwise add
        for i, existing in enumerate(items):
            if existing.id == item.id:
                items[i] = item
                return
        items.append(item)

    async def load_item(
        self, thread_id: str, item_id: str, context: dict
    ):
        """Load a specific item"""
        items = self._items.get(thread_id, [])
        for item in items:
            if item.id == item_id:
                return item
        raise ValueError(f"Item {item_id} not found")

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        """Delete a thread and all its items"""
        if thread_id in self._threads:
            del self._threads[thread_id]
        if thread_id in self._items:
            del self._items[thread_id]

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict,
    ):
        """Load list of threads"""
        from chatkit.types import Page

        threads = list(self._threads.values())
        # Simple pagination
        has_more = len(threads) > limit
        threads = threads[:limit]

        return Page(
            data=threads,
            has_more=has_more,
            after=threads[-1].id if threads and has_more else None,
        )

    # Optional attachment methods (not used in our implementation)
    async def save_attachment(self, attachment, context: dict) -> None:
        pass

    async def load_attachment(self, attachment_id: str, context: dict):
        raise NotImplementedError("Attachments not supported in MemoryStore")

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        pass


# =============================================================================
# MARKET DATA TOOLS with Native Widget Streaming
# =============================================================================


@function_tool(
    description_override="Display latest market news for a stock with interactive news feed widget"
)
async def show_market_news(
    ctx: RunContextWrapper[AgentContext],
    symbol: str,
) -> dict[str, Any]:
    """
    Fetch and display market news with interactive ListView widget

    Args:
        ctx: Agent execution context
        symbol: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Dict with news count and source information
    """
    market_service = get_market_service()

    # Fetch news
    news_data = await market_service.get_stock_news(symbol)

    # Build news widget
    news_items = []
    for article in news_data.get("articles", [])[:10]:  # Limit to 10 articles
        news_items.append(
            ListViewItem(
                children=[
                    Text(value=article.get("title", ""), weight="semibold"),
                    Caption(
                        value=f"{article.get('source', 'Unknown')} • {article.get('time_ago', '')}",
                        size="sm",
                    ),
                ]
            )
        )

    widget = Card(
        size="lg",
        status={"text": "Live News", "icon": "newspaper"},
        children=[
            Title(value=f"{symbol} Market News", size="lg"),
            Divider(spacing=12),
            (
                ListView(limit=10, children=news_items)
                if news_items
                else Text(value="No recent news available")
            ),
        ],
    )

    # Stream widget to ChatKit UI
    await ctx.context.stream_widget(widget)

    return {
        "symbol": symbol,
        "news_count": len(news_items),
        "data_source": news_data.get("data_source", "unknown"),
    }


@function_tool(description_override="Display economic calendar events with impact badges")
async def show_economic_calendar(
    ctx: RunContextWrapper[AgentContext],
    time_period: str = "today",
    impact: str = "high",
) -> dict[str, Any]:
    """
    Fetch and display economic calendar events

    Args:
        ctx: Agent execution context
        time_period: Time period (today, tomorrow, this_week, next_week)
        impact: Event impact level (high, medium, low)

    Returns:
        Dict with event count
    """
    market_service = get_market_service()

    # Fetch economic calendar
    try:
        calendar_data = await market_service.get_economic_calendar(time_period, impact)
    except AttributeError:
        # Fallback if economic calendar not available
        calendar_data = {"events": []}

    # Build calendar widget
    event_items = []
    for event in calendar_data.get("events", [])[:10]:
        impact_color = {
            "high": "danger",
            "medium": "warning",
            "low": "info",
        }.get(event.get("impact", "low"), "info")

        event_items.append(
            ListViewItem(
                children=[
                    Row(
                        children=[
                            Box(
                                children=[
                                    Text(
                                        value=event.get("title", ""), weight="semibold"
                                    ),
                                    Caption(value=event.get("time", ""), size="sm"),
                                ]
                            ),
                            Badge(
                                label=event.get("impact", "").upper(), color=impact_color
                            ),
                        ],
                        justify="between",
                        align="center",
                    )
                ]
            )
        )

    widget = Card(
        size="lg",
        status={"text": "Economic Calendar", "icon": "calendar"},
        children=[
            Title(value="Upcoming Economic Events", size="lg"),
            Divider(spacing=12),
            (
                ListView(limit=10, children=event_items)
                if event_items
                else Text(value="No upcoming events")
            ),
        ],
    )

    await ctx.context.stream_widget(widget)

    return {
        "time_period": time_period,
        "impact": impact,
        "event_count": len(event_items),
    }


@function_tool(description_override="Display stock quote with current price and metrics")
async def show_stock_quote(
    ctx: RunContextWrapper[AgentContext],
    symbol: str,
) -> dict[str, Any]:
    """
    Fetch and display real-time stock quote

    Args:
        ctx: Agent execution context
        symbol: Stock ticker symbol

    Returns:
        Dict with price data
    """
    market_service = get_market_service()

    # Fetch quote
    quote_data = await market_service.get_stock_price(symbol)

    # Build quote widget
    price = quote_data.get("price", 0)
    change = quote_data.get("change", 0)
    change_percent = quote_data.get("change_percent", 0)

    change_color = "success" if change >= 0 else "danger"
    change_sign = "+" if change >= 0 else ""

    widget = Card(
        size="md",
        children=[
            Row(
                children=[
                    Box(
                        children=[
                            Title(value=symbol, size="xl"),
                            Caption(value=quote_data.get("name", ""), size="sm"),
                        ]
                    ),
                    Box(
                        children=[
                            Text(value=f"${price:.2f}", size="xl", weight="bold"),
                            Text(
                                value=f"{change_sign}{change:.2f} ({change_sign}{change_percent:.2f}%)",
                                color=change_color,
                                size="sm",
                            ),
                        ]
                    ),
                ],
                justify="between",
                align="center",
            ),
        ],
    )

    await ctx.context.stream_widget(widget)

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_percent": change_percent,
    }


# =============================================================================
# GVSES ChatKit Server
# =============================================================================


class GVSESChatKitServer(ChatKitServer[dict]):
    """
    GVSES Market Analysis ChatKit Server

    Provides native widget streaming for market data queries including:
    - Stock quotes
    - News feeds (CNBC + Yahoo Finance)
    - Economic calendar events
    - Comprehensive market analysis
    """

    def __init__(self, data_store: Store):
        super().__init__(data_store)

        # Define the market analysis agent
        self.assistant_agent = Agent[AgentContext](
            model="gpt-4.1-mini",
            name="GVSES Market Analyst",
            instructions="""
You are a senior portfolio manager with 30+ years of experience in global markets.
You provide professional market analysis using real-time data and interactive widgets.

When users ask about stocks or markets:
1. Call the appropriate tool to fetch and display market data
2. The tool will automatically display an interactive widget
3. Provide concise, professional analysis

Query types you support:
- Quote: "What's AAPL trading at?" → show_stock_quote
- News: "Latest news on TSLA?" → show_market_news
- Economic Events: "When is NFP?" → show_economic_calendar

Always use the tools to display widgets. Keep your text responses brief and professional.
Focus on actionable insights and professional market commentary.
""",
            tools=[
                show_stock_quote,
                show_market_news,
                show_economic_calendar,
            ],
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user messages and stream agent responses with widgets
        """
        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Convert user input to agent format
        if input is None:
            return

        # Use simple_to_agent_input helper
        agent_input = await simple_to_agent_input(input)

        # Run agent with streaming
        result = Runner.run_streamed(
            self.assistant_agent,
            input=agent_input,
            context=agent_context,
        )

        # Stream agent response events (includes widgets)
        async for event in stream_agent_response(agent_context, result):
            yield event
