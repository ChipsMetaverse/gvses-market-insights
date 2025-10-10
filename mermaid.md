# GVSES Market Analysis Assistant - Architecture Diagrams

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        App[App.tsx]
        Dashboard[TradingDashboardSimple]
        Chart[TradingChart]
        Toolbar[ChartToolbar]
        TimeRange[TimeRangeSelector]
        VoiceUI[Voice Assistant UI]

        App --> Dashboard
        Dashboard --> Chart
        Dashboard --> VoiceUI
        Chart --> Toolbar
        Chart --> TimeRange
    end

    subgraph "Backend (FastAPI)"
        API[FastAPI Server]
        MarketService[MarketServiceWrapper]
        AlpacaService[Alpaca Service]
        MCPService[MCP Service]
        ElevenLabsProxy[ElevenLabs Proxy]

        API --> MarketService
        MarketService --> AlpacaService
        MarketService --> MCPService
        API --> ElevenLabsProxy
    end

    subgraph "External APIs"
        AlpacaAPI[Alpaca Markets API]
        YahooAPI[Yahoo Finance via MCP]
        CNBCAPI[CNBC News via MCP]
        ElevenLabs[ElevenLabs Conversational AI]
        Claude[Claude AI]
    end

    subgraph "MCP Servers"
        MarketMCP[market-mcp-server<br/>Node.js 22]
        AlpacaMCP[alpaca-mcp-server<br/>Python]
    end

    Dashboard -->|API Calls| API
    VoiceUI -->|WebSocket| ElevenLabsProxy

    AlpacaService --> AlpacaAPI
    AlpacaService --> AlpacaMCP
    MCPService --> MarketMCP

    MarketMCP --> YahooAPI
    MarketMCP --> CNBCAPI
    ElevenLabsProxy --> ElevenLabs
    API --> Claude

    style Toolbar fill:#e1f5ff
    style Dashboard fill:#fff4e6
    style Chart fill:#e8f5e9
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

## Recent Updates

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
