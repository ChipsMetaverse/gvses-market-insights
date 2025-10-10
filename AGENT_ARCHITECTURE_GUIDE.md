# G'sves Agent Architecture Guide

## Overview

This document describes the current architecture and provides a roadmap for evolving to OpenAI's Agent Builder/Workflows API when available.

## Current Architecture (Phase 0: Responses API)

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TradingDashboardSimple.tsx                            │ │
│  │  ├─ Market Insights Panel (watchlist)                  │ │
│  │  ├─ TradingView Chart (AAPL, TSLA, etc.)              │ │
│  │  └─ Voice Assistant Button                             │ │
│  └────────────────────────────────────────────────────────┘ │
│           │                              │                   │
│           │ HTTP                         │ WebSocket         │
│           ▼                              ▼                   │
└───────────┼──────────────────────────────┼───────────────────┘
            │                              │
┌───────────┼──────────────────────────────┼───────────────────┐
│           │         Backend (FastAPI)    │                   │
│           │                              │                   │
│  ┌────────▼─────────────────────────────────────────┐       │
│  │  /api/agent/orchestrate                           │       │
│  │  ├─ Intent Classification                         │       │
│  │  ├─ Chart Commands (fast-path)                    │       │
│  │  └─ Trading Analysis → G'sves Assistant           │       │
│  └───────────────────────────────────────────────────┘       │
│           │                              │                   │
│           ▼                              ▼                   │
│  ┌─────────────────────┐      ┌────────────────────────┐   │
│  │ agent_orchestrator.py│      │ OpenAI Realtime Relay  │   │
│  │                      │      │ /ws/openai-realtime    │   │
│  │ _process_with_gvses_ │      │ (Voice WebSocket)      │   │
│  │     assistant()      │      └────────────────────────┘   │
│  │                      │                 │                 │
│  │ - Responses API call │                 │                 │
│  │ - Tool execution     │                 │                 │
│  │ - Knowledge base     │                 │                 │
│  └─────────────────────┘                 │                 │
│           │                              │                  │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            ▼                              ▼
    ┌────────────────────────────────────────────────┐
    │          OpenAI Platform                       │
    │                                                 │
    │  ┌──────────────────────────────────────────┐ │
    │  │ G'sves Assistant                         │ │
    │  │ ID: asst_FgdYMBvUvKUy0mxX5AF7Lmyg       │ │
    │  │                                          │ │
    │  │ Model: gpt-4o                           │ │
    │  │ Tools: file_search                      │ │
    │  │ Knowledge Base:                         │ │
    │  │  - gvses_methodology.md                 │ │
    │  │  - gvses_options_guide.md               │ │
    │  │  - gvses_analysis_checklist.md          │ │
    │  │  - AGENT_BUILDER_INSTRUCTIONS.md        │ │
    │  └──────────────────────────────────────────┘ │
    │                                                 │
    │  ┌──────────────────────────────────────────┐ │
    │  │ Realtime API (Voice)                     │ │
    │  │                                          │ │
    │  │ Model: gpt-realtime                     │ │
    │  │ Turn Detection: server_vad              │ │
    │  │ Voice: alloy                            │ │
    │  │ Transcription: whisper-1                │ │
    │  └──────────────────────────────────────────┘ │
    └────────────────────────────────────────────────┘
```

### Data Flow

#### Text Query Flow
```
1. User types "What's your trading philosophy?" in chat
   ↓
2. Frontend → POST /api/agent/orchestrate
   ↓
3. Backend: agent_orchestrator.py
   - Classify intent: "trading-analysis" (not chart-only)
   - Check: USE_GVSES_ASSISTANT=true
   ↓
4. _process_with_gvses_assistant()
   - Build messages from conversation_history
   - Call OpenAI Responses API:
     * model: gpt-4o
     * assistant_id: asst_FgdYMBvUvKUy0mxX5AF7Lmyg
     * tools: [get_stock_price, get_stock_news, ...]
     * store: true (multi-turn)
   ↓
5. OpenAI processes with G'sves knowledge base
   - file_search retrieves relevant methodology
   - Responds with G'sves personality
   ↓
6. Backend returns JSON response
   ↓
7. Frontend displays answer
```

#### Voice Query Flow
```
1. User clicks voice button
   ↓
2. Frontend: useOpenAIRealtimeConversation hook
   - Request microphone permission
   - Fetch session: POST /openai/realtime/session
   ↓
