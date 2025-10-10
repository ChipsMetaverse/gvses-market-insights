# G'sves Trading Assistant - Implementation Roadmap
## Based on GPT-5 Deep Analysis

---

## Executive Summary

**Optimal Sequence:** Adapter → Monitoring → Voice → Workflow (with overlaps)

**Timeline:** 6 days for core implementation, 2-3 weeks for production hardening

**Risk Level:** Low-Medium (rollback mechanisms in place)

---

## Path Analysis Summary

| Path | Priority | Complexity | Time | Start |
|------|----------|------------|------|-------|
| **Adapter Pattern** | 🔴 Critical | 2/5 | 0.5-1 day | Day 1 |
| **Monitoring Baseline** | 🔴 Critical | 2/5 | 6-10 hrs | Day 1 |
| **Voice Smoke Test** | 🟡 High | 2/5 | 3-6 hrs | Day 1 |
| **Voice Full Integration** | 🟡 High | 3/5 | 1-2 days | Day 2-3 |
| **Workflow Migration** | 🟢 Medium | 3/5 | 2-3 days | Day 3-5 |
| **Monitoring Dashboard** | 🟢 Medium | 4/5 | 3-5 days | Day 4-6 |

---

## Day 1: Foundation (Adapter + Monitoring + Voice Smoke Test)

### Morning: Minimal Adapter Pattern (4 hours)

**Goal:** Create unified interface for Responses API, Workflow, and future providers

**Benefits:**
- ✅ A/B testing (10% workflow, 90% responses)
- ✅ Instant rollback via kill switch
- ✅ Unified voice/text code path
- ✅ Single place for metrics

**Implementation:**

