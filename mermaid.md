# GVSES AI Market Analysis Assistant - Architecture

## System Overview

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        App[App.tsx]
        App --> TradingDashboardSimple[TradingDashboardSimple]
        
        subgraph "Trading Components"
            TradingDashboardSimple --> TradingChart[TradingChart]
            TradingDashboardSimple --> MarketInsights[Market Insights Panel]
            TradingDashboardSimple --> ChartAnalysis[Chart Analysis Panel]
            TradingDashboardSimple --> VoiceInterface[Voice Interface]
        end
        
        subgraph "Voice Components"
            VoiceInterface --> AudioVisualizer[AudioVisualizer]
            VoiceInterface --> VoiceConversation[Voice Conversation]
            VoiceAssistantFixed[VoiceAssistantFixed]
            VoiceAssistant[VoiceAssistant]
            VoiceAssistantElevenlabs[VoiceAssistantElevenlabs]
        end
        
        subgraph "Chart Components"
            TradingChart --> LightweightCharts[lightweight-charts v5]
            TradingChart --> CandlestickSeries[Candlestick Series]
            TradingChart --> TechnicalLevels[Technical Levels]
        end
        
        subgraph "Hooks"
            useElevenLabsConversation[useElevenLabsConversation]
            useAgentConversation[useAgentConversation]
            useVoiceRecording[useVoiceRecording]
            useSupabase[useSupabase]
        end
        
        VoiceInterface --> useElevenLabsConversation
        VoiceAssistant --> useAgentConversation
    end
    
    subgraph "Backend (FastAPI)"
        FastAPI[mcp_server.py]
        FastAPI --> ElevenLabsProxy["/elevenlabs/signed-url"]
        FastAPI --> AskEndpoint["/ask"]
        FastAPI --> ConversationsAPI["/conversations/*"]
        FastAPI --> MarketDataService[market_data_service.py]
    end
    
    subgraph "External Services"
        ElevenLabs[ElevenLabs API]
        Claude[Claude API via MCP]
        Supabase[(Supabase DB)]
    end
    
    Frontend --> FastAPI
    FastAPI --> ElevenLabs
    FastAPI --> Claude
    Frontend --> Supabase
    FastAPI --> Supabase
```

## Component Hierarchy

```mermaid
graph TD
    Root[main.tsx]
    Root --> App[App.tsx]
    App --> TradingDashboardSimple[TradingDashboardSimple.tsx]
    
    TradingDashboardSimple --> Header[Dashboard Header]
    TradingDashboardSimple --> MarketInsights[Market Insights Panel]
    TradingDashboardSimple --> MainContent[Main Content Area]
    TradingDashboardSimple --> ChartAnalysis[Chart Analysis Panel]
    TradingDashboardSimple --> Footer[Dashboard Footer]
    
    MainContent --> TradingChart[TradingChart.tsx]
    MainContent --> VoiceSection[Voice Section]
    
    VoiceSection --> ListeningInterface[Listening Interface]
    VoiceSection --> VoiceConversation[Voice Conversation]
    
    ListeningInterface --> MicIcon[Animated Mic Icon]
    ListeningInterface --> AudioVisualizer[Audio Visualizer]
    ListeningInterface --> ConnectionStatus[Connection Status]
    
    subgraph "Alternative Components"
        VoiceAssistant[VoiceAssistant.tsx]
        VoiceAssistantFixed[VoiceAssistantFixed.tsx]
        VoiceAssistantElevenlabs[VoiceAssistantElevenlabs.tsx]
    end
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant ElevenLabs
    participant Claude
    participant Supabase
    
    User->>Frontend: Start Voice Chat
    Frontend->>Backend: GET /elevenlabs/signed-url
    Backend->>ElevenLabs: Request signed URL
    ElevenLabs-->>Backend: Return signed URL
    Backend-->>Frontend: Return signed URL
    Frontend->>ElevenLabs: WebSocket Connection
    
    User->>Frontend: Speak (Audio)
    Frontend->>ElevenLabs: Stream audio chunks
    ElevenLabs-->>Frontend: user_transcript
    ElevenLabs-->>Frontend: agent_response + audio
    Frontend->>User: Play audio response
    
    alt Text Input Mode
        User->>Frontend: Type message
        Frontend->>Backend: POST /ask
        Backend->>Claude: Process via MCP
        Claude-->>Backend: Response
        Backend-->>Frontend: Return response
    end
    
    Frontend->>Supabase: Save conversation
    Supabase-->>Frontend: Confirmation
