"""
Agent Router
============
API endpoints for the OpenAI agent orchestrator with function calling.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
import time
from datetime import datetime
from services.agent_orchestrator import get_orchestrator
from services.openai_relay_server import openai_relay_server
from services.chart_tool_registry import get_chart_tool_registry
from utils.request_context import set_request_id, get_request_id, generate_request_id
from utils.telemetry import build_request_telemetry, persist_request_log
# Phase 3: Cost tracking
from services.cost_tracker import get_cost_tracker
from models.cost_record import TimeWindow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])

class AgentQuery(BaseModel):
    """Request model for agent queries."""
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    stream: bool = False
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    chart_context: Optional[Dict[str, Any]] = None  # NEW: Current chart state

class AgentResponse(BaseModel):
    """Response model for agent queries."""
    text: str
    tools_used: List[str]
    data: Dict[str, Any]
    timestamp: str
    model: str
    cached: bool = False
    session_id: Optional[str] = None
    request_id: Optional[str] = None  # Phase 3: Request ID for distributed tracing
    # Ensure chart command array is preserved and delivered to frontend
    chart_commands: Optional[List[str]] = None
    chart_commands_structured: Optional[List[Dict[str, Any]]] = None

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

@router.post("/orchestrate")
async def orchestrate_query(body: AgentQuery, request: Request):
    """
    Process a query using the OpenAI agent with function calling.

    This endpoint:
    1. Accepts a user query and optional conversation history
    2. Uses OpenAI to determine which tools to call
    3. Executes the necessary market data tools
    4. Returns a comprehensive response with data

    Phase 2: Supports both streaming and non-streaming based on request.stream
    Phase 3: Request ID propagation for distributed tracing
    """
    # Phase 3: Extract or generate request ID
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)

    telemetry = build_request_telemetry(
        request,
        request_id,
        session_id=body.session_id,
        user_id=body.user_id,
    )

    # Phase 2: If client requested streaming, redirect to streaming logic
    if body.stream:
        return await stream_query(body, request)

    start_time = time.perf_counter()
    cost_tracker = get_cost_tracker()

    try:
        orchestrator = get_orchestrator()

        logger.info(
            "agent_query_received",
            extra=telemetry.for_logging(
                timestamp=datetime.utcnow().isoformat(),
                query=body.query,
                stream=body.stream,
            ),
        )

        # Process the query (non-streaming)
        result = await orchestrator.process_query(
            query=body.query,
            conversation_history=body.conversation_history,
            stream=False,  # Non-streaming path
            chart_context=body.chart_context,  # Pass chart context if provided
            request_id=request_id  # Phase 3: Pass request ID for tracing
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        cost_summary = cost_tracker.get_cost_summary_for_request(request_id)
        completed_telemetry = telemetry.with_duration(duration_ms).with_cost_summary(cost_summary)

        # Add session ID and request ID if provided
        if body.session_id:
            result["session_id"] = body.session_id
        result["request_id"] = request_id
        if cost_summary:
            result["cost_summary"] = cost_summary

        response_preview = (result.get("text") or "")[:250] or None

        logger.info(
            "agent_query_completed",
            extra=completed_telemetry.for_logging(
                timestamp=datetime.utcnow().isoformat(),
                session_id=result.get("session_id"),
                model=result.get("model"),
                tools_used=result.get("tools_used", []),
                chart_commands=result.get("chart_commands"),
                response_preview=response_preview,
            ),
        )

        await persist_request_log(
            completed_telemetry,
            {
                "event": "agent_query_completed",
                "query": body.query,
                "response_preview": response_preview,
                "tools_used": result.get("tools_used", []),
                "chart_commands": result.get("chart_commands"),
            },
        )

        return AgentResponse(**result)
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        error_telemetry = telemetry.with_duration(duration_ms)
        logger.error(
            "Error in agent orchestration",
            exc_info=True,
            extra=error_telemetry.for_logging(message=str(e)),
        )
        await persist_request_log(
            error_telemetry,
            {
                "event": "agent_query_error",
                "query": body.query,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_query(body: AgentQuery, request: Request):
    """
    Stream a response from the agent.

    Returns a streaming response that yields text chunks as they're generated.
    Note: Tool calling happens before streaming begins.
    Phase 3: Request ID propagation for distributed tracing
    """
    # Phase 3: Extract or generate request ID
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)

    if not body.stream:
        # If not streaming, redirect to regular orchestrate
        return await orchestrate_query(body, request)

    start_time = time.perf_counter()
    cost_tracker = get_cost_tracker()

    try:
        orchestrator = get_orchestrator()

        async def generate():
            """Generate TRUE streaming response with progressive tool execution."""
            # First, send metadata about the query
            metadata = {
                "type": "metadata",
                "session_id": body.session_id,
                "request_id": request_id,  # Phase 3: Include request ID in stream
                "model": orchestrator.model,
                "streaming": True,
                "version": "2.0"  # New streaming version
            }
            yield f"data: {json.dumps(metadata)}\n\n"

            # Stream the response with progressive updates
            async for chunk in orchestrator.stream_query(
                query=body.query,
                conversation_history=body.conversation_history,
                request_id=request_id  # Phase 3: Pass request ID to orchestrator
            ):
                # The new stream_query yields dictionaries with type and data
                # Types: content, tool_start, tool_result, done, error
                if chunk.get("type") == "content":
                    logger.debug(
                        "agent_stream_chunk",
                        extra=telemetry.for_logging(chunk_type=chunk.get("type")),
                    )
                yield f"data: {json.dumps(chunk)}\n\n"

                # If this is the done signal, we're finished
                if chunk.get("type") == "done":
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    cost_summary = cost_tracker.get_cost_summary_for_request(request_id)
                    completed_telemetry = telemetry.with_duration(duration_ms).with_cost_summary(cost_summary)
                    logger.info(
                        "agent_stream_completed",
                        extra=completed_telemetry.for_logging(
                            tools_used=chunk.get("tools_used", []),
                            chart_commands=chunk.get("chart_commands"),
                        ),
                    )
                    await persist_request_log(
                        completed_telemetry,
                        {
                            "event": "agent_stream_completed",
                            "query": body.query,
                            "tools_used": chunk.get("tools_used", []),
                            "chart_commands": chunk.get("chart_commands"),
                        },
                    )
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
        duration_ms = (time.perf_counter() - start_time) * 1000
        error_telemetry = telemetry.with_duration(duration_ms)
        logger.error(
            "Error in agent streaming",
            exc_info=True,
            extra=error_telemetry.for_logging(message=str(e)),
        )
        await persist_request_log(
            error_telemetry,
            {
                "event": "agent_stream_error",
                "query": body.query,
                "error": str(e),
            },
        )
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
            conversation_history=request.conversation_history,
            chart_context=request.chart_context  # Pass chart context if provided
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
            chart_commands=result.get("chart_commands"),
            chart_commands_structured=result.get("chart_commands_structured")
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


# ============================================================================
# Phase 3: Cost Tracking Endpoints
# ============================================================================

@router.get("/costs/summary")
async def get_cost_summary(
    window: str = "day",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """
    Get cost summary for a time window.

    Phase 3: Observability Infrastructure - Cost Tracking

    Args:
        window: Time window (hour, day, week, month, custom)
        start_time: ISO format datetime for custom window
        end_time: ISO format datetime for custom window

    Returns:
        CostSummary with aggregated cost data
    """
    try:
        cost_tracker = get_cost_tracker()

        # Parse time window
        try:
            time_window = TimeWindow(window.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid window: {window}. Must be one of: hour, day, week, month, custom"
            )

        # Parse custom time range if provided
        start_dt = None
        end_dt = None
        if time_window == TimeWindow.CUSTOM:
            if not start_time or not end_time:
                raise HTTPException(
                    status_code=400,
                    detail="start_time and end_time required for custom window"
                )
            try:
                from datetime import datetime
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")

        # Get summary
        summary = cost_tracker.get_summary(
            window=time_window,
            start_time=start_dt,
            end_time=end_dt
        )

        return {
            "period_start": summary.period_start.isoformat(),
            "period_end": summary.period_end.isoformat(),
            "total_requests": summary.total_requests,
            "total_tokens": summary.total_tokens,
            "total_cost_usd": summary.total_cost_usd,
            "avg_cost_per_request_usd": summary.avg_cost_per_request_usd,
            "cost_by_model": summary.cost_by_model,
            "cost_by_endpoint": summary.cost_by_endpoint,
            "cost_by_intent": summary.cost_by_intent,
            "total_cached_savings_usd": summary.total_cached_savings_usd,
            "cache_hit_rate": summary.cache_hit_rate
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/stats")
async def get_cost_stats():
    """
    Get overall cost tracking statistics.

    Phase 3: Observability Infrastructure - Cost Tracking

    Returns:
        Overall statistics including total cost, records, models used
    """
    try:
        cost_tracker = get_cost_tracker()
        stats = cost_tracker.get_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting cost stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/recent")
async def get_recent_costs(limit: int = 100):
    """
    Get recent cost records.

    Phase 3: Observability Infrastructure - Cost Tracking

    Args:
        limit: Maximum number of records to return (default: 100, max: 1000)

    Returns:
        List of recent cost records with request details
    """
    try:
        if limit > 1000:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")

        cost_tracker = get_cost_tracker()
        records = cost_tracker.get_recent_records(limit=limit)

        # Convert to serializable format
        return [
            {
                "request_id": record.request_id,
                "timestamp": record.timestamp.isoformat(),
                "model": record.model,
                "tokens": {
                    "prompt_tokens": record.tokens.prompt_tokens,
                    "completion_tokens": record.tokens.completion_tokens,
                    "total_tokens": record.tokens.total_tokens,
                    "cached_tokens": record.tokens.cached_tokens
                },
                "cost_usd": record.cost_usd,
                "input_cost_usd": record.input_cost_usd,
                "output_cost_usd": record.output_cost_usd,
                "cached_savings_usd": record.cached_savings_usd,
                "tags": {
                    "endpoint": record.tags.endpoint,
                    "session_id": record.tags.session_id,
                    "user_id": record.tags.user_id,
                    "intent": record.tags.intent,
                    "tools_used": record.tags.tools_used,
                    "stream": record.tags.stream
                }
            }
            for record in records
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
