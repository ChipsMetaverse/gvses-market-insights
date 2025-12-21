# GVSES System Architecture - Mermaid Diagrams

## 1. OpenAI Agent Builder Workflow (v44 - Production)

```mermaid
graph TD
    Start[User Input] --> Transform[Transform Input]
    Transform --> IntentClassifier[Intent Classifier Agent]
    IntentClassifier --> IfElse{If/Else Decision}

    IfElse -->|Single Ticker Query| GVSES[GVSES Widget Agent]
    IfElse -->|General Query| GeneralAgent[General G'sves Agent]

    GVSES --> WidgetRender[Render Stock Widget]
    GeneralAgent --> TextResponse[Text Response]

    style IfElse fill:#f9f,stroke:#333,stroke-width:4px
    style GVSES fill:#9f9,stroke:#333,stroke-width:2px
    style GeneralAgent fill:#99f,stroke:#333,stroke-width:2px
```

### If/Else Condition Logic (v44)
```javascript
// Routes to GVSES Widget Agent if:
(input.intent == "market_data" || input.intent == "chart_command")
&& input.symbol
&& input.symbol.length > 0
&& !input.symbol.contains(',')
&& !input.symbol.contains(' ')

// Otherwise routes to General G'sves Agent
```

## 2. GVSES Widget Agent Data Flow

```mermaid
graph LR
    A[User Query: "show me AAPL"] --> B[Intent Classifier]
    B --> C{Intent Type}
    C -->|market_data| D[Extract Symbol]
    C -->|chart_command| D

    D --> E{Validate Symbol}
    E -->|Single Ticker| F[Call MCP Tools]
    E -->|Multiple/None| G[General Agent]

    F --> F1[get_stock_quote]
    F --> F2[get_stock_history]
    F --> F3[get_market_news]
    F --> F4[get_earnings_calendar]

    F1 --> H[Format JSON Response]
    F2 --> H
    F3 --> H
    F4 --> H

    H --> I{Validate 15 Fields}
    I -->|All Present| J[Render Widget]
    I -->|Missing Fields| K[Widget Fails Silently]

    style F fill:#9f9,stroke:#333,stroke-width:2px
    style H fill:#ff9,stroke:#333,stroke-width:2px
    style J fill:#9f9,stroke:#333,stroke-width:2px
    style K fill:#f99,stroke:#333,stroke-width:2px
```

## 3. Widget JSON Schema (15 Required Fields)

```mermaid
graph TD
    JSON[Widget JSON Response] --> BasicInfo[Basic Info]
    JSON --> Price[Price Data]
    JSON --> Chart[Chart Data]
    JSON --> Stats[Stats]
    JSON --> Technical[Technical Analysis]
    JSON --> Patterns[Patterns]
    JSON --> News[News]
    JSON --> Events[Events]

    BasicInfo --> B1[1. company]
    BasicInfo --> B2[2. symbol]
    BasicInfo --> B3[3. analysis]
    BasicInfo --> B4[4. timestamp]

    Price --> P1[5. price.current]
    Price --> P2[price.changeLabel]
    Price --> P3[price.changeColor]
    Price --> P4[price.afterHours?]

    Chart --> C1[6. timeframes]
    Chart --> C2[7. selectedTimeframe]
    Chart --> C3[8. chartData]

    Stats --> S1[9. stats.open/volume/marketCap]
    Stats --> S2[stats.dayLow/High]
    Stats --> S3[stats.yearLow/High]
    Stats --> S4[stats.eps/peRatio]

    Technical --> T1[10. technical.position]
    Technical --> T2[technical.color]
    Technical --> T3[technical.levels]

    Patterns --> PA1[11. patterns array]

    News --> N1[12. newsFilters]
    News --> N2[13. selectedSource]
    News --> N3[14. news array]

    Events --> E1[15. events array ⚠️]

    style E1 fill:#f99,stroke:#333,stroke-width:4px
    style JSON fill:#9f9,stroke:#333,stroke-width:2px
```

## 4. Chart Component Rendering Flow