3. Backend creates ephemeral session
   - Returns ws_url and api_key
   ↓
4. Frontend: OpenAIRealtimeService.connect()
   - Create RealtimeClient with relay URL
   - Call updateSession() with server_vad config
   ↓
5. User speaks: "What's the price of Tesla?"
   - Microphone → PCM16 audio chunks
   - appendInputAudio() to WebSocket
   ↓
6. OpenAI Realtime API
   - Voice Activity Detection (server_vad)
   - Detects speech end (500ms silence)
   - Transcribes with Whisper-1
   ↓
7. Model generates response
   - May call tools (get_stock_price)
   - Generates text response
   - Converts to speech (TTS)
   ↓
8. Audio chunks stream back
   - response.output_audio.delta events
   - base64 → Int16Array conversion
   - Audio playback in browser
```

### Key Components

#### 1. Agent Orchestrator (`backend/services/agent_orchestrator.py`)

**Lines 212-218: Initialization**
```python
# G'sves Assistant Configuration
self.gvses_assistant_id = os.getenv("GVSES_ASSISTANT_ID")
self.use_gvses_assistant = os.getenv("USE_GVSES_ASSISTANT", "false").lower() == "true"
if self.gvses_assistant_id and self.use_gvses_assistant:
    logger.info(f"G'sves Assistant enabled: {self.gvses_assistant_id}")
else:
    logger.info("G'sves Assistant disabled - using default orchestrator")
```

**Lines 4350-4355: Routing Logic**
```python
# Route trading analysis queries to G'sves assistant if enabled
if self.use_gvses_assistant and self.gvses_assistant_id:
    # Use G'sves for trading analysis, but not for chart commands or indicator toggles
    if intent not in ["chart-only", "indicator-toggle"]:
        logger.info("Routing query to G'sves trading assistant")
        return await self._process_with_gvses_assistant(query, conversation_history)
