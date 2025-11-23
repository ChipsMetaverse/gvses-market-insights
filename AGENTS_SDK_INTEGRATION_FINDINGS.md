# Agents SDK Integration Findings

**Date**: November 15, 2025
**Investigation**: OpenAI Agents SDK + ChatKit Integration
**Status**: ❌ More Complex Than Documented

---

## Summary

The integration between OpenAI Agents SDK and ChatKit for widget streaming is **more complex than the available documentation suggests**. The actual API requires:

1. **Store Implementation**: ChatKitServer requires a complete `Store` class with 14+ abstract methods for thread/item persistence
2. **Separate SDKs**: `openai-agents` and `openai-chatkit` are separate packages with different concerns
3. **Unclear Integration Pattern**: No clear examples of widget streaming from agent tools to ChatKit frontend

---

## What We Discovered

### ChatKit SDK Actual API (from installed package)

```python
from chatkit.server import ChatKitServer
from chatkit.store import Store

class ChatKitServer(ABC, Generic[TContext]):
    def __init__(
        self,
        store: Store[TContext],  # ← REQUIRED, not optional
        attachment_store: AttachmentStore[TContext] | None = None,
    ):
        self.store = store
        self.attachment_store = attachment_store
```

**Store Requirements** (14 abstract methods):
- `load_thread()`
- `save_thread()`
- `load_thread_items()`
- `save_attachment()`
- `load_attachment()`
- `delete_attachment()`
- `load_threads()`
- `add_thread_item()`
- `save_item()`
- `load_item()`
- `delete_thread()`
- `delete_thread_item()`
- Plus ID generation methods

### Agents SDK API (from documentation)

```python
from agents import Agent, function_tool, Runner

@function_tool
def my_tool(param: str) -> str:
    return "result"

agent = Agent(
    model="gpt-5-nano",
    instructions="...",
    tools=[my_tool]
)

result = Runner.run_streamed(agent, input="query")
async for event in result.stream_events():
    # Handle events
```

**Key Finding**: Agents SDK has no built-in widget streaming mechanism - it's designed for general agent workflows, not specifically for ChatKit.

---

## Integration Complexity

### What Documentation Suggested
- Simple agent + tools + widget streaming
- "Use ChatKit widgets in agent tools"
- Direct integration pattern

### What's Actually Required
1. **Implement Store Class**: Full persistence layer with 14+ methods
2. **Thread Management**: ThreadMetadata, ThreadItem handling
3. **Attachment Management**: File upload/download if needed
4. **Session Management**: Conversation state tracking
5. **Widget Streaming Protocol**: Unknown integration point between Agent SDK events and ChatKit widgets

---

## Alternative Approaches

### Option A: Minimal In-Memory Store
Create a simple in-memory `Store` implementation:
- **Pros**: No database dependency
- **Cons**: No persistence across restarts, still 14+ methods to implement

### Option B: Agent Builder (Current Working Solution)
Use OpenAI Agent Builder platform (already deployed as v54):
- **Pros**: 83% success rate generating widget JSON, already working
- **Cons**: Widget rendering issue is frontend integration, not agent output

### Option C: Custom Backend Integration
Skip ChatKit SDK entirely, build custom integration:
- **Pros**: Full control, simpler architecture
- **Cons**: More custom code to maintain

---

## Critical Realization

**The problem was never the agent backend!**

From `CHATKIT_WIDGET_RENDERING_STATUS.md`:
- ✅ Agent generates perfect widget JSON (83% success rate)
- ✅ MCP integration works flawlessly
- ✅ All 5 widget types generate correctly
- ❌ ChatKit React component displays JSON as text instead of rendering widgets

**The issue is frontend widget rendering**, not backend agent implementation.

---

## Recommended Path Forward

### Priority 1: Investigate Frontend Rendering (Playwright)
Use Playwright to investigate why ChatKit React component isn't rendering widgets:

```bash
# Navigate to demo page
# Send test query: "What's the latest news on TSLA?"
# Inspect ChatKit iframe to see actual DOM rendering
# Identify why widget JSON displays as text instead of visual components
```

### Priority 2: Frontend Widget Renderer
If ChatKit React component can't parse widgets from Agent Builder responses:

**Create custom widget renderer**:
```typescript
// In RealtimeChatKit.tsx or new component
const parseAndRenderWidgets = (response: string) => {
  try {
    const parsed = JSON.parse(response);
    if (parsed.widgets && Array.isArray(parsed.widgets)) {
      return <ChatKitWidgetRenderer widgets={parsed.widgets} />;
    }
  } catch {
    return <TextResponse text={response} />;
  }
};
```

### Priority 3: Agents SDK (If Frontend Fix Insufficient)
Only pursue Agents SDK if frontend fix doesn't work:
1. Implement minimal in-memory Store class
2. Create basic ChatKitServer integration
3. Test widget streaming end-to-end

---

## Files Affected

### Created (Not Working)
- `backend/services/chatkit_gvses_server.py` - Incomplete, has API mismatches
- `AGENTS_SDK_IMPLEMENTATION_STATUS.md` - Based on incorrect assumptions

### Existing (Working)
- Agent Builder workflow v54 (published, production)
- `backend/mcp_server.py:149` - Workflow ID configured correctly
- `frontend/src/components/RealtimeChatKit.tsx` - ChatKit React component (needs investigation)

---

## Next Immediate Action

**Use Playwright to investigate frontend rendering** per user's explicit request:
> "Option 2 also Great now investigate via playwright. run all necessary servers"

Focus on:
1. How ChatKit React component receives agent responses
2. Where widget parsing should happen
3. Why widgets display as JSON text instead of visual components
4. What changes needed in frontend to enable visual rendering

---

## Lessons Learned

1. **Documentation ≠ Reality**: Package APIs often differ from high-level documentation
2. **Start with Working Solution**: Agent Builder v54 already generates perfect widgets
3. **Focus on Actual Problem**: Frontend rendering, not backend generation
4. **Playwright Investigation**: Best way to understand actual browser behavior

---

**Status**: 🔴 Agents SDK Integration Too Complex
**Recommendation**: ✅ Investigate frontend rendering with Playwright
**Timeline**: 30 minutes for Playwright investigation vs days for full SDK integration