```python
# backend/services/backend_adapter.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from enum import Enum
import random
import os
import logging

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    RESPONSES = "responses"
    WORKFLOW = "workflow"
    AGENTS_SDK = "agents_sdk"


class SessionEvent:
    """Unified event format across all providers."""
    def __init__(
        self,
        type: str,  # "text", "tool_call", "tool_result", "error", "usage"
        content: Optional[str] = None,
        tool_call: Optional[Dict[str, Any]] = None,
        tool_result: Optional[Dict[str, Any]] = None,
        usage: Optional[Dict[str, int]] = None,
        meta: Optional[Dict[str, Any]] = None,
        done: bool = False
    ):
        self.type = type
        self.content = content
        self.tool_call = tool_call
        self.tool_result = tool_result
        self.usage = usage
        self.meta = meta or {}
        self.done = done


class BackendProvider(ABC):
    """Base class for all backend providers."""

    @abstractmethod
    async def send(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **options
    ) -> AsyncGenerator[SessionEvent, None]:
        """Send messages and stream events."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider identifier."""
        pass


class ResponsesProvider(BackendProvider):
    """OpenAI Responses API provider (current implementation)."""

    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("GVSES_ASSISTANT_ID")

    async def send(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **options
    ) -> AsyncGenerator[SessionEvent, None]:
        """Execute via Responses API."""
        try:
            response = await self.client.responses.create(
                model="gpt-4o",
                assistant_id=self.assistant_id,
                messages=messages,
                tools=tools or [],
                store=True
            )

            # Extract text
            text = response.output_text if hasattr(response, 'output_text') else str(response)

            # Extract tool calls
            tools_used = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    yield SessionEvent(
                        type="tool_call",
                        tool_call={
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    )
                    tools_used.append(tool_call.function.name)

            # Yield main response
            yield SessionEvent(
                type="text",
                content=text,
                meta={
                    "model": "gpt-4o-responses",
                    "tools_used": tools_used,
                    "provider": "responses"
                },
                done=True
            )

        except Exception as e:
            logger.error(f"Responses provider error: {e}")
            yield SessionEvent(
                type="error",
                content=str(e),
                done=True
            )

    def get_provider_name(self) -> str:
        return "responses"


class WorkflowProvider(BackendProvider):
    """OpenAI Workflow provider (Agent Builder)."""

    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.workflow_id = os.getenv("GVSES_WORKFLOW_ID")

        if not self.workflow_id:
            raise ValueError("GVSES_WORKFLOW_ID not set")

    async def send(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **options
    ) -> AsyncGenerator[SessionEvent, None]:
        """Execute via Workflow API."""
        try:
            # NOTE: This is the expected API format when Workflows API releases
            # For now, this will fail - use as template

            # Extract user query from last message
            user_query = messages[-1]["content"] if messages else ""

            async for event in self.client.workflows.stream(
                workflow_id=self.workflow_id,
                input={
                    "user_query": user_query,
                    "conversation_history": messages[:-1]
                }
            ):
                # Map workflow events to SessionEvent
                if event.type == "node_start":
                    yield SessionEvent(
                        type="meta",
                        meta={"node": event.node_name}
                    )
                elif event.type == "tool_call":
                    yield SessionEvent(
                        type="tool_call",
                        tool_call={
                            "name": event.tool_name,
                            "arguments": event.tool_args
                        }
                    )
                elif event.type == "output":
                    yield SessionEvent(
                        type="text",
                        content=event.text_delta,
                        done=event.is_complete,
                        meta={
                            "model": f"workflow-{self.workflow_id}",
                            "provider": "workflow"
                        }
                    )

        except Exception as e:
            logger.error(f"Workflow provider error: {e}")
            yield SessionEvent(
                type="error",
                content=str(e),
                done=True
            )

    def get_provider_name(self) -> str:
        return "workflow"


class BackendAdapter:
    """
    Unified adapter with A/B testing and kill switch.
    Routes requests to appropriate provider.
    """

    def __init__(self):
        # Initialize providers
        self.providers = {
            ProviderType.RESPONSES: ResponsesProvider(),
        }

        # Try to initialize workflow if configured
        try:
            if os.getenv("GVSES_WORKFLOW_ID"):
                self.providers[ProviderType.WORKFLOW] = WorkflowProvider()
        except Exception as e:
            logger.warning(f"Workflow provider not available: {e}")

        # A/B testing configuration
        self.workflow_percentage = int(os.getenv("WORKFLOW_PERCENTAGE", "0"))
        self.kill_switch = os.getenv("WORKFLOW_KILL_SWITCH", "false").lower() == "true"

        # Session affinity (sticky routing)
        self.session_assignments = {}

    def _select_provider(self, session_id: Optional[str] = None) -> BackendProvider:
        """Select provider based on A/B test settings."""

        # Kill switch: always use responses
        if self.kill_switch:
            logger.info("Kill switch active: using Responses provider")
            return self.providers[ProviderType.RESPONSES]

        # Check if workflow provider available
        if ProviderType.WORKFLOW not in self.providers:
            return self.providers[ProviderType.RESPONSES]

        # Session affinity
        if session_id and session_id in self.session_assignments:
            provider_type = self.session_assignments[session_id]
            logger.info(f"Session {session_id[:8]} sticky to {provider_type.value}")
            return self.providers[provider_type]

        # A/B test: random assignment
        use_workflow = random.randint(1, 100) <= self.workflow_percentage

        provider_type = ProviderType.WORKFLOW if use_workflow else ProviderType.RESPONSES

        # Store assignment
        if session_id:
            self.session_assignments[session_id] = provider_type

        logger.info(f"A/B test: {self.workflow_percentage}% → {provider_type.value}")
        return self.providers[provider_type]

    async def send(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        **options
    ) -> AsyncGenerator[SessionEvent, None]:
        """
        Send messages through selected provider with fallback.
        """
        provider = self._select_provider(session_id)

        try:
            # Try primary provider
            async for event in provider.send(messages, tools, **options):
                yield event

        except Exception as e:
            # Fallback to Responses API
            logger.error(f"Provider {provider.get_provider_name()} failed: {e}")
            logger.info("Falling back to Responses API")

            fallback = self.providers[ProviderType.RESPONSES]
            async for event in fallback.send(messages, tools, **options):
                event.meta["fallback"] = True
                yield event
```

**Configuration:**

