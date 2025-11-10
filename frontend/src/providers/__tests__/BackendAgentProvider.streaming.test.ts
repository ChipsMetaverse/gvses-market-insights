/**
 * BackendAgentProvider Streaming Tests
 * Tests for SSE streaming with chart commands integration
 *
 * Streaming Chart Commands - Phase 2: Regression Coverage
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { BackendAgentProvider } from '../BackendAgentProvider';

// Mock fetch for streaming responses
const createMockStreamingResponse = (chunks: any[]) => {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of chunks) {
        const line = `data: ${JSON.stringify(chunk)}\n\n`;
        controller.enqueue(encoder.encode(line));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  });
};

describe('BackendAgentProvider - Streaming', () => {
  let provider: BackendAgentProvider;
  let originalFetch: typeof global.fetch;

  beforeEach(async () => {
    originalFetch = global.fetch;
    provider = new BackendAgentProvider({
      apiUrl: 'http://localhost:8000',
    });
    await provider.initialize({
      apiUrl: 'http://localhost:8000',
    });
  });

  afterEach(async () => {
    global.fetch = originalFetch;
    await provider.destroy();
  });

  describe('streamMessage', () => {
    it('should emit content chunks during streaming', async () => {
      const chunks = [
        { type: 'content', text: 'Hello ' },
        { type: 'content', text: 'World' },
        { type: 'done', tools_used: [] },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      const contentChunks: string[] = [];
      const generator = provider.streamMessage('test message');

      for await (const chunk of generator) {
        contentChunks.push(chunk);
      }

      expect(contentChunks).toEqual(['Hello ', 'World']);
    });

    it('should emit chartCommands event with normalized payload', async () => {
      const chunks = [
        { type: 'content', text: 'Loading TSLA chart' },
        {
          type: 'done',
          chart_commands: ['LOAD:TSLA', 'INDICATOR:RSI'],
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA' } },
            { type: 'indicator', payload: { name: 'RSI', enabled: true } },
          ],
          tools_used: ['change_chart_symbol'],
        },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let chartCommandsEmitted = false;
      let emittedPayload: any = null;

      provider.on('chartCommands', (payload) => {
        chartCommandsEmitted = true;
        emittedPayload = payload;
      });

      // Consume the stream
      const generator = provider.streamMessage('show me Tesla');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(chartCommandsEmitted).toBe(true);
      expect(emittedPayload).toBeTruthy();
      expect(emittedPayload.legacy).toEqual(['LOAD:TSLA', 'INDICATOR:RSI']);
      expect(emittedPayload.structured).toHaveLength(2);
      expect(emittedPayload.structured[0].type).toBe('load');
      expect(emittedPayload.responseText).toBe('Loading TSLA chart');
    });

    it('should emit toolData events for tool_start and tool_result', async () => {
      const chunks = [
        {
          type: 'tool_start',
          tool: 'get_stock_quote',
          arguments: { symbol: 'AAPL' },
        },
        {
          type: 'tool_result',
          tool: 'get_stock_quote',
          data: { price: 178.50, symbol: 'AAPL' },
        },
        { type: 'content', text: 'Apple is trading at $178.50' },
        { type: 'done', tools_used: ['get_stock_quote'] },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      const toolEvents: any[] = [];

      provider.on('toolData', (event) => {
        toolEvents.push(event);
      });

      // Consume the stream
      const generator = provider.streamMessage('what is Apple trading at?');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(toolEvents).toHaveLength(2);

      // Check tool_start event
      expect(toolEvents[0].type).toBe('start');
      expect(toolEvents[0].tool).toBe('get_stock_quote');
      expect(toolEvents[0].arguments).toEqual({ symbol: 'AAPL' });
      expect(toolEvents[0].timestamp).toBeDefined();

      // Check tool_result event
      expect(toolEvents[1].type).toBe('result');
      expect(toolEvents[1].tool).toBe('get_stock_quote');
      expect(toolEvents[1].data).toEqual({ price: 178.50, symbol: 'AAPL' });
      expect(toolEvents[1].duration).toBeDefined();
    });

    it('should handle structured data chunks', async () => {
      const structuredData = {
        analysis: 'Bullish trend detected',
        data: {
          symbol: 'NVDA',
          price: 505.23,
          change_percent: 2.5,
          technical_levels: {
            se: 520,
            buy_low: 490,
            btd: 485,
            retest: 500,
          },
        },
        tools_used: ['get_stock_quote', 'analyze_chart'],
        confidence: 0.85,
      };

      const chunks = [
        { type: 'content', text: 'Analyzing NVDA...' },
        { type: 'structured', data: structuredData },
        { type: 'done', tools_used: ['get_stock_quote', 'analyze_chart'] },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let messageReceived = false;
      let receivedMessage: any = null;

      provider.on('message', (msg) => {
        if (msg.role === 'assistant') {
          messageReceived = true;
          receivedMessage = msg;
        }
      });

      // Consume the stream
      const generator = provider.streamMessage('analyze NVDA');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(messageReceived).toBe(true);
      expect(receivedMessage.metadata.structured_output).toEqual(structuredData);
    });

    it('should emit error events for streaming errors', async () => {
      const chunks = [
        { type: 'content', text: 'Processing...' },
        { type: 'error', message: 'API rate limit exceeded' },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let errorEmitted = false;
      let errorMessage = '';

      provider.on('error', (event) => {
        errorEmitted = true;
        errorMessage = event.error;
      });

      // Consume the stream
      const generator = provider.streamMessage('test');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(errorEmitted).toBe(true);
      expect(errorMessage).toBe('API rate limit exceeded');
    });

    it('should not emit chartCommands if no commands present', async () => {
      const chunks = [
        { type: 'content', text: 'Hello' },
        { type: 'done', tools_used: [] },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let chartCommandsEmitted = false;

      provider.on('chartCommands', () => {
        chartCommandsEmitted = true;
      });

      // Consume the stream
      const generator = provider.streamMessage('hello');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(chartCommandsEmitted).toBe(false);
    });

    it('should handle empty chart_commands gracefully', async () => {
      const chunks = [
        { type: 'content', text: 'No chart commands' },
        {
          type: 'done',
          chart_commands: [],
          chart_commands_structured: [],
          tools_used: [],
        },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let chartCommandsEmitted = false;

      provider.on('chartCommands', () => {
        chartCommandsEmitted = true;
      });

      // Consume the stream
      const generator = provider.streamMessage('test');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(chartCommandsEmitted).toBe(false);
    });

    it('should include all metadata in final message', async () => {
      const chunks = [
        { type: 'content', text: 'Response text' },
        {
          type: 'done',
          chart_commands: ['LOAD:SPY'],
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'SPY' } }],
          tools_used: ['change_chart_symbol'],
        },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let finalMessage: any = null;

      provider.on('message', (msg) => {
        if (msg.role === 'assistant') {
          finalMessage = msg;
        }
      });

      // Consume the stream
      const generator = provider.streamMessage('show SPY');
      for await (const chunk of generator) {
        // Just consume
      }

      expect(finalMessage).toBeTruthy();
      expect(finalMessage.content).toBe('Response text');
      expect(finalMessage.metadata.chart_commands).toEqual(['LOAD:SPY']);
      expect(finalMessage.metadata.chart_commands_structured).toHaveLength(1);
      expect(finalMessage.metadata.tools_used).toEqual(['change_chart_symbol']);
    });
  });

  describe('Normalization', () => {
    it('should normalize both legacy and structured chart commands', async () => {
      const chunks = [
        { type: 'content', text: 'Chart updated' },
        {
          type: 'done',
          chart_commands: ['LOAD:TSLA'],
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'TSLA' } }],
          tools_used: [],
        },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      let emittedPayload: any = null;

      provider.on('chartCommands', (payload) => {
        emittedPayload = payload;
      });

      // Consume the stream
      const generator = provider.streamMessage('load Tesla');
      for await (const chunk of generator) {
        // Just consume
      }

      // Verify normalization occurred
      expect(emittedPayload.legacy).toEqual(['LOAD:TSLA']);
      expect(emittedPayload.structured).toHaveLength(1);
      expect(emittedPayload.structured[0].type).toBe('load');
      expect(emittedPayload.structured[0].payload.symbol).toBe('TSLA');
    });
  });

  describe('Telemetry', () => {
    it('should track tool execution duration', async () => {
      const chunks = [
        {
          type: 'tool_start',
          tool: 'slow_tool',
          arguments: {},
        },
        // Simulate delay
        {
          type: 'tool_result',
          tool: 'slow_tool',
          data: { result: 'done' },
        },
        { type: 'done', tools_used: ['slow_tool'] },
      ];

      global.fetch = vi.fn().mockResolvedValue(createMockStreamingResponse(chunks));

      const toolEvents: any[] = [];

      provider.on('toolData', (event) => {
        toolEvents.push(event);
      });

      // Consume the stream
      const generator = provider.streamMessage('test');
      for await (const chunk of generator) {
        // Just consume
      }

      const startEvent = toolEvents.find((e) => e.type === 'start');
      const resultEvent = toolEvents.find((e) => e.type === 'result');

      expect(startEvent).toBeDefined();
      expect(resultEvent).toBeDefined();
      expect(resultEvent.duration).toBeDefined();
      expect(resultEvent.duration).toBeGreaterThanOrEqual(0);
    });
  });
});