```mermaid
sequenceDiagram
    participant Agent as GVSES Agent
    participant Widget as Widget Template
    participant Chart as Chart Component
    participant UI as User Interface

    Agent->>Widget: JSON with chartData
    Widget->>Widget: Validate JSON Schema

    alt All 15 Fields Present
        Widget->>Chart: Pass chartData + config
        Chart->>Chart: Validate Chart Properties

        alt Valid Properties
            Chart->>UI: Render Chart
            UI->>UI: Display Stock Analysis
        else Invalid Properties
            Chart->>UI: Component Error
        end
    else Missing Fields (e.g., events)
        Widget->>UI: Silent Failure (No Render)
    end

    Note over Agent,UI: Critical: events field must be present even if empty
```

## 5. Intent Classification Decision Tree

```mermaid
graph TD
    Input[User Input] --> Classify[Intent Classifier]

    Classify --> Intent1{Intent Type}

    Intent1 -->|market_data| Symbol1{Has Symbol?}
    Intent1 -->|chart_command| Symbol1
    Intent1 -->|Other| General[General Agent]

    Symbol1 -->|Yes| Length{Symbol Length > 0?}
    Symbol1 -->|No| General

    Length -->|Yes| Contains{Contains , or space?}
    Length -->|No| General

    Contains -->|No Comma/Space| Widget[GVSES Widget]
    Contains -->|Has Comma/Space| General

    style Widget fill:#9f9,stroke:#333,stroke-width:3px
    style General fill:#99f,stroke:#333,stroke-width:3px
```

## 6. Example Query Routing (v44)

```mermaid
graph LR
    Q1["show me AAPL"] --> R1[✅ GVSES Widget]
    Q2["analyze Tesla"] --> R2[✅ GVSES Widget]
    Q3["NVDA chart"] --> R3[✅ GVSES Widget]

    Q4["scan the market"] --> R4[✅ General Agent]
    Q5["AAPL, TSLA"] --> R5[✅ General Agent]
    Q6["AAPL TSLA"] --> R6[✅ General Agent]
    Q7["what's trending"] --> R7[✅ General Agent]

    style R1 fill:#9f9,stroke:#333,stroke-width:2px
    style R2 fill:#9f9,stroke:#333,stroke-width:2px
    style R3 fill:#9f9,stroke:#333,stroke-width:2px
    style R4 fill:#99f,stroke:#333,stroke-width:2px
    style R5 fill:#99f,stroke:#333,stroke-width:2px
    style R6 fill:#99f,stroke:#333,stroke-width:2px
    style R7 fill:#99f,stroke:#333,stroke-width:2px
```

## 7. System Architecture Overview

```mermaid
graph TB
    User[User] --> OpenAI[OpenAI Agent Builder]

    OpenAI --> Workflow[GVSES Workflow v44]

    Workflow --> Widget[GVSES Widget Agent]
    Workflow --> General[General G'sves Agent]

    Widget --> MCP[MCP Tools]
    General --> MCP

    MCP --> Market[market-mcp-server]
    MCP --> Alpaca[alpaca-mcp-server]

    Market --> Yahoo[Yahoo Finance API]
    Market --> CNBC[CNBC API]

    Alpaca --> AlpacaAPI[Alpaca Markets API]

    Widget --> Render[Widget Renderer]
    Render --> ChartComp[Chart Component]
    Render --> Display[User Interface]

    style OpenAI fill:#f9f,stroke:#333,stroke-width:3px
    style Widget fill:#9f9,stroke:#333,stroke-width:2px
    style MCP fill:#ff9,stroke:#333,stroke-width:2px
```

## 8. Widget Validation Flow

