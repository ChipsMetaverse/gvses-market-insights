"""
Chart Tool Registry
===================
Auto-registers chart capabilities from knowledge base as callable tools.
Maps knowledge base terms (RSI, MACD, etc.) to chart manipulation functions.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from services.vector_retriever import VectorRetriever

logger = logging.getLogger(__name__)


class ChartTool:
    """Represents a chart manipulation tool derived from knowledge base"""

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        topic: str,
        parameters: Dict[str, Any],
        frontend_command: str,
        knowledge_chunks: List[Dict[str, Any]]
    ):
        self.name = name
        self.description = description
        self.category = category
        self.topic = topic
        self.parameters = parameters
        self.frontend_command = frontend_command
        self.knowledge_chunks = knowledge_chunks

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "topic": self.topic,
            "parameters": self.parameters,
            "frontend_command": self.frontend_command,
            "knowledge_source": [
                {
                    "doc_id": chunk.get("doc_id"),
                    "source": chunk.get("source"),
                    "text_preview": chunk.get("text", "")[:150] + "..."
                }
                for chunk in self.knowledge_chunks[:2]  # First 2 chunks only
            ]
        }


class ChartToolRegistry:
    """
    Auto-registers chart capabilities from knowledge base as callable tools.
    Provides tool discovery and knowledge-based command generation.
    """

    # Indicator configuration with knowledge topic mappings
    INDICATOR_CONFIG = {
        "rsi": {
            "name": "toggle_rsi",
            "description": "Enable/disable RSI (Relative Strength Index) oscillator",
            "category": "momentum_indicator",
            "frontend_command": "INDICATOR:RSI",
            "knowledge_topic": "ta_dummies:rsi",
            "parameters": {
                "enabled": {"type": "boolean", "description": "Enable or disable the indicator"}
            }
        },
        "macd": {
            "name": "toggle_macd",
            "description": "Enable/disable MACD (Moving Average Convergence Divergence) indicator",
            "category": "momentum_indicator",
            "frontend_command": "INDICATOR:MACD",
            "knowledge_topic": "ta_dummies:macd",
            "parameters": {
                "enabled": {"type": "boolean", "description": "Enable or disable the indicator"}
            }
        },
        "moving_average": {
            "name": "toggle_moving_averages",
            "description": "Enable/disable Moving Average indicators (MA20, MA50, MA200)",
            "category": "trend_indicator",
            "frontend_command": "INDICATOR:MA",
            "knowledge_topic": "ta_dummies:sma",
            "parameters": {
                "enabled": {"type": "boolean", "description": "Enable or disable the indicator"},
                "periods": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Moving average periods (default: [20, 50, 200])"
                }
            }
        },
        "bollinger": {
            "name": "toggle_bollinger_bands",
            "description": "Enable/disable Bollinger Bands volatility indicator",
            "category": "volatility_indicator",
            "frontend_command": "INDICATOR:BOLLINGER",
            "knowledge_topic": None,
            "parameters": {
                "enabled": {"type": "boolean", "description": "Enable or disable the indicator"}
            }
        },
        "volume": {
            "name": "toggle_volume",
            "description": "Enable/disable Volume indicator",
            "category": "volume_indicator",
            "frontend_command": "INDICATOR:VOLUME",
            "knowledge_topic": "ta_dummies:volume",
            "parameters": {
                "enabled": {"type": "boolean", "description": "Enable or disable the indicator"}
            }
        }
    }

    # Drawing tool configuration
    DRAWING_CONFIG = {
        "trend": {
            "name": "draw_trendline",
            "description": "Draw trend line on chart connecting price points",
            "category": "drawing_tool",
            "frontend_command": "DRAW:TRENDLINE",
            "parameters": {
                "start_time": {"type": "number", "description": "Start timestamp"},
                "start_price": {"type": "number", "description": "Start price"},
                "end_time": {"type": "number", "description": "End timestamp"},
                "end_price": {"type": "number", "description": "End price"}
            }
        },
        "support_resistance": {
            "name": "draw_horizontal_line",
            "description": "Draw support/resistance horizontal line at specific price",
            "category": "drawing_tool",
            "frontend_command": "DRAW:HORIZONTAL",
            "parameters": {
                "price": {"type": "number", "description": "Price level"},
                "type": {
                    "type": "string",
                    "enum": ["support", "resistance", "pivot"],
                    "description": "Line type"
                }
            }
        }
    }

    def __init__(self, vector_retriever: VectorRetriever):
        """
        Initialize tool registry with knowledge base integration.

        Args:
            vector_retriever: Vector retriever instance for knowledge access
        """
        self.vector_retriever = vector_retriever
        self.tools: Dict[str, ChartTool] = {}
        self._register_all_tools()
        logger.info(f"ChartToolRegistry initialized with {len(self.tools)} tools")

    def _register_all_tools(self):
        """Register all chart tools from knowledge base"""
        # Register indicator tools
        for topic, config in self.INDICATOR_CONFIG.items():
            self._register_indicator_tool(topic, config)

        # Register drawing tools
        for topic, config in self.DRAWING_CONFIG.items():
            self._register_drawing_tool(topic, config)

        logger.info(f"Registered {len(self.tools)} chart tools")

    def _register_indicator_tool(self, topic: str, config: Dict[str, Any]):
        """Register an indicator tool with knowledge base integration"""
        # Use knowledge_topic from config if available, otherwise fallback to topic
        knowledge_topic = config.get('knowledge_topic', topic)

        # Find relevant knowledge chunks
        chunks = []
        if knowledge_topic:
            chunks = [
                chunk for chunk in self.vector_retriever.knowledge_base
                if chunk.get('topic') == knowledge_topic
            ]

        if not chunks and knowledge_topic:
            logger.warning(f"No knowledge chunks found for topic: {knowledge_topic}")
        elif chunks:
            logger.info(f"Loaded {len(chunks)} knowledge chunks for {topic} from topic '{knowledge_topic}'")

        # Use knowledge description if available, otherwise use config
        description = config["description"]
        if chunks:
            # Enhance description with knowledge excerpt
            first_chunk = chunks[0].get("text", "")
            if len(first_chunk) > 100:
                knowledge_excerpt = first_chunk[:200].strip()
                description = f"{description}. {knowledge_excerpt}"

        tool = ChartTool(
            name=config["name"],
            description=description,
            category=config["category"],
            topic=topic,
            parameters=config["parameters"],
            frontend_command=config["frontend_command"],
            knowledge_chunks=chunks
        )

        self.tools[config["name"]] = tool
        logger.debug(f"Registered indicator tool: {config['name']} with {len(chunks)} knowledge chunks")

    def _register_drawing_tool(self, topic: str, config: Dict[str, Any]):
        """Register a drawing tool"""
        # Find relevant knowledge chunks (support/resistance, trendlines, etc.)
        chunks = [
            chunk for chunk in self.vector_retriever.knowledge_base
            if topic.lower() in chunk.get('text', '').lower()[:500]
        ]

        tool = ChartTool(
            name=config["name"],
            description=config["description"],
            category=config["category"],
            topic=topic,
            parameters=config["parameters"],
            frontend_command=config["frontend_command"],
            knowledge_chunks=chunks[:3]  # Limit to 3 most relevant
        )

        self.tools[config["name"]] = tool
        logger.debug(f"Registered drawing tool: {config['name']}")

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools as dictionaries"""
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool(self, name: str) -> Optional[ChartTool]:
        """Get a specific tool by name"""
        return self.tools.get(name)

    def get_tools_by_category(self, category: str) -> List[ChartTool]:
        """Get all tools in a specific category"""
        return [
            tool for tool in self.tools.values()
            if tool.category == category
        ]

    async def search_tools_by_query(self, query: str, top_k: int = 5) -> List[ChartTool]:
        """
        Search for relevant tools using semantic search.

        Args:
            query: Natural language query (e.g., "show me momentum indicators")
            top_k: Number of results to return

        Returns:
            List of relevant ChartTool objects
        """
        # Use vector retriever to find relevant knowledge
        knowledge_results = await self.vector_retriever.search_knowledge(query, top_k=top_k * 2)

        # Map knowledge topics to tools
        relevant_tools = []
        seen_tools = set()

        for result in knowledge_results:
            topic = result.get('topic', '')

            # Find tools matching this topic
            for tool in self.tools.values():
                if tool.topic == topic and tool.name not in seen_tools:
                    relevant_tools.append(tool)
                    seen_tools.add(tool.name)
                    if len(relevant_tools) >= top_k:
                        break

            if len(relevant_tools) >= top_k:
                break

        return relevant_tools

    def get_frontend_command(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[str]:
        """
        Generate frontend command string from tool name and parameters.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Frontend command string or None
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return None

        # For indicators, command is simple
        if tool.category.endswith('_indicator'):
            enabled = parameters.get('enabled', True)
            if enabled:
                return tool.frontend_command
            else:
                return f"HIDE:{tool.frontend_command.split(':')[1]}"

        # For drawing tools, construct command with parameters
        if tool.category == 'drawing_tool':
            cmd = tool.frontend_command
            param_str = ",".join([f"{k}={v}" for k, v in parameters.items()])
            return f"{cmd}:{param_str}"

        return tool.frontend_command


# Singleton instance
_registry_instance: Optional[ChartToolRegistry] = None


def get_chart_tool_registry() -> ChartToolRegistry:
    """Get or create the singleton chart tool registry instance"""
    global _registry_instance

    if _registry_instance is None:
        from services.vector_retriever import VectorRetriever
        retriever = VectorRetriever()
        _registry_instance = ChartToolRegistry(retriever)

    return _registry_instance