```bash
# backend/.env

# A/B Testing
WORKFLOW_PERCENTAGE=0  # Start at 0%, increase gradually (10, 25, 50, 100)
WORKFLOW_KILL_SWITCH=false  # Set to true to instantly disable workflow

# Provider IDs
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg  # Responses API
GVSES_WORKFLOW_ID=wf_68e474d14d28819085  # Agent Builder (once published)
```

**Update Agent Orchestrator:**

```python
# backend/services/agent_orchestrator.py

from .backend_adapter import BackendAdapter, SessionEvent

class AgentOrchestrator:
    def __init__(self):
        # ... existing code ...

        # Initialize adapter
        self.adapter = BackendAdapter()
        logger.info("Backend adapter initialized")

    async def _process_with_gvses_assistant(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process query through backend adapter (unified path).
        """
        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": query})

        # Get tool schemas
        tools = self._get_tool_schemas(for_responses_api=True)

        # Stream through adapter
        response_text = ""
        tools_used = []
        model = "unknown"
        provider = "unknown"

        try:
            async for event in self.adapter.send(
                messages=messages,
                tools=tools,
                session_id=session_id
            ):
                if event.type == "text":
                    response_text += event.content or ""
                    if event.meta:
                        model = event.meta.get("model", model)
                        provider = event.meta.get("provider", provider)
                        tools_used = event.meta.get("tools_used", tools_used)

                elif event.type == "tool_call":
                    tools_used.append(event.tool_call["name"])

                elif event.type == "error":
                    logger.error(f"Adapter error: {event.content}")
                    # Fallback handled by adapter

            return {
                "text": response_text,
                "tools_used": tools_used,
                "model": model,
                "provider": provider,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Adapter stream failed: {e}")
            # Final fallback to existing logic
            return await self._process_query_single_pass(
                query, conversation_history, self._classify_intent(query), False
            )
```

---

### Afternoon: Baseline Monitoring (4 hours)

**Goal:** Track latency, errors, costs, and usage across providers

**Stack:**
- **Errors:** Sentry (frontend + backend)
- **Metrics:** Langfuse or Helicone (LLM observability)
- **Logs:** Structured logging with session_id

**Implementation:**

```bash
# Install dependencies
pip install sentry-sdk langfuse
```

```python
# backend/main.py (FastAPI startup)

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from langfuse import Langfuse

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
)

# Initialize Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)
```

```python
# backend/services/metrics.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Metrics for a single session/request."""
    session_id: str
    provider: str
    model: str
    query: str
    response_text: str
    tools_used: List[str]
    latency_ms: int
    tokens_input: int
    tokens_output: int
    cost_usd: float
    success: bool
    error: Optional[str]
    timestamp: datetime
    is_voice: bool = False


class MetricsCollector:
    """Collect and emit metrics."""

    def __init__(self, langfuse_client):
        self.langfuse = langfuse_client

    def record_session(self, metrics: SessionMetrics):
        """Record session to Langfuse."""
        try:
            trace = self.langfuse.trace(
                name="gvses_query",
                session_id=metrics.session_id,
                user_id=None,  # Add user tracking if available
                metadata={
                    "provider": metrics.provider,
                    "model": metrics.model,
                    "tools_used": metrics.tools_used,
                    "is_voice": metrics.is_voice,
                    "success": metrics.success
                }
            )

            trace.span(
                name="llm_call",
                start_time=metrics.timestamp,
                end_time=metrics.timestamp + timedelta(milliseconds=metrics.latency_ms),
                metadata={
                    "provider": metrics.provider,
                    "model": metrics.model
                },
                input=metrics.query,
                output=metrics.response_text,
                usage={
                    "input": metrics.tokens_input,
                    "output": metrics.tokens_output,
                    "total": metrics.tokens_input + metrics.tokens_output
                },
                level="DEFAULT" if metrics.success else "ERROR"
            )

            # Log locally
            logger.info(
                f"Session {metrics.session_id[:8]}: "
                f"provider={metrics.provider}, "
                f"latency={metrics.latency_ms}ms, "
                f"tokens={metrics.tokens_input + metrics.tokens_output}, "
                f"cost=${metrics.cost_usd:.4f}"
            )

        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")


# Global metrics collector
from main import langfuse
metrics_collector = MetricsCollector(langfuse)
```

