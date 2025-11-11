"""
Main entrypoint for the forex_mcp MCP server.

This file launches the ForexFactory MCP server using the FastMCP framework.
It supports multiple transports (stdio, http, sse) and allows command-line
overrides of host and port parameters.

Usage Examples:
  • HTTP mode (Docker/production):
      python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002

  • Local dev (stdio):
      python src/forex_mcp/server.py --transport stdio

  • Run in Docker:
      docker compose up forex-mcp-server
"""

import argparse
import asyncio
import logging
import sys

from mcp.server.fastmcp import FastMCP

from forex_mcp.settings import get_settings
from forex_mcp.tools.tools_manager import register_tools

# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------
logger = logging.getLogger("forex-mcp")
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s %(message)s %(filename)s:%(lineno)d",
    datefmt="%m/%d/%y %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# -----------------------------------------------------------------------------
# CLI argument parsing
# -----------------------------------------------------------------------------
def parse_arguments():
    """
    Parse command-line arguments for transport, host, and port.
    Allows Docker or manual execution to override defaults from settings.py.
    """
    parser = argparse.ArgumentParser(description="ForexFactory MCP Server")

    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default=None,
        help="Transport method for the MCP server (default: http)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind (http/sse only, default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind (http/sse only, default: 3002)",
    )

    # Allow extra args without breaking (useful for MCP CLI compatibility)
    args, _unknown = parser.parse_known_args()
    return args


# -----------------------------------------------------------------------------
# App setup helper
# -----------------------------------------------------------------------------
def setup_app(_app: FastMCP, namespace: str):
    """
    Register all tools with the FastMCP app.

    Parameters
    ----------
    _app : FastMCP
        The FastMCP application instance.
    namespace : str
        Namespace prefix for tool names.
    """
    register_tools(_app, namespace)


# -----------------------------------------------------------------------------
# Resolve configuration (CLI > ENV > defaults)
# -----------------------------------------------------------------------------
args = parse_arguments()
settings = get_settings()

transport = args.transport or settings.MCP_TRANSPORT
host = args.host or settings.MCP_HOST
port = args.port or settings.MCP_PORT

# -----------------------------------------------------------------------------
# Create global FastMCP app
# -----------------------------------------------------------------------------
app = FastMCP(
    name="forex-mcp",
    host=host,
    port=port,
)

setup_app(app, settings.NAMESPACE)


# -----------------------------------------------------------------------------
# Async Entrypoint
# -----------------------------------------------------------------------------
async def main_async():
    """
    Main async entrypoint that starts the MCP server with the chosen transport.
    Supports stdio (local dev), HTTP (Docker/remote), and SSE (legacy).
    """
    logger.info(f"Starting ForexFactory MCP server (transport={transport})")
    logger.info(f"Server configuration: host={host}, port={port}, namespace={settings.NAMESPACE}")

    try:
        if transport == "stdio":
            # Standard input/output transport for local inspectors
            logger.info("Using stdio transport for local development")
            await app.run_stdio_async()

        elif transport == "http":
            # Streamable HTTP mode (recommended for Docker/production)
            logger.info(f"Starting HTTP server on {host}:{port}")
            await app.run_streamable_http_async()

        elif transport == "sse":
            # Legacy Server-Sent Events transport (deprecated)
            logger.warning(
                "SSE transport is deprecated. Consider using HTTP instead."
            )
            await app.run_sse_async()

        else:
            raise ValueError(f"Unknown transport: {transport}")

    except KeyboardInterrupt:
        logger.info("Server interrupted and shutting down...")

    except Exception as e:
        # User-friendly diagnostics for common startup errors
        logger.exception(f"Error starting MCP server: {e}")
        if transport in ["http", "sse"]:
            logger.error(f"Configured host/port: {host}:{port}")
            logger.error("Common fixes:")
            logger.error(f"1. Ensure port {port} is available.")
            logger.error("2. Check if another service is already bound.")
            logger.error("3. Try a different port with --port <PORT>.")
        sys.exit(1)


# -----------------------------------------------------------------------------
# Entrypoint wrapper
# -----------------------------------------------------------------------------
def main():
    """Entrypoint wrapper for synchronous execution."""
    asyncio.run(main_async())


# -----------------------------------------------------------------------------
# Script entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