```

## File Structure

```mermaid
graph LR
    subgraph "Frontend Structure"
        src[src/]
        src --> components[components/]
        src --> hooks[hooks/]
        src --> lib[lib/]
        src --> styles[styles/]
        
        components --> ui[ui/]
        components --> voice[voice/]
        
        ui --> AudioVisualizerTsx[AudioVisualizer.tsx]
        ui --> ChatHistoryTsx[ChatHistory.tsx]
        
        voice --> VoiceAssistantTsx[VoiceAssistant.tsx]
        voice --> VoiceAssistantElevenlabsTsx[VoiceAssistantElevenlabs.tsx]
        voice --> VoiceAssistantFixedTsx[VoiceAssistantFixed.tsx]
        
        hooks --> useElevenLabs[useElevenLabsConversation.ts]
        hooks --> useAgent[useAgentConversation.ts]
        hooks --> useVoice[useVoiceRecording.ts]
        hooks --> useSupabaseTsx[useSupabase.tsx]
        
        styles --> AppCss[App.css]
        styles --> IndexCss[index.css]
        styles --> ComponentsCss[*.css]
    end
```

## WebSocket Communication Flow

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: startConversation()
    Connecting --> Connected: WebSocket Open
    Connected --> Listening: User Activates Mic
    Listening --> Processing: Audio Detected
    Processing --> Speaking: Agent Response
    Speaking --> Listening: Response Complete
    Connected --> Disconnected: stopConversation()
    Listening --> Connected: User Releases Mic
```

## API Endpoints

```mermaid
graph TD
    subgraph "Backend API Routes"
        Health[GET /health]
        SignedURL[GET /elevenlabs/signed-url]
        Ask[POST /ask]
        RecordConv[POST /conversations/record]
        GetConv[GET /conversations/:session_id]
        StockHistory[GET /api/stock-history]
    end
    
    subgraph "Request Flow"
        SignedURL --> ElevenLabsAPI[ElevenLabs API]
        Ask --> ClaudeAPI[Claude via MCP]
        RecordConv --> SupabaseDB[(Supabase)]
        GetConv --> SupabaseDB
        StockHistory --> MarketData[Market Data Service]
    end
```

## Voice Processing Pipeline

```mermaid
graph LR
    subgraph "Audio Input"
        Microphone[Microphone] --> MediaStream[MediaStream API]
        MediaStream --> AudioContext[AudioContext]
        AudioContext --> PCM[PCM Audio Chunks]
    end
    
    subgraph "Processing"
        PCM --> WebSocket[WebSocket to ElevenLabs]
        WebSocket --> ASR[Speech Recognition]
        ASR --> LLM[LLM Processing]
        LLM --> TTS[Text-to-Speech]
    end
    
    subgraph "Audio Output"
        TTS --> AudioQueue[Audio Queue]
        AudioQueue --> AudioElement[Audio Element]
        AudioElement --> Speaker[Speaker]
    end
```

## State Management

```mermaid
graph TD
    subgraph "Application State"
        ConnectionState[Connection State]
        MessageHistory[Message History]
        AudioLevel[Audio Level]
        SessionID[Session ID]
        
        ConnectionState --> isConnected{isConnected?}
        isConnected -->|true| EnableVoice[Enable Voice Input]
        isConnected -->|false| DisableVoice[Disable Voice Input]
        
        MessageHistory --> LocalState[Local State Array]
        MessageHistory --> SupabaseSync[Supabase Sync]
        
        AudioLevel --> Visualizer[Audio Visualizer]
        SessionID --> ConversationTracking[Conversation Tracking]
    end
```

## Technology Stack

```mermaid
mindmap
  root((GVSES Market Assistant))
    Frontend
      React 18
      TypeScript
      Vite
      TradingView Charts
        lightweight-charts v5
        Candlestick Series
        Technical Indicators
      ElevenLabs SDK
      Supabase Client
    Backend
      FastAPI
      Python 3.x
      httpx
      python-dotenv
      MCP Integration
    Services
      ElevenLabs
        Conversational AI
        ASR (Nova-2)
        TTS (Multilingual)
      Claude
        via MCP
        Text Processing
      Supabase
        PostgreSQL
        Real-time
        Auth
    Deployment
      Docker
      docker-compose
      Fly.io ready
```

## Error Handling Flow

