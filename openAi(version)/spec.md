# Voice-Enabled Trading Assistant: Complete Technical Specification v2.0

## Executive Summary

A real-time, voice-interactive trading assistant combining OpenAI's audio models, MCP-based market data architecture, pattern recognition, and risk management. Delivered initially as a React web application with Supabase backend, extending to mobile platforms.

---

## 1. System Architecture

### 1.1 Multi-Layer Architecture

```typescript
interface TradingAssistantArchitecture {
  presentation: {
    web: ReactWebClient;
    mobile: ReactNativeClient;
    api: RESTfulGateway;
  };
  
  application: {
    voice: VoicePipelineOrchestrator;
    agent: TradingAgentCore;
    session: ConversationStateManager;
  };
  
  integration: {
    mcp: MCPServerCluster;
    knowledge: RAGKnowledgeBase;
    compliance: AuditLogger;
  };
  
  infrastructure: {
    database: SupabasePostgreSQL;
    cache: RedisCluster;
    queue: BullMQJobQueue;
    monitoring: DatadogAPM;
  };
}
```

### 1.2 Component Topology

```yaml
┌─────────────────────────────────────────────────┐
│                   CLIENT LAYER                   │
├─────────────────────────────────────────────────┤
│ • React Web App (WebRTC/WebSocket)              │
│ • Voice UI Components                           │
│ • Real-time Chart Visualizations                │
│ • Position/Portfolio Dashboard                  │
└────────────────┬───────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────┐
│              APPLICATION BACKEND                │
├─────────────────────────────────────────────────┤
│ • Voice Pipeline Controller                     │
│ • Trading Agent (GPT-4o + Tools)               │
│ • Session State Manager                        │
│ • Risk Management Engine                       │
└────────┬──────────────┬──────────────┬────────┘
         │              │              │
┌────────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐
│  MCP SERVERS  │ │  OPENAI   │ │ DATABASES │
├───────────────┤ ├───────────┤ ├───────────┤
│ • Market Data │ │ • STT/TTS │ │ • Supabase│
│ • Execution   │ │ • GPT-4o  │ │ • pgvector│
│ • Patterns    │ │ • Realtime│ │ • Redis   │
│ • Risk        │ │ • Agents  │ │ • TimeSCALE│
└───────────────┘ └───────────┘ └───────────┘
```

---

## 2. Voice Pipeline Specification

### 2.1 Speech-to-Text (STT) Configuration

```typescript
interface STTConfig {
  model: 'gpt-4o-transcribe' | 'gpt-4o-mini-transcribe';
  
  parameters: {
    language: 'en';  // Initial: English only
    chunking_strategy: 'server_vad';  // Voice activity detection
    format: 'pcm';  // 16kHz mono PCM
    temperature: 0.2;  // Lower for financial accuracy
    timestamp_granularities: ['word', 'segment'];
  };
  
  streaming: {
    protocol: 'WebRTC' | 'WebSocket';
    partial_results: true;  // Show live transcription
    end_of_speech_timeout: 1500;  // ms
    max_silence_duration: 3000;  // ms
  };
  
  preprocessing: {
    noise_suppression: true;
    gain_control: 'auto';
    echo_cancellation: true;
  };
}
```

### 2.2 Text-to-Speech (TTS) Configuration

```typescript
interface TTSConfig {
  model: 'gpt-4o-mini-tts';
  
  voice_profiles: {
    default: {
      voice: 'nova';  // Professional, clear
      speed: 1.0;
      instructions: `
        Professional trading advisor tone.
        Read numbers precisely:
        - Integers: "232" → "two hundred thirty-two"
        - Decimals: "2.32" → "two point three two"
        - Large numbers: "1,500,000" → "one point five million"
        - Percentages: "5.2%" → "five point two percent"
        - Currency: "$100" → "one hundred dollars"
        Pause briefly before critical numbers.
        Emphasize changes with subtle pitch variation.
        Maintain calm confidence.
      `;
    };
    
    alert: {
      voice: 'onyx';  // More urgent
      speed: 1.1;
      instructions: 'Urgent but clear. Emphasize key price levels.';
    };
    
    educational: {
      voice: 'alloy';  // Friendly, patient
      speed: 0.95;
      instructions: 'Patient, explanatory tone. Pause between concepts.';
    };
  };
  
  streaming: {
    format: 'opus';  // Efficient for streaming
    chunk_size: 1024;
    buffer_size: 4096;
  };
}
```

### 2.3 Realtime API Integration