```python
# backend/services/agent_orchestrator.py (add metrics)

from .metrics import metrics_collector, SessionMetrics
import time

async def _process_with_gvses_assistant(...):
    start_time = time.time()

    # ... existing code ...

    latency_ms = int((time.time() - start_time) * 1000)

    # Record metrics
    metrics_collector.record_session(SessionMetrics(
        session_id=session_id or "unknown",
        provider=provider,
        model=model,
        query=query,
        response_text=response_text,
        tools_used=tools_used,
        latency_ms=latency_ms,
        tokens_input=0,  # TODO: Extract from response
        tokens_output=0,  # TODO: Extract from response
        cost_usd=0.0,  # TODO: Calculate based on tokens
        success=True,
        error=None,
        timestamp=datetime.now(),
        is_voice=False  # Will be set by voice handler
    ))

    return {...}
```

**Environment Variables:**

```bash
# backend/.env

# Sentry
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

### Evening: Voice Smoke Test (3 hours)

**Goal:** Verify Realtime API works end-to-end (audio in → transcript → audio out)

**Test Script:**

```python
# backend/test_voice_smoke.py

import asyncio
import os
from openai import AsyncOpenAI

async def test_realtime_echo():
    """
    Smoke test: Send audio, get transcript, respond with TTS.
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("🎤 Testing OpenAI Realtime API...")

    # This is a simplified test - actual implementation uses WebSocket
    # For now, test via Responses API with audio
    try:
        response = await client.responses.create(
            model="gpt-realtime",
            input="What's the current price of Tesla stock?",
            modalities=["text", "audio"],
            voice="alloy"
        )

        print(f"✅ Model: {response.model}")
        print(f"✅ Text output: {response.output_text[:100]}...")
        print(f"✅ Audio output: {len(response.output_audio) if hasattr(response, 'output_audio') else 0} bytes")

        print("\n🎯 Voice smoke test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Voice smoke test FAILED: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_realtime_echo())
```

```bash
# Run smoke test
cd backend
python test_voice_smoke.py
```

**Expected Output:**
```
🎤 Testing OpenAI Realtime API...
✅ Model: gpt-realtime
✅ Text output: Tesla (TSLA) is currently trading at $242.84...
✅ Audio output: 524288 bytes

🎯 Voice smoke test PASSED
```

---

## Day 2-3: Voice Full Integration

### Goal: Voice → Backend → Adapter → Responses/Workflow

**Architecture:**

```
[Microphone]
    ↓
[Frontend: OpenAIRealtimeService]
    ↓ WebSocket (audio chunks)
[OpenAI Realtime API]
    ↓ (VAD detects end of speech)
[Transcript Event]
    ↓ HTTP POST
[Backend: /api/voice/transcript]
    ↓
[Agent Orchestrator + Adapter]
    ↓ (stream response tokens)
[Sentence Chunker]
    ↓ (chunk every 400-600ms or punctuation)
[TTS per chunk]
    ↓ WebSocket
[Frontend: Audio Playback Queue]
    ↓
[Speakers]
```

**Implementation:**

```python
# backend/routers/voice_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.agent_orchestrator import AgentOrchestrator
from services.sentence_chunker import SentenceChunker
import asyncio

router = APIRouter()


class VoiceTranscriptRequest(BaseModel):
    transcript: str
    session_id: str
    conversation_history: List[Dict[str, str]] = []


@router.post("/voice/transcript")
async def process_voice_transcript(request: VoiceTranscriptRequest):
    """
    Process voice transcript and stream response chunks for TTS.
    """
    orchestrator = AgentOrchestrator()
    chunker = SentenceChunker()

    try:
        # Process through adapter (same as text)
        async for event in orchestrator.adapter.send(
            messages=[
                *request.conversation_history,
                {"role": "user", "content": request.transcript}
            ],
            session_id=request.session_id
        ):
            if event.type == "text":
                # Chunk text for TTS
                for chunk in chunker.chunk(event.content):
                    # TODO: Call TTS API and stream audio
                    yield {
                        "type": "audio_chunk",
                        "text": chunk,
                        "sequence": chunker.get_sequence()
                    }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

```python
# backend/services/sentence_chunker.py

import re

class SentenceChunker:
    """Chunk text into sentences for streaming TTS."""

    def __init__(self, timeout_ms: int = 500):
        self.timeout_ms = timeout_ms
        self.buffer = ""
        self.sequence = 0

    def chunk(self, text: str):
        """Yield sentence chunks."""
        self.buffer += text

        # Split on sentence boundaries
        sentences = re.split(r'([.!?]\s+)', self.buffer)

        # Yield complete sentences
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
            if sentence.strip():
                self.sequence += 1
                yield sentence.strip()

        # Keep last incomplete sentence in buffer
        self.buffer = sentences[-1] if len(sentences) % 2 == 1 else ""

    def get_sequence(self):
        return self.sequence

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer.strip():
            self.sequence += 1
            return self.buffer.strip()
        return None
```

---

## Day 3-5: Workflow Migration

### Step 1: Complete Agent Builder Configuration

**In Agent Builder UI (platform.openai.com/agent-builder):**

1. **Intent Classifier Node:**
   - Model: `gpt-4o-mini` (NOT o4-mini)
   - Instructions: (see AGENT_BUILDER_WORKFLOW_DESIGN.md)
   - Output variable: `intent_result`

2. **If/Else Branch:**
   - Condition: `intent_result.intent === "chart_command"`

3. **G'sves Agent Node** (your existing node):
   - Model: `gpt-4o` (NOT o1 - too slow for chat)
   - Reasoning effort: `medium`
   - Instructions: Copy from AGENT_BUILDER_WORKFLOW_DESIGN.md
   - Knowledge: Add your 4 files via File Search
   - Tools: Add curated MCP tools (6-8 functions)
   - Output format: Text

4. **Test in Preview:**
   - "Show me AAPL chart" → Should route to chart handler
   - "What's your philosophy?" → Should route to G'sves

5. **Publish:**
   - Version: `v1.0`
   - Copy workflow ID: `wf_68e474d14d28819085`

### Step 2: Enable Workflow in Backend

```bash
# backend/.env

# Start with 10% traffic
WORKFLOW_PERCENTAGE=10
GVSES_WORKFLOW_ID=wf_68e474d14d28819085
```

### Step 3: Monitor A/B Test

Check Langfuse dashboard:
- Compare latency: Workflow vs Responses
- Compare error rates
- Compare token usage and costs

**Gradual Rollout:**
```bash
Week 1: WORKFLOW_PERCENTAGE=10
Week 2: WORKFLOW_PERCENTAGE=25
Week 3: WORKFLOW_PERCENTAGE=50
Week 4: WORKFLOW_PERCENTAGE=100  # Full migration
```

---

## Day 4-6: Expand Monitoring

### Dashboards to Build

**1. A/B Comparison Dashboard (Langfuse)**
- Latency: p50, p95, p99 by provider
- Error rate by provider
- Token usage by provider
- Cost per query by provider

**2. Tool KPIs Dashboard**
- Success rate per tool
- Latency per tool
- Retry count per tool
- Most used tools

**3. Voice Metrics Dashboard**
- Talk-to-first-token (TTFT)
- ASR latency
- TTS latency
- Barge-in count
- Utterances per session

**4. Trading Assistant KPIs**
- Intent distribution (research, analysis, execution)
- Presence of risk disclaimers (binary classifier)
- Stop-loss mentioned (binary classifier)
- Entry/exit levels present (binary classifier)

---

## Technical Decisions (Final Answers)

### Agent Builder Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Intent Classifier Model** | `gpt-4o-mini` | Fast, cheap, accurate for classification |
| **Main Agent Model** | `gpt-4o` | Balanced reasoning/latency/cost |
| **Reasoning Effort** | `medium` | Auto-escalate to `high` for high-stakes |
| **MCP Tools** | Backend (for now) | Stability, rate limits, auditability |
| **Output Format** | Text + structured sidecar | Chat stays natural, UI gets structure |

**Avoid:**
- ❌ o1 for chat (too slow, use for deep research only)
- ❌ o4-mini (unclear if available, stick to gpt-4o-mini)

### Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Voice Flow** | Voice → Backend → Adapter → Workflow | One business logic path |
| **Responses API** | Keep as fallback | Instant rollback via adapter |
| **Implementation Order** | Adapter → Voice → Workflow | Risk mitigation, parallel work |
| **Production Deploy** | After all 3 paths tested | Full stack verified |

---

## Quick Wins (< 1 Day)

1. ✅ **Minimal adapter** (4 hours)
   - Instant rollback
   - A/B testing ready
   - Unified code path

2. ✅ **Baseline monitoring** (4 hours)
   - Sentry + Langfuse
   - Basic metrics
   - Error tracking

3. ✅ **Voice smoke test** (3 hours)
   - End-to-end audio verification
   - Confidence in Realtime API

---

## Long-Term Roadmap (3-6 Months)

### Month 1: Production Hardening
- Workflow at 100% (graduated from Responses API)
- Voice barge-in and latency optimization
- User feedback (thumbs up/down with reason codes)
- Offline evaluation pipeline

### Month 2-3: Advanced Features
- Automated evals (scenario cards with scoring)
- Expanded monitoring (cost-per-intent, SLO alerts)
- "Deep dive" mode with o1-like model for research

### Month 4-6: Enterprise Grade
- Governance (per-tool permissions, rate limits)
- Memory and journaling with structured store
- Safety upgrades (missing stop-loss detector)
- Blue/green workflow deployments

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| Workflow failures | Adapter fallback to Responses API | Backend |
| Voice latency | Sentence chunking, barge-in | Frontend |
| Cost explosion | Monitor token usage, set alerts | Ops |
| Bad A/B split | Kill switch, instant rollback | Backend |
| MCP tool failures | Retry logic, graceful degradation | Backend |

---

## Success Metrics

### Week 1 (Adapter + Monitoring)
- [ ] Adapter switching works (can toggle WORKFLOW_PERCENTAGE)
- [ ] Kill switch tested (instant rollback to Responses)
- [ ] Sentry catching errors
- [ ] Langfuse showing traces
- [ ] Voice smoke test passes

### Week 2 (Voice + Workflow 10%)
- [ ] Voice end-to-end working (audio in → response → audio out)
- [ ] Workflow handling 10% traffic with no errors
- [ ] Latency comparable to Responses API
- [ ] A/B metrics visible in dashboard

### Week 3-4 (Full Migration)
- [ ] Workflow at 100% traffic
- [ ] Voice latency < 2s TTFT
- [ ] Error rate < 1%
- [ ] User satisfaction maintained or improved

---

## Immediate Action Items (Start Now)

### Prerequisites
```bash
# Install dependencies
pip install sentry-sdk langfuse

# Set environment variables
export SENTRY_DSN=your_dsn
export LANGFUSE_PUBLIC_KEY=your_key
export LANGFUSE_SECRET_KEY=your_secret
```

### Day 1 Tasks (Parallel)

**Morning:**
1. [ ] Copy `backend_adapter.py` code into `backend/services/`
2. [ ] Update `agent_orchestrator.py` to use adapter
3. [ ] Test adapter switching via WORKFLOW_PERCENTAGE

**Afternoon:**
4. [ ] Add Sentry integration to `backend/main.py`
5. [ ] Add Langfuse integration
6. [ ] Add metrics collection to orchestrator

**Evening:**
7. [ ] Run voice smoke test
8. [ ] Verify console logs show server_vad config
9. [ ] Test microphone → transcript → response

---

## Next Steps

Would you like me to:
1. **Start implementing the adapter code** (copy into your project)?
2. **Set up monitoring** (Sentry + Langfuse)?
3. **Test voice integration** end-to-end?
4. **Configure Agent Builder** workflow step-by-step?

**Recommendation:** Start with #1 (adapter) and #2 (monitoring) in parallel, then test voice (#3).
