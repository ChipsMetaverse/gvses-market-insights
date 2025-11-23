"""
ChatKit GVSES Server Integration
Provides singleton instance of the ChatKit Python Server for widget streaming
"""

from chatkit_server import GVSESChatKitServer, MemoryStore, set_market_service
from services.market_service_factory import MarketServiceFactory

# Singleton instances
_chatkit_server = None
_memory_store = None


def get_chatkit_server() -> GVSESChatKitServer:
    """
    Get or create the singleton ChatKit server instance

    Returns:
        GVSESChatKitServer: Configured ChatKit server with native widget support
    """
    global _chatkit_server, _memory_store

    if _chatkit_server is None:
        # Create in-memory store
        _memory_store = MemoryStore()

        # Set market service for tools to use
        market_service = MarketServiceFactory.get_service()
        set_market_service(market_service)

        # Create ChatKit server
        _chatkit_server = GVSESChatKitServer(data_store=_memory_store)

        print("✅ ChatKit Python Server initialized with native widget streaming")
        print(f"   - Tools: {len(_chatkit_server.assistant_agent.tools)}")
        print(f"   - Model: {_chatkit_server.assistant_agent.model}")
        print(f"   - Store: MemoryStore (in-memory)")

    return _chatkit_server


def reset_chatkit_server():
    """
    Reset the ChatKit server (useful for testing)
    """
    global _chatkit_server, _memory_store
    _chatkit_server = None
    _memory_store = None