```mermaid
graph TD
    Start[User Action] --> Try{Try Operation}
    Try -->|Success| Complete[Operation Complete]
    Try -->|WebSocket Error| WSReconnect[Reconnect WebSocket]
    Try -->|API Error| APIRetry[Retry with Backoff]
    Try -->|Auth Error| AuthRefresh[Refresh Auth]
    
    WSReconnect -->|Success| Complete
    WSReconnect -->|Fail| Fallback[Text Mode Fallback]
    
    APIRetry -->|Success| Complete
    APIRetry -->|Fail| ErrorDisplay[Display Error]
    
    AuthRefresh -->|Success| Retry[Retry Operation]
    AuthRefresh -->|Fail| LoginPrompt[Prompt Login]
    
    Fallback --> Complete
    ErrorDisplay --> End[End]
    LoginPrompt --> End
    Retry --> Complete
```

## Database Schema

```mermaid
erDiagram
    SESSIONS ||--o{ CONVERSATIONS : contains
    CONVERSATIONS ||--o| AUDIO_FILES : may_have
    
    SESSIONS {
        uuid id PK
        timestamp created_at
        jsonb metadata
    }
    
    CONVERSATIONS {
        uuid id PK
        uuid session_id FK
        text role
        text content
        timestamp created_at
        jsonb metadata
    }
    
    AUDIO_FILES {
        uuid id PK
        uuid conversation_id FK
        text file_path
        text file_type
        timestamp created_at
    }
```

---

## Trading Dashboard Architecture

```mermaid
graph LR
    subgraph "Dashboard Layout"
        Header[Header<br/>GVSES Brand + Tabs]
        
        subgraph "Three Panel Layout"
            LeftPanel[Market Insights<br/>240px width]
            CenterPanel[Interactive Charts<br/>+ Voice Assistant<br/>Flexible width]
            RightPanel[Chart Analysis<br/>300px width]
        end
        
        Footer[Footer<br/>Tab Navigation]
    end
    
    Header --> LeftPanel
    Header --> CenterPanel
    Header --> RightPanel
    LeftPanel --> Footer
    CenterPanel --> Footer
    RightPanel --> Footer
```

## Trading Dashboard State Flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> ChartsTab: Select Charts Tab
    Idle --> VoiceTab: Select Voice Tab
    
    ChartsTab --> DisplayChart: Show Trading Chart
    VoiceTab --> DisplayChart: Show Trading Chart
    
    DisplayChart --> Listening: Click Mic/Listen Button
    Listening --> Recording: Start Recording
    Recording --> Processing: Stop Recording
    Processing --> DisplayResponse: Show AI Response
    DisplayResponse --> Listening: Continue
    
    Listening --> Idle: Cancel
    Recording --> Idle: Cancel
```

## Market Data Components

```mermaid
graph TD
    subgraph "Market Insights Panel"
        StockCard[Stock Card]
        StockCard --> Symbol[Stock Symbol]
        StockCard --> Price[Current Price]
        StockCard --> Change[Price Change %]
        StockCard --> Label[Technical Label<br/>ST/LTB/QE]
        StockCard --> Description[Momentum Description]
    end
    
    subgraph "Chart Analysis Panel"
        AnalysisItem[Analysis Item]
        AnalysisItem --> StockName[Stock Name]
        AnalysisItem --> TimeAgo[Time Ago]
        AnalysisItem --> Analysis[Analysis Text]
        
        TechnicalLevels[Technical Levels]
        TechnicalLevels --> QELevel[QE Level + Price]
        TechnicalLevels --> STLevel[ST Level + Price]
        TechnicalLevels --> LTBLevel[LTB Level + Price]
        
        PatternDetection[Pattern Detection]
        PatternDetection --> PatternName[Pattern Name]
        PatternDetection --> Confidence[Confidence %]
    end
```

## Voice Interface Components

```mermaid
graph TD
    subgraph "Voice Assistant Interface"
        ListeningUI[Listening Interface]
        ListeningUI --> MicButton[Animated Mic Button<br/>with Pulse Rings]
        ListeningUI --> StatusText[AI Analysis/Listening]
        ListeningUI --> Timer[Recording Timer]
        ListeningUI --> Visualizer[Audio Visualizer Bars]
        ListeningUI --> Connection[Connection Status]
        
        ConversationUI[Voice Conversation]
        ConversationUI --> Messages[Message History]
        ConversationUI --> ControlChart[Control the Chart Button]
        ConversationUI --> Commands[Voice Commands Text]
        
        Messages --> UserMsg[User Message + Icon]
        Messages --> AssistantMsg[Assistant Message + Icon]
    end
```

*Last Updated: 2025-08-24*
*This document represents the current architecture of the GVSES AI Market Analysis Assistant application.*