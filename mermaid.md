# GVSES Market Analysis Assistant - Architecture Diagrams

## System Architecture Overview with OpenAI Agent Builder Integration

```mermaid
graph TB
    subgraph "OpenAI Agent Builder Workflow"
        Start[Start Node]
        IntentClass[Intent Classifier<br/>- market_data<br/>- chart_command<br/>- general_chat]
        IfElse[If/Else Router<br/>Market Data Branch]
        MarketAgent[Market Data Agent]
        Transform[Transform Node]
        MCPNode[MCP Integration]
        GsvesAgent[G'sves Agent]
        EndNode1[End Node 1]
        EndNode2[End Node 2]
        
        Start --> IntentClass
        IntentClass --> IfElse
        IfElse -->|market_data| MarketAgent
        MarketAgent --> Transform
        Transform --> EndNode1
        IfElse -->|else| MCPNode
        MCPNode --> GsvesAgent
        GsvesAgent --> EndNode2
    end

    subgraph "Frontend (React + TypeScript)"
        App[App.tsx]
        Dashboard[TradingDashboardSimple]
        Chart[TradingChart]
        Toolbar[ChartToolbar]
        TimeRange[TimeRangeSelector]
        VoiceUI[Voice Assistant UI]
        ChartService[chartToolService]
        ControlService[chartControlService]

        App --> Dashboard
        Dashboard --> Chart
        Dashboard --> VoiceUI
        Chart --> Toolbar
        Chart --> TimeRange
        VoiceUI --> ChartService
        ChartService --> ControlService
    end

    subgraph "Backend (FastAPI)"
        API[FastAPI Server]
        MarketWrapper[MarketServiceWrapper<br/>Alpaca-first + MCP fallback]
        AlpacaService[Alpaca Service<br/>300-400ms]
        MCPService[MCP Service<br/>3-15s fallback]
        VoiceRelay[OpenAIRealtimeRelay<br/>Triple Provider System]
        AgentOrch[AgentOrchestrator]

        API --> MarketWrapper
        MarketWrapper --> AlpacaService
        MarketWrapper --> MCPService
        API --> VoiceRelay
        API --> AgentOrch
    end

    subgraph "External APIs"
        AlpacaAPI[Alpaca Markets API<br/>Professional Data]
        YahooAPI[Yahoo Finance via MCP]
        CNBCAPI[CNBC News via MCP]
        ElevenLabs[ElevenLabs Conversational AI]
        OpenAIRT[OpenAI Realtime API]
        Claude[Claude AI]
        OpenAIBuilder[OpenAI Agent Builder API]
    end

    subgraph "MCP Servers"
        MarketMCP[market-mcp-server<br/>Node.js 22<br/>35+ tools]
        AlpacaMCP[alpaca-mcp-server<br/>Python]
    end

    Dashboard -->|API Calls| API
    VoiceUI -->|WebSocket| VoiceRelay
    
    IntentClass -->|Classification| API
    MarketAgent -->|Data Request| MarketWrapper
    MCPNode -->|Tool Call| MCPService
    GsvesAgent -->|AI Response| AgentOrch

    AlpacaService --> AlpacaAPI
    AlpacaService --> AlpacaMCP
    MCPService --> MarketMCP

    MarketMCP --> YahooAPI
    MarketMCP --> CNBCAPI
    
    VoiceRelay --> ElevenLabs
    VoiceRelay --> OpenAIRT
    VoiceRelay --> OpenAIBuilder
    
    API --> Claude
    AgentOrch --> OpenAIBuilder

    style IntentClass fill:#ffebee
    style MarketWrapper fill:#e8f5e9
    style VoiceRelay fill:#fff3e0
    style Dashboard fill:#fff4e6
    style Chart fill:#e1f5ff
```

## Frontend Component Architecture