```mermaid
stateDiagram-v2
    [*] --> ReceiveJSON
    ReceiveJSON --> ValidateSchema

    ValidateSchema --> CheckFields

    CheckFields --> Field1: company
    CheckFields --> Field2: symbol
    CheckFields --> Field3: analysis
    CheckFields --> Field4: timestamp
    CheckFields --> Field5: price
    CheckFields --> Field6: timeframes
    CheckFields --> Field7: selectedTimeframe
    CheckFields --> Field8: chartData
    CheckFields --> Field9: stats
    CheckFields --> Field10: technical
    CheckFields --> Field11: patterns
    CheckFields --> Field12: newsFilters
    CheckFields --> Field13: selectedSource
    CheckFields --> Field14: news
    CheckFields --> Field15: events ⚠️

    Field1 --> AllPresent
    Field2 --> AllPresent
    Field3 --> AllPresent
    Field4 --> AllPresent
    Field5 --> AllPresent
    Field6 --> AllPresent
    Field7 --> AllPresent
    Field8 --> AllPresent
    Field9 --> AllPresent
    Field10 --> AllPresent
    Field11 --> AllPresent
    Field12 --> AllPresent
    Field13 --> AllPresent
    Field14 --> AllPresent
    Field15 --> AllPresent

    AllPresent --> RenderWidget
    CheckFields --> MissingField: Any Field Missing

    MissingField --> SilentFailure
    RenderWidget --> [*]
    SilentFailure --> [*]

    note right of Field15
        Most commonly forgotten field!
        Must include even if empty array
    end note
```

## 9. Pattern Detection & Key Levels Data Flow (Dec 14, 2025)

```mermaid
graph TB
    Request[Pattern Detection Request] --> CheckInterval{Check Interval Type}

    CheckInterval -->|Intraday: 1m,5m,15m,30m,1H,2H,4H| FetchIntraday[Fetch Intraday Candles]
    CheckInterval -->|Daily: 1d,1wk,1mo| FetchDaily[Fetch Daily Candles]

    FetchIntraday --> FetchDailyForBTD[Fetch 365 Days Daily Candles]
    FetchDaily --> UseSameCandles[Use Same Candles for All Levels]

    FetchDailyForBTD --> ProcessBoth[Process Both Datasets]
    UseSameCandles --> ProcessDaily[Process Daily Data]

    ProcessBoth --> CalcPivots[Calculate Pivot Points from Intraday]
    ProcessBoth --> CalcBTDDaily[Calculate BTD from 365 Daily Candles]
    ProcessBoth --> CalcPDH[Calculate PDH/PDL from Previous Day]

    ProcessDaily --> CalcDailyPivots[Calculate Pivot Points from Daily]
    ProcessDaily --> CalcDailyBTD[Calculate BTD from Daily Candles]
    ProcessDaily --> CalcDailyPDH[Calculate PDH/PDL from Daily]

    CalcPivots --> GenerateBL[Generate BL Level]
    CalcPivots --> GenerateSH[Generate SH Level]

    CalcDailyPivots --> GenerateDailyBL[Generate BL Level]
    CalcDailyPivots --> GenerateDailySH[Generate SH Level]

    CalcBTDDaily --> BTDLevel[BTD 200-Day SMA]
    CalcDailyBTD --> DailyBTDLevel[BTD 200-Day SMA]

    CalcPDH --> PDHPDLLevels[PDH/PDL Levels]
    CalcDailyPDH --> DailyPDHPDLLevels[PDH/PDL Levels]

    GenerateBL --> Combine[Combine All 5 Levels]
    GenerateSH --> Combine
    BTDLevel --> Combine
    PDHPDLLevels --> Combine

    GenerateDailyBL --> CombineDaily[Combine All 5 Levels]
    GenerateDailySH --> CombineDaily
    DailyBTDLevel --> CombineDaily
    DailyPDHPDLLevels --> CombineDaily

    Combine --> Frontend[Send to Frontend]
    CombineDaily --> Frontend

    Frontend --> Display[Display on Chart]

    style FetchDailyForBTD fill:#9f9,stroke:#333,stroke-width:2px
    style CalcBTDDaily fill:#9f9,stroke:#333,stroke-width:2px
    style BTDLevel fill:#2196f3,stroke:#333,stroke-width:3px
    style DailyBTDLevel fill:#2196f3,stroke:#333,stroke-width:3px
    style Combine fill:#ff9,stroke:#333,stroke-width:2px
```

### Key Level Types and Data Sources

```mermaid
graph LR
    subgraph "Intraday Timeframes (1m, 5m, 15m, 30m, 1H, 2H, 4H)"
        I1[Intraday Candles] --> BL1[BL - Buy Low]
        I1 --> SH1[SH - Sell High]
        D1[365 Days Daily Candles] --> BTD1[BTD - 200 Day SMA]
        PD1[Previous Day Data] --> PDH1[PDH - Previous Day High]
        PD1 --> PDL1[PDL - Previous Day Low]
    end

    subgraph "Daily Timeframes (1d, 1wk, 1mo)"
        D2[Daily Candles] --> BL2[BL - Buy Low]
        D2 --> SH2[SH - Sell High]
        D2 --> BTD2[BTD - 200 Day SMA]
        D2 --> PDH2[PDH - Previous Day High]
        D2 --> PDL2[PDL - Previous Day Low]
    end

    style BTD1 fill:#2196f3,stroke:#333,stroke-width:3px
    style BTD2 fill:#2196f3,stroke:#333,stroke-width:3px
    style D1 fill:#9f9,stroke:#333,stroke-width:2px
```

### BTD Calculation Consistency

```mermaid
graph TD
    A[All Timeframes] --> B{Data Source for BTD}
    B -->|Always| C[365 Days of Daily Candles]

    C --> D[Extract Last 200 Trading Days]
    D --> E[Calculate Simple Moving Average]
    E --> F[BTD Value: Consistent Across All Timeframes]

    F --> G1[1m Chart: BTD = $368.34]
    F --> G2[5m Chart: BTD = $368.34]
    F --> G3[15m Chart: BTD = $368.34]
    F --> G4[1H Chart: BTD = $368.34]
    F --> G5[1d Chart: BTD = $368.34]

    style C fill:#9f9,stroke:#333,stroke-width:2px
    style F fill:#2196f3,stroke:#333,stroke-width:3px
    style G1 fill:#ff9,stroke:#333,stroke-width:1px
    style G2 fill:#ff9,stroke:#333,stroke-width:1px
    style G3 fill:#ff9,stroke:#333,stroke-width:1px
    style G4 fill:#ff9,stroke:#333,stroke-width:1px
    style G5 fill:#ff9,stroke:#333,stroke-width:1px
```

## 10. 3-Tier Historical Data Caching Architecture (Dec 20, 2025)

```mermaid
graph TB
    Request[Chart Data Request: 1Y Interval] --> CheckInterval{Determine<br/>Interval Type}

    CheckInterval -->|Yearly| FetchMonthly[Request Monthly Bars<br/>50 years: 1976-2025]
    CheckInterval -->|Other| DirectFetch[Standard Fetch]

    FetchMonthly --> L1{L1: Redis Cache<br/>2ms response}

    L1 -->|Cache Hit| Return1[Return Cached Data<br/>~15 yearly candles]
    L1 -->|Cache Miss| L2{L2: Supabase DB<br/>20ms response}

    L2 -->|Complete Data| CheckGaps{Check Data<br/>Coverage}
    L2 -->|Partial/No Data| L3[L3: Fetch from APIs]

    CheckGaps -->|Complete| Return2[Return from DB<br/>Store in Redis]
    CheckGaps -->|Has Gaps| L3

    L3 --> DateCheck{Data Age<br/>Check}

    DateCheck -->|Pre-2020<br/>Old Data| YahooMCP[Yahoo Finance<br/>via Market MCP<br/>HTTP Mode Port 3001]
    DateCheck -->|Post-2020<br/>Recent Data| Alpaca[Alpaca Markets API<br/>~5 year limit]

    YahooMCP --> Store[Store Bars in<br/>Supabase + Redis]
    Alpaca --> Store

    Store --> Aggregate{Is Yearly<br/>Interval?}

    Aggregate -->|Yes| MonthlyToYearly[Bar Aggregator:<br/>12 months → 1 year<br/>Jan open, Dec close]
    Aggregate -->|No| Return3[Return Bars]

    MonthlyToYearly --> Return3
    Return3 --> Frontend[Send to Frontend:<br/>~15 yearly candles]

    style L1 fill:#ff9,stroke:#333,stroke-width:3px
    style L2 fill:#9f9,stroke:#333,stroke-width:3px
    style L3 fill:#f99,stroke:#333,stroke-width:2px
    style YahooMCP fill:#9cf,stroke:#333,stroke-width:2px
    style MonthlyToYearly fill:#f9f,stroke:#333,stroke-width:2px
```

### Cache Performance Metrics

```mermaid
graph LR
    subgraph "First Request (Cache Miss)"
        R1[Request] --> API1[Fetch from Yahoo MCP<br/>4-8 seconds]
        API1 --> DB1[Store in Supabase]
        DB1 --> Cache1[Cache in Redis]
        Cache1 --> Response1[Return: ~15 yearly candles<br/>Total: 4-8s]
    end

    subgraph "Second Request (Cache Hit)"
        R2[Request] --> Redis2[Check Redis L1<br/>2ms]
        Redis2 -->|Hit| Response2[Return: ~15 yearly candles<br/>Total: 2ms]
        Redis2 -->|Miss| Supabase2[Check Supabase L2<br/>20ms]
        Supabase2 --> Response3[Return: ~15 yearly candles<br/>Total: 20ms]
    end

    style API1 fill:#f99,stroke:#333,stroke-width:2px
    style Redis2 fill:#ff9,stroke:#333,stroke-width:2px
    style Supabase2 fill:#9f9,stroke:#333,stroke-width:2px
    style Response2 fill:#9f9,stroke:#333,stroke-width:3px
```

## 11. Yearly Aggregation Data Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant Backend
    participant HistoricalService
    participant Redis
    participant Supabase
    participant MarketMCP
    participant YahooFinance
    participant Aggregator

    Frontend->>Backend: GET /api/intraday?interval=1y&symbol=TSLA
    Backend->>HistoricalService: get_bars(TSLA, 1mo, 1976-2025)

    HistoricalService->>Redis: Check cache key: TSLA:1mo:18250
    Redis-->>HistoricalService: Cache miss

    HistoricalService->>Supabase: Query historical_bars table
    Supabase-->>HistoricalService: Partial data (3 years)

    HistoricalService->>HistoricalService: Detect gaps (1976-2020)

    HistoricalService->>MarketMCP: Call get_stock_history<br/>{start_date: 1976-01-01,<br/>end_date: 2025-12-20,<br/>interval: 1mo}

    MarketMCP->>YahooFinance: Fetch 50 years monthly data
    YahooFinance-->>MarketMCP: 188 monthly bars (2010-2025)
    MarketMCP-->>HistoricalService: 188 monthly bars

    HistoricalService->>Supabase: Store 188 bars in historical_bars
    HistoricalService->>Redis: Cache monthly data

    HistoricalService-->>Backend: Return 188 monthly bars

    Backend->>Aggregator: aggregate_to_yearly(188 monthly bars)

    Aggregator->>Aggregator: Group by year:<br/>2010: 12 bars<br/>2011: 12 bars<br/>...<br/>2025: 12 bars

    Aggregator->>Aggregator: For each year:<br/>Open = Jan open<br/>Close = Dec close<br/>High = max(highs)<br/>Low = min(lows)<br/>Volume = sum(volumes)

    Aggregator-->>Backend: ~15 yearly bars (2010-2025)
    Backend-->>Frontend: JSON response with yearly candles

    Frontend->>Frontend: Render chart with 15 yearly candles

    Note over HistoricalService,Supabase: Next request: <200ms<br/>(served from Supabase cache)
```

## 12. Market MCP Server Extension (Absolute Date Ranges)

```mermaid
graph TB
    Request[Historical Data Request] --> CheckParams{Check<br/>Parameters}

    CheckParams -->|Has start_date<br/>& end_date| AbsoluteDates[Use Absolute Date Range<br/>Supports 50+ years]
    CheckParams -->|Has period only| RelativePeriod[Use Relative Period<br/>Max 5 years]

    AbsoluteDates --> ParseDates[Parse ISO Dates:<br/>period1 = new Date(start_date)<br/>period2 = new Date(end_date)]
    RelativePeriod --> GetPeriodDate[Use getPeriodDate():<br/>1d, 5d, 1mo, 3mo, 6mo,<br/>1y, 2y, 5y]

    ParseDates --> YahooAPI[Yahoo Finance API Call:<br/>yahooFinance.historical()]
    GetPeriodDate --> YahooAPI

    YahooAPI --> ProcessData[Process OHLCV Bars]

    ProcessData --> Return[Return Historical Data<br/>Monthly/Daily/Intraday]

    style AbsoluteDates fill:#9f9,stroke:#333,stroke-width:3px
    style RelativePeriod fill:#ff9,stroke:#333,stroke-width:2px
    style YahooAPI fill:#9cf,stroke:#333,stroke-width:2px
```

### Extended API Parameters

```mermaid
graph LR
    subgraph "Legacy API (5 Year Limit)"
        L1[period: '5y'<br/>interval: '1mo'] --> L2[Max 60 months data]
    end

    subgraph "Extended API (50+ Years)"
        E1[start_date: '1976-01-01'<br/>end_date: '2025-12-20'<br/>interval: '1mo'] --> E2[~600 months data<br/>50 years]
    end

    style E2 fill:#9f9,stroke:#333,stroke-width:3px
    style L2 fill:#ff9,stroke:#333,stroke-width:2px
```

## 13. Database Schema (Historical Data Storage)

```mermaid
erDiagram
    HISTORICAL_BARS ||--o{ DATA_COVERAGE : tracks
    HISTORICAL_BARS ||--o{ API_CALL_LOG : logs

    HISTORICAL_BARS {
        text symbol PK
        text interval PK
        timestamptz timestamp PK
        decimal open
        decimal high
        decimal low
        decimal close
        bigint volume
        integer trade_count
        decimal vwap
        text data_source
        timestamptz created_at
    }

    DATA_COVERAGE {
        text symbol PK
        text interval PK
        timestamptz earliest_bar
        timestamptz latest_bar
        integer total_bars
        timestamptz last_fetched_at
        timestamptz last_api_call
        boolean is_complete
        integer max_history_days
    }

    API_CALL_LOG {
        serial id PK
        text provider
        text endpoint
        text symbol
        text interval
        timestamptz start_date
        timestamptz end_date
        integer bars_fetched
        integer duration_ms
        boolean success
        text error_message
        integer http_status
        timestamptz created_at
    }
```

### Storage Example (TSLA Monthly Data)

```mermaid
graph TD
    A[TSLA 1Y Request] --> B[historical_bars Table]

    B --> C1[2010-06-01: O:19.20 C:23.89]
    B --> C2[2010-07-01: O:25.00 C:19.20]
    B --> C3[...]
    B --> C4[2025-12-01: O:481.07 C:459.16]

    A --> D[data_coverage Table]
    D --> D1[symbol: TSLA<br/>interval: 1mo<br/>earliest_bar: 2010-06-01<br/>latest_bar: 2025-12-19<br/>total_bars: 188<br/>is_complete: true]

    style B fill:#9f9,stroke:#333,stroke-width:2px
    style D fill:#ff9,stroke:#333,stroke-width:2px
```

## Version History

- **Dec 20, 2025**: Added 3-tier caching architecture, yearly aggregation, and Market MCP server extension diagrams
- **v44 (Current Production)**: Fixed CEL syntax error, replaced JavaScript regex with CEL-compatible string methods
- **v43 (Deprecated)**: Had JavaScript regex syntax error in if/else condition
- **Earlier Versions**: Various iterations of widget and agent improvements

## Critical Notes

1. **CEL Syntax**: OpenAI Agent Builder uses Common Expression Language, NOT JavaScript
2. **Events Field**: Must always be included in JSON response, even as empty array `[]`
3. **Single Ticker Routing**: Uses string methods `contains()` instead of regex for validation
4. **Silent Failures**: Missing required fields cause widget to fail without error messages
5. **Chart Properties**: Only use officially supported Chart component properties
6. **BTD (200-Day SMA)**: Always calculated from 365 days of daily candles, regardless of current timeframe, ensuring consistent reference level
7. **3-Tier Cache**: Redis (L1) → Supabase (L2) → API (L3) for optimal performance and cost reduction
8. **Market MCP HTTP Mode**: Must run on port 3001 for historical data service to access Yahoo Finance data
9. **Yearly Aggregation**: Converts monthly bars to yearly candles using Jan open, Dec close, year high/low

---

Last Updated: 2025-12-20 (3-Tier Caching & Yearly Aggregation Implementation)
