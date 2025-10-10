# Agent Builder MCP Integration - Current Knowledge Base

**Last Updated**: October 8, 2025
**Status**: ⚠️ ~65% COMPLETE - Missing 5+ critical node types
**Sources**: Complete Agent Builder tutorial, UI screenshot discovery, OpenAI documentation, TwelveLabs video analysis

---

## 📚 Complete Knowledge - Updated

### 1. Agent Builder UI & Interface (COMPLETE ✅)

**Source**: Complete Agent Builder Tutorial + Initial video analysis

#### Access & Navigation:
- **Access**: Visit OpenAI website → Log in to account → Agent Builder available
- **Sidebar**: Left side contains:
  - 'Create' - New workflows
  - 'Manage' - Existing workflows
  - 'Images' - Image handling
  - 'Audio' - Audio processing
  - 'Links' - External connections
  - 'Logs' - Workflow execution logs
  - 'Storage' - Data storage
  - 'Optimize' - Performance tuning
  - 'Fine-tune' - Model customization

#### Canvas Interface Mechanics:
- **Drag & Drop**: Click nodes from sidebar → Drag onto canvas
- **Connect Nodes**: Click and drag from one node's output → Another node's input
- **Properties Panel**: Right side shows selected node details
- **Customize**: Edit node configurations in properties panel

#### Properties Panel Usage:
- **Location**: Right side of screen
- **Function**: View and edit selected node details
- **Customization**: Configure workflow settings per node

---

### 2. Node Types - INCOMPLETE ⚠️

**Status**: We documented 11 node types, but Agent Builder has 16+ nodes available

**What We Documented (65% Complete):**

1. **Agent Node**
   - AI reasoning with custom instructions
   - Configurable model selection
   - User prompts and system instructions
   - Variable passing via `{{variable_name}}`

2. **Jailbreak Guardrail Node**
   - Checks for unusual/malicious inputs
   - Security layer for workflows
   - Error handling for suspicious requests

3. **Classification Agent Node**
   - AI-powered intent detection
   - Categorizes user queries
   - Routes to appropriate workflow paths

4. **Condition Node (If/Else)**
   - Conditional logic routing
   - Boolean evaluation
   - Multiple branch support

5. **User Approval Node**
   - Human-in-the-loop workflows
   - Routes to "Approve" or "Reject"
   - Manual review gates

6. **Set State Node**
   - Variable management
   - Workflow state persistence
   - Data storage between steps

7. **Transform Node**
   - Data manipulation
   - Format conversion
   - Field extraction/mapping

8. **MCP Node** ⭐ (CRITICAL)
   - Connect to external MCP servers
   - Authentication configuration
   - Tool discovery and execution

9. **Web Search Node**
   - Built-in web search capability
   - Real-time information retrieval
   - No API key required (appears built-in)

10. **Code Interpreter Node**
    - Python code execution
    - Data analysis
    - Custom computations

11. **File Search Node**
    - Document retrieval
    - Knowledge base integration
    - File parsing and searching

**Missing Nodes (35% Gap) - See COMPLETE_NODE_TYPES_LIST.md:**

12. **Vector Store Node** ❌ CRITICAL MISSING
    - Vector embeddings for RAG
    - Efficient retrieval from large datasets
    - Knowledge base storage and search
    - **Use Case for G'sves**: Store market research, historical analyses

13. **Loop Node** ❌ CRITICAL MISSING
    - Iteration through arrays/lists
    - Batch operations
    - Repetitive task handling
    - **Use Case for G'sves**: Analyze multiple stocks, process watchlists

14. **Exec Node** ❌ MISSING
    - Execute commands or scripts
    - System-level operations
    - Custom processing

15. **Note Node** ❌ MISSING
    - Documentation and comments within workflow
    - Workflow annotations
    - Team collaboration

16. **User Type Node** ❌ MISSING
    - Classify user types
    - Route by user category
    - Personalization logic