```mermaid
graph TB
    subgraph "TradingDashboardSimple Component"
        MarketInsights[Market Insights Panel<br/>- Dynamic Watchlist<br/>- Symbol Search<br/>- Real-time Prices]
        ChartPanel[Interactive Charts Panel<br/>- TradingChart<br/>- ChartToolbar<br/>- TimeRangeSelector]
        AnalysisPanel[Chart Analysis Panel<br/>- News Feed<br/>- Technical Levels<br/>- Expandable Cards]
    end

    subgraph "TradingChart Component"
        Toolbar[ChartToolbar<br/>- Chart Types<br/>- Drawing Tools<br/>- Indicators<br/>- Quick Actions]
        MainChart[Lightweight Charts<br/>- Candlestick Series<br/>- Technical Levels<br/>- Price Lines]
        OscillatorChart[Oscillator Pane<br/>- RSI<br/>- MACD]
        TimeSelector[TimeRangeSelector<br/>- 1D/5D/1M/6M/1Y/2Y/3Y/YTD/MAX]
    end

    subgraph "State Management"
        IndicatorState[useIndicatorState<br/>- MA20/50/200<br/>- Bollinger Bands<br/>- RSI/MACD]
        ChartSeries[useChartSeries<br/>- Series Management<br/>- Add/Remove/Update]
        SymbolSearch[useSymbolSearch<br/>- Debounced Search<br/>- Alpaca API Integration]
    end

    ChartPanel --> Toolbar
    ChartPanel --> MainChart
    ChartPanel --> OscillatorChart
    ChartPanel --> TimeSelector

    MainChart --> IndicatorState
    MainChart --> ChartSeries
    MarketInsights --> SymbolSearch

    style Toolbar fill:#bbdefb
    style MainChart fill:#c8e6c9
    style IndicatorState fill:#fff9c4
```

## ChartToolbar Component Structure

```mermaid
graph LR
    subgraph "ChartToolbar Features"
        ChartType[Chart Type Selector<br/>📊 Candlestick<br/>📉 Line<br/>📈 Area<br/>▅ Bars]
        DrawTools[Drawing Tools<br/>📈 Trend Line<br/>━ Horizontal<br/>┃ Vertical<br/>▭ Rectangle<br/>φ Fibonacci<br/>A Text]
        Indicators[Technical Indicators<br/>MA<br/>Bollinger<br/>RSI<br/>MACD<br/>Volume<br/>Stochastic]
        Actions[Quick Actions<br/>🔍+ Zoom In<br/>🔍- Zoom Out<br/>⊞ Fit Content<br/>📷 Screenshot<br/>⚙️ Settings]
    end

    ChartType --> TradingChart
    DrawTools --> TradingChart
    Indicators --> IndicatorState
    Actions --> TradingChart

    style ChartType fill:#e3f2fd
    style DrawTools fill:#f3e5f5
    style Indicators fill:#fff3e0
    style Actions fill:#e0f2f1
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant Chart
    participant Toolbar
    participant API
    participant Alpaca
    participant MCP

    User->>Dashboard: Select Symbol "TSLA"
    Dashboard->>API: GET /api/stock-price?symbol=TSLA
    API->>Alpaca: Request Quote

    alt Alpaca Success
        Alpaca-->>API: Quote Data (300-400ms)
        API-->>Dashboard: {price, change, data_source: "alpaca"}
    else Alpaca Failure
        API->>MCP: Fallback Request
        MCP-->>API: Quote Data (3-15s)
        API-->>Dashboard: {price, change, data_source: "yahoo_mcp"}
    end

    Dashboard->>Chart: Display Price
    Chart->>API: GET /api/stock-history?symbol=TSLA&days=100
    API->>Alpaca: Request Historical Data
    Alpaca-->>API: Candles Data
    API-->>Chart: Historical OHLCV

    Chart->>Chart: Render Candlestick Series
    User->>Toolbar: Click "Moving Averages"
    Toolbar->>Chart: Toggle MA Indicator
    Chart->>Chart: Calculate & Display MA20/50/200

    User->>Toolbar: Select "Trend Line" Tool
    Toolbar->>Chart: Activate Drawing Mode
    Chart->>Chart: Enable Trend Line Drawing
```

## Performance Characteristics