```typescript
class RealtimeVoiceSession {
  private session: RealtimeSession;
  private agent: TradingAgent;
  
  constructor() {
    this.agent = new TradingAgent({
      name: 'TradingAssistant',
      model: 'gpt-realtime-2025-08-28-2025-06-03',
      instructions: this.buildInstructions(),
      tools: this.loadTools(),
      voice: 'nova',
      
      turn_detection: {
        type: 'server_vad',
        threshold: 0.5,
        prefix_padding_ms: 300,
        silence_duration_ms: 700,
        create_response: true
      },
      
      modalities: ['text', 'audio'],
      audio: {
        input: { format: 'pcm16', sample_rate: 16000 },
        output: { format: 'pcm16', sample_rate: 24000 }
      }
    });
  }
  
  // Interrupt handling
  handleInterrupt(priority: InterruptPriority) {
    const handlers = {
      EMERGENCY_STOP: () => {
        this.session.cancel();
        this.agent.tools.cancel_all_orders();
        this.speak("All orders cancelled immediately.");
      },
      
      CORRECTION: () => {
        this.session.cancel();
        this.speak("I'll stop. What correction?");
      },
      
      MARKET_EVENT: (event: MarketEvent) => {
        this.session.interrupt();
        this.speak(`Breaking: ${event.description}`);
      }
    };
  }
}
```

---

## 3. MCP Server Architecture

### 3.1 Market Data MCP Server

```typescript
interface MarketDataMCPServer {
  transport: 'http-stream';  // SSE for real-time
  endpoint: 'https://mcp.trading.app/market-data';
  
  tools: {
    // Instrument Discovery
    'instruments.search': {
      input: {
        query: string;
        asset_class?: 'equity' | 'crypto' | 'fx' | 'futures' | 'options';
        exchange?: string;
        limit?: number;
      };
      output: {
        results: Array<{
          symbol: string;
          name: string;
          asset_class: string;
          exchange: string;
          tradeable: boolean;
          marginable: boolean;
          shortable: boolean;
        }>;
      };
    };
    
    // Real-time Quotes
    'quotes.get': {
      input: {
        symbols: string[];
        fields?: QuoteField[];
      };
      output: {
        [symbol: string]: {
          last: number;
          bid: number;
          ask: number;
          mid: number;
          volume: number;
          prev_close: number;
          change: number;
          change_pct: number;
          high_52w: number;
          low_52w: number;
          timestamp: string;
          source: string;
          confidence: 'live' | 'delayed' | 'stale';
        };
      };
      latency: {
        p50: 150,  // ms
        p95: 500,
        p99: 800
      };
    };
    
    // Historical Data
    'ohlcv.get': {
      input: {
        symbol: string;
        interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w';
        start: string;  // ISO 8601
        end?: string;
        limit?: number;
        adjustment?: 'split' | 'dividend' | 'all' | 'none';
      };
      output: {
        bars: Array<{
          t: string;  // timestamp
          o: number;  // open
          h: number;  // high
          l: number;  // low
          c: number;  // close
          v: number;  // volume
          vw?: number;  // VWAP
          n?: number;  // trade count
        }>;
        symbol: string;
        interval: string;
        attribution: string;
      };
    };
    
    // Order Book
    'orderbook.get': {
      input: {
        symbol: string;
        depth?: number;  // default: 10
      };
      output: {
        bids: Array<[price: number, size: number, orders?: number]>;
        asks: Array<[price: number, size: number, orders?: number]>;
        spread: number;
        mid: number;
        timestamp: string;
      };
    };
    
    // Market Status
    'market.status': {
      input: {
        venue?: string;  // XNYS, XNAS, etc.
      };
      output: {
        is_open: boolean;
        session: 'pre' | 'regular' | 'post' | 'closed';
        next_open: string;
        next_close: string;
        timezone: string;
      };
    };
    
    // Streaming Subscriptions
    'stream.subscribe': {
      input: {
        channels: Array<{
          type: 'quote' | 'trade' | 'bar' | 'orderbook';
          symbols: string[];
        }>;
      };
      output: {
        subscription_id: string;
        resource_uri: string;  // 'md://stream/{id}'
        websocket_url?: string;
      };
    };
  };
  
  resources: {
    'md://stream/{subscription_id}': {
      type: 'stream';
      format: 'json-lines';
      example: '{"type":"quote","symbol":"AAPL","last":232.45,"timestamp":"2025-08-21T10:30:00Z"}';
    };
  };
}
```

### 3.2 Trading Execution MCP Server