17. **Start/End Nodes** ⚠️
    - Implicit in every workflow
    - Should be explicitly documented

**Additional Missing Features:**
- Model Parameters configuration
- Output Format specification
- Include History toggle
- Advanced storage beyond Set State

**Action Required**: Research and document all missing nodes. See COMPLETE_NODE_TYPES_LIST.md for details.

#### Node Configuration:
- **Instructions**: Custom prompts per node
- **Input/Output**: Manage connections via Input/Output fields
- **Variable Passing**: Use `{{variable_name}}` in curly braces
- **Naming**: Label nodes clearly for workflow clarity

---

### 3. MCP Integration (100% COMPLETE ✅)

**Source**: Complete Agent Builder Tutorial + UI Screenshot Discovery

#### Complete Process - Pre-built and Custom Servers:

**Step-by-Step: Adding MCP Node**
1. Select "MCP" from sidebar node list
2. Drag MCP node onto canvas
3. Connect to other nodes (input/output)
4. Open properties panel (click MCP node)

**Pre-built Servers:**
- Microsoft Outlook, Gmail, etc.
- Select from dropdown
- Pre-configured by OpenAI

**✅ SOLVED: Custom MCP Server Registration**

**How to Add Custom Servers** (Discovered via UI Screenshot):

1. **Access**: Click MCP node → Click "+ Add" button (top right of MCP panel)

2. **Connection Dialog Opens** with fields:
   - **URL**: `https://your-server.com` (HTTPS required)
   - **Label**: Friendly name (e.g., "Market Data MCP")
   - **Description**: Optional description
   - **Authentication**: Dropdown (Access token/API key, OAuth, etc.)
   - **Token Field**: Add authentication token if needed

3. **Click "Connect"**:
   - Agent Builder attempts connection
   - Verifies MCP protocol handshake
   - Auto-discovers tools via MCP protocol
   - Adds server to your MCP server list

4. **Tools Auto-Discovered**:
   - Agent Builder sends `tools/list` MCP request
   - Server responds with available tools + schemas
   - All tools appear in MCP node configuration
   - Select which tools to enable

**Example: market-mcp-server Configuration**
```
URL: https://market-mcp.fly.dev
Label: Market Data MCP
Description: Real-time market data and analysis tools
Authentication: Access token / API key (if needed)
Token: [Your API key or leave blank for public]
```

**Authentication Options:**
- Access token / API key (Bearer token)
- OAuth (if supported)
- Custom headers (possibly)
- Sent as `Authorization: Bearer {token}` header

**Server Requirements:**
- ✅ HTTPS endpoint (required, no HTTP)
- ✅ MCP protocol implementation
- ✅ HTTP/SSE transport
- ✅ Publicly accessible
- ❌ Localhost NOT accessible from Agent Builder

**Security:**
- Warning: "Only use MCP servers you trust and verify"
- User takes responsibility for custom servers
- No OpenAI approval/whitelisting required
- Self-service registration

---

### 4. Workflow Building Patterns (COMPLETE ✅)

**Source**: Complete Agent Builder Tutorial

#### Common Patterns:

**1. Routing Pattern:**
```
User Input
  ↓
Classification Agent
  ↓
Condition Node
  ├─ Intent A → Agent A
  └─ Intent B → Agent B
```

**2. Approval Pattern:**
```
Agent → User Approval Node
  ├─ Approve → Continue Workflow
  └─ Reject → End/Alternative Path
```

**3. Parallel Processing:**
```
Input
  ├─ Agent 1 (parallel)
  ├─ Agent 2 (parallel)
  └─ Agent 3 (parallel)
    ↓
  Combine Results
```

**4. Security Pattern:**
```
User Input → Jailbreak Guardrail
  ├─ Safe → Continue
  └─ Suspicious → Block/Alert
```

#### Best Practices:
- ✅ Label nodes clearly
- ✅ Maintain logical flow (top-to-bottom, left-to-right)
- ✅ Use Transform nodes for data cleanup
- ✅ Implement error handling (Jailbreak Guardrail)
- ✅ Test each branch separately in preview mode

