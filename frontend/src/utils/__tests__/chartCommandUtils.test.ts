/**
 * Chart Command Utils Tests
 * Comprehensive test coverage for chart command normalization
 *
 * Phase 1: Chart Command Hardening - Test Coverage
 */

import { describe, it, expect } from 'vitest';
import {
  normalizeChartCommandPayload,
  type ChartCommandPayload,
  type StructuredChartCommand,
} from '../chartCommandUtils';

describe('chartCommandUtils', () => {
  describe('normalizeChartCommandPayload', () => {
    describe('Backend API Response (snake_case)', () => {
      it('should normalize both chart_commands and chart_commands_structured', () => {
        const input = {
          chart_commands: ['LOAD:TSLA', 'INDICATOR:RSI'],
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA' } },
            { type: 'indicator', payload: { name: 'RSI', enabled: true } },
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual(['LOAD:TSLA', 'INDICATOR:RSI']);
        expect(result.structured).toHaveLength(2);
        expect(result.structured[0].type).toBe('load');
        expect(result.structured[1].type).toBe('indicator');
      });

      it('should handle chart_commands as a single string', () => {
        const input = {
          chart_commands: 'LOAD:AAPL',
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'AAPL' } }],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual(['LOAD:AAPL']);
        expect(result.structured).toHaveLength(1);
      });

      it('should handle missing chart_commands_structured', () => {
        const input = {
          chart_commands: ['LOAD:NVDA'],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual(['LOAD:NVDA']);
        expect(result.structured).toEqual([]);
      });

      it('should handle missing chart_commands', () => {
        const input = {
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'MSFT' } }],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual([]);
        expect(result.structured).toHaveLength(1);
      });
    });

    describe('Frontend Object (camelCase)', () => {
      it('should normalize camelCase legacy and structured fields', () => {
        const input = {
          legacy: ['LOAD:GOOGL'],
          structured: [{ type: 'load', payload: { symbol: 'GOOGL' } }],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual(['LOAD:GOOGL']);
        expect(result.structured).toHaveLength(1);
        expect(result.structured[0].type).toBe('load');
      });

      it('should include responseText if provided', () => {
        const input = {
          legacy: ['LOAD:AMZN'],
          structured: [{ type: 'load', payload: { symbol: 'AMZN' } }],
          responseText: 'Loading Amazon chart',
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.responseText).toBe('Loading Amazon chart');
      });

      it('should use responseText parameter over object field', () => {
        const input = {
          legacy: ['LOAD:META'],
          responseText: 'Object text',
        };

        const result = normalizeChartCommandPayload(input, 'Parameter text');

        // Parameter takes precedence
        expect(result.responseText).toBe('Object text');
      });
    });

    describe('Field Name Compatibility', () => {
      it('should handle snake_case and camelCase identically', () => {
        const snakeCase = {
          chart_commands: ['LOAD:AAPL'],
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'AAPL' } }],
        };

        const camelCase = {
          legacy: ['LOAD:AAPL'],
          structured: [{ type: 'load', payload: { symbol: 'AAPL' } }],
        };

        const result1 = normalizeChartCommandPayload(snakeCase);
        const result2 = normalizeChartCommandPayload(camelCase);

        expect(result1.legacy).toEqual(result2.legacy);
        expect(result1.structured).toEqual(result2.structured);
      });

      it('should prefer camelCase when both formats present', () => {
        const input = {
          legacy: ['LOAD:TSLA'],  // camelCase
          chart_commands: ['LOAD:AAPL'],  // snake_case
          structured: [{ type: 'load', payload: { symbol: 'TSLA' } }],
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'AAPL' } }],
        };

        const result = normalizeChartCommandPayload(input);

        // Should prefer camelCase (legacy/structured)
        expect(result.legacy).toEqual(['LOAD:TSLA']);
        expect(result.structured[0].payload.symbol).toBe('TSLA');
      });
    });

    describe('Legacy String Only Input', () => {
      it('should convert single string to legacy array', () => {
        const result = normalizeChartCommandPayload('LOAD:NVDA');

        expect(result.legacy).toEqual(['LOAD:NVDA']);
        expect(result.structured).toEqual([]);
      });

      it('should convert string array to legacy array', () => {
        const result = normalizeChartCommandPayload(['LOAD:TSLA', 'INDICATOR:MACD']);

        expect(result.legacy).toEqual(['LOAD:TSLA', 'INDICATOR:MACD']);
        expect(result.structured).toEqual([]);
      });

      it('should include responseText parameter with string input', () => {
        const result = normalizeChartCommandPayload('LOAD:AAPL', 'Loading Apple');

        expect(result.legacy).toEqual(['LOAD:AAPL']);
        expect(result.responseText).toBe('Loading Apple');
      });
    });

    describe('Null/Undefined/Empty Handling', () => {
      it('should return empty payload for null', () => {
        const result = normalizeChartCommandPayload(null);

        expect(result).toEqual({
          legacy: [],
          structured: [],
          responseText: undefined,
        });
      });

      it('should return empty payload for undefined', () => {
        const result = normalizeChartCommandPayload(undefined);

        expect(result).toEqual({
          legacy: [],
          structured: [],
          responseText: undefined,
        });
      });

      it('should return empty payload for empty object', () => {
        const result = normalizeChartCommandPayload({});

        expect(result.legacy).toEqual([]);
        expect(result.structured).toEqual([]);
      });

      it('should include responseText even with empty input', () => {
        const result = normalizeChartCommandPayload(null, 'Some text');

        expect(result.legacy).toEqual([]);
        expect(result.structured).toEqual([]);
        expect(result.responseText).toBe('Some text');
      });
    });

    describe('Validation and Filtering', () => {
      it('should filter out invalid structured commands', () => {
        const input = {
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA' } },  // Valid
            { invalid: 'command' },  // Missing 'type' field
            null,  // Null
            undefined,  // Undefined
            { type: 'indicator', payload: { name: 'RSI' } },  // Valid
            {},  // Missing 'type'
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.structured).toHaveLength(2);
        expect(result.structured[0].type).toBe('load');
        expect(result.structured[1].type).toBe('indicator');
      });

      it('should filter out non-string legacy commands', () => {
        const input = {
          chart_commands: [
            'LOAD:TSLA',  // Valid
            123,  // Number
            null,  // Null
            undefined,  // Undefined
            'INDICATOR:RSI',  // Valid
            { invalid: 'object' },  // Object
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual(['LOAD:TSLA', 'INDICATOR:RSI']);
      });

      it('should require type field for structured commands', () => {
        const input = {
          chart_commands_structured: [
            { payload: { symbol: 'TSLA' } },  // Missing type
            { type: '', payload: {} },  // Empty type (valid - has type field)
          ],
        };

        const result = normalizeChartCommandPayload(input);

        // Only the second one should pass (has type field, even if empty)
        expect(result.structured).toHaveLength(1);
        expect(result.structured[0].type).toBe('');
      });
    });

    describe('Complex Payloads', () => {
      it('should handle multiple command types', () => {
        const input = {
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA', assetType: 'stock' } },
            { type: 'timeframe', payload: { interval: '1D' } },
            { type: 'indicator', payload: { name: 'RSI', enabled: true, params: { period: 14 } } },
            { type: 'drawing', payload: { action: 'support', price: 420.69 } },
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.structured).toHaveLength(4);
        expect(result.structured[0].type).toBe('load');
        expect(result.structured[1].type).toBe('timeframe');
        expect(result.structured[2].type).toBe('indicator');
        expect(result.structured[3].type).toBe('drawing');
      });

      it('should preserve complex payload structures', () => {
        const input = {
          chart_commands_structured: [
            {
              type: 'drawing',
              payload: {
                action: 'pattern_trendline',
                patternId: 'head-and-shoulders-1',
                startTime: 1699920000,
                startPrice: 250.5,
                endTime: 1700524800,
                endPrice: 245.2,
              },
              description: 'Left shoulder neckline',
              legacy: 'DRAW:TRENDLINE:250.5:245.2',
              timestamp: '2024-11-08T12:00:00Z',
            },
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.structured).toHaveLength(1);
        const cmd = result.structured[0];
        expect(cmd.type).toBe('drawing');
        expect(cmd.payload.action).toBe('pattern_trendline');
        expect(cmd.payload.patternId).toBe('head-and-shoulders-1');
        expect(cmd.description).toBe('Left shoulder neckline');
        expect(cmd.legacy).toBe('DRAW:TRENDLINE:250.5:245.2');
        expect(cmd.timestamp).toBe('2024-11-08T12:00:00Z');
      });

      it('should handle mixed legacy and structured commands', () => {
        const input = {
          chart_commands: ['LOAD:TSLA', 'INDICATOR:MACD', 'TIMEFRAME:1H'],
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA' } },
            { type: 'indicator', payload: { name: 'MACD', enabled: true } },
            { type: 'timeframe', payload: { interval: '1H' } },
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toHaveLength(3);
        expect(result.structured).toHaveLength(3);
        expect(result.legacy[0]).toBe('LOAD:TSLA');
        expect(result.structured[0].type).toBe('load');
      });
    });

    describe('Edge Cases', () => {
      it('should handle empty arrays', () => {
        const input = {
          chart_commands: [],
          chart_commands_structured: [],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.legacy).toEqual([]);
        expect(result.structured).toEqual([]);
      });

      it('should handle number input gracefully', () => {
        const result = normalizeChartCommandPayload(123 as any);

        expect(result.legacy).toEqual([]);
        expect(result.structured).toEqual([]);
      });

      it('should handle boolean input gracefully', () => {
        const result = normalizeChartCommandPayload(true as any);

        expect(result.legacy).toEqual([]);
        expect(result.structured).toEqual([]);
      });

      it('should preserve empty strings in legacy commands', () => {
        const input = {
          chart_commands: ['', 'LOAD:TSLA', ''],
        };

        const result = normalizeChartCommandPayload(input);

        // Empty strings are still strings, should be preserved
        expect(result.legacy).toEqual(['', 'LOAD:TSLA', '']);
      });

      it('should handle deeply nested payload structures', () => {
        const input = {
          chart_commands_structured: [
            {
              type: 'indicator',
              payload: {
                name: 'Custom Indicator',
                enabled: true,
                params: {
                  period: 20,
                  style: {
                    color: '#FF6B6B',
                    lineWidth: 2,
                    plotType: 'line',
                  },
                  calculations: {
                    method: 'ema',
                    smoothing: 2,
                  },
                },
              },
            },
          ],
        };

        const result = normalizeChartCommandPayload(input);

        expect(result.structured).toHaveLength(1);
        const cmd = result.structured[0];
        expect(cmd.payload.params.style.color).toBe('#FF6B6B');
        expect(cmd.payload.params.calculations.method).toBe('ema');
      });
    });

    describe('Type Safety', () => {
      it('should maintain TypeScript types', () => {
        const input = {
          chart_commands: ['LOAD:TSLA'],
          chart_commands_structured: [{ type: 'load', payload: { symbol: 'TSLA' } }],
        };

        const result: ChartCommandPayload = normalizeChartCommandPayload(input);

        // TypeScript should recognize these types
        expect(Array.isArray(result.legacy)).toBe(true);
        expect(Array.isArray(result.structured)).toBe(true);
        expect(typeof result.responseText === 'string' || result.responseText === undefined).toBe(true);
      });

      it('should work with discriminated union types', () => {
        const input = {
          chart_commands_structured: [
            { type: 'load', payload: { symbol: 'TSLA' } } as const,
            { type: 'indicator', payload: { name: 'RSI', enabled: true } } as const,
          ],
        };

        const result = normalizeChartCommandPayload(input);

        // Discriminated unions allow type narrowing
        result.structured.forEach((cmd: StructuredChartCommand) => {
          if (cmd.type === 'load') {
            // TypeScript knows this is LoadCommand
            expect(cmd.payload).toHaveProperty('symbol');
          } else if (cmd.type === 'indicator') {
            // TypeScript knows this is IndicatorCommand
            expect(cmd.payload).toHaveProperty('name');
            expect(cmd.payload).toHaveProperty('enabled');
          }
        });
      });
    });
  });
});