```typescript
interface TradingExecutionMCPServer {
  transport: 'stdio';  // Local for security
  
  tools: {
    // Portfolio Management
    'portfolio.summary': {
      output: {
        total_value: number;
        cash: number;
        buying_power: number;
        day_pl: number;
        day_pl_pct: number;
        total_pl: number;
        margin_used: number;
        positions_count: number;
      };
    };
    
    'positions.list': {
      input: {
        status?: 'open' | 'closed' | 'all';
        sort?: 'symbol' | 'value' | 'pl' | 'pl_pct';
      };
      output: {
        positions: Array<{
          symbol: string;
          quantity: number;
          avg_entry: number;
          current_price: number;
          market_value: number;
          unrealized_pl: number;
          unrealized_pl_pct: number;
          realized_pl: number;
          open_date: string;
        }>;
      };
    };
    
    // Order Management
    'orders.create': {
      input: {
        symbol: string;
        side: 'buy' | 'sell';
        quantity: number;
        type: 'market' | 'limit' | 'stop' | 'stop_limit';
        limit_price?: number;
        stop_price?: number;
        time_in_force: 'day' | 'gtc' | 'ioc' | 'fok';
        extended_hours?: boolean;
        
        // Risk controls
        stop_loss?: {
          type: 'price' | 'percent';
          value: number;
        };
        take_profit?: {
          type: 'price' | 'percent';
          value: number;
        };
        
        // Confirmation
        requires_confirmation: boolean;
        confirmation_token?: string;
      };
      output: {
        order_id: string;
        status: 'pending' | 'accepted' | 'rejected';
        confirmation_required?: {
          token: string;
          expires_at: string;
          summary: string;
        };
      };
    };
    
    'orders.list': {
      input: {
        status?: 'open' | 'filled' | 'cancelled' | 'all';
        since?: string;
        limit?: number;
      };
      output: {
        orders: Array<{
          order_id: string;
          symbol: string;
          side: string;
          quantity: number;
          filled_quantity: number;
          status: string;
          created_at: string;
          filled_at?: string;
          avg_fill_price?: number;
        }>;
      };
    };
    
    'orders.cancel': {
      input: {
        order_id?: string;
        all?: boolean;  // Cancel all open orders
      };
    };
    
    // Trade History
    'trades.history': {
      input: {
        symbol?: string;
        since?: string;
        until?: string;
        limit?: number;
      };
      output: {
        trades: Array<{
          trade_id: string;
          order_id: string;
          symbol: string;
          side: string;
          quantity: number;
          price: number;
          commission: number;
          executed_at: string;
        }>;
      };
    };
  };
}
```

### 3.3 Pattern Recognition MCP Server

```typescript
interface PatternRecognitionMCPServer {
  transport: 'http-stream';
  
  tools: {
    'patterns.detect': {
      input: {
        symbol: string;
        timeframe: string;
        bars?: number;  // How many bars to analyze
        patterns?: string[];  // Specific patterns to look for
      };
      output: {
        detected: Array<{
          pattern: string;  // 'bull_flag', 'head_shoulders', etc.
          confidence: number;  // 0-1
          timeframe: string;
          start_time: string;
          end_time: string;
          
          characteristics: {
            support?: number;
            resistance?: number;
            target?: number;
            stop_loss?: number;
            risk_reward?: number;
          };
          
          action: 'buy' | 'sell' | 'hold' | 'wait';
          notes: string;  // From Candlestick Bible
        }>;
      };
    };
    
    'indicators.calculate': {
      input: {
        symbol: string;
        indicators: Array<{
          type: 'RSI' | 'MACD' | 'BB' | 'EMA' | 'SMA' | 'VWAP';
          period?: number;
          params?: Record<string, any>;
        }>;
        timeframe: string;
      };
      output: {
        [indicator: string]: {
          value: number | { line: number; signal: number; histogram: number };
          interpretation: 'bullish' | 'bearish' | 'neutral';
          strength: number;  // 0-1
        };
      };
    };
    
    'analysis.comprehensive': {
      input: {
        symbol: string;
        include: Array<'patterns' | 'indicators' | 'volume' | 'sentiment'>;
      };
      output: {
        summary: {
          bias: 'bullish' | 'bearish' | 'neutral';
          confidence: number;
          timeframe: string;
        };
        
        patterns?: PatternAnalysis[];
        indicators?: IndicatorAnalysis[];
        volume_profile?: VolumeAnalysis;
        
        recommendation: {
          action: string;
          entry?: number;
          stop_loss?: number;
          targets: number[];
          reasoning: string[];
        };
      };
    };
  };
}
```

### 3.4 Risk Management MCP Server

```typescript
interface RiskManagementMCPServer {
  transport: 'stdio';  // Local only for security
  
  tools: {
    'risk.position_size': {
      input: {
        account_value: number;
        risk_percent: number;  // % of account to risk
        entry_price: number;
        stop_loss: number;
      };
      output: {
        position_size: number;
        dollar_risk: number;
        shares: number;
        max_loss: number;
      };
    };
    
    'risk.validate_order': {
      input: {
        order: OrderRequest;
      };
      output: {
        valid: boolean;
        violations?: Array<{
          rule: string;
          message: string;
          severity: 'warning' | 'error';
        }>;
        
        adjusted_order?: OrderRequest;  // Suggested safe version
      };
    };
    
    'risk.portfolio_analysis': {
      output: {
        metrics: {
          var_95: number;  // Value at Risk
          sharpe_ratio: number;
          max_drawdown: number;
          beta: number;
          correlation_matrix: Record<string, Record<string, number>>;
        };
        
        concentration: {
          largest_position_pct: number;
          sector_exposure: Record<string, number>;
          asset_class_exposure: Record<string, number>;
        };
        
        alerts: Array<{
          type: 'concentration' | 'correlation' | 'volatility';
          severity: 'low' | 'medium' | 'high';
          message: string;
        }>;
      };
    };
    
    'risk.circuit_breaker': {
      output: {
        daily_loss: number;
        daily_loss_pct: number;
        max_daily_loss: number;
        trading_enabled: boolean;
        
        triggers: {
          daily_loss_exceeded: boolean;
          position_limit_reached: boolean;
          margin_call: boolean;
        };
      };
    };
  };
}
```

---

## 4. Trading Agent Configuration

### 4.1 Agent System Prompt

