#!/usr/bin/env python3
"""
Orchestrator Performance Profiler
=================================
Instrument key AgentOrchestrator phases (knowledge retrieval, cache usage,
Responses API calls, tool execution) to understand latency bottlenecks.
"""

import asyncio
import contextvars
import json
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from services.agent_orchestrator import AgentOrchestrator, get_orchestrator
from services.vector_retriever import VectorRetriever

# Context variable to collect per-query timing data inside async wrappers
_current_timings: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "current_timings", default=None
)

# Track original class methods for restoration
_PATCHED_METHODS: List[Tuple[Any, str, Any]] = []


def _patch_method(cls: Any, attr: str, wrapper: Any) -> None:
    """Patch a class method and remember the original for restoration."""
    original = getattr(cls, attr)
    _PATCHED_METHODS.append((cls, attr, original))
    setattr(cls, attr, wrapper)


async def _instrumented_embed_query(self, query: str) -> Optional[List[float]]:  # type: ignore[override]
    timings = _current_timings.get()
    start = time.perf_counter()
    error: Optional[BaseException] = None
    try:
        result = await _ORIGINALS['embed_query'](self, query)
        return result
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        error = exc
        raise
    finally:
        if timings is not None:
            timings.setdefault("embedding_calls", []).append({
                "query": query,
                "duration": time.perf_counter() - start,
                "error": error.__class__.__name__ if error else None,
            })


async def _instrumented_search_knowledge(  # type: ignore[override]
    self,
    query: str,
    top_k: int = 3,
    min_score: float = 0.65,
) -> List[Dict[str, Any]]:
    timings = _current_timings.get()
    start = time.perf_counter()
    error: Optional[BaseException] = None
    result: List[Dict[str, Any]] = []
    try:
        result = await _ORIGINALS['search_knowledge'](self, query, top_k=top_k, min_score=min_score)
        return result
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        error = exc
        raise
    finally:
        if timings is not None:
            timings.setdefault("knowledge_searches", []).append({
                "query": query,
                "duration": time.perf_counter() - start,
                "results": len(result) if result else 0,
                "min_score": min_score,
                "error": error.__class__.__name__ if error else None,
            })


async def _instrumented_get_cached_knowledge(  # type: ignore[override]
    self,
    query: str,
) -> str:
    timings = _current_timings.get()
    start = time.perf_counter()
    error: Optional[BaseException] = None
    result: Optional[str] = None
    try:
        result = await _ORIGINALS['get_cached_knowledge'](self, query)
        return result
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        error = exc
        raise
    finally:
        if timings is not None:
            timings.setdefault("knowledge_cache_calls", []).append({
                "query": query,
                "duration": time.perf_counter() - start,
                "result_chars": len(result) if isinstance(result, str) else 0,
                "error": error.__class__.__name__ if error else None,
            })


async def _instrumented_get_cached_response(  # type: ignore[override]
    self,
    query: str,
    context: str = "",
) -> Optional[Dict[str, Any]]:
    timings = _current_timings.get()
    start = time.perf_counter()
    error: Optional[BaseException] = None
    result: Optional[Dict[str, Any]] = None
    try:
        result = await _ORIGINALS['get_cached_response'](self, query, context)
        return result
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        error = exc
        raise
    finally:
        if timings is not None:
            timings.setdefault("response_cache_checks", []).append({
                "query": query,
                "duration": time.perf_counter() - start,
                "hit": bool(result),
                "error": error.__class__.__name__ if error else None,
            })


async def _instrumented_cache_response(  # type: ignore[override]
    self,
    query: str,
    context: str,
    response: Dict[str, Any],
) -> None:
    timings = _current_timings.get()
    start = time.perf_counter()
    error: Optional[BaseException] = None
    try:
        await _ORIGINALS['cache_response'](self, query, context, response)
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        error = exc
        raise
    finally:
        if timings is not None:
            timings.setdefault("response_cache_writes", []).append({
                "query": query,
                "duration": time.perf_counter() - start,
                "error": error.__class__.__name__ if error else None,
            })


async def _instrumented_execute_tool_with_timeout(  # type: ignore[override]
    self,
    function_name: str,
    function_args: Dict[str, Any],
) -> Any:
    timings = _current_timings.get()
    start = time.perf_counter()
    status = "success"
    result: Any = None
    try:
        result = await _ORIGINALS['execute_tool_with_timeout'](self, function_name, function_args)
        return result
    except Exception as exc:  # pragma: no cover - diagnostic wrapper
        status = f"error:{exc.__class__.__name__}"
        raise
    finally:
        if timings is not None:
            entry: Dict[str, Any] = {
                "tool": function_name,
                "duration": time.perf_counter() - start,
                "status": status,
            }
            if isinstance(result, dict):
                entry["result_status"] = result.get("status")
            timings.setdefault("tool_calls", []).append(entry)


_ORIGINALS: Dict[str, Any] = {}


