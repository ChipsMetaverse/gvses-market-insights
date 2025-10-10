"""
OpenAI Tool Schema Mapper
=========================
Converts MCP server tools to OpenAI function definitions for the Realtime API.
Dynamically generates tool schemas from the market MCP server.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from mcp_client import get_mcp_client
from services.chart_tool_registry import get_chart_tool_registry

logger = logging.getLogger(__name__)


class OpenAIToolMapper:
    """
    Maps MCP tools to OpenAI function definitions for the Realtime API.
    Handles dynamic schema generation and tool validation.
    """
    
    def __init__(self):
        self.mcp_client = None
        self.tool_cache = {}
        self.schema_cache = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize MCP connection and load tool schemas."""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing OpenAI tool mapper...")
            self.mcp_client = get_mcp_client()
            
            if not self.mcp_client._initialized:
                await self.mcp_client.start()
            
            # Load and convert all available tools
            await self._load_mcp_tools()
            self._initialized = True
            logger.info(f"OpenAI tool mapper initialized with {len(self.tool_cache)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI tool mapper: {e}")
            raise
    
    async def _load_mcp_tools(self):
        """Load tools from MCP server and chart registry, convert to OpenAI format."""
        try:
            # Get list of available tools from MCP server
            tools_response = await self.mcp_client.list_tools()

            if not tools_response or "tools" not in tools_response:
                logger.warning("No tools received from MCP server")
                return

            mcp_tools = tools_response["tools"]
            logger.info(f"Loading {len(mcp_tools)} tools from MCP server...")

            for tool in mcp_tools:
                openai_tool = self._convert_mcp_to_openai_tool(tool)
                if openai_tool:
                    tool_name = tool["name"]
                    self.tool_cache[tool_name] = openai_tool
                    self.schema_cache[tool_name] = tool
                    logger.debug(f"Converted MCP tool: {tool_name}")

            logger.info(f"Successfully converted {len(self.tool_cache)} MCP tools to OpenAI format")

            # Load chart control tools from knowledge-based registry
            await self._load_chart_control_tools()

        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}")
            # Continue with empty tool cache for graceful degradation
            self.tool_cache = {}
            self.schema_cache = {}

    async def _load_chart_control_tools(self):
        """Load chart manipulation tools from the chart tool registry."""
        try:
            registry = get_chart_tool_registry()
            chart_tools = registry.get_all_tools()

            logger.info(f"Loading {len(chart_tools)} chart control tools...")

            for tool_dict in chart_tools:
                # Convert chart tool to OpenAI function format
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool_dict["name"],
                        "description": tool_dict["description"],
                        "parameters": {
                            "type": "object",
                            "properties": tool_dict["parameters"],
                            "required": list(tool_dict["parameters"].keys())
                        }
                    }
                }

                # Add to cache
                self.tool_cache[tool_dict["name"]] = openai_tool
                self.schema_cache[tool_dict["name"]] = {
                    "name": tool_dict["name"],
                    "description": tool_dict["description"],
                    "category": tool_dict["category"],
                    "frontend_command": tool_dict["frontend_command"]
                }

                logger.debug(f"Converted chart tool: {tool_dict['name']}")

            logger.info(f"Successfully added {len(chart_tools)} chart control tools")

        except Exception as e:
            logger.error(f"Failed to load chart control tools: {e}")
            # Non-fatal - chart tools are optional enhancement
    
    def _convert_mcp_to_openai_tool(self, mcp_tool: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert an MCP tool definition to OpenAI function format with comprehensive validation.
        
        Args:
            mcp_tool: MCP tool definition with name, description, inputSchema
            
        Returns:
            OpenAI function definition or None if conversion fails
        """
        try:
            # Validate tool name
            tool_name = mcp_tool.get("name")
            if not tool_name or not isinstance(tool_name, str) or not tool_name.strip():
                logger.warning(f"MCP tool has invalid or missing name: {mcp_tool}")
                return None
            
            # Sanitize tool name for OpenAI (must be alphanumeric with underscores)
            tool_name = tool_name.strip()
            if not tool_name.replace("_", "").replace("-", "_").isalnum():
                # Replace invalid characters with underscores
                import re
                original_name = tool_name
                tool_name = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
                logger.info(f"Sanitized tool name from '{original_name}' to '{tool_name}'")
            
            # Ensure description exists and is valid
            description = mcp_tool.get("description", "")
            if not description or not isinstance(description, str):
                description = f"Execute {tool_name} function"
            
            # Convert MCP input schema to OpenAI parameters format
            input_schema = mcp_tool.get("inputSchema", {})
            openai_parameters = self._convert_schema(input_schema)
            
            # Create OpenAI function definition with validation
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": description[:1024],  # Limit description length
                    "parameters": openai_parameters
                }
            }
            
            # Validate the final tool structure
            if not self._validate_openai_tool(openai_tool):
                logger.warning(f"Tool validation failed for {tool_name}")
                return None
            
            logger.debug(f"Successfully converted tool: {tool_name}")
            return openai_tool
            
        except Exception as e:
            logger.error(f"Failed to convert MCP tool {mcp_tool.get('name', 'unknown')}: {e}")
            return None
    
    def _convert_mcp_to_realtime_tool(self, mcp_tool: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert an MCP tool definition to OpenAI Realtime API format.
        The Realtime API uses a FLAT structure, not nested under 'function'.
        
        Args:
            mcp_tool: MCP tool definition with name, description, inputSchema
            
        Returns:
            OpenAI Realtime tool definition or None if conversion fails
        """
        try:
            # Validate tool name
            tool_name = mcp_tool.get("name")
            if not tool_name or not isinstance(tool_name, str) or not tool_name.strip():
                logger.warning(f"MCP tool has invalid or missing name: {mcp_tool}")
                return None
            
            # Sanitize tool name for OpenAI (must be alphanumeric with underscores)
            tool_name = tool_name.strip()
            if not tool_name.replace("_", "").replace("-", "_").isalnum():
                # Replace invalid characters with underscores
                import re
                original_name = tool_name
                tool_name = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
                logger.info(f"Sanitized tool name from '{original_name}' to '{tool_name}'")
            
            # Ensure description exists and is valid
            description = mcp_tool.get("description", "")
            if not description or not isinstance(description, str):
                description = f"Execute {tool_name} function"
            
            # Convert MCP input schema to OpenAI parameters format
            input_schema = mcp_tool.get("inputSchema", {})
            openai_parameters = self._convert_schema(input_schema)
            
            # Create OpenAI Realtime tool definition (FLAT structure, not nested)
            realtime_tool = {
                "type": "function",
                "name": tool_name,
                "description": description[:1024],  # Limit description length
                "parameters": openai_parameters
            }
            
            logger.debug(f"Successfully converted tool to Realtime format: {tool_name}")
            return realtime_tool
            
        except Exception as e:
            logger.error(f"Failed to convert MCP tool to Realtime format {mcp_tool.get('name', 'unknown')}: {e}")
            return None
    
    def _validate_openai_tool(self, tool: Dict[str, Any]) -> bool:
        """
        Validate that an OpenAI tool definition meets all requirements.
        
        Args:
            tool: OpenAI tool definition to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            if tool.get("type") != "function":
                return False
            
            function = tool.get("function", {})
            if not function:
                return False
            
            # Check required function fields
            name = function.get("name")
            if not name or not isinstance(name, str) or not name.strip():
                logger.warning(f"Invalid tool name: {name}")
                return False
            
            description = function.get("description")
            if not description or not isinstance(description, str):
                logger.warning(f"Invalid tool description for {name}")
                return False
            
            # Check parameters
            parameters = function.get("parameters", {})
            if not isinstance(parameters, dict):
                logger.warning(f"Invalid parameters for tool {name}")
                return False
            
            # Parameters should have 'type' field
            if "type" not in parameters:
                parameters["type"] = "object"
            
            return True
            
        except Exception as e:
            logger.error(f"Tool validation error: {e}")
            return False
    
    def _convert_schema(self, mcp_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP input schema to OpenAI parameters format.
        
        Args:
            mcp_schema: MCP tool input schema
            
        Returns:
            OpenAI parameters schema
        """
        if not mcp_schema:
            return {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        # Handle different schema formats
        schema_type = mcp_schema.get("type", "object")
        properties = mcp_schema.get("properties", {})
        required = mcp_schema.get("required", [])
        
        # Convert properties to OpenAI format
        converted_properties = {}
        for prop_name, prop_def in properties.items():
            converted_properties[prop_name] = self._convert_property(prop_def)
        
        return {
            "type": schema_type,
            "properties": converted_properties,
            "required": required
        }
    
    def _convert_property(self, prop_def: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single property definition to OpenAI format."""
        converted = {}
        
        # Copy basic fields
        for field in ["type", "description", "enum"]:
            if field in prop_def:
                converted[field] = prop_def[field]
        
        # Handle nested objects and arrays
        if prop_def.get("type") == "object" and "properties" in prop_def:
            converted["properties"] = {}
            for nested_name, nested_def in prop_def["properties"].items():
                converted["properties"][nested_name] = self._convert_property(nested_def)
        
        if prop_def.get("type") == "array" and "items" in prop_def:
            converted["items"] = self._convert_property(prop_def["items"])
        
        return converted
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools in OpenAI format for the Realtime API.
        
        Returns:
            List of OpenAI function definitions
        """
        if not self._initialized:
            logger.warning("Tool mapper not initialized, returning empty tools list")
            return []
        
        return list(self.tool_cache.values())
    
    def get_high_priority_tools(self) -> List[Dict[str, Any]]:
        """
        Get high-priority tools commonly used in voice conversations.
        Returns tools in OpenAI Realtime API format (flat structure).
        
        Returns:
            Subset of tools most relevant for voice interactions in Realtime format
        """
        priority_tool_names = [
            "get_stock_quote",
            "get_stock_history", 
            "get_stock_news",
            "get_market_overview",
            "get_market_movers",
            "get_crypto_price",
            "get_technical_indicators",
            "get_analyst_ratings"
        ]
        
        tools = []
        for tool_name in priority_tool_names:
            if tool_name in self.schema_cache:
                # Get the original MCP tool
                mcp_tool = self.schema_cache[tool_name]
                # Convert to Realtime format (flat structure)
                realtime_tool = self._convert_mcp_to_realtime_tool(mcp_tool)
                if realtime_tool:
                    tools.append(realtime_tool)
        
        logger.info(f"Returning {len(tools)} high-priority tools in Realtime format for voice interaction")
        return tools
    
    def get_realtime_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools in OpenAI Realtime API format (flat structure).
        
        Returns:
            List of tools in Realtime API format
        """
        if not self._initialized:
            logger.warning("Tool mapper not initialized, returning empty tools list")
            return []
        
        realtime_tools = []
        for tool_name, mcp_tool in self.schema_cache.items():
            realtime_tool = self._convert_mcp_to_realtime_tool(mcp_tool)
            if realtime_tool:
                realtime_tools.append(realtime_tool)
        
        logger.info(f"Returning {len(realtime_tools)} tools in Realtime format")
        return realtime_tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool via MCP client.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self._initialized:
            raise RuntimeError("Tool mapper not initialized")
        
        if tool_name not in self.schema_cache:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        try:
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            
            # Execute via MCP client
            result = await self.mcp_client.call_tool(tool_name, arguments)
            
            logger.debug(f"Tool {tool_name} completed successfully")
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "arguments": arguments
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
                "arguments": arguments
            }
    
    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """Get description for a specific tool."""
        if tool_name in self.schema_cache:
            return self.schema_cache[tool_name].get("description")
        return None
    
    def is_streaming_tool(self, tool_name: str) -> bool:
        """Check if a tool supports streaming responses."""
        streaming_tools = [
            "stream_stock_prices",
            "stream_crypto_prices", 
            "stream_market_news",
            "stream_price_alerts"
        ]
        return tool_name in streaming_tools
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on tool mapper and MCP connection."""
        try:
            if not self._initialized:
                return {"status": "error", "message": "Not initialized"}
            
            # Test MCP connection with a simple tool call
            test_result = await self.mcp_client.call_tool("get_market_overview", {})
            
            return {
                "status": "healthy",
                "tools_loaded": len(self.tool_cache),
                "mcp_connection": "active",
                "test_call": "success" if test_result else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "tools_loaded": len(self.tool_cache) if hasattr(self, 'tool_cache') else 0
            }


# Global instance for singleton pattern
_tool_mapper = None

async def get_openai_tool_mapper() -> OpenAIToolMapper:
    """Get or create the global OpenAI tool mapper instance."""
    global _tool_mapper
    
    if _tool_mapper is None:
        _tool_mapper = OpenAIToolMapper()
        await _tool_mapper.initialize()
    elif not _tool_mapper._initialized:
        await _tool_mapper.initialize()
    
    return _tool_mapper