```typescript
const TRADING_AGENT_PROMPT = `
You are a professional trading assistant with expertise in technical analysis,
risk management, and market psychology. You have been trained on:
- The Candlestick Bible (candlestick patterns and interpretations)
- Thomas Bulkowski's Chart Pattern Encyclopedia
- Modern portfolio theory and risk management
- Behavioral finance principles

CRITICAL RULES:
1. Always confirm numbers verbally: "Did you say [number]?"
2. Never execute trades without explicit confirmation
3. Express prices clearly: dollars and cents, not decimals
4. Warn about high-risk situations
5. Refuse requests that violate risk parameters
6. Maintain professional, confident, but not overconfident tone

VOICE INTERACTION GUIDELINES:
- Keep responses concise for voice (under 3 sentences when possible)
- State the most important information first
- Use natural pauses between key points
- Avoid technical jargon unless user demonstrates expertise
- Adapt explanation depth based on user's apparent experience level

MARKET HOURS AWARENESS:
- Current timezone: Europe/Berlin (CET/CEST)
- Adjust urgency based on market session
- Mention relevant market hours when discussing trades
- Alert to after-hours limitations

NUMBER FORMATTING FOR SPEECH:
- Prices: "$232.45" → "two thirty-two dollars and forty-five cents"
- Quantities: "1,500" → "fifteen hundred shares"
- Percentages: "5.2%" → "five point two percent"
- Large numbers: "1.5M" → "one point five million"
`;
```

### 4.2 Tool Orchestration

```typescript
class TradingAgentOrchestrator {
  private agent: Agent;
  private mcpServers: MCPServerCluster;
  private knowledgeBase: RAGKnowledgeBase;
  
  async processQuery(transcript: string, context: ConversationContext) {
    // 1. Intent Classification
    const intent = await this.classifyIntent(transcript);
    
    // 2. Entity Extraction
    const entities = await this.extractEntities(transcript);
    
    // 3. Risk Check
    if (intent.category === 'execution') {
      const riskCheck = await this.mcpServers.risk.validate({
        intent,
        entities,
        context
      });
      
      if (!riskCheck.approved) {
        return this.generateRiskWarning(riskCheck);
      }
    }
    
    // 4. Knowledge Retrieval
    const knowledge = await this.knowledgeBase.retrieve({
      query: transcript,
      k: 5,
      filters: {
        source: ['candlestick_bible', 'bulkowski_patterns'],
        relevance_threshold: 0.7
      }
    });
    
    // 5. Market Data Gathering
    const marketData = await this.gatherMarketData(entities);
    
    // 6. Generate Response
    const response = await this.agent.run({
      messages: [
        { role: 'system', content: TRADING_AGENT_PROMPT },
        { role: 'system', content: `Knowledge: ${knowledge}` },
        { role: 'system', content: `Market Data: ${marketData}` },
        { role: 'user', content: transcript }
      ],
      tools: this.getRelevantTools(intent),
      temperature: 0.3  // Lower for financial accuracy
    });
    
    // 7. Post-process for voice
    return this.optimizeForVoice(response);
  }
  
  private async classifyIntent(text: string): Promise<Intent> {
    const categories = {
      query: /what|how|when|where|why|explain/i,
      execution: /buy|sell|place|order|execute/i,
      analysis: /analyze|pattern|chart|technical/i,
      portfolio: /position|portfolio|balance|profit|loss/i,
      alert: /alert|notify|when.*reaches/i
    };
    
    // Use GPT for complex intent classification
    // Falls back to regex for simple cases
  }
}
```

---

## 5. Knowledge Base (RAG) Specification

### 5.1 Document Processing Pipeline

```typescript
interface KnowledgeBaseConfig {
  sources: {
    candlestick_bible: {
      type: 'pdf';
      path: './knowledge/candlestick_bible.pdf';
      
      chunking: {
        strategy: 'semantic';
        max_tokens: 500;
        overlap: 50;
        
        // Special handling for pattern descriptions
        pattern_extraction: {
          regex: /Pattern:\s*([^\n]+)/;
          include_images: true;  // Store pattern diagrams
        };
      };
    };
    
    bulkowski_patterns: {
      type: 'structured';
      path: './knowledge/bulkowski_encyclopedia.json';
      
      schema: {
        pattern_name: string;
        success_rate: number;
        identification_rules: string[];
        trading_tactics: string;
      };
    };
    
    personal_trades: {
      type: 'csv';
      path: './knowledge/trade_history.csv';
      
      preprocessing: {
        anonymize_values: true;
        extract_patterns: true;
        calculate_statistics: true;
      };
    };
  };
  
  embedding: {
    model: 'text-embedding-3-large';
    dimensions: 3072;
    
    // Hybrid search combining vector + keyword
    search_strategy: {
      vector_weight: 0.7;
      keyword_weight: 0.3;
      reranking: true;
    };
  };
  
  storage: {
    provider: 'supabase';
    
    schema: {
      embeddings_table: 'knowledge_embeddings';
      
      columns: {
        id: 'uuid';
        content: 'text';
        embedding: 'vector(3072)';
        metadata: 'jsonb';
        source: 'text';
        chunk_index: 'integer';
        created_at: 'timestamp';
      };
      
      indexes: [
        'CREATE INDEX ON knowledge_embeddings USING ivfflat (embedding vector_cosine_ops)',
        'CREATE INDEX ON knowledge_embeddings (source)',
        'CREATE INDEX ON knowledge_embeddings USING gin (metadata)'
      ];
    };
  };
}
```