| Component | Response Time | Data Source |
|-----------|---------------|-------------|
| Stock Quote (Alpaca) | 300-400ms | Alpaca Markets |
| Stock Quote (MCP Fallback) | 3-15s | Yahoo Finance |
| Historical Data (Alpaca) | 400-500ms | Alpaca Markets |
| News Feed (MCP) | 3-5s | CNBC + Yahoo |
| Symbol Search | <500ms | Alpaca Asset DB |
| Voice Command Processing | 1-3s | ElevenLabs AI |
| Chart Render | <100ms | Client-side |

## Voice Command Flow with Agent Builder

```mermaid
sequenceDiagram
    participant User
    participant Voice as Voice UI
    participant Agent as Agent Builder
    participant Intent as Intent Classifier
    participant Router as If/Else Router
    participant Market as Market Agent
    participant MCP as MCP Node
    participant API as FastAPI
    participant Alpaca
    participant Chart

    User->>Voice: "Show me Tesla stock"
    Voice->>Agent: Voice Command
    Agent->>Intent: Classify Intent
    Intent-->>Agent: {intent: "chart_command", symbol: "TSLA"}
    
    Agent->>Router: Route Based on Intent
    
    alt Chart Command Path
        Router->>Market: Get Market Data
        Market->>API: Request TSLA Data
        API->>Alpaca: Fetch Quote/History
        Alpaca-->>API: Data (300-400ms)
        API-->>Market: Formatted Data
        Market-->>Chart: Display Chart
    else General Query Path
        Router->>MCP: Use MCP Tools
        MCP->>API: Fallback Query
        API-->>MCP: Response (3-15s)
        MCP-->>Voice: AI Response
    end
```

## Triple Voice Provider Architecture

```mermaid
graph LR
    subgraph "Voice Providers"
        EL[ElevenLabs<br/>Primary Provider<br/>1-3s response]
        OAI[OpenAI Realtime<br/>Alternative Provider<br/>Sub-second]
        IA[Internal Agent<br/>Fallback System]
    end
    
    subgraph "Unified Interface"
        Relay[OpenAIRealtimeRelay<br/>- Session Management<br/>- Provider Switching<br/>- Error Handling]
    end
    
    subgraph "Features"
        F1[Session Limits<br/>Max 10 concurrent]
        F2[Timeout Management<br/>300s session / 60s idle]
        F3[Background Cleanup<br/>Every 60s]
    end
    
    EL --> Relay
    OAI --> Relay
    IA --> Relay
    
    Relay --> F1
    Relay --> F2
    Relay --> F3
    
    style EL fill:#e8f5e9
    style Relay fill:#fff3e0
```

## Agent Builder Enhancement Roadmap

```mermaid
graph TD
    subgraph "Current State (85% Complete)"
        C1[✅ Intent Classifier]
        C2[✅ If/Else Routing]
        C3[✅ MCP Integration]
        C4[✅ Transform Nodes]
        C5[✅ Agent Nodes]
        C6[✅ End Nodes]
    end
    
    subgraph "Missing Components (15%)"
        M1[⏳ File Search<br/>Vector DB Integration]
        M2[⏳ Guardrails<br/>Content Moderation]
        M3[⏳ While Loops<br/>Retry Logic]
        M4[⏳ User Approval<br/>Trade Confirmation]
        M5[⏳ Set State<br/>Variable Management]
    end
    
    subgraph "Benefits When Complete"
        B1[Visual Workflow Editing]
        B2[No-Code Modifications]
        B3[Real-time Testing]
        B4[Version Control]
        B5[A/B Testing Flows]
    end
    
    C1 --> B1
    M1 --> B2
    M2 --> B3
    M3 --> B4
    M4 --> B5
    
    style C1 fill:#c8e6c9
    style C2 fill:#c8e6c9
    style C3 fill:#c8e6c9
    style M1 fill:#fff9c4
    style M2 fill:#fff9c4
```

## System Integration Points

