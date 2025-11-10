/**
 * Chart Command Utilities
 * Normalizes chart commands from various formats into a consistent payload structure
 *
 * Phase 1: Chart Command Hardening - Enhanced Type Safety
 */

import type {
  ChartCommandIndicatorConfig,
  ChartCommandOverlayConfig,
  ChartCommandPayload,
  ChartObjectsPayload,
  StructuredChartCommand,
} from '../types/chartCommands';
import {
  validateChartObjectsPayload,
  validateStructuredCommandArray,
} from '../schemas/chartCommands.schema';

type ChartObjectsLike = ChartObjectsPayload | null | undefined | { [key: string]: unknown };

function normalizeChartObjects(
  candidate: ChartObjectsLike,
  structuredFallback: StructuredChartCommand[],
): ChartObjectsPayload | null {
  if (!candidate || typeof candidate !== 'object') {
    return null;
  }

  const version = String((candidate as any).version ?? '').trim();
  if (version !== '2.0') {
    return null;
  }

  const symbolRaw = (candidate as any).symbol ?? (candidate as any).ticker ?? null;
  const timeframeRaw = (candidate as any).timeframe ?? (candidate as any).interval ?? null;
  const overlaysRaw = (candidate as any).overlays ?? [];
  const indicatorsRaw = (candidate as any).indicators ?? [];
  const notesRaw = (candidate as any).notes ?? (candidate as any).description ?? null;

  const normalizeOverlays = (value: unknown): ChartCommandOverlayConfig[] => {
    if (!Array.isArray(value)) {
      return [];
    }
    return value.reduce<ChartCommandOverlayConfig[]>((acc, item) => {
      if (typeof item !== 'object' || item === null) {
        return acc;
      }
      const rawName = (item as any).name ?? (item as any).indicator ?? (item as any).overlay;
      if (typeof rawName !== 'string' || rawName.trim() === '') {
        return acc;
      }

      const overlay: ChartCommandOverlayConfig = {
        name: rawName.trim(),
      };

      const rawType = (item as any).type;
      if (typeof rawType === 'string' && rawType.trim() !== '') {
        overlay.type = rawType.trim();
      }

      const rawParams = (item as any).params;
      if (rawParams && typeof rawParams === 'object') {
        overlay.params = { ...(rawParams as Record<string, unknown>) };
      }

      acc.push(overlay);
      return acc;
    }, []);
  };

  const normalizeIndicators = (value: unknown): ChartCommandIndicatorConfig[] => {
    if (!Array.isArray(value)) {
      return [];
    }
    return value.reduce<ChartCommandIndicatorConfig[]>((acc, item) => {
      if (typeof item !== 'object' || item === null) {
        return acc;
      }
      const rawName = (item as any).name ?? (item as any).indicator;
      if (typeof rawName !== 'string' || rawName.trim() === '') {
        return acc;
      }

      const indicator: ChartCommandIndicatorConfig = {
        name: rawName.trim(),
      };

      if (typeof (item as any).enabled === 'boolean') {
        indicator.enabled = (item as any).enabled;
      }

      const rawParams = (item as any).params;
      if (rawParams && typeof rawParams === 'object') {
        indicator.params = { ...(rawParams as Record<string, unknown>) };
      }

      acc.push(indicator);
      return acc;
    }, []);
  };

  const candidateCommandsRaw = normalizeStructuredCommands((candidate as any).commands ?? []);
  const validatedCandidateCommands = validateStructuredCommandArray(candidateCommandsRaw);
  const commands = validatedCandidateCommands ?? structuredFallback;

  const payloadCandidate: ChartObjectsPayload = {
    version: '2.0',
    symbol: typeof symbolRaw === 'string' ? symbolRaw : null,
    timeframe: typeof timeframeRaw === 'string' ? timeframeRaw : null,
    overlays: normalizeOverlays(overlaysRaw),
    indicators: normalizeIndicators(indicatorsRaw),
    commands,
    notes: typeof notesRaw === 'string' ? notesRaw : null,
  };

  const validatedPayload = validateChartObjectsPayload(payloadCandidate);

  if (!validatedPayload) {
    console.warn('[chartCommandUtils] Discarding invalid chart_objects payload');
    return null;
  }

  return validatedPayload;
}

// Re-export for backwards compatibility
export type { ChartCommandPayload, StructuredChartCommand } from '../types/chartCommands';

/**
 * Normalizes legacy chart commands into a string array
 *
 * @param commands - Input can be string, string[], or unknown
 * @returns Array of valid string commands, empty array if invalid
 *
 * @example
 * normalizeLegacyCommands('LOAD:TSLA') // ['LOAD:TSLA']
 * normalizeLegacyCommands(['LOAD:TSLA', 'INDICATOR:RSI']) // ['LOAD:TSLA', 'INDICATOR:RSI']
 * normalizeLegacyCommands(null) // []
 */