### 5.2 Retrieval Strategy

```typescript
class EnhancedRetriever {
  async retrieve(query: string, context: TradingContext) {
    // 1. Query Expansion
    const expanded = await this.expandQuery(query);
    // "bull flag" → ["bull flag", "bullish flag pattern", "flag continuation"]
    
    // 2. Multi-stage Retrieval
    const stages = [
      // Stage 1: Pattern-specific search
      this.searchPatterns(expanded.patterns),
      
      // Stage 2: Technical indicator search
      this.searchIndicators(expanded.indicators),
      
      // Stage 3: Historical similar trades
      this.searchSimilarTrades(context.symbol, context.timeframe),
      
      // Stage 4: General knowledge
      this.searchGeneral(query)
    ];
    
    const results = await Promise.all(stages);
    
    // 3. Reranking
    const reranked = await this.rerank(results.flat(), query);
    
    // 4. Context Assembly
    return this.assembleContext({
      chunks: reranked.slice(0, 5),
      include_images: context.requesting_visual,
      format: 'voice_optimized'  // Shorter chunks for voice
    });
  }
}
```

---

## 6. Risk Management Framework

### 6.1 Position Sizing Calculator

```typescript
class PositionSizer {
  calculate(params: {
    account_value: number;
    risk_percentage: number;  // Usually 1-2%
    entry_price: number;
    stop_loss: number;
    symbol: string;
  }): PositionSizeResult {
    const dollarRisk = params.account_value * (params.risk_percentage / 100);
    const priceRisk = Math.abs(params.entry_price - params.stop_loss);
    const shares = Math.floor(dollarRisk / priceRisk);
    
    // Additional checks
    const positionValue = shares * params.entry_price;
    const maxPositionSize = params.account_value * 0.25;  // Max 25% in one position
    
    if (positionValue > maxPositionSize) {
      const adjustedShares = Math.floor(maxPositionSize / params.entry_price);
      return {
        shares: adjustedShares,
        position_value: adjustedShares * params.entry_price,
        risk_amount: adjustedShares * priceRisk,
        warning: 'Position size reduced to meet 25% maximum rule'
      };
    }
    
    return {
      shares,
      position_value: positionValue,
      risk_amount: dollarRisk,
      risk_reward: this.calculateRiskReward(params)
    };
  }
}
```

### 6.2 Circuit Breakers

```typescript
class TradingCircuitBreaker {
  private rules: CircuitBreakerRule[] = [
    {
      name: 'daily_loss_limit',
      check: (metrics) => metrics.daily_loss_pct > 3,
      action: 'halt_all_trading',
      message: 'Daily loss limit of 3% reached. Trading halted.'
    },
    {
      name: 'position_concentration',
      check: (metrics) => metrics.largest_position_pct > 30,
      action: 'block_increases',
      message: 'Position concentration too high. Cannot increase positions.'
    },
    {
      name: 'margin_usage',
      check: (metrics) => metrics.margin_usage_pct > 80,
      action: 'block_margin_trades',
      message: 'Margin usage critical. Only closing trades allowed.'
    },
    {
      name: 'consecutive_losses',
      check: (metrics) => metrics.consecutive_losses >= 5,
      action: 'require_confirmation',
      message: 'Five consecutive losses. Extra confirmation required.'
    },
    {
      name: 'volatility_spike',
      check: (metrics) => metrics.vix > 35,
      action: 'reduce_position_sizes',
      message: 'High market volatility. Position sizes reduced by 50%.'
    }
  ];
  
  async evaluate(): Promise<CircuitBreakerStatus> {
    const metrics = await this.gatherMetrics();
    const triggered = this.rules.filter(rule => rule.check(metrics));
    
    return {
      trading_enabled: triggered.every(r => r.action !== 'halt_all_trading'),
      restrictions: triggered.map(r => r.action),
      messages: triggered.map(r => r.message)
    };
  }
}
```

---

## 7. Alert System

### 7.1 Alert Configuration

```typescript
interface AlertSystem {
  types: {
    price_alert: {
      conditions: 'crosses_above' | 'crosses_below' | 'reaches';
      threshold: number;
      symbol: string;
    };
    
    pattern_alert: {
      pattern: string;
      confidence_threshold: number;
      timeframes: string[];
    };
    
    portfolio_alert: {
      metric: 'daily_pl' | 'position_pl' | 'margin_call';
      threshold: number;
      comparison: 'greater' | 'less';
    };
    
    news_alert: {
      symbols: string[];
      keywords: string[];
      sentiment?: 'positive' | 'negative' | 'any';
    };
  };
  
  delivery: {
    immediate_voice: {
      interrupt_current: boolean;
      priority: 1 | 2 | 3;
      voice_profile: 'alert';
    };
    
    queued_voice: {
      batch_interval: number;  // seconds
      summary_style: 'brief' | 'detailed';
    };
    
    visual: {
      toast_notification: boolean;
      dashboard_indicator: boolean;
      chart_annotation: boolean;
    };
  };
  
  // Voice alert examples
  templates: {
    price_cross: "{{symbol}} just crossed {{direction}} {{price}}";
    pattern_detected: "{{pattern}} pattern detected on {{symbol}} {{timeframe}} chart";
    stop_hit: "Stop loss triggered on {{symbol}} position";
  };
}
```