#### Error Handling Strategies:
- Use Jailbreak Guardrail for input validation
- Implement fallback paths with Condition nodes
- Set default values with Set State nodes
- Log errors for debugging (via Logs sidebar)

#### Performance Optimization:
- Minimize sequential dependencies (use parallel when possible)
- Cache results with Set State nodes
- Use efficient agents (appropriate model selection)
- Test workflow performance in preview mode

---

### 5. Testing & Debugging (COMPLETE ✅)

**Source**: Complete Agent Builder Tutorial

#### Preview Mode:
- **Location**: "Preview" button (top of screen)
- **Function**: Test workflow before publishing
- **Shows**: Real-time execution flow
- **Use Case**: Validate logic and connections

#### View Tool Call Logs:
- **Button**: "View tool call logs" in preview
- **Shows**: All agent tool calls and responses
- **Details**: Request/response payloads
- **Use Case**: Debug tool execution issues

#### Debugging Failures:
- **Button**: "Debug" button in preview
- **Process**: Follow prompts to identify issues
- **Shows**: Error messages and stack traces
- **Use Case**: Fix failed workflows

#### Testing Authentication:
- **Button**: "Test authentication" in MCP node settings
- **Process**: Verifies connection to external server
- **Shows**: Success/failure status
- **Use Case**: Validate API keys/headers before publishing

#### Debugging Best Practices:
1. Test each node individually first
2. Check variable passing with simple values
3. Verify authentication with Test button
4. Review tool call logs for failures
5. Use Debug mode for complex issues

---

### 6. Publishing & Integration (COMPLETE ✅)

**Source**: Complete Agent Builder Tutorial

#### Complete Publishing Process:
1. **Test Thoroughly**: Use preview mode
2. **Verify Components**: Ensure all nodes configured
3. **Click Publish**: Navigate to publish interface
4. **Name Workflow**: Assign descriptive name
5. **Generate Credentials**: Receive Workflow ID + version

#### Workflow ID & Version Management:
- **Workflow ID**: Unique identifier for API calls
- **Version Number**: Increments with each publish
- **Rollback**: Can revert to previous versions
- **Tracking**: Manage versions via 'Manage' sidebar

#### API Integration Code Examples:

**Example 1: Weather Data Fetch**
```python
import requests

url = "https://api.openweathermap.org/data/2.5/weather"
params = {
    'q': 'Melbourne',
    'appid': 'YOUR_API_KEY',
    'units': 'metric'
}
response = requests.get(url, params=params)
weather_data = response.json()
```

**Example 2: ChatKit/SDK Integration**
- Customize chat interface (colors, fonts, visual elements)
- Handle user interactions programmatically
- Manage conversation state
- Track workflow execution

#### ChatKit/SDK Usage Patterns:
- Embed workflows in web applications
- Customize appearance to match brand
- Track user conversations
- Monitor performance metrics

---

### 7. Your Current Architecture (Unchanged)

#### Backend (Python FastAPI)
**File**: `backend/services/agent_orchestrator.py`

```python
# Lines 4295-4301
response = await self.client.responses.create(
    model="gpt-4o",
    assistant_id=self.gvses_assistant_id,  # asst_FgdYMBvUvKUy0mxX5AF7Lmyg
    messages=messages,
    tools=tools,  # ← Tools already configured
    store=True
)
```

**Current Tools** (lines 878-908+):
1. `get_stock_price` - Real-time quotes
2. `get_stock_history` - Historical OHLCV data
3. `get_stock_news` - News articles
4. `get_market_overview` - Market indices
5. `search_symbol` - Company name → ticker resolution
6. (+ additional tools)

**Status**: ✅ Backend tools working via Responses API

#### MCP Server (Node.js)
**File**: `market-mcp-server/index.js`

```javascript
// Line 2 - Current transport
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
```

