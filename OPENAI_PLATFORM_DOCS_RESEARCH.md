# OpenAI Platform Documentation Research Report

**Date:** January 2025  
**Source:** https://platform.openai.com/docs/overview  
**Research Focus:** Voice implementation, chart control, and agent architecture

---

## Executive Summary

Comprehensive research of the OpenAI Platform documentation reveals **critical architectural patterns** for voice agents, function calling, and production deployment. Key findings:

1. **Voice Agents**: Two architectures (Speech-to-Speech vs Chained) with distinct trade-offs
2. **Function Calling**: Official recommendation to use structured function schemas (validates our chart control implementation)
3. **Agent Builder**: Visual workflow builder with ChatKit integration for frontend deployment
4. **Production Best Practices**: Latency optimization, cost optimization, and accuracy optimization guides available

---

## 1. Voice Implementation Architecture

### 1.1 Two Primary Architectures

#### **Speech-to-Speech (Realtime) Architecture** ✅ **RECOMMENDED FOR OUR USE CASE**

**Flow:**
```
User Speech → gpt-4o-realtime-preview → Agent Response (Audio)
```

**Key Characteristics:**
- **Low latency interactions** - Native audio handling
- **Rich multimodal understanding** - Audio and text simultaneously
- **Natural conversational flow** - Model thinks and responds in speech
- **Enhanced vocal context** - Understands emotion and intent, filters noise

**Best For:**
- Interactive and unstructured conversations
- Language tutoring and interactive learning
- Conversational search and discovery
- Interactive customer service scenarios

**Transport Methods:**
- **WebRTC** (Browser/client-side) - Peer-to-peer, lowest latency
- **WebSocket** (Server-side) - For server-side agents (e.g., phone calls)

**Implementation:**
```typescript
import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";

const agent = new RealtimeAgent({
  name: "Assistant",
  instructions: "You are a helpful assistant.",
});

const session = new RealtimeSession(agent);
await session.connect({
  apiKey: "<client-api-key>",
});
```

**Documentation:** `/docs/guides/voice-agents` (Speech-to-Speech section)

---

#### **Chained Architecture** (Alternative)

**Flow:**
```
User Speech → gpt-4o-transcribe → gpt-4.1 → gpt-4o-mini-tts → Audio Response
```

**Key Characteristics:**
- **High control and transparency** - Text transcripts available
- **Robust function calling** - Structured interactions
- **Reliable, predictable responses** - Sequential processing
- **Extended conversational context** - Full transcript history

**Best For:**
- Structured workflows focused on specific objectives
- Customer support (with transcripts)
- Sales and inbound triage
- Scenarios requiring transcripts and scripted responses

**Documentation:** `/docs/guides/voice-agents?voice-agent-architecture=chained`

---

### 1.2 Voice Agent Design Best Practices

#### **Prompting Guidelines**

**Personality and Tone Structure:**
```markdown
# Personality and Tone
## Identity
## Task
## Demeanor
## Tone
## Level of Enthusiasm
## Level of Formality
## Level of Emotion
## Filler Words (none, occasionally, often, very often)
## Pacing
## Other details
```

