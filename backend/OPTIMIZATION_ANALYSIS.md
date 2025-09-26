# Optimization Analysis and Plan

This document captures the current latency profile, key bottlenecks, and concrete changes to make the agent fast and reliable.

## Goals (SLAs)
- Price-only queries: 2–4s P50, <6s P95
- Technical analysis (TA): 6–9s P50, <12s P95
- News queries: 5–8s P50, <12s P95

## Current State (summary)
- Two execution paths exist (feature-flagged):
  - Default: Single‑pass Chat Completions with function calling (fast and predictable)
  - Optional: OpenAI Responses API (USE_RESPONSES=true)
- Tools run in parallel; news is gated by intent; token budgets trimmed.
- Chart commands + TA drawing are generated server‑side and returned once.

## Main Bottlenecks Observed
- LLM “second pass” (when used): adds 10–22s if not skipped.
- Tool calls in sequence (when a code path misses parallelization).
- News fetch on non-news queries (avoidable 1–3s).
- Excess tokens in prompts/responses.
- Persistence or network hiccups (Supabase save and MCP clients) on the hot path.

## Optimizations (Actionable)
1) Keep single‑pass by default
- Route via `process_query -> _process_query_single_pass` (Chat Completions). Use `USE_RESPONSES=true` only when testing Responses path.

2) Parallelize all tools consistently
- Ensure `responses` path uses `_execute_tools_parallel` (already implemented). Verify no sequential loops remain.

3) Skip second LLM call
- In Responses path, use preliminary text when sufficient. Only do a second call for clearly technical/swing cases lacking text.

4) Reduce tokens
- Set `max_output_tokens`/`max_completion_tokens` ≈ 600 (already done). Trim system prompts and tool schemas passed to the model.

5) Gate/defer news
- Only include `get_stock_news` when query mentions news/headlines/catalyst. Optionally fetch news asynchronously post‑response.

6) Aggressive short‑TTL cache
- Price/history cache 30–60s keyed by symbol+granularity. Ensure all fast paths check cache before calling tools.

7) Remove persistence from the critical path
- Save conversation messages in a background task (fire‑and‑forget) with retry. Do not block user response on Supabase latency.

8) Connection hygiene
- Reuse `httpx.AsyncClient` pools; set per‑request timeouts (e.g., 6–10s). Auto‑recreate MCP clients on `WriteUnixTransport closed` errors.

9) Observability
- Add per‑phase timings: LLM#1, tools(total/per‑tool), LLM#2, total. Expose `/api/agent/diag` to dump timings + flags (optional).

## Code Touchpoints
- Backend: `backend/services/agent_orchestrator.py`
  - Fast path: `_process_query_single_pass`
  - Responses path: `_process_query_responses`
  - Tool parallelization: `_execute_tools_parallel`
  - News gating + intent router; token budgets
- Routers: `backend/routers/agent_router.py` (ensure fields returned are minimal and needed)
- MCP/perf: `backend/mcp_server.py` (init pools, avoid blocking operations)

## Flags & Config
- `USE_RESPONSES=true` to enable Responses path
- `CACHE_WARM_ON_STARTUP=true` to prewarm cache
- Suggested: `DISABLE_NEWS_DEFAULT=true`, `TOOL_TIMEOUT_SECONDS=8`

## Validation (smoke)
- Price: `curl -sS -X POST :8000/api/agent/orchestrate -H 'Content-Type: application/json' -d '{"query":"Get AAPL price"}'`
- TA: `curl -sS -X POST :8000/api/agent/orchestrate -H 'Content-Type: application/json' -d '{"query":"Show technical analysis for NVDA with support, resistance, fib and trendline"}'`
- Timing logs: tail server log and verify per‑phase durations and that news is gated.

## Expected Impact
- Parallel tools: save 2–4s
- Skip second pass: save 1–3s (most cases)
- Token + news gating: save 0.5–1.5s
- Background persistence + connection reuse: smoother tail latencies

> Next steps: I can add `/api/agent/diag` for structured timings, make Supabase saves fully async, and tighten tool timeouts if you want me to proceed.