**Current State**:
- ❌ Uses stdio transport (localhost only)
- ❌ Not accessible from Agent Builder (cloud-based)
- ✅ 35+ market data tools defined
- ❌ No HTTP/SSE network transport
- ❌ No public HTTPS endpoint

**Next Step Required**: Migrate to HTTP/SSE transport (see MCP_NODE_MIGRATION_GUIDE.md)

---

## ⚠️ SIGNIFICANT GAPS REMAINING - ~65% Complete

### ✅ Custom MCP Server Registration - SOLVED
### ❌ Missing 5+ Critical Node Types - See COMPLETE_NODE_TYPES_LIST.md

**Screenshot Discovery** (October 7, 2025, 7:39 PM) revealed the complete process!

**What We Now Know:**
- ✅ "+ Add" button in MCP panel adds custom servers
- ✅ Direct URL input: `https://your-server.com`
- ✅ No approval/whitelisting process needed
- ✅ Self-service, user-initiated registration
- ✅ Auto-discovery via MCP protocol
- ✅ HTTPS required, HTTP not allowed
- ✅ Authentication configured during connection

**For Your market-mcp-server:**
1. Deploy to Fly.io: `https://market-mcp.fly.dev`
2. Click "+ Add" in MCP panel
3. Enter URL, label, optional auth token
4. Click "Connect"
5. 35+ tools auto-discovered
6. Ready to use in workflows!

**No barriers remaining - full integration path documented**

---

## 📊 Corrected Knowledge Completeness Assessment

| Topic | Completeness | Source | Status |
|-------|--------------|--------|--------|
| Agent Builder UI basics | **100%** | Complete Tutorial | ✅ **Complete** |
| **All node types** | **~65%** | Tutorial + TwelveLabs | ⚠️ **INCOMPLETE** |
| Workflow patterns | **80%** | Complete Tutorial | ⚠️ **Missing Loop/Vector Store patterns** |
| Testing & debugging | **100%** | Complete Tutorial | ✅ **Complete** |
| Publishing & integration | **100%** | Complete Tutorial | ✅ **Complete** |
| MCP node (pre-built servers) | **100%** | Complete Tutorial | ✅ **Complete** |
| **Custom MCP server registration** | **100%** | UI Screenshot Discovery | ✅ **SOLVED** |
| Network transport | **100%** | MCP_NODE_MIGRATION_GUIDE | ✅ **Complete** |
| Authentication setup | **100%** | Tutorial + Screenshot | ✅ **Complete** |
| **Vector Store node** | **0%** | Not documented | ❌ **MISSING** |
| **Loop node** | **0%** | Not documented | ❌ **MISSING** |
| **Advanced features** | **30%** | Partial knowledge | ⚠️ **INCOMPLETE** |

**Overall Completeness**: **~65%** ⚠️

**Critical Gaps**:
- Vector Store configuration and usage
- Loop Node configuration and patterns
- Exec, Note, User Type nodes
- Advanced features (Model Parameters, Output Format, Include History)

---

## 🚀 Next Steps - Implementation Ready

### Documentation Phase Complete:
1. ✅ **Document complete tutorial knowledge** (this file)
2. ✅ **Create comprehensive integration guide** (AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md)
3. ✅ **Solve custom MCP server registration** (via screenshot discovery)

### Ready for Implementation:
1. **Migrate market-mcp-server to HTTP/SSE transport** (see MCP_NODE_MIGRATION_GUIDE.md)
2. **Deploy MCP server to Fly.io** (public HTTPS endpoint)
3. **Register market-mcp-server in Agent Builder**:
   - Click MCP node → "+ Add"
   - URL: `https://market-mcp.fly.dev`
   - Label: "Market Data MCP"
   - Authentication: Configure if needed
4. **Build G'sves workflow with MCP tools**
5. **Test and publish workflow**
6. **Integrate with frontend**

---

## 📌 Corrected Knowledge Summary