```mermaid
graph TB
    subgraph "Knowledge Base Integration"
        KB[Knowledge Base<br/>Chart Tools & Indicators]
        CTR[ChartToolRegistry<br/>Auto-discovery]
        TSS[Semantic Search<br/>Natural Language]
        
        KB --> CTR
        CTR --> TSS
    end
    
    subgraph "Market Data Pipeline"
        MDP[Market Data Request]
        ALP[Alpaca API<br/>300-400ms]
        MCPF[MCP Fallback<br/>3-15s]
        
        MDP --> ALP
        ALP -->|Failure| MCPF
    end
    
    subgraph "Voice Processing"
        VC[Voice Command]
        IC[Intent Classification]
        CM[Command Mapping]
        EX[Execution]
        
        VC --> IC
        IC --> CM
        CM --> EX
    end
    
    TSS --> CM
    ALP --> EX
    MCPF --> EX
    
    style KB fill:#e1f5ff
    style ALP fill:#c8e6c9
    style IC fill:#ffebee
```

## Recent Updates

### OpenAI Agent Builder Integration (Oct 11, 2025)
- **Workflow Created**: Intent Classifier → If/Else → Market Data/MCP branches
- **85% Complete**: Missing File Search, Guardrails, While loops, User Approval
- **Integration Points**: Direct connection to MarketServiceWrapper and MCP servers
- **Future Vision**: Visual workflow editing replacing code-based orchestration

### Deep System Investigation (Oct 11, 2025)
- **Triple Voice Provider System**: ElevenLabs + OpenAI Realtime + Internal Agent
- **Performance Metrics Documented**: Alpaca (300-400ms) vs MCP (3-15s)
- **Security Issue Found**: Hardcoded API key in test_openai_realtime.py
- **Architecture Validated**: Professional-grade with intelligent fallbacks

### Knowledge Base → Chart Tools Integration (Oct 2, 2025)
- **ChartToolRegistry Service**: Auto-registers chart capabilities from knowledge base as callable tools
- **Tool Discovery API**: `/api/agent/tools/chart` endpoint returns all available chart tools with knowledge context
- **Semantic Tool Search**: `/api/agent/tools/chart/search` for natural language tool discovery
- **OpenAI Tool Mapper Integration**: Chart control tools automatically added to OpenAI function calling
- **Frontend chartToolService**: Unified access to knowledge-based chart tools
- **Voice Command Integration**: Knowledge-based tool mapping in `chartControlService.parseAgentResponse()`
- **Knowledge → Tool Mapping**: RSI, MACD, Bollinger, MA indicators mapped from knowledge base topics

**Architecture Flow**:
```
User Voice Command → chartToolService.mapVoiceCommandToTool()
                  → Semantic Search on Knowledge Base
                  → Match to ChartTool (RSI, MACD, etc.)
                  → Generate Frontend Command (INDICATOR:RSI)
                  → Execute via chartControlService
```

### ChartToolbar (Oct 2, 2025)
- Added TradingView-style toolbar component
- Chart type selector (Candlestick, Line, Area, Bars)
- Drawing tools panel with 6 tools
- Technical indicators quick access
- Quick actions (Zoom, Fit, Screenshot, Settings)
- Integrated with existing indicator system

### TimeRangeSelector Styling Fix (Oct 1, 2025)
- Fixed unstyled button display issue
- Added comprehensive CSS styling
- Flexbox layout with proper spacing
- Hover and active states
- Touch-friendly 44px minimum width

## Security & Optimization Recommendations

### Critical Security Issues
1. **Hardcoded API Key**: Remove from `backend/test_openai_realtime.py`
2. **Environment Variables**: Ensure all keys in `.env` files only
3. **API Key Rotation**: Implement regular key rotation policy

### Performance Optimizations
1. **Redis Caching**: Implement for frequent stock queries
2. **Circuit Breaker**: Add for Alpaca API failures
3. **Request Batching**: Combine multiple symbol requests
4. **WebSocket Pooling**: Reuse connections for efficiency

### Agent Builder Enhancements Needed
1. **File Search Node**: Connect to vector database for knowledge queries
2. **Guardrails Node**: Add content moderation for trading commands
3. **While Loop**: Implement retry logic before fallback
4. **User Approval**: Require confirmation for trades
5. **Set State Node**: Manage conversation variables
