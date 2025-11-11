"""
Tools manager for registering all MCP tools.
"""

import logging

from mcp.server.fastmcp import FastMCP

from forex_mcp.tools.get_calendar_tool import register_get_calendar_tool

logger = logging.getLogger(__name__)


def register_tools(app: FastMCP, namespace: str) -> None:
    """
    Register all available MCP tools with the FastMCP app.

    Parameters
    ----------
    app : FastMCP
        The FastMCP application instance.
    namespace : str
        Namespace prefix for tool names (e.g., "ffcal").
    """
    logger.info(f"Registering MCP tools with namespace '{namespace}'...")

    # Register calendar tool
    register_get_calendar_tool(app, namespace)

    logger.info("All tools registered successfully.")