### What We Know - ~65% Complete:
1. ✅ Agent Builder has **16+ node types** (we documented 11)
2. ✅ MCP node is standard sidebar option
3. ✅ Pre-built MCP servers (Outlook, etc.) available in dropdown
4. ✅ **Custom MCP servers added via "+ Add" button**
5. ✅ **URL format: `https://your-server.com` (HTTPS required)**
6. ✅ **No OpenAI approval/whitelisting needed**
7. ✅ **Self-service registration with auto-discovery**
8. ✅ Authentication configured during connection
9. ✅ Test button validates connection before publishing
10. ✅ Complete workflow building, testing, and publishing process
11. ✅ Full debugging and error handling procedures

### What We're Missing - ~35% Gap:
1. ❌ **Vector Store node** - RAG capabilities, knowledge base storage
2. ❌ **Loop node** - Iteration, batch operations, multi-item processing
3. ❌ Exec node - Command execution
4. ❌ Note node - Documentation and comments
5. ❌ User Type node - User classification
6. ❌ Advanced features - Model Parameters, Output Format, Include History

### Ready for Basic Implementation:
1. ✅ Build workflows with documented 11 node types
2. ✅ Add custom MCP servers via UI
3. ✅ Migrate market-mcp-server to HTTP/SSE transport
4. ✅ Deploy to public HTTPS endpoint
5. ⚠️ Complete G'sves integration (missing advanced features)

---

## 📚 Documentation Status - Complete

### ✅ All Documentation Complete:

**1. MCP_NODE_MIGRATION_GUIDE.md** (500+ lines)
- Adding HTTP/SSE transport to MCP servers
- Code examples for Node.js and Python
- Deployment to Fly.io/Railway
- Security hardening
- **Status**: ✅ Complete and ready to use

**2. AGENT_BUILDER_VIDEO_INSIGHTS.md**
- Initial video analysis (travel agent example)
- **Status**: ✅ Complete

**3. CURRENT_ARCHITECTURE_CLARIFICATION.md**
- Explains Responses API vs Agent Builder
- **Status**: ✅ Complete

**4. THIS FILE (AGENT_BUILDER_MCP_CURRENT_KNOWLEDGE.md)**
- Comprehensive knowledge base (100% complete)
- **Status**: ✅ Complete

**5. AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md**
- Step-by-step workflow building
- Complete integration process with Part 4 custom server registration
- Code examples
- **Status**: ✅ Complete

**6. CUSTOM_MCP_SERVER_QUESTIONS.md**
- 30+ questions answered via screenshot discovery
- Complete integration path documented
- All knowledge gaps resolved
- **Status**: ✅ Complete

---

## 🔍 Information Sources

### Primary Sources:
1. ✅ Complete Agent Builder Tutorial (1-hour course, 2x speed video)
2. ✅ "Intro to Agent Builder" initial video
3. ✅ OpenAI official documentation
4. ✅ Node Reference documentation
5. ✅ **UI Screenshot Discovery** (custom server registration)
6. ✅ TwelveLabs MCP installation example

### Documentation URLs:
- https://openai.github.io/openai-agents-python/mcp/
- https://platform.openai.com/docs/mcp
- https://openai.com/index/introducing-agentkit/
- https://openai.com/index/new-tools-for-building-agents/

### Screenshot Evidence:
- **"Connect to MCP Server" Dialog** - Revealed complete custom server registration process
- **MCP Panel "+ Add" Button** - Entry point for custom server registration
- **Authentication Dropdown** - Shows available auth methods (Access token/API key, OAuth, etc.)

---

**Status**: ⚠️ ~65% COMPLETE - Missing critical node types and advanced features
**Blocking Issues**: Need Vector Store and Loop Node documentation for full G'sves capabilities
**Ready for**: Basic implementation with 11 documented nodes
**Goal Status**: Partial - Custom MCP registration solved, but missing 5+ node types
**Next Priority**: Research and document Vector Store and Loop Node configurations

**See COMPLETE_NODE_TYPES_LIST.md for comprehensive gap analysis and action items.**