---

## 8. Conversation State Management

### 8.1 Context Tracking

```typescript
class ConversationStateManager {
  private state: ConversationState = {
    session_id: uuid(),
    user_id: null,
    
    context: {
      current_symbol: null,
      current_timeframe: '5m',
      recent_symbols: [],  // Last 5 discussed
      open_positions: [],
      pending_orders: [],
    },
    
    preferences: {
      voice_speed: 1.0,
      confirmation_required: true,
      risk_level: 'conservative',
      preferred_timeframes: ['5m', '15m', '1h'],
    },
    
    history: {
      messages: [],  // Ring buffer of last 20
      actions: [],   // Trades, alerts set, etc.
      queries: [],   // For pattern learning
    },
    
    analytics: {
      session_start: new Date(),
      interaction_count: 0,
      successful_trades: 0,
      cancelled_orders: 0,
    }
  };
  
  updateContext(event: ContextEvent) {
    switch(event.type) {
      case 'symbol_mentioned':
        this.state.context.current_symbol = event.symbol;
        this.addToRecentSymbols(event.symbol);
        break;
        
      case 'timeframe_changed':
        this.state.context.current_timeframe = event.timeframe;
        break;
        
      case 'position_opened':
        this.state.context.open_positions.push(event.position);
        break;
    }
    
    this.persistState();
  }
  
  // Smart context inference
  inferContext(transcript: string): InferredContext {
    // "What about the hourly?" → infer current symbol
    // "Buy 100 more" → infer symbol from recent context
    // "Show me that pattern again" → recall last pattern discussed
    
    return {
      symbol: this.state.context.current_symbol,
      timeframe: this.extractTimeframe(transcript) || this.state.context.current_timeframe,
      referring_to_previous: this.detectBackReference(transcript)
    };
  }
}
```

---

## 9. Testing Framework

### 9.1 Voice Accuracy Tests

```typescript
interface VoiceTestSuite {
  numeric_accuracy: [
    {
      input_text: "Buy 232 shares at 2.32",
      expected_stt: "Buy 232 shares at 2.32",
      expected_tts: "Buy two hundred thirty-two shares at two dollars and thirty-two cents",
      tolerance: 0.95  // 95% word accuracy required
    },
    {
      input_text: "Set stop loss at 198.50",
      expected_stt: "Set stop loss at 198.50",
      expected_tts: "Set stop loss at one ninety-eight dollars and fifty cents",
    }
  ];
  
  pattern_recognition: [
    {
      scenario: "Bull flag on 5-minute chart",
      market_data: "mock_ohlcv_bull_flag.json",
      expected_detection: {
        pattern: "bull_flag",
        confidence: ">0.7",
        action: "buy"
      }
    }
  ];
  
  risk_scenarios: [
    {
      name: "Oversized position attempt",
      command: "Buy 10000 shares of TSLA",
      account_value: 50000,
      expected_response: /position.*too large|exceeds.*risk/i,
      should_block: true
    }
  ];
}
```

### 9.2 Integration Tests

```typescript
class TradingAssistantE2ETests {
  @Test('Complete trade flow with voice')
  async testVoiceTradeFlow() {
    const session = await this.createSession();
    
    // 1. Ask about a stock
    const q1 = await session.speak("What's the current price of Apple?");
    expect(q1.response).toContain("Apple");
    expect(q1.response).toMatch(/\$\d+/);
    
    // 2. Request analysis
    const q2 = await session.speak("Any patterns on the 15-minute chart?");
    expect(q2.tools_called).toContain('patterns.detect');
    expect(q2.response).toMatch(/pattern|formation|setup/i);
    
    // 3. Place order with confirmation
    const q3 = await session.speak("Buy 100 shares at market");
    expect(q3.response).toContain("confirm");
    
    const q4 = await session.speak("Yes, confirmed");
    expect(q4.tools_called).toContain('orders.create');
    expect(q4.response).toMatch(/order.*placed|executed/i);
  }
  
  @Test('Circuit breaker activation')
  async testCircuitBreaker() {
    const session = await this.createSession({
      mock_portfolio: {
        daily_loss_pct: -3.5
      }
    });
    
    const response = await session.speak("Buy 500 shares of Tesla");
    expect(response.response).toContain("trading halted");
    expect(response.order_placed).toBe(false);
  }
}
```

---

## 10. Performance Requirements

### 10.1 Latency Budgets

