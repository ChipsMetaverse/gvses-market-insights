"""
Agent Router
============
API endpoints for the OpenAI agent orchestrator with function calling.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from services.agent_orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])

class AgentQuery(BaseModel):
    """Request model for agent queries."""
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    stream: bool = False
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class AgentResponse(BaseModel):
    """Response model for agent queries."""
    text: str
    tools_used: List[str]
    data: Dict[str, Any]
    timestamp: str
    model: str
    cached: bool = False
    session_id: Optional[str] = None

class ToolSchema(BaseModel):
    """Model for tool schema information."""
    name: str
    description: str
    parameters: Dict[str, Any]

@router.post("/orchestrate", response_model=AgentResponse)
async def orchestrate_query(request: AgentQuery):
    """
    Process a query using the OpenAI agent with function calling.
    
    This endpoint:
    1. Accepts a user query and optional conversation history
    2. Uses OpenAI to determine which tools to call
    3. Executes the necessary market data tools
    4. Returns a comprehensive response with data
    """
    try:
        orchestrator = get_orchestrator()
        
        # Process the query
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=request.conversation_history,
            stream=False  # Streaming handled separately
        )
        
        # Add session ID if provided
        if request.session_id:
            result["session_id"] = request.session_id
        
        return AgentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in agent orchestration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_query(request: AgentQuery):
    """
    Stream a response from the agent.
    
    Returns a streaming response that yields text chunks as they're generated.
    Note: Tool calling happens before streaming begins.
    """
    if not request.stream:
        # If not streaming, redirect to regular orchestrate
        return await orchestrate_query(request)
    
    try:
        orchestrator = get_orchestrator()
        
        async def generate():
            """Generate streaming response."""
            # First, send metadata about the query
            metadata = {
                "type": "metadata",
                "session_id": request.session_id,
                "model": orchestrator.model
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
            # Stream the response
            async for chunk in orchestrator.stream_query(
                query=request.query,
                conversation_history=request.conversation_history
            ):
                data = {
                    "type": "content",
                    "text": chunk
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error(f"Error in agent streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools", response_model=List[ToolSchema])
async def get_available_tools():
    """
    Get list of available tools the agent can use.
    
    This is useful for debugging and for showing users what capabilities
    the agent has access to.
    """
    try:
        orchestrator = get_orchestrator()
        schemas = orchestrator._get_tool_schemas()
        
        # Extract tool information
        tools = []
        for schema in schemas:
            function = schema["function"]
            tools.append(ToolSchema(
                name=function["name"],
                description=function["description"],
                parameters=function["parameters"]
            ))
        
        return tools
        
    except Exception as e:
        logger.error(f"Error getting tool schemas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-cache")
async def clear_cache():
    """
    Clear the agent's tool result cache.
    
    This is useful when you want to force fresh data fetching.
    """
    try:
        orchestrator = get_orchestrator()
        orchestrator.clear_cache()
        
        return {"status": "success", "message": "Cache cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def agent_health():
    """Check agent service health."""
    try:
        orchestrator = get_orchestrator()
        
        # Try to get tool schemas as a health check
        schemas = orchestrator._get_tool_schemas()
        
        return {
            "status": "healthy",
            "model": orchestrator.model,
            "tools_available": len(schemas),
            "cache_size": len(orchestrator.cache)
        }
        
    except Exception as e:
        logger.error(f"Agent health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }