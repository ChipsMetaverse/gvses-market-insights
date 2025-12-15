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

## Version History

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

---

Last Updated: 2025-12-14 (BTD All-Timeframe Implementation)