```yaml
Voice Pipeline:
  speech_to_text:
    first_byte: < 300ms
    full_transcription: < 1500ms
  
  agent_processing:
    simple_query: < 500ms
    with_market_data: < 1000ms
    with_pattern_analysis: < 2000ms
  
  text_to_speech:
    first_audio_byte: < 200ms
    complete_utterance: < sentence_length * 150ms

End-to-End:
  simple_question: < 2s
  market_data_query: < 3s
  complex_analysis: < 5s
  trade_execution: < 3s

Market Data:
  quote_fetch: < 150ms (p50), < 500ms (p99)
  ohlcv_fetch: < 300ms (p50), < 1000ms (p99)
  pattern_detection: < 1000ms (p50), < 3000ms (p99)
```

### 10.2 Scalability Targets

```yaml
Concurrent Users:
  initial: 100
  6_months: 1,000
  12_months: 10,000

Request Volume:
  voice_interactions: 50/user/day
  market_data_queries: 500/user/day
  pattern_analyses: 20/user/day
  trades: 5/user/day

Data Storage:
  embeddings: 1M chunks
  audio_logs: 30 days retention
  trade_history: Indefinite
  market_data_cache: 7 days
```

---

## 11. Security & Compliance

### 11.1 Security Architecture

```typescript
interface SecurityLayers {
  authentication: {
    method: 'OAuth2' | 'WebAuthn';
    mfa: {
      required: true;
      methods: ['totp', 'sms', 'biometric'];
    };
  };
  
  authorization: {
    rbac: {
      roles: ['viewer', 'trader', 'admin'];
      permissions: {
        viewer: ['read_market_data', 'read_positions'];
        trader: ['...viewer', 'place_orders', 'manage_alerts'];
        admin: ['...trader', 'manage_users', 'view_all_accounts'];
      };
    };
  };
  
  encryption: {
    in_transit: 'TLS 1.3';
    at_rest: 'AES-256-GCM';
    audio: {
      streams: 'SRTP';  // For WebRTC
      storage: 'encrypted_s3';
    };
  };
  
  api_security: {
    rate_limiting: {
      per_user: '1000/hour';
      per_ip: '100/hour';
    };
    
    api_keys: {
      rotation: 'monthly';
      scopes: ['read', 'trade', 'admin'];
    };
  };
}
```

### 11.2 Compliance & Audit

```typescript
interface ComplianceFramework {
  regulations: {
    financial: ['MiFID II', 'RegNMS', 'GDPR'];
    
    requirements: {
      best_execution: {
        log_all_orders: true;
        timestamp_precision: 'microsecond';
        venue_selection_logic: 'documented';
      };
      
      suitability: {
        risk_assessment: 'required';
        experience_verification: true;
        appropriateness_checks: true;
      };
    };
  };
  
  audit_trail: {
    voice_commands: {
      store: 'encrypted_s3';
      retention: '7_years';
      
      fields: [
        'timestamp',
        'user_id',
        'session_id',
        'transcript',
        'audio_hash',
        'actions_taken',
        'confirmations'
      ];
    };
    
    trades: {
      pre_trade: ['intent', 'risk_check', 'confirmation'];
      execution: ['venue', 'price', 'timestamp', 'slippage'];
      post_trade: ['settlement', 'reconciliation'];
    };
  };
  
  reporting: {
    regulatory: {
      transaction_reporting: 'T+1';
      best_execution: 'quarterly';
    };
    
    internal: {
      risk_metrics: 'real-time';
      user_activity: 'daily';
      system_performance: 'real-time';
    };
  };
}
```

---

## 12. Mobile Platform Extensions

### 12.1 React Native Architecture

```typescript
interface MobileArchitecture {
  platforms: {
    ios: {
      min_version: 'iOS 14';
      audio: 'AVAudioEngine';
      permissions: ['microphone', 'notifications'];
      biometric: 'FaceID/TouchID';
    };
    
    android: {
      min_version: 'API 26';
      audio: 'AudioRecord/MediaRecorder';
      permissions: ['RECORD_AUDIO', 'VIBRATE'];
      biometric: 'BiometricPrompt';
    };
  };
  
  offline_capabilities: {
    cache: {
      positions: 'last_known';
      market_data: '15_min_stale_ok';
      patterns: 'reference_data_only';
    };
    
    degraded_mode: {
      features: ['view_positions', 'basic_charts', 'alerts'];
      disabled: ['trading', 'real_time_data'];
    };
  };
  
  push_notifications: {
    providers: ['FCM', 'APNS'];
    
    types: {
      price_alerts: {
        priority: 'high';
        sound: 'custom_alert.wav';
        actions: ['view', 'trade', 'dismiss'];
      };
      
      pattern_alerts: {
        priority: 'normal';
        rich_content: true;  // Include chart image
      };
    };
  };
  
  background_processing: {
    ios: 'BGTaskScheduler';
    android: 'WorkManager';
    
    tasks: [
      'sync_positions',
      'update_watchlist',
      'check_alerts'
    ];
  };
}
```

---

## 13. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
```yaml
Week 1-2:
  - Setup React web app with WebRTC audio
  - Implement basic STT with gpt-4o-transcribe
  - Create simple TTS with gpt-4o-mini-tts
  - Basic voice loop (speak → transcribe → respond)

Week 3-4:
  - Integrate Realtime API for low latency
  - Implement VAD and interrupt handling
  - Setup Supabase with pgvector
  - Load knowledge base documents
  - Create basic RAG pipeline
```