```

**Lines 4273-4324: G'sves Processing**
```python
async def _process_with_gvses_assistant(
    self,
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Process query using the G'sves trading assistant.
    Uses OpenAI Responses API with the G'sves assistant for intelligent trading analysis.
    """
    logger.info(f"Processing query with G'sves assistant: {query[:50]}...")

    try:
        # Build messages for the assistant
        messages = []
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Keep last 10 messages
        messages.append({"role": "user", "content": query})

        # Get tool schemas for Responses API format
        tools = self._get_tool_schemas(for_responses_api=True)

        # Call Responses API with G'sves assistant
        response = await self.client.responses.create(
            model="gpt-4o",
            assistant_id=self.gvses_assistant_id,
            messages=messages,
            tools=tools,
            store=True  # Enable multi-turn conversations
        )

        # Extract response text
        response_text = response.output_text if hasattr(response, 'output_text') else str(response)

        # Track which tools were used
        tools_used = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tools_used = [tool.function.name for tool in response.tool_calls]

        return {
            "text": response_text,
            "tools_used": tools_used,
            "data": {},
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o-gvses-assistant",
            "cached": False,
            "session_id": None
        }

    except Exception as e:
        logger.error(f"Error processing query with G'sves assistant: {e}")
        # Fall back to regular orchestrator on error
        return await self._process_query_single_pass(query, conversation_history, self._classify_intent(query), False)
```

#### 2. Voice Service (`frontend/src/services/OpenAIRealtimeService.ts`)

**Lines 188-219: Session Configuration (NEW - Fixed audio output)**
```typescript
/**
 * Configure session with server-side voice activity detection
 * This enables automatic turn detection so the model responds when user stops speaking
 */
private async updateSession(): Promise<void> {
  if (!this.client) {
    throw new Error('Client not initialized');
  }

  console.log('⚙️ Configuring session with server_vad turn detection...');

  try {
    await this.client.updateSession({
      turn_detection: {
        type: 'server_vad',
        threshold: 0.5,              // Voice activity detection sensitivity (0.0-1.0)
        silence_duration_ms: 500,    // Silence duration before ending turn (ms)
        prefix_padding_ms: 100       // Audio to include before speech starts (ms)
      },
      modalities: ['text', 'audio'],  // Enable both text and audio responses
      voice: 'alloy',                 // OpenAI voice model
      input_audio_transcription: {    // Enable user speech transcription
        model: 'whisper-1'
      }
    });

    console.log('✅ Session configured successfully with automatic turn detection');
  } catch (error) {
    console.error('❌ Failed to update session:', error);
    throw error;
  }
}
```

### Environment Configuration

#### Backend `.env`
```bash
# G'sves Assistant Configuration
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg
USE_GVSES_ASSISTANT=true

# OpenAI API Keys
OPENAI_API_KEY=sk-proj-...        # For Responses API
OPENAI_ADMIN_KEY=sk-...           # For assistant management (optional)

# OpenAI Realtime API Configuration
OPENAI_REALTIME_MODEL=gpt-realtime
```

#### Frontend `.env`
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
```

## Phase 1: Adapter Pattern (Optional Enhancement)

### Goal
Decouple agent implementation from API contracts to enable future migration to Agents SDK or Workflows API.

### Implementation

#### 1.1 Create Backend Agent Interface

```python
# backend/services/backend_agent.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator

class BackendAgent(ABC):
    """
    Abstract interface for agent implementations.
    Allows swapping between Responses API, Agents SDK, and future Workflows API.
    """

    @abstractmethod
    async def run_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a single message and return response.

        Args:
            query: User's query text
            conversation_history: Previous messages in conversation
            tools: Available tools/functions

        Returns:
            {
                "text": str,              # Response text
                "tools_used": List[str],  # Tools called
                "model": str,             # Model identifier
                "data": Dict,             # Tool results
                "timestamp": str
            }
        """
        pass

    @abstractmethod
    async def stream_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response chunks as they're generated.
        """
        pass

    @abstractmethod
    def get_conversation_state(self) -> Dict[str, Any]:
        """
        Get current conversation state for persistence.
        """
        pass

    @abstractmethod
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Manually invoke a tool (for testing or explicit calls).
        """
        pass
```

#### 1.2 Responses API Adapter (Current Implementation)

```python
# backend/services/responses_adapter.py
from typing import Dict, List, Any, Optional, AsyncGenerator
from .backend_agent import BackendAgent
from openai import AsyncOpenAI
import os

class ResponsesAdapter(BackendAgent):
    """
    Adapter for OpenAI Responses API (current G'sves implementation).
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("GVSES_ASSISTANT_ID")

    async def run_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Implementation using Responses API (current approach).
        """
        messages = []
        if conversation_history:
            messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": query})

        response = await self.client.responses.create(
            model="gpt-4o",
            assistant_id=self.assistant_id,
            messages=messages,
            tools=tools or [],
            store=True
        )

        return {
            "text": response.output_text if hasattr(response, 'output_text') else str(response),
            "tools_used": [tool.function.name for tool in (response.tool_calls or [])],
            "model": "gpt-4o-gvses-assistant",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }

    async def stream_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming not yet implemented for Responses API.
        """
        result = await self.run_message(query, conversation_history, tools)
        yield result

    def get_conversation_state(self) -> Dict[str, Any]:
        return {"adapter": "responses", "assistant_id": self.assistant_id}

    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        # Tool invocation happens automatically in Responses API
        raise NotImplementedError("Manual tool invocation not supported in Responses adapter")
```

#### 1.3 Update Agent Orchestrator

```python
# backend/services/agent_orchestrator.py (modified)

from .backend_agent import BackendAgent
from .responses_adapter import ResponsesAdapter
# Future imports:
# from .agents_sdk_adapter import AgentsSDKAdapter
# from .workflows_adapter import WorkflowsAdapter

class AgentOrchestrator:
    def __init__(self):
        # ... existing initialization ...

        # Initialize backend agent (swappable)
        adapter_type = os.getenv("AGENT_ADAPTER", "responses")  # responses | agents_sdk | workflows

        if adapter_type == "responses":
            self.backend_agent = ResponsesAdapter()
        # elif adapter_type == "agents_sdk":
        #     self.backend_agent = AgentsSDKAdapter()
        # elif adapter_type == "workflows":
        #     self.backend_agent = WorkflowsAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")

        logger.info(f"Backend agent adapter: {adapter_type}")

    async def _process_with_gvses_assistant(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Simplified - now delegates to adapter.
        """
        tools = self._get_tool_schemas(for_responses_api=True)

        try:
            return await self.backend_agent.run_message(
                query=query,
                conversation_history=conversation_history,
                tools=tools
            )
        except Exception as e:
            logger.error(f"Error in backend agent: {e}")
            # Fallback to original logic
            return await self._process_query_single_pass(query, conversation_history, self._classify_intent(query), False)
```

### Benefits of Adapter Pattern

1. **Zero frontend changes** - Voice and UI remain unchanged
2. **Easy A/B testing** - Switch adapters via environment variable
3. **Gradual migration** - Run Responses in prod, test SDK in staging
4. **Future-proof** - Drop in Workflows adapter when API releases
5. **Rollback safety** - Instant switch back if issues arise

## Phase 2: Agents SDK Migration (Optional, When Needed)

### When to Migrate

Migrate to Agents SDK if you need:
- ✅ Complex multi-step workflows (e.g., trade intent → risk check → approval → execution)
- ✅ Built-in retries and error handling
- ✅ Better observability and tracing
- ✅ Type-safe tool definitions
- ✅ Parallel tool execution

### Implementation

#### 2.1 Install Agents SDK

```bash
# In backend/
pip install openai-agents-sdk
```

#### 2.2 Create Agents SDK Adapter

```python
# backend/services/agents_sdk_adapter.py
from typing import Dict, List, Any, Optional, AsyncGenerator
from .backend_agent import BackendAgent
from agents import Agent, Runner, function_tool
import os

class AgentsSDKAdapter(BackendAgent):
    """
    Adapter using OpenAI Agents SDK (code-first approach).
    """

    def __init__(self):
        # Define G'sves agent using SDK
        self.agent = Agent(
            name="GvsesAssistant",
            instructions=self._load_instructions(),
            tools=self._register_tools(),
            model="gpt-4o"
        )

    def _load_instructions(self) -> str:
        """
        Load G'sves personality from knowledge base.
        """
        # Read from AGENT_BUILDER_INSTRUCTIONS.md or similar
        with open("backend/knowledge/AGENT_BUILDER_INSTRUCTIONS.md") as f:
            return f.read()

    def _register_tools(self) -> List:
        """
        Register market data tools with SDK.
        """
        tools = []

        @function_tool
        def get_stock_price(symbol: str) -> Dict[str, Any]:
            """Get current stock price."""
            # Call your existing market data service
            return market_data_service.get_stock_price(symbol)

        @function_tool
        def get_stock_news(symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
            """Get latest news for a symbol."""
            return market_data_service.get_stock_news(symbol, limit)

        tools.extend([get_stock_price, get_stock_news])
        # Add more tools...

        return tools

    async def run_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run query through Agents SDK.
        """
        # Convert conversation_history to SDK format
        context = self._build_context(conversation_history)

        # Run agent
        result = await Runner.run_async(
            starting_agent=self.agent,
            input=query,
            context=context
        )

        return {
            "text": result.final_output,
            "tools_used": result.tools_called,
            "model": "gpt-4o-agents-sdk",
            "data": result.tool_results,
            "timestamp": datetime.now().isoformat()
        }

    async def stream_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses using SDK's streaming API.
        """
        context = self._build_context(conversation_history)

        async for chunk in Runner.stream_async(
            starting_agent=self.agent,
            input=query,
            context=context
        ):
            yield {
                "text": chunk.text,
                "done": chunk.is_final,
                "tool_call": chunk.tool_name if chunk.is_tool_call else None
            }

    def get_conversation_state(self) -> Dict[str, Any]:
        return {"adapter": "agents_sdk", "agent_name": self.agent.name}

    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Manually invoke a registered tool.
        """
        tool = next((t for t in self.agent.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        return await tool.execute(**arguments)
```

#### 2.3 Enable SDK Adapter

```bash
# backend/.env
AGENT_ADAPTER=agents_sdk  # Switch from 'responses' to 'agents_sdk'
```

#### 2.4 Test Both Adapters

```python
# backend/test_adapter_comparison.py
import asyncio
from services.agent_orchestrator import AgentOrchestrator
import os

async def compare_adapters():
    """
    Compare Responses API vs Agents SDK responses.
    """
    test_query = "What's your trading philosophy on risk management?"

    # Test Responses API
    os.environ["AGENT_ADAPTER"] = "responses"
    orchestrator_responses = AgentOrchestrator()
    result_responses = await orchestrator_responses._process_with_gvses_assistant(test_query)

    # Test Agents SDK
    os.environ["AGENT_ADAPTER"] = "agents_sdk"
    orchestrator_sdk = AgentOrchestrator()
    result_sdk = await orchestrator_sdk._process_with_gvses_assistant(test_query)

    print("=" * 80)
    print("RESPONSES API RESULT:")
    print(f"Model: {result_responses['model']}")
    print(f"Text: {result_responses['text'][:200]}...")
    print(f"Tools: {result_responses['tools_used']}")

    print("\n" + "=" * 80)
    print("AGENTS SDK RESULT:")
    print(f"Model: {result_sdk['model']}")
    print(f"Text: {result_sdk['text'][:200]}...")
    print(f"Tools: {result_sdk['tools_used']}")

if __name__ == "__main__":
    asyncio.run(compare_adapters())
```

## Phase 3: Workflows API Migration (When Released)

### Prerequisites
- Workflows API released by OpenAI
- Beta access granted
- Testing environment set up

### Implementation Steps

#### 3.1 Export Current Logic to Workflow

```python
# backend/services/workflows_adapter.py
from typing import Dict, List, Any, Optional, AsyncGenerator
from .backend_agent import BackendAgent
from openai import AsyncOpenAI  # Hypothetical Workflows client
import os

class WorkflowsAdapter(BackendAgent):
    """
    Adapter for OpenAI Workflows API (when available).
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.workflow_id = os.getenv("GVSES_WORKFLOW_ID")  # Created in Agent Builder

    async def run_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow via Workflows API.
        """
        # Hypothetical API (not yet released)
        response = await self.client.workflows.run(
            workflow_id=self.workflow_id,
            input=query,
            context={
                "conversation_history": conversation_history,
                "available_tools": tools
            }
        )

        return {
            "text": response.output,
            "tools_used": response.tools_executed,
            "model": f"workflow-{self.workflow_id}",
            "data": response.tool_results,
            "timestamp": response.completed_at
        }

    async def stream_message(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream workflow execution.
        """
        async for event in self.client.workflows.stream(
            workflow_id=self.workflow_id,
            input=query,
            context={"conversation_history": conversation_history}
        ):
            yield {
                "text": event.text,
                "node": event.current_node,
                "done": event.is_complete
            }

    def get_conversation_state(self) -> Dict[str, Any]:
        return {"adapter": "workflows", "workflow_id": self.workflow_id}

    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        # Tools are managed by workflow graph
        raise NotImplementedError("Workflows manage tools internally")
```

#### 3.2 Create Workflow in Agent Builder UI

```
Visual Workflow Design:

┌─────────────────────────────────────────────────────┐
│              Start: User Query                       │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│        Intent Classification Node                    │
│  Model: gpt-4o-mini (fast)                          │
│  Output: intent (chart-only | trading-analysis)     │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        │                      │
        ▼                      ▼
┌─────────────────┐    ┌──────────────────────────────┐
│ Chart Command   │    │  G'sves Trading Agent Node   │
│  Fast Path      │    │  Model: gpt-4o               │
│  No LLM call    │    │  Knowledge: file_search      │
└─────────────────┘    │  Tools: [market_data...]     │
                       └──────────┬───────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────────────┐
                       │  Risk Check Node             │
                       │  If order intent detected    │
                       └──────────┬───────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────────────┐
                       │  Human Approval Gate         │
                       │  (for order execution)       │
                       └──────────┬───────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────────────┐
                       │  Final Response              │
                       └──────────────────────────────┘
```

#### 3.3 Export and Deploy Workflow

```bash
# 1. Design workflow in Agent Builder UI
# 2. Test in preview mode
# 3. Publish workflow → Get workflow_id
# 4. Export code (optional for version control)

# 5. Update backend .env
AGENT_ADAPTER=workflows
GVSES_WORKFLOW_ID=wf_abc123xyz  # From Agent Builder

# 6. Deploy
fly deploy
```

#### 3.4 Canary Deployment Strategy

```python
# backend/services/agent_orchestrator.py

async def _process_with_gvses_assistant(
    self,
    query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Canary deployment: Route percentage of traffic to new workflow.
    """
    import random

    # Canary percentage from env (0-100)
    canary_pct = int(os.getenv("WORKFLOW_CANARY_PCT", "0"))

    if random.randint(1, 100) <= canary_pct:
        logger.info(f"Canary: Routing to Workflows adapter")
        os.environ["AGENT_ADAPTER"] = "workflows"
    else:
        logger.info(f"Canary: Using current adapter")
        os.environ["AGENT_ADAPTER"] = "responses"  # or agents_sdk

    # Reinitialize adapter if changed
    self.backend_agent = self._create_adapter()

    # Execute
    return await self.backend_agent.run_message(
        query=query,
        conversation_history=conversation_history,
        tools=self._get_tool_schemas(for_responses_api=True)
    )
```

**Rollout Schedule:**
```bash
Day 1:  WORKFLOW_CANARY_PCT=5   # 5% traffic
Day 3:  WORKFLOW_CANARY_PCT=10  # 10% traffic
Day 7:  WORKFLOW_CANARY_PCT=25  # 25% traffic
Day 14: WORKFLOW_CANARY_PCT=50  # 50% traffic
Day 21: WORKFLOW_CANARY_PCT=100 # Full migration
```

## Monitoring and Observability

### Metrics to Track

```python
# backend/services/metrics.py
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AgentMetrics:
    adapter_type: str         # responses | agents_sdk | workflows
    query: str
    response_time_ms: int
    tools_used: List[str]
    tokens_used: int
    success: bool
    error: Optional[str]
    timestamp: datetime

class MetricsCollector:
    """
    Collect and report agent performance metrics.
    """

    def __init__(self):
        self.metrics = []

    def record(self, metric: AgentMetrics):
        self.metrics.append(metric)

        # Log to file
        with open("logs/agent_metrics.jsonl", "a") as f:
            f.write(json.dumps({
                "adapter": metric.adapter_type,
                "query": metric.query[:50],
                "response_time_ms": metric.response_time_ms,
                "tools": metric.tools_used,
                "success": metric.success,
                "timestamp": metric.timestamp.isoformat()
            }) + "\n")

    def get_stats(self, adapter_type: str) -> Dict[str, Any]:
        """
        Get performance statistics for an adapter.
        """
        adapter_metrics = [m for m in self.metrics if m.adapter_type == adapter_type]

        if not adapter_metrics:
            return {}

        return {
            "adapter": adapter_type,
            "total_queries": len(adapter_metrics),
            "success_rate": sum(1 for m in adapter_metrics if m.success) / len(adapter_metrics),
            "avg_response_time_ms": sum(m.response_time_ms for m in adapter_metrics) / len(adapter_metrics),
            "p95_response_time_ms": sorted([m.response_time_ms for m in adapter_metrics])[int(len(adapter_metrics) * 0.95)],
            "total_tools_used": sum(len(m.tools_used) for m in adapter_metrics)
        }

# Global metrics collector
metrics_collector = MetricsCollector()
```

### Dashboard Queries

```sql
-- Query metrics from logs (if using PostgreSQL/Supabase)

-- Compare adapter performance
SELECT
    adapter,
    COUNT(*) as queries,
    AVG(response_time_ms) as avg_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_latency,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM agent_metrics
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY adapter;

-- Track tool usage
SELECT
    adapter,
    tool_name,
    COUNT(*) as calls
FROM agent_metrics, UNNEST(tools_used) as tool_name
GROUP BY adapter, tool_name
ORDER BY calls DESC;
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_adapters.py
import pytest
from services.responses_adapter import ResponsesAdapter
# from services.agents_sdk_adapter import AgentsSDKAdapter
# from services.workflows_adapter import WorkflowsAdapter

@pytest.mark.asyncio
async def test_responses_adapter():
    """Test Responses API adapter."""
    adapter = ResponsesAdapter()

    result = await adapter.run_message(
        query="What's your trading philosophy?",
        conversation_history=[],
        tools=[]
    )

    assert result["text"] is not None
    assert "risk" in result["text"].lower()  # G'sves mentions risk management
    assert result["model"] == "gpt-4o-gvses-assistant"

@pytest.mark.asyncio
async def test_adapter_interface_consistency():
    """Ensure all adapters return consistent response format."""
    adapters = [
        ResponsesAdapter(),
        # AgentsSDKAdapter(),
        # WorkflowsAdapter()
    ]

    query = "What's the current price of AAPL?"

    for adapter in adapters:
        result = await adapter.run_message(query, [], [])

        # All adapters must return same keys
        assert "text" in result
        assert "tools_used" in result
        assert "model" in result
        assert "timestamp" in result
```

### Integration Tests

```python
# backend/tests/test_voice_integration.py
import pytest
from services.agent_orchestrator import AgentOrchestrator

@pytest.mark.asyncio
async def test_voice_to_gvses_flow():
    """
    Test complete voice → G'sves assistant → response flow.
    """
    orchestrator = AgentOrchestrator()

    # Simulate voice transcript
    query = "What's your opinion on trading options versus stocks?"

    result = await orchestrator._process_with_gvses_assistant(
        query=query,
        conversation_history=[]
    )

    assert result["text"] is not None
    assert len(result["text"]) > 50  # Substantial response
    assert "options" in result["text"].lower()
```

### Load Tests

```python
# backend/tests/test_load.py
import asyncio
import time
from services.agent_orchestrator import AgentOrchestrator

async def load_test_adapter(adapter_type: str, num_requests: int = 100):
    """
    Simulate concurrent load on adapter.
    """
    orchestrator = AgentOrchestrator()
    orchestrator.backend_agent.adapter_type = adapter_type

    queries = [
        "What's the price of TSLA?",
        "Explain your trading methodology",
        "Show me the chart for AAPL",
        "What are the risks of options trading?"
    ] * (num_requests // 4)

    start_time = time.time()

    tasks = [
        orchestrator._process_with_gvses_assistant(q)
        for q in queries
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.time() - start_time
    successes = sum(1 for r in results if not isinstance(r, Exception))

    print(f"Adapter: {adapter_type}")
    print(f"Requests: {num_requests}")
    print(f"Success: {successes}/{num_requests}")
    print(f"Time: {elapsed:.2f}s")
    print(f"RPS: {num_requests/elapsed:.2f}")

if __name__ == "__main__":
    asyncio.run(load_test_adapter("responses", 100))
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (unit + integration)
- [ ] Voice integration tested locally
- [ ] G'sves assistant responding correctly
- [ ] Environment variables documented
- [ ] Rollback plan prepared

### Phase 1 (Current - Responses API)
- [x] G'sves assistant created programmatically
- [x] Backend integration complete
- [x] Voice with server_vad configured
- [ ] Voice tested and verified working
- [ ] Documentation complete

### Phase 2 (Optional - Agents SDK)
- [ ] Adapter pattern implemented
- [ ] Agents SDK installed and tested
- [ ] A/B test between adapters
- [ ] Performance metrics collected
- [ ] Decision: Migrate or stay on Responses

### Phase 3 (Future - Workflows API)
- [ ] Workflows API released by OpenAI
- [ ] Beta access granted
- [ ] Workflow designed in Agent Builder
- [ ] Workflow exported and version controlled
- [ ] Canary deployment tested
- [ ] Full migration complete

## Troubleshooting Guide

### Voice Not Working

**Symptom:** Audio input works but no audio output

**Solution:** ✅ FIXED - Ensure `updateSession()` called with `server_vad`

**Verify:**
```bash
# Check frontend console for:
⚙️ Configuring session with server_vad turn detection...
✅ Session configured successfully with automatic turn detection
```

### G'sves Not Responding

**Symptom:** Regular orchestrator used instead of G'sves

**Solution:**
```bash
# Check backend/.env
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg
USE_GVSES_ASSISTANT=true

# Restart backend
cd backend && uvicorn mcp_server:app --reload
```

### Adapter Not Switching

**Symptom:** Wrong adapter used despite env change

**Solution:**
```python
# Ensure orchestrator reinitializes adapter
# In agent_orchestrator.py __init__:
self.backend_agent = self._create_adapter()  # Call method instead of inline

def _create_adapter(self):
    adapter_type = os.getenv("AGENT_ADAPTER", "responses")
    if adapter_type == "responses":
        return ResponsesAdapter()
    # elif ...
```

## Next Steps

1. **Test voice integration** using VOICE_TEST_CHECKLIST.md
2. **Verify G'sves responses** match expected personality
3. **Monitor performance** with current Responses API implementation
4. **Optional:** Implement adapter pattern for future flexibility
5. **Wait for Workflows API** announcement from OpenAI

## References

- [GVSES_INTEGRATION_SUMMARY.md](./GVSES_INTEGRATION_SUMMARY.md) - Current implementation details
- [VOICE_TEST_CHECKLIST.md](./VOICE_TEST_CHECKLIST.md) - Voice testing procedure
- [test_gvses_integration.py](./test_gvses_integration.py) - Backend testing script
- OpenAI Agents SDK: https://github.com/openai/agents-sdk (when released)
- OpenAI Agent Builder: https://platform.openai.com/agents (beta)

---

**Document Version:** 1.0
**Last Updated:** October 7, 2025
**Status:** Phase 1 Complete (Responses API) ✅