**Key Prompting Tips:**
1. **Include critical information in prompt** (don't require tool calls for essential data)
2. **Limit tools** - Keep agent focused on single task
3. **Provide escape hatch** - Handoff to human or fallback phrase
4. **Use conversation states** - Encode flows in JSON markup for structured workflows

**Example Conversation States:**
```json
[
  {
    "id": "1_greeting",
    "description": "Greet the caller and explain the verification process.",
    "instructions": [
      "Greet the caller warmly.",
      "Inform them about the need to collect personal information."
    ],
    "transitions": [{
      "next_step": "2_get_first_name",
      "condition": "After greeting is complete."
    }]
  }
]
```

**Documentation:** `/docs/guides/voice-agents` (Design section)

---

### 1.3 Agent Handoff Pattern

**Use Case:** Transfer to specialized agents or human operators

**Implementation (Agents SDK):**
```typescript
const productSpecialist = new RealtimeAgent({
  name: 'Product Specialist',
  instructions: 'You are a product specialist...',
});

const triageAgent = new RealtimeAgent({
  name: 'Triage Agent',
  instructions: 'You are a customer service frontline agent...',
  tools: [productSpecialist], // SDK handles handoff automatically
});
```

**Custom Implementation:**
```typescript
const tool = {
  type: "function",
  function: {
    name: "transferAgents",
    description: `Triggers transfer to specialized agent...`,
    parameters: {
      type: "object",
      properties: {
        rationale_for_transfer: { type: "string" },
        conversation_context: { type: "string" },
        destination_agent: {
          type: "string",
          enum: ["returns_agent", "product_specialist_agent"]
        }
      }
    }
  }
};
```

**Documentation:** `/docs/guides/voice-agents` (Handle agent handoff section)

---

### 1.4 Extending with Specialized Models

**Pattern:** Speech-to-speech model calls text-based agents as tools

**Use Case:** Use o3 for validation, detailed policy checks, etc.

**Implementation:**
```typescript
import { RealtimeAgent, tool } from '@openai/agents/realtime';
import { z } from 'zod';

const supervisorAgent = tool({
  name: 'supervisorAgent',
  description: 'Passes a case to your supervisor for approval.',
  parameters: z.object({
    caseDetails: z.string(),
  }),
  execute: async ({ caseDetails }, details) => {
    const history = details.context.history;
    const response = await fetch('/request/to/your/specialized/agent', {
      method: 'POST',
      body: JSON.stringify({ caseDetails, history }),
    });
    return response.text();
  },
});

const returnsAgent = new RealtimeAgent({
  name: 'Returns Agent',
  instructions: 'Always check with your supervisor before making a decision.',
  tools: [supervisorAgent],
});
```

**Documentation:** `/docs/guides/voice-agents` (Extend with specialized models section)

---

## 2. Function Calling for Chart Control

### 2.1 Official Function Calling Pattern ✅ **VALIDATES OUR IMPLEMENTATION**

**Documentation:** `/docs/guides/function-calling`

**Key Principles:**
1. **Structured schemas** - Define function parameters with types and required fields
2. **Type safety** - Use enums for constrained values
3. **Required parameters** - Enforce at API level (prevents malformed calls)
4. **Tool execution** - Return structured results with success/failure status

**Our Implementation Alignment:**
- ✅ `load_chart(symbol: string)` - Required symbol parameter
- ✅ `set_chart_timeframe(timeframe: enum)` - Enum-validated timeframes
- ✅ `add_chart_indicator(indicator: enum, period?: int)` - Optional period
- ✅ Structured tool results with `command` field

**Documentation confirms:** Using function calling instead of string parsing is the **official recommended approach**.

---

### 2.2 Structured Outputs

**Documentation:** `/docs/guides/structured-outputs`

**Use Case:** Get model responses that adhere to JSON schema

**Relevance:** Could be used for chart command responses, but function calling is more appropriate for tool execution.

---

## 3. Agents Architecture

### 3.1 AgentKit Overview

**Components:**
1. **Agent Builder** - Visual canvas for creating workflows
2. **ChatKit** - Embeddable UI component for frontend
3. **Agents SDK** - Code-level control for custom implementations

**Documentation:** `/docs/guides/agents`

---

### 3.2 Building Agents

**Workflow Components:**

| Goal | What to Use | Description |
|------|-------------|-------------|
| Build workflow | Agent Builder | Visual canvas with models, tools, knowledge, logic |
| Connect to LLMs | OpenAI models | Core intelligence (GPT-5, GPT-5 mini, GPT-5 nano) |
| Equip agent | Tools, guardrails | Connectors, MCP, search, vector stores |
| Provide knowledge | Vector stores, file search, embeddings | External persistent knowledge |
| Add control-flow | Logic nodes | Custom logic, routing, conditions |
| Write custom code | Agents SDK | Build agentic applications programmatically |

**Key Insight:** Voice agents are **NOT supported in Agent Builder** - must use Agents SDK or Realtime API directly.

---

### 3.3 Deploying Agents

**ChatKit Integration:**
- **Standard ChatKit**: Paste workflow ID to embed agent in product
- **Advanced ChatKit**: Run on own infrastructure, connect to any backend

**Documentation:** `/docs/guides/chatkit`

**Relevance:** Our current implementation uses custom React components, but ChatKit could be considered for future standardization.

---

### 3.4 Optimizing Agents

**Evaluation Platform:**
- **Evals features** - Full evaluation platform
- **Trace grading** - Develop, deploy, monitor, improve
- **Datasets** - Build agent-level evals
- **Prompt optimizer** - Measure performance, identify improvements

**Documentation:** `/docs/guides/agent-evals`

---

## 4. Production Best Practices

### 4.1 Latency Optimization

**Documentation:** `/docs/guides/production-best-practices` → Latency optimization

**Key Strategies:**
- Use appropriate transport (WebRTC for browser, WebSocket for server)
- Optimize prompt length
- Use smaller models for simple tasks (gpt-5-mini, gpt-5-nano)
- Parallel tool execution
- Caching strategies

---

### 4.2 Cost Optimization

**Documentation:** `/docs/guides/production-best-practices` → Cost optimization

**Key Strategies:**
- Use smaller models when appropriate
- Cache responses
- Optimize token usage
- Monitor usage patterns

---

### 4.3 Accuracy Optimization

**Documentation:** `/docs/guides/optimizing-llm-accuracy`

**Key Strategies:**
- Fine-tuning for specific use cases
- Prompt engineering
- Evaluation and iteration
- Structured outputs for consistency

---

## 5. Realtime API Details

### 5.1 Connection Methods

**Three Primary Interfaces:**

1. **WebRTC** (`/docs/guides/realtime-webrtc`)
   - Ideal for browser/client-side
   - Peer-to-peer protocol
   - Lowest latency

2. **WebSocket** (`/docs/guides/realtime-websocket`)
   - Ideal for server-side applications
   - Consistent low-latency network connections
   - **Our current implementation uses this**

3. **SIP** (`/docs/guides/realtime-sip`)
   - Ideal for VoIP telephony
   - Phone call integrations

---

### 5.2 API Usage Guides

**Available Guides:**
- **Prompting guide** (`/docs/guides/realtime-models-prompting`) - Tips for prompting Realtime models
- **Managing conversations** (`/docs/guides/realtime-conversations`) - Session lifecycle and events
- **Webhooks and server-side controls** (`/docs/guides/realtime-server-controls`) - Control sessions server-side, call tools, implement guardrails
- **Managing costs** (`/docs/guides/realtime-costs`) - Monitor and optimize usage
- **Realtime audio transcription** (`/docs/guides/realtime-transcription`) - Transcribe audio streams

---

### 5.3 Beta to GA Migration

**Key Changes:**
- New header format
- Ephemeral API key generation
- New URL for WebRTC SDP data
- New event names and shapes
- New conversation item events
- Input/output item changes

**Documentation:** `/docs/guides/realtime` (Beta to GA migration section)

---

## 6. Tools and MCP Integration

### 6.1 Connectors and MCP

**Documentation:** `/docs/guides/tools-connectors-mcp`

**Key Points:**
- MCP (Model Context Protocol) for tool integration
- Connectors for third-party services
- File search and retrieval
- Code interpreter
- Web search

**Relevance:** Our `market-mcp-server` uses MCP protocol - aligns with official patterns.

---

## 7. Models Available

### 7.1 GPT-5 Series

**Models:**
- **GPT-5** - Best for coding and agentic tasks across domains
- **GPT-5 mini** - Faster, cost-efficient for well-defined tasks
- **GPT-5 nano** - Fastest, most cost-efficient

**Documentation:** `/docs/models`

**Relevance:** Consider `gpt-5-mini` for faster agent responses (as noted in our TODO list).

---

## 8. Key Insights for Our Implementation

### 8.1 Voice Architecture ✅ **ALIGNED**

**Current Implementation:**
- Uses Realtime API via WebSocket (server-side relay)
- Speech-to-speech architecture (gpt-4o-realtime-preview)
- Custom React components for UI

**Validation:**
- ✅ Using recommended Speech-to-Speech architecture
- ✅ WebSocket appropriate for server-side relay pattern
- ✅ Aligns with official best practices

**Potential Improvements:**
- Consider WebRTC for direct browser connections (lower latency)
- Implement agent handoff pattern for specialized workflows
- Add conversation state management (JSON markup)

---

### 8.2 Chart Control ✅ **VALIDATED**

**Current Implementation:**
- Function calling with structured schemas
- Required parameters enforced
- Type-safe enums

**Validation:**
- ✅ Matches official function calling pattern
- ✅ Prevents malformed commands (LOAD: without symbol)
- ✅ Structured tool results

**Documentation Confirms:** Function calling is the **official recommended approach** over string parsing.

---

### 8.3 Agent Orchestration

**Current Implementation:**
- Custom orchestrator (`agent_orchestrator.py`)
- Tool execution pipeline
- Chart command extraction

**Comparison with Agent Builder:**
- Agent Builder: Visual workflow builder (not for voice agents)
- Our approach: Code-based orchestration (more flexible, required for voice)

**Recommendation:** Continue with custom orchestration - Agent Builder doesn't support voice agents.

---

## 9. Production Deployment Considerations

### 9.1 Latency Optimization

**Current State:**
- WebSocket relay server
- Agent processing pipeline
- Chart command execution

**Recommendations:**
1. **Measure latency** at each stage (TODO: voice-1)
2. **Use gpt-5-mini** for faster responses (TODO: voice-2)
3. **Parallel tool execution** (already implemented)
4. **Cache common queries** (already implemented)

---

### 9.2 Cost Optimization

**Recommendations:**
1. Use `gpt-5-mini` for simple queries
2. Cache responses (already implemented)
3. Monitor usage patterns
4. Optimize prompt length

---

### 9.3 Error Handling

**Documentation:** `/docs/guides/realtime-server-controls`

**Key Points:**
- Webhooks for server-side control
- Implement guardrails
- Handle tool execution failures
- Session management

**Current Implementation:** Has error handling, but could add webhook pattern for advanced control.

---

## 10. Documentation Structure

### 10.1 Main Sections

**Navigation Structure:**
1. **Get started** - Overview, Quickstart, Models, Pricing, Libraries
2. **Core concepts** - Text generation, Images/vision, Audio/speech, Structured output, Function calling, GPT-5, Responses API migration
3. **Agents** - Overview, Build agents, Deploy, Optimize, Voice agents
4. **Tools** - Using tools, Connectors/MCP, Web search, Code interpreter, File search
5. **Run and scale** - Conversation state, Background mode, Streaming, Webhooks, File inputs, Prompting, Reasoning
6. **Evaluation** - Getting started, Working with evals, Prompt optimizer, External models, Best practices
7. **Realtime API** - Overview, Connect, Usage
8. **Model optimization** - Optimization cycle, Fine-tuning, Graders
9. **Specialized models** - Image generation, Video generation, TTS, STT, Deep research, Embeddings, Moderation
10. **Coding agents** - Codex cloud, Agent internet access, Local shell tool, Codex CLI, Codex IDE
11. **Going live** - Production best practices, Latency optimization, Cost optimization, Accuracy optimization, Safety
12. **Specialized APIs** - Assistants API
13. **Resources** - Terms/policies, Changelog, Your data, Rate limits, Deprecations, MCP for deep research, Developer mode, ChatGPT Actions

---

## 11. Actionable Recommendations

### 11.1 Immediate Actions

1. **✅ Chart Control Function Calling** - Already implemented correctly
2. **⏳ Voice Latency Measurement** - Add timestamps at each stage (TODO: voice-1)
3. **⏳ Switch to gpt-5-mini** - For faster agent responses (TODO: voice-2)
4. **⏳ WebSocket Auto-Reconnect** - Implement session resume (TODO: voice-3)
5. **⏳ Visual Indicators** - Add Listening/Thinking/Speaking states (TODO: voice-4)

### 11.2 Future Enhancements

1. **Consider WebRTC** - For direct browser connections (lower latency)
2. **Agent Handoff Pattern** - For specialized workflows
3. **Conversation State Management** - JSON markup for structured flows
4. **Evaluation Platform** - Use OpenAI evals for agent performance
5. **Prompt Optimizer** - Measure and improve agent performance

---

## 12. Conclusion

**Key Findings:**
1. ✅ **Voice architecture is correct** - Speech-to-Speech with Realtime API
2. ✅ **Chart control implementation validated** - Function calling is official pattern
3. ✅ **Agent orchestration approach appropriate** - Code-based required for voice
4. ⏳ **Optimization opportunities identified** - Latency, cost, accuracy guides available

**Documentation Quality:**
- Comprehensive guides for all major use cases
- Clear architectural patterns
- Production best practices well-documented
- Code examples and SDKs available

**Next Steps:**
1. Implement latency measurement (voice-1)
2. Switch to gpt-5-mini for faster responses (voice-2)
3. Add WebSocket auto-reconnect (voice-3)
4. Add visual indicators (voice-4)
5. Consider WebRTC for direct browser connections

---

## References

**Primary Documentation:**
- Overview: `/docs/overview`
- Voice Agents: `/docs/guides/voice-agents`
- Realtime API: `/docs/guides/realtime`
- Function Calling: `/docs/guides/function-calling`
- Agents: `/docs/guides/agents`
- Production Best Practices: `/docs/guides/production-best-practices`

**SDKs:**
- Agents SDK (TypeScript): `https://openai.github.io/openai-agents-js/`
- Realtime API Examples: `https://github.com/openai/openai-realtime-agents`

**Tools:**
- Realtime Playground: `/playground/realtime`
- Voice Agent Metaprompter: `https://chatgpt.com/g/g-678865c9fb5c81918fa28699735dd08e-voice-agent-metaprompt-gpt`

