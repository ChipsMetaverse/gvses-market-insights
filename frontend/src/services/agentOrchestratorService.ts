/**
 * Agent Orchestrator Service
 * Handles communication with the backend agent orchestrator for intelligent responses
 */

import { getApiUrl } from '../utils/apiConfig';

interface ChartContext {
  symbol?: string;
  timeframe?: string;
  snapshot_id?: string;
  has_analysis?: boolean;
}

interface AgentQuery {
  query: string;
  conversation_history?: Array<{ role: string; content: string }>;
  stream?: boolean;
  session_id?: string;
  user_id?: string;
  chart_context?: ChartContext;  // NEW: Current chart state
}

export interface StructuredChartCommand {
  type: string;
  payload: Record<string, any>;
  description?: string | null;
  legacy?: string | null;
}

interface AgentResponse {
  text: string;
  tools_used: string[];
  data: Record<string, any>;
  timestamp: string;
  model: string;
  cached: boolean;
  session_id?: string;
  structured_output?: StructuredMarketAnalysis; // New field for Responses API
  chart_commands?: string[];
  chart_commands_structured?: StructuredChartCommand[];
}

interface StructuredMarketAnalysis {
  analysis: string;
  data: {
    symbol: string;
    price: number;
    change_percent: number;
    technical_levels: {
      se: number;       // Sell High
      buy_low: number;  // Buy Low
      btd: number;      // Buy the Dip
      retest: number;   // Retest
    };
  };
  tools_used: string[];
  confidence: number;
}

interface AgentHealth {
  status: 'healthy' | 'unhealthy';
  model?: string;
  tools_available?: number;
  cache_size?: number;
  error?: string;
}

interface ChartSnapshot {
  symbol: string;
  timeframe: string;
  captured_at: string;
  chart_commands?: string[];
  chart_commands_structured?: StructuredChartCommand[];
  metadata?: Record<string, any>;
  vision_model?: string;
  analysis?: {
    patterns?: Array<{
      type: string;
      confidence: number;
      coordinates?: any;
      description?: string;
      targets?: number[];
    }>;
    summary?: string;
    indicators?: Record<string, any>;
  };
  analysis_error?: string;
}

class AgentOrchestratorService {
  private baseUrl: string;
  private sessionId: string;
  private sdkRolloutPercentage: number;