function normalizeLegacyCommands(commands: unknown): string[] {
  if (!commands) {
    return [];
  }

  if (Array.isArray(commands)) {
    return commands.filter((item): item is string => typeof item === 'string');
  }

  if (typeof commands === 'string') {
    return [commands];
  }

  return [];
}

/**
 * Normalizes structured chart commands into a typed array
 *
 * Validates each command has a valid 'type' field and filters out invalid entries
 *
 * @param commands - Input can be StructuredChartCommand[], mixed array, or unknown
 * @returns Array of valid StructuredChartCommand objects, empty array if invalid
 *
 * @example
 * normalizeStructuredCommands([{ type: 'load', payload: { symbol: 'TSLA' } }])
 * // [{ type: 'load', payload: { symbol: 'TSLA' } }]
 *
 * normalizeStructuredCommands([{ type: 'load' }, { invalid: 'command' }, null])
 * // [{ type: 'load' }]  - Filters out invalid commands
 */
function normalizeStructuredCommands(commands: unknown): StructuredChartCommand[] {
  if (!commands) {
    return [];
  }

  if (Array.isArray(commands)) {
    return commands.filter((item): item is StructuredChartCommand => {
      return (
        typeof item === 'object' &&
        item !== null &&
        typeof (item as StructuredChartCommand).type === 'string'
      );
    });
  }

  return [];
}

/**
 * Normalizes chart commands from various input formats into a consistent ChartCommandPayload
 *
 * Handles both backend API responses (snake_case) and frontend objects (camelCase)
 * Supports multiple input formats for maximum flexibility
 *
 * @param input - Can be:
 *   - ChartCommandPayload object (already normalized)
 *   - API response with `chart_commands` and `chart_commands_structured` (snake_case)
 *   - Frontend object with `legacy` and `structured` (camelCase)
 *   - String or string array (legacy format only)
 *   - null/undefined (returns empty payload)
 *
 * @param responseText - Optional agent response text to include in payload
 *
 * @returns ChartCommandPayload with normalized legacy and structured arrays
 *
 * @example
 * // Backend API response (snake_case)
 * normalizeChartCommandPayload({
 *   chart_commands: ['LOAD:TSLA'],
 *   chart_commands_structured: [{ type: 'load', payload: { symbol: 'TSLA' } }]
 * })
 * // { legacy: ['LOAD:TSLA'], structured: [{ type: 'load', payload: { symbol: 'TSLA' } }] }
 *
 * @example
 * // Frontend object (camelCase)
 * normalizeChartCommandPayload({
 *   legacy: ['LOAD:AAPL'],
 *   structured: [{ type: 'load', payload: { symbol: 'AAPL' } }]
 * })
 * // { legacy: ['LOAD:AAPL'], structured: [{ type: 'load', payload: { symbol: 'AAPL' } }] }
 *
 * @example
 * // Legacy string only
 * normalizeChartCommandPayload('LOAD:NVDA')
 * // { legacy: ['LOAD:NVDA'], structured: [] }
 *
 * @example
 * // Null/undefined
 * normalizeChartCommandPayload(null)
 * // { legacy: [], structured: [] }
 */
export function normalizeChartCommandPayload(
  input: unknown,
  responseText?: string
): ChartCommandPayload {
  if (!input) {
    return { legacy: [], structured: [], responseText };
  }

  if (typeof input === 'object' && input !== null && !Array.isArray(input)) {
    const candidate = input as Partial<ChartCommandPayload> & {
      chart_commands?: unknown;
      chart_commands_structured?: unknown;
      chart_objects?: unknown;
      chartObjects?: unknown;
    };

    const legacy = normalizeLegacyCommands(candidate.legacy ?? candidate.chart_commands);
    const structuredNormalized = normalizeStructuredCommands(
      candidate.structured ?? candidate.chart_commands_structured
    );

    const structuredValidated = validateStructuredCommandArray(structuredNormalized) ?? structuredNormalized;

    const objects = normalizeChartObjects(
      (candidate.objects as ChartObjectsLike) ??
        (candidate.chart_objects as ChartObjectsLike) ??
        (candidate.chartObjects as ChartObjectsLike),
      structuredValidated,
    );

    const result: ChartCommandPayload = {
      legacy,
      structured: objects?.commands ?? structuredValidated,
      responseText: candidate.responseText ?? responseText,
    };

    if (objects) {
      result.objects = objects;
    }

    return result;
  }

  const legacy = normalizeLegacyCommands(input);
  return { legacy, structured: [], responseText };
}
