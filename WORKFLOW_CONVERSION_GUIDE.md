"""
OpenAI Workflows API Adapter for G'sves Assistant
Connects Python backend to Agent Builder workflow
"""

from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)


class WorkflowAdapter:
    """
    Adapter for executing Agent Builder workflows via API.
    Replaces direct Responses API calls with workflow execution.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.workflow_id = os.getenv("GVSES_WORKFLOW_ID")  # e.g., wf_68e474d14d28819085

        if not self.workflow_id:
            raise ValueError("GVSES_WORKFLOW_ID not set in environment")

        logger.info(f"Workflow adapter initialized with ID: {self.workflow_id}")

    async def run_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with user query.

        Args:
            query: User's query text
            conversation_history: Previous messages (optional)
            tools: Ignored (workflow manages tools internally)

        Returns:
            Standardized response dict
        """
        logger.info(f"Executing workflow for query: {query[:50]}...")

        try:
            # Call Workflows API (hypothetical endpoint based on Agent Builder)
            # Note: This is the expected API format when Workflows API releases
            response = await self.client.workflows.run(
                workflow_id=self.workflow_id,
                input={
                    "user_query": query,
                    "conversation_history": conversation_history or []
                }
            )

            # Extract response from workflow output
            return {
                "text": response.output.get("text", ""),
                "tools_used": response.output.get("tools_used", []),
                "chart_commands": response.output.get("chart_commands", []),
                "model": response.output.get("model", f"workflow-{self.workflow_id}"),
                "data": response.output.get("data", {}),
                "timestamp": response.completed_at or datetime.now().isoformat(),
                "cached": False,
                "session_id": None,
                "workflow_id": self.workflow_id,
                "workflow_version": response.version
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")

            # Return error response in standard format
            return {
                "text": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "tools_used": [],
                "chart_commands": [],
                "model": "error",
                "data": {"error": str(e)},
                "timestamp": datetime.now().isoformat(),
                "cached": False
            }

    async def stream_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream workflow execution events.

        Yields:
            Event dicts with incremental updates
        """
        logger.info(f"Streaming workflow for query: {query[:50]}...")

        try:
            # Stream workflow execution (hypothetical API)
            async for event in self.client.workflows.stream(
                workflow_id=self.workflow_id,
                input={
                    "user_query": query,
                    "conversation_history": conversation_history or []
                }
            ):
                # Yield standardized event format
                yield {
                    "type": event.type,  # "node_start", "node_complete", "tool_call", "output"
                    "node": event.node_name,
                    "text": event.text_delta or "",
                    "done": event.is_complete,
                    "timestamp": event.timestamp
                }

        except Exception as e:
            logger.error(f"Workflow streaming failed: {e}")
            yield {
                "type": "error",
                "text": str(e),
                "done": True,
                "timestamp": datetime.now().isoformat()
            }

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get adapter metadata."""
        return {
            "adapter_type": "workflows",
            "workflow_id": self.workflow_id,
            "backend": "agent_builder"
        }

    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Manual tool invocation not supported (workflow manages tools).
        """
        raise NotImplementedError(
            "Workflows adapter does not support manual tool invocation. "
            "Tools are managed by the workflow graph."
        )

    async def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get workflow metadata from Agent Builder.

        Returns:
            Workflow details (name, version, nodes, etc.)
        """
        try:
            info = await self.client.workflows.get(self.workflow_id)
            return {
                "id": info.id,
                "name": info.name,
                "version": info.version,
                "nodes": [n.name for n in info.nodes],
                "created_at": info.created_at,
                "updated_at": info.updated_at
            }
        except Exception as e:
            logger.error(f"Failed to fetch workflow info: {e}")
            return {}