  constructor() {
    this.baseUrl = getApiUrl();
    this.sessionId = this.generateSessionId();
    // Get SDK rollout percentage from environment variable (0-100)
    this.sdkRolloutPercentage = parseInt(import.meta.env.VITE_AGENTS_SDK_PERCENTAGE || '0', 10);
    
    console.log(`[AGENT ORCHESTRATOR] SDK rollout percentage: ${this.sdkRolloutPercentage}%`);
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Determine whether to use the SDK endpoint based on rollout percentage
   */
  private shouldUseSDK(): boolean {
    if (this.sdkRolloutPercentage <= 0) return false;
    if (this.sdkRolloutPercentage >= 100) return true;
    
    // Use deterministic random based on session ID for consistency
    const hash = this.sessionId.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    const randomPercent = Math.abs(hash) % 100;
    const useSDK = randomPercent < this.sdkRolloutPercentage;
    
    console.log(`[AGENT ORCHESTRATOR] A/B Test: ${useSDK ? 'SDK' : 'Current'} (${randomPercent} < ${this.sdkRolloutPercentage})`);
    return useSDK;
  }

  /**
   * Get the appropriate endpoint based on A/B testing
   */
  private getOrchestratorEndpoint(): string {
    const useSDK = this.shouldUseSDK();
    const endpoint = useSDK ? '/api/agent/sdk-orchestrate' : '/api/agent/orchestrate';
    console.log(`[AGENT ORCHESTRATOR] Using endpoint: ${endpoint}`);
    return endpoint;
  }

  /**
   * Send a query to the agent orchestrator
   *
   * Phase 2: Supports optional streaming for progressive UI updates
   *
   * @param query - The user's query
   * @param conversationHistory - Optional conversation history
   * @param chartContext - Optional chart context
   * @param stream - Whether to use streaming (default: false for backwards compatibility)
   */
  async sendQuery(
    query: string,
    conversationHistory?: Array<{ role: string; content: string }>,
    chartContext?: ChartContext,
    stream: boolean = false
  ): Promise<AgentResponse> {
    const endpoint = this.getOrchestratorEndpoint();
    const payload: AgentQuery = {
      query,
      conversation_history: conversationHistory,
      stream: stream,  // Phase 2: Honor caller's streaming preference
      session_id: this.sessionId,
      chart_context: chartContext  // Pass chart context if provided
    };

    console.log(`[AGENT ORCHESTRATOR SERVICE] 🌐 Making HTTP request to ${endpoint}`);
    console.log('[AGENT ORCHESTRATOR SERVICE] 📨 Request payload:', {
      query: payload.query,
      historyLength: payload.conversation_history?.length || 0,
      sessionId: payload.session_id,
      endpoint: endpoint
    });

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('[AGENT ORCHESTRATOR SERVICE] 📡 HTTP response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      const errorMsg = `Agent orchestrator error: ${response.status} ${response.statusText}`;
      console.error('[AGENT ORCHESTRATOR SERVICE] ❌', errorMsg);
      throw new Error(errorMsg);
    }

    const data = await response.json();
    console.log('[AGENT ORCHESTRATOR SERVICE] 📦 Parsed JSON response:', {
      hasText: !!data.text,
      textLength: data.text?.length || 0,
      textPreview: data.text?.substring(0, 100),
      toolsUsed: data.tools_used,
      endpoint: endpoint,
      model: data.model
    });

    // Add metadata to track which endpoint was used
    if (!data.data) data.data = {};
    data.data.endpoint_used = endpoint;
    data.data.sdk_enabled = endpoint.includes('sdk-orchestrate');
    if (data.chart_commands_structured && !data.data.chart_commands_structured) {
      data.data.chart_commands_structured = data.chart_commands_structured;
    }

    return data;
  }

  /**
   * Get agent health status
   */
  async getHealth(): Promise<AgentHealth> {
    const response = await fetch(`${this.baseUrl}/api/agent/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get available tools
   */
  async getTools(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/api/agent/tools`);
    
    if (!response.ok) {
      throw new Error(`Tools fetch failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Clear agent cache
   */
  async clearCache(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/agent/clear-cache`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Cache clear failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get the latest chart snapshot for a symbol
   * @param symbol The stock symbol (e.g., "AAPL")
   * @param timeframe Optional timeframe filter (e.g., "1D", "1H")
   * @param includeImage Whether to include the base64 image in response
   */
  async getChartSnapshot(
    symbol: string,
    timeframe?: string,
    includeImage: boolean = false
  ): Promise<ChartSnapshot | null> {
    const params = new URLSearchParams();
    if (timeframe) params.append('timeframe', timeframe);
    if (includeImage) params.append('include_image', 'true');
    
    const url = `${this.baseUrl}/api/agent/chart-snapshot/${symbol.toUpperCase()}${params.toString() ? '?' + params.toString() : ''}`;
    
    try {
      const response = await fetch(url);
      
      if (response.status === 404) {
        // No snapshot available for this symbol
        return null;
      }
      
      if (!response.ok) {
        console.error(`Chart snapshot fetch failed: ${response.status} ${response.statusText}`);
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching chart snapshot:', error);
      return null;
    }
  }

  /**
   * Convert message history to agent format
   */
  convertMessageHistory(messages: Array<{ role: 'user' | 'assistant'; content: string }>): Array<{ role: string; content: string }> {
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }

  /**
   * Stream query response with SSE
   * Supports both legacy text streaming and new structured JSON events
   */
  async streamQuery(
    query: string,
    conversationHistory?: Array<{ role: string; content: string }>,
    chartContext?: ChartContext,
    onChunk?: (chunk: StreamChunk) => void
  ): Promise<void> {
    const payload: AgentQuery = {
      query,
      conversation_history: conversationHistory,
      stream: true,
      session_id: this.sessionId,
      chart_context: chartContext
    };

    const response = await fetch(`${this.baseUrl}/api/agent/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Stream error: ${response.status} ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available for streaming response');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const chunk = JSON.parse(data);
              
              // Handle structured data from Responses API
              if (chunk.type === 'structured_data') {
                const structured = chunk.data as StructuredMarketAnalysis;
                if (onChunk) {
                  onChunk({
                    type: 'structured',
                    data: structured
                  });
                }
              }
              // Handle regular content streaming
              else if (chunk.type === 'content') {
                if (onChunk) {
                  onChunk({
                    type: 'content',
                    text: chunk.text
                  });
                }
              }
              // Handle tool events
              else if (chunk.type === 'tool_start') {
                if (onChunk) {
                  onChunk({
                    type: 'tool_start',
                    tool: chunk.tool
                  });
                }
              }
              else if (chunk.type === 'tool_result') {
                if (onChunk) {
                  onChunk({
                    type: 'tool_result',
                    tool: chunk.tool,
                    data: chunk.data
                  });
                }
              }
              // Handle completion - Phase 2: Pass chart commands
              else if (chunk.type === 'done') {
                if (onChunk) {
                  onChunk({
                    type: 'done',
                    chart_commands: chunk.chart_commands,
                    chart_commands_structured: chunk.chart_commands_structured,
                    tools_used: chunk.tools_used
                  });
                }
              }
            } catch (e) {
              console.error('Error parsing SSE chunk:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Get current session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Generate new session ID
   */
  newSession(): string {
    this.sessionId = this.generateSessionId();
    return this.sessionId;
  }
}

// Stream chunk types
interface StreamChunk {
  type: 'content' | 'structured' | 'tool_start' | 'tool_result' | 'done';
  text?: string;
  data?: any;
  tool?: string;
  // Phase 2: Chart commands in done event
  chart_commands?: string[];
  chart_commands_structured?: StructuredChartCommand[];
  tools_used?: string[];
}

// Export singleton instance
export const agentOrchestratorService = new AgentOrchestratorService();
export type { AgentResponse, AgentQuery, AgentHealth, StructuredMarketAnalysis, StreamChunk, ChartSnapshot, ChartContext };
