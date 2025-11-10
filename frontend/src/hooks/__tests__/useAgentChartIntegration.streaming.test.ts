/**
 * useAgentChartIntegration Streaming Tests
 * Tests for provider event listening and chart command processing
 *
 * Streaming Chart Commands - Phase 2: Integration Coverage
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useAgentChartIntegration } from '../useAgentChartIntegration';
import type { ChatProvider } from '../../providers/types';

// Mock enhancedChartControl
vi.mock('../../services/enhancedChartControl', () => ({
  enhancedChartControl: {
    processEnhancedResponse: vi.fn().mockResolvedValue([]),
    toggleIndicator: vi.fn(),
    applyIndicatorPreset: vi.fn(),
    highlightLevel: vi.fn(),
    clearDrawings: vi.fn(),
  },
}));

// Create a mock provider
class MockChatProvider {
  private eventHandlers: Map<string, Set<Function>> = new Map();

  on(event: string, handler: Function) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
  }

  off(event: string, handler: Function) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  emit(event: string, data: any) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => handler(data));
    }
  }

  // Required ChatProvider methods (minimal implementation)
  async initialize() {}
  async connect() {}
  async disconnect() {}
  async sendMessage() {
    return {
      id: 'test',
      role: 'assistant' as const,
      content: 'test',
      timestamp: new Date().toISOString(),
    };
  }
  async *streamMessage() {
    yield 'test';
  }
  async destroy() {}
  async setModel() {}
  async getAvailableModels() {
    return [];
  }
}

describe('useAgentChartIntegration - Streaming', () => {
  let mockProvider: MockChatProvider;
  let enhancedChartControl: any;

  beforeEach(async () => {
    mockProvider = new MockChatProvider();
    // Get mocked enhancedChartControl
    const module = await import('../../services/enhancedChartControl');
    enhancedChartControl = module.enhancedChartControl;
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Provider event listening', () => {
    it('should register chartCommands event listener when provider is provided', () => {
      const onSpy = vi.spyOn(mockProvider, 'on');

      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      expect(onSpy).toHaveBeenCalledWith('chartCommands', expect.any(Function));
    });

    it('should not register listener when provider is not provided', () => {
      const onSpy = vi.spyOn(mockProvider, 'on');

      renderHook(() => useAgentChartIntegration({}));

      expect(onSpy).not.toHaveBeenCalled();
    });

    it('should remove listener on unmount', () => {
      const offSpy = vi.spyOn(mockProvider, 'off');

      const { unmount } = renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      unmount();

      expect(offSpy).toHaveBeenCalledWith('chartCommands', expect.any(Function));
    });
  });

  describe('Chart command processing', () => {
    it('should process chart commands when chartCommands event is emitted', async () => {
      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      // Emit chartCommands event
      mockProvider.emit('chartCommands', {
        legacy: ['LOAD:TSLA', 'INDICATOR:RSI'],
        structured: [
          { type: 'load', payload: { symbol: 'TSLA' } },
          { type: 'indicator', payload: { name: 'RSI', enabled: true } },
        ],
        responseText: 'Loading Tesla chart with RSI indicator',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledWith(
          'Loading Tesla chart with RSI indicator',
          ['LOAD:TSLA', 'INDICATOR:RSI'],
          [
            { type: 'load', payload: { symbol: 'TSLA' } },
            { type: 'indicator', payload: { name: 'RSI', enabled: true } },
          ]
        );
      });
    });

    it('should handle empty chart commands', async () => {
      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      // Emit chartCommands event with empty arrays
      mockProvider.emit('chartCommands', {
        legacy: [],
        structured: [],
        responseText: 'No chart commands',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledWith(
          'No chart commands',
          [],
          []
        );
      });
    });

    it('should handle legacy commands only', async () => {
      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      // Emit chartCommands event with only legacy commands
      mockProvider.emit('chartCommands', {
        legacy: ['LOAD:AAPL'],
        structured: [],
        responseText: 'Loading Apple',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledWith(
          'Loading Apple',
          ['LOAD:AAPL'],
          []
        );
      });
    });

    it('should handle structured commands only', async () => {
      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      // Emit chartCommands event with only structured commands
      mockProvider.emit('chartCommands', {
        legacy: [],
        structured: [{ type: 'load', payload: { symbol: 'NVDA' } }],
        responseText: 'Loading NVIDIA',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledWith(
          'Loading NVIDIA',
          [],
          [{ type: 'load', payload: { symbol: 'NVDA' } }]
        );
      });
    });

    it('should log received chart commands', async () => {
      const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      mockProvider.emit('chartCommands', {
        legacy: ['LOAD:SPY'],
        structured: [{ type: 'load', payload: { symbol: 'SPY' } }],
        responseText: 'Loading SPY',
      });

      await waitFor(() => {
        expect(consoleLogSpy).toHaveBeenCalledWith(
          '[useAgentChartIntegration] Received chart commands from streaming:',
          {
            legacyCount: 1,
            structuredCount: 1,
          }
        );
      });

      consoleLogSpy.mockRestore();
    });
  });

  describe('Error handling', () => {
    it('should handle errors in processEnhancedResponse gracefully', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      // Make processEnhancedResponse throw an error
      enhancedChartControl.processEnhancedResponse.mockRejectedValueOnce(
        new Error('Chart processing failed')
      );

      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      mockProvider.emit('chartCommands', {
        legacy: ['INVALID:COMMAND'],
        structured: [],
        responseText: 'Invalid command',
      });

      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Error processing agent response:',
          expect.any(Error)
        );
      });

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Multiple emissions', () => {
    it('should process multiple chartCommands events sequentially', async () => {
      renderHook(() =>
        useAgentChartIntegration({
          provider: mockProvider as unknown as ChatProvider,
        })
      );

      // Emit first command
      mockProvider.emit('chartCommands', {
        legacy: ['LOAD:TSLA'],
        structured: [{ type: 'load', payload: { symbol: 'TSLA' } }],
        responseText: 'Loading TSLA',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledTimes(1);
      });

      // Emit second command
      mockProvider.emit('chartCommands', {
        legacy: ['LOAD:AAPL'],
        structured: [{ type: 'load', payload: { symbol: 'AAPL' } }],
        responseText: 'Loading AAPL',
      });

      await waitFor(() => {
        expect(enhancedChartControl.processEnhancedResponse).toHaveBeenCalledTimes(2);
      });
    });
  });
});