### Phase 2: Market Data (Weeks 5-8)
```yaml
Week 5-6:
  - Build first MCP server (market data)
  - Implement quotes.get and ohlcv.get
  - Add caching layer
  - Connect to data vendor

Week 7-8:
  - Add pattern recognition MCP server
  - Implement basic patterns (flags, triangles)
  - Integration test with voice pipeline
  - Add market status awareness
```

### Phase 3: Trading Features (Weeks 9-12)
```yaml
Week 9-10:
  - Build execution MCP server
  - Implement paper trading mode
  - Add position tracking
  - Create risk management tools

Week 11-12:
  - Implement confirmation flows
  - Add circuit breakers
  - Build alert system
  - Complete audit logging
```

### Phase 4: Production Ready (Weeks 13-16)
```yaml
Week 13-14:
  - Performance optimization
  - Security hardening
  - Compliance implementation
  - Load testing

Week 15-16:
  - Beta testing with users
  - Bug fixes and refinements
  - Documentation
  - Deployment preparation
```

### Phase 5: Mobile & Advanced (Weeks 17-20)
```yaml
Week 17-18:
  - React Native app scaffold
  - Mobile voice implementation
  - Offline mode basics

Week 19-20:
  - Advanced patterns
  - Portfolio analytics
  - Multi-user support
  - Production launch
```

---

## 14. Configuration Templates

### 14.1 Environment Variables

```bash
# .env.production

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
OPENAI_REALTIME_ENABLED=true

# MCP Servers
MCP_MARKET_DATA_URL=https://mcp.trading.app/market-data
MCP_MARKET_DATA_KEY=mcp_...
MCP_EXECUTION_MODE=paper  # paper|live
MCP_RISK_ENABLED=true

# Supabase
SUPABASE_URL=https://....supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# Market Data Vendors
POLYGON_API_KEY=...
ALPACA_API_KEY=...
ALPACA_SECRET=...

# Security
SESSION_SECRET=...
ENCRYPTION_KEY=...
JWT_SECRET=...

# Features
FEATURE_VOICE_ENABLED=true
FEATURE_TRADING_ENABLED=true
FEATURE_PATTERN_DETECTION=true
FEATURE_RISK_MANAGEMENT=true

# Monitoring
DATADOG_API_KEY=...
SENTRY_DSN=...
```

### 14.2 Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - redis
      - postgres
  
  mcp-market-data:
    image: trading-assistant/mcp-market-data:latest
    ports:
      - "8001:8001"
    environment:
      - MCP_TRANSPORT=http-stream
  
  mcp-execution:
    image: trading-assistant/mcp-execution:latest
    ports:
      - "8002:8002"
    environment:
      - MCP_TRANSPORT=stdio
      - TRADING_MODE=${MCP_EXECUTION_MODE}
  
  redis:
    image: redis:alpine
    volumes:
      - redis-data:/data
  
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=trading
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  redis-data:
  postgres-data:
```

---

## 15. Monitoring & Observability

### 15.1 Key Metrics

```typescript
interface MonitoringMetrics {
  voice_pipeline: {
    stt_latency: Histogram;
    tts_latency: Histogram;
    e2e_latency: Histogram;
    
    transcription_accuracy: Gauge;  // Sample and measure
    voice_quality_score: Gauge;     // User feedback
    
    interrupts_per_session: Counter;
    confirmations_required: Counter;
  };
  
  trading_operations: {
    orders_placed: Counter;
    orders_cancelled: Counter;
    orders_rejected: Counter;
    
    position_value: Gauge;
    daily_pnl: Gauge;
    
    risk_violations: Counter;
    circuit_breaker_trips: Counter;
  };
  
  system_health: {
    api_latency: Histogram;
    db_query_time: Histogram;
    cache_hit_rate: Gauge;
    
    error_rate: Counter;
    mcp_server_health: Gauge;
    
    concurrent_sessions: Gauge;
    audio_bandwidth: Gauge;
  };
}
```

---

## 16. Error Handling & Recovery

### 16.1 Graceful Degradation

```typescript
class ErrorRecoverySystem {
  strategies = {
    openai_api_down: {
      fallback: 'queue_requests',
      user_message: "I'm having connection issues. Your request is queued.",
      recovery: 'auto_retry_with_backoff'
    },
    
    market_data_unavailable: {
      fallback: 'use_cached_data',
      user_message: "Using slightly delayed market data.",
      recovery: 'switch_to_backup_vendor'
    },
    
    pattern_recognition_timeout: {
      fallback: 'basic_analysis_only',
      user_message: "Running simplified analysis.",
      recovery: 'async_pattern_detection'
    },
    
    voice_stream_interrupted: {
      fallback: 'text_interface',
      user_message: "Voice connection lost. Type your question.",
      recovery: 'reconnect_websocket'
    }
  };
}
```

---

This comprehensive specification provides everything needed to build a production-grade voice-enabled trading assistant. The architecture is modular, scalable, and includes all critical components for a financial application including risk management, compliance, and robust error handling.