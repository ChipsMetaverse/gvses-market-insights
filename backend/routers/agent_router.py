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
from datetime import datetime
from services.agent_orchestrator import get_orchestrator
from services.openai_relay_server import openai_relay_server
from services.chart_tool_registry import get_chart_tool_registry

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
    # Ensure chart command array is preserved and delivered to frontend
    chart_commands: Optional[List[str]] = None

class ToolSchema(BaseModel):
    """Model for tool schema information."""
    name: str
    description: str
    parameters: Dict[str, Any]


class ChartImageRequest(BaseModel):
    """Request model for chart image analysis."""
    image_base64: str
    context: Optional[str] = None


class ChartSnapshotIngestRequest(BaseModel):
    """Payload for ingesting chart snapshots from headless service."""

    symbol: str
    timeframe: str
    image_base64: str
    chart_commands: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    vision_model: Optional[str] = None
    auto_analyze: Optional[bool] = None


class ChartSnapshotResponse(BaseModel):
    """Response model for chart snapshot operations."""

    symbol: str
    timeframe: str
    captured_at: datetime
    chart_commands: List[str]
    metadata: Dict[str, Any]
    vision_model: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    analysis_error: Optional[str] = None

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

        logger.info(
            "agent_query_received",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "query": request.query,
                "session_id": request.session_id,
                "stream": request.stream,
            },
        )

        # Process the query
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=request.conversation_history,
            stream=False  # Streaming handled separately
        )

        # Add session ID if provided
        if request.session_id:
            result["session_id"] = request.session_id

        logger.info(
            "agent_query_completed",
            extra={
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": result.get("session_id"),
                "model": result.get("model"),
                "tools_used": result.get("tools_used", []),
                "chart_commands": result.get("chart_commands"),
            },
        )

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
            """Generate TRUE streaming response with progressive tool execution."""
            # First, send metadata about the query
            metadata = {
                "type": "metadata",
                "session_id": request.session_id,
                "model": orchestrator.model,
                "streaming": True,
                "version": "2.0"  # New streaming version
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
            # Stream the response with progressive updates
            async for chunk in orchestrator.stream_query(
                query=request.query,
                conversation_history=request.conversation_history
            ):
                # The new stream_query yields dictionaries with type and data
                # Types: content, tool_start, tool_result, done, error
                yield f"data: {json.dumps(chunk)}\n\n"
                
                # If this is the done signal, we're finished
                if chunk.get("type") == "done":
                    break
        
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

@router.get("/tools/chart")
async def get_chart_tools():
    """
    Get all available chart manipulation tools derived from knowledge base.

    Returns chart indicators, drawing tools, and other chart controls
    that the voice agent can use to manipulate the trading chart.
    """
    try:
        registry = get_chart_tool_registry()
        tools = registry.get_all_tools()

        return {
            "tools": tools,
            "count": len(tools),
            "categories": list(set(tool["category"] for tool in tools))
        }

    except Exception as e:
        logger.error(f"Error getting chart tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/chart/search")
async def search_chart_tools(query: str, top_k: int = 5):
    """
    Search for chart tools using semantic search.

    Args:
        query: Natural language query (e.g., "show momentum indicators")
        top_k: Maximum number of results to return

    Returns:
        List of relevant chart tools with knowledge base context
    """
    try:
        registry = get_chart_tool_registry()
        tools = await registry.search_tools_by_query(query, top_k=top_k)

        return {
            "query": query,
            "tools": [tool.to_dict() for tool in tools],
            "count": len(tools)
        }

    except Exception as e:
        logger.error(f"Error searching chart tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agent_health():
    """Check agent service health."""
    try:
        orchestrator = get_orchestrator()

        # Try to get tool schemas as a health check
        schemas = orchestrator._get_tool_schemas()

        # Check chart tool registry
        try:
            registry = get_chart_tool_registry()
            chart_tools_count = len(registry.tools)
        except Exception:
            chart_tools_count = 0

        return {
            "status": "healthy",
            "model": orchestrator.model,
            "tools_available": len(schemas),
            "chart_tools_available": chart_tools_count,
            "cache_size": len(orchestrator.cache),
            "education_mode": "llm" if orchestrator.use_llm_for_education else "template"
        }

    except Exception as e:
        logger.error(f"Agent health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/test/toggle-education-mode")
async def toggle_education_mode(enabled: bool):
    """Toggle education mode between LLM and templates (for A/B testing)."""
    try:
        orchestrator = get_orchestrator()
        orchestrator.use_llm_for_education = enabled
        mode = "LLM" if enabled else "Templates"
        logger.info(f"Education mode toggled to: {mode}")
        
        return {
            "status": "success",
            "education_mode": mode,
            "use_llm_for_education": enabled,
            "message": f"Educational queries will now use {mode}"
        }
        
    except Exception as e:
        logger.error(f"Error toggling education mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-chart")
async def analyze_chart(request: ChartImageRequest):
    """Analyze a chart image using the vision model-based analyzer."""
    orchestrator = get_orchestrator()
    analyzer = getattr(orchestrator, "chart_image_analyzer", None)
    if not analyzer:
        logger.error("Chart image analyzer unavailable")
        raise HTTPException(status_code=503, detail="Chart analysis is currently unavailable")

    try:
        result = await analyzer.analyze_chart(
            image_base64=request.image_base64,
            user_context=request.context,
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing chart image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chart-snapshot", response_model=ChartSnapshotResponse)
async def ingest_chart_snapshot(request: ChartSnapshotIngestRequest):
    """Ingest a chart snapshot and optionally trigger automated analysis."""

    orchestrator = get_orchestrator()
    try:
        result = await orchestrator.ingest_chart_snapshot(
            symbol=request.symbol,
            timeframe=request.timeframe,
            image_base64=request.image_base64,
            chart_commands=request.chart_commands,
            metadata=request.metadata,
            vision_model=request.vision_model,
            auto_analyze=request.auto_analyze,
        )
        return ChartSnapshotResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        logger.error(f"Chart snapshot ingestion failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to ingest chart snapshot")


@router.get("/chart-snapshot/{symbol}", response_model=Optional[ChartSnapshotResponse])
async def get_latest_chart_snapshot(symbol: str, timeframe: Optional[str] = None, include_image: bool = False):
    """Return the latest chart snapshot for a symbol/timeframe."""

    orchestrator = get_orchestrator()
    snapshot = await orchestrator.get_chart_state(
        symbol=symbol,
        timeframe=timeframe,
        include_image=include_image,
    )
    if not snapshot:
        return None

    if not include_image:
        snapshot.pop("image_base64", None)

    return ChartSnapshotResponse(**snapshot)


@router.post("/voice-query")
async def process_voice_query(request: AgentQuery):
    """
    Process a voice query: agent processes it and sends response to TTS.
    
    This is the integration point between the agent and voice interface:
    1. Receives transcript from STT
    2. Agent processes query with tools
    3. Sends response text to TTS via Realtime API
    
    Returns the agent response data (text version).
    """
    try:
        # Get the orchestrator
        orchestrator = get_orchestrator()
        
        # Process the query with the agent
        if request.stream:
            # For streaming, we'd need a different approach
            raise HTTPException(status_code=400, detail="Streaming not supported for voice queries")
        
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=request.conversation_history
        )
        
        # Send the response text to TTS if session_id provided
        if request.session_id and result.get("text"):
            tts_success = await openai_relay_server.send_tts_to_session(
                session_id=request.session_id,
                text=result["text"]
            )
            
            if not tts_success:
                logger.warning(f"Failed to send TTS for session {request.session_id}")
                # Continue anyway - the text response is still valid
        
        # Return the agent response
        return AgentResponse(
            text=result["text"],
            tools_used=result.get("tools_used", []),
            data=result.get("data", {}),
            timestamp=result["timestamp"],
            model=result.get("model", "unknown"),
            cached=result.get("cached", False),
            session_id=request.session_id,
            chart_commands=result.get("chart_commands")
        )
        
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Phase 3: Pattern Verdict Endpoints

class PatternVerdict(BaseModel):
    """Request model for pattern verdict submission."""
    pattern_id: str
    verdict: str  # 'accepted', 'rejected', 'deferred'
    operator_id: Optional[str] = None
    notes: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    

class PatternVerdictResponse(BaseModel):
    """Response model for pattern verdict operations."""
    pattern_id: str
    verdict: str
    submitted_at: datetime
    operator_id: Optional[str]
    notes: Optional[str]
    symbol: Optional[str]
    timeframe: Optional[str]


class PatternHistoryEntry(BaseModel):
    """Model for pattern verdict history entry."""
    pattern_id: str
    verdict: str
    submitted_at: datetime
    operator_id: Optional[str]
    notes: Optional[str]
    symbol: str
    timeframe: str
    pattern_type: Optional[str]
    confidence: Optional[float]


@router.post("/pattern-verdict", response_model=PatternVerdictResponse)
async def submit_pattern_verdict(verdict: PatternVerdict, background_tasks: BackgroundTasks):
    """
    Submit analyst verdict for a pattern.
    
    This endpoint:
    1. Records the analyst's decision (accept/reject/defer)
    2. Updates pattern state in the system
    3. Triggers pattern overlay updates via WebSocket
    4. Creates audit trail for compliance
    """
    try:
        orchestrator = get_orchestrator()
        
        # Store verdict in snapshot store
        snapshot_store = getattr(orchestrator, "chart_snapshot_store", None)
        if not snapshot_store:
            raise HTTPException(status_code=503, detail="Chart snapshot store unavailable")
        
        # Record the verdict
        symbol = verdict.symbol.upper() if verdict.symbol else None
        timeframe = verdict.timeframe.upper() if verdict.timeframe else None

        verdict_data = {
            "pattern_id": verdict.pattern_id,
            "verdict": verdict.verdict,
            "submitted_at": datetime.utcnow(),
            "operator_id": verdict.operator_id or "anonymous",
            "notes": verdict.notes,
            "symbol": symbol,
            "timeframe": timeframe,
        }
        
        # Store verdict (implementation will be in chart_snapshot_store)
        await snapshot_store.store_pattern_verdict(verdict_data)
        
        # Trigger background update to pattern lifecycle
        background_tasks.add_task(
            orchestrator.update_pattern_lifecycle,
            pattern_id=verdict.pattern_id,
            verdict=verdict.verdict,
            operator_id=verdict.operator_id or "anonymous",
            notes=verdict.notes,
            symbol=symbol,
            timeframe=timeframe,
        )
        
        logger.info(
            "pattern_verdict_submitted",
            extra={
                "pattern_id": verdict.pattern_id,
                "verdict": verdict.verdict,
                "operator": verdict.operator_id,
                "symbol": verdict.symbol
            }
        )
        
        return PatternVerdictResponse(**verdict_data)
        
    except Exception as e:
        logger.error(f"Error submitting pattern verdict: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pattern-history", response_model=List[PatternHistoryEntry])
async def get_pattern_history(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    operator_id: Optional[str] = None,
    limit: int = 100
):
    """
    Retrieve pattern verdict history with optional filtering.
    
    This endpoint provides audit trail and analytics for:
    - Pattern validation accuracy over time
    - Operator performance metrics
    - Pattern success rates by type
    """
    try:
        orchestrator = get_orchestrator()
        snapshot_store = getattr(orchestrator, "chart_snapshot_store", None)
        
        if not snapshot_store:
            raise HTTPException(status_code=503, detail="Chart snapshot store unavailable")
        
        # Retrieve verdict history
        history = await snapshot_store.get_pattern_history(
            symbol=symbol,
            timeframe=timeframe,
            operator_id=operator_id,
            limit=limit
        )
        
        # Convert to response models
        entries = []
        for record in history:
            entries.append(PatternHistoryEntry(
                pattern_id=record["pattern_id"],
                verdict=record["verdict"],
                submitted_at=record["submitted_at"],
                operator_id=record.get("operator_id"),
                notes=record.get("notes"),
                symbol=record["symbol"],
                timeframe=record["timeframe"],
                pattern_type=record.get("pattern_type"),
                confidence=record.get("confidence")
            ))
        
        return entries
        
    except Exception as e:
        logger.error(f"Error retrieving pattern history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