def install_instrumentation() -> None:
    """Monkey patch key AgentOrchestrator and VectorRetriever methods."""
    _ORIGINALS.update({
        'embed_query': VectorRetriever.embed_query,
        'search_knowledge': VectorRetriever.search_knowledge,
        'get_cached_knowledge': AgentOrchestrator._get_cached_knowledge,
        'get_cached_response': AgentOrchestrator._get_cached_response,
        'cache_response': AgentOrchestrator._cache_response,
        'execute_tool_with_timeout': AgentOrchestrator._execute_tool_with_timeout,
    })

    _patch_method(VectorRetriever, 'embed_query', _instrumented_embed_query)
    _patch_method(VectorRetriever, 'search_knowledge', _instrumented_search_knowledge)
    _patch_method(AgentOrchestrator, '_get_cached_knowledge', _instrumented_get_cached_knowledge)
    _patch_method(AgentOrchestrator, '_get_cached_response', _instrumented_get_cached_response)
    _patch_method(AgentOrchestrator, '_cache_response', _instrumented_cache_response)
    _patch_method(AgentOrchestrator, '_execute_tool_with_timeout', _instrumented_execute_tool_with_timeout)


def restore_instrumentation() -> None:
    """Restore original methods after profiling."""
    while _PATCHED_METHODS:
        cls, attr, original = _PATCHED_METHODS.pop()
        setattr(cls, attr, original)
    _PATCHED_METHODS.clear()
    _ORIGINALS.clear()


async def profile_query(
    orchestrator: AgentOrchestrator,
    query: str,
    label: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Profile a single orchestrator query, returning timing details."""
    timings: Dict[str, Any] = {
        "label": label,
        "query": query,
    }
    token = _current_timings.set(timings)

    responses_client = getattr(orchestrator, "_responses_client", None)
    original_create = None

    if responses_client and hasattr(responses_client, "create"):
        original_create = responses_client.create

        async def _instrumented_create(*args, **kwargs):
            rc_timings = _current_timings.get()
            start = time.perf_counter()
            error: Optional[BaseException] = None
            try:
                response = await original_create(*args, **kwargs)
                return response
            except Exception as exc:  # pragma: no cover - diagnostic wrapper
                error = exc
                raise
            finally:
                if rc_timings is not None:
                    rc_timings.setdefault("responses_api_calls", []).append({
                        "duration": time.perf_counter() - start,
                        "error": error.__class__.__name__ if error else None,
                    })

        responses_client.create = _instrumented_create  # type: ignore[assignment]

    start_total = time.perf_counter()
    result = await orchestrator.process_query(
        query,
        conversation_history=conversation_history,
        stream=False,
    )
    total_duration = time.perf_counter() - start_total
    timings["total_duration"] = total_duration
    timings["cached_response"] = bool(result.get("cached"))
    timings["tool_count"] = len(result.get("tools_used") or [])

    if responses_client and original_create:
        responses_client.create = original_create  # type: ignore[assignment]

    _current_timings.reset(token)
    return timings


def summarize_timings(timings: Dict[str, Any]) -> Dict[str, Any]:
    """Create a compact summary with key durations for quick inspection."""
    summary = {
        "label": timings.get("label"),
        "total": timings.get("total_duration"),
        "cached_response": timings.get("cached_response"),
    }

    def _max_duration(entries: List[Dict[str, Any]]) -> float:
        return max((entry.get("duration", 0.0) for entry in entries), default=0.0)

    summary["embed_max"] = _max_duration(timings.get("embedding_calls", []))
    summary["search_max"] = _max_duration(timings.get("knowledge_searches", []))
    summary["responses_api"] = _max_duration(timings.get("responses_api_calls", []))
    summary["tool_max"] = _max_duration(timings.get("tool_calls", []))
    summary["knowledge_cache"] = _max_duration(timings.get("knowledge_cache_calls", []))
    return summary


async def main() -> None:
    install_instrumentation()
    orchestrator = get_orchestrator()

    # Representative queries (cold vs warm) matching smoke/regression tests
    queries = [
        ("Explain MACD indicator", "MACD cold"),
        ("Explain MACD indicator", "MACD warm"),
        ("What is RSI indicator?", "RSI cold"),
        ("What is RSI indicator?", "RSI warm"),
    ]

    all_timings: List[Dict[str, Any]] = []

    try:
        for query, label in queries:
            timings = await profile_query(orchestrator, query, label)
            all_timings.append(timings)
            summary = summarize_timings(timings)
            print(
                f"{label:<12} | total={summary['total']:.2f}s | embed={summary['embed_max']:.2f}s | "
                f"search={summary['search_max']:.2f}s | responses={summary['responses_api']:.2f}s | "
                f"cached={summary['cached_response']}"
            )
            await asyncio.sleep(1.0)

    finally:
        restore_instrumentation()

    # Pretty print full timing data as JSON for deeper inspection
    print("\nFull timing data:\n")
    json.dump(all_timings, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    asyncio.run(main())
