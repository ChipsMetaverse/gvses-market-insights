import { z } from 'zod';

import type { ChartObjectsPayload, StructuredChartCommand } from '../types/chartCommands';

const BaseStructuredCommandSchema = z
  .object({
    type: z.string(),
    description: z.string().nullable().optional(),
    legacy: z.string().nullable().optional(),
    timestamp: z.string().optional(),
    payload: z.record(z.any()).optional(),
  })
  .passthrough();

const LoadCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('load'),
  payload: z
    .object({
      symbol: z.string(),
      assetType: z.enum(['stock', 'crypto']).optional(),
    })
    .passthrough(),
});

const TimeframeCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('timeframe'),
  payload: z
    .object({
      interval: z.string().optional(),
      value: z.string().optional(),
    })
    .passthrough(),
});

const IndicatorCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('indicator'),
  payload: z
    .object({
      name: z.string().optional(),
      indicator: z.string().optional(),
      enabled: z.boolean().optional(),
      params: z.record(z.any()).optional(),
    })
    .passthrough(),
});

const DrawingCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('drawing'),
  payload: z
    .object({
      action: z.string(),
    })
    .passthrough(),
});

const ZoomCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('zoom'),
  payload: z
    .object({
      direction: z.string().optional(),
      level: z.number().optional(),
      amount: z.number().optional(),
    })
    .passthrough(),
});

const ScrollCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('scroll'),
  payload: z
    .object({
      time: z.number().optional(),
      date: z.union([z.string(), z.number()]).optional(),
    })
    .passthrough(),
});

const StyleCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('style'),
  payload: z
    .object({
      chartType: z.string(),
    })
    .passthrough(),
});

const ResetCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('reset'),
  payload: z.object({}).passthrough(),
});

const CrosshairCommandSchema = BaseStructuredCommandSchema.extend({
  type: z.literal('crosshair'),
  payload: z
    .object({
      enabled: z.boolean().optional(),
      mode: z.string().optional(),
      state: z.string().optional(),
    })
    .passthrough(),
});

const FallbackCommandSchema = BaseStructuredCommandSchema;

export const StructuredChartCommandSchema = z.union([
  LoadCommandSchema,
  TimeframeCommandSchema,
  IndicatorCommandSchema,
  DrawingCommandSchema,
  ZoomCommandSchema,
  ScrollCommandSchema,
  StyleCommandSchema,
  ResetCommandSchema,
  CrosshairCommandSchema,
  FallbackCommandSchema,
]);

const StructuredChartCommandArraySchema = z.array(StructuredChartCommandSchema);

const ChartCommandOverlayConfigSchema = z
  .object({
    name: z.string(),
    type: z.string().nullish(),
    params: z.record(z.any()).optional(),
  })
  .passthrough();

const ChartCommandIndicatorConfigSchema = z
  .object({
    name: z.string(),
    enabled: z.boolean().nullish(),
    params: z.record(z.any()).optional(),
  })
  .passthrough();

const ChartObjectsPayloadSchema = z
  .object({
    version: z.literal('2.0'),
    symbol: z.string().nullish(),
    timeframe: z.string().nullish(),
    overlays: z.array(ChartCommandOverlayConfigSchema),
    indicators: z.array(ChartCommandIndicatorConfigSchema),
    commands: StructuredChartCommandArraySchema,
    notes: z.string().nullish(),
  })
  .passthrough();

export function validateStructuredCommandArray(
  commands: StructuredChartCommand[],
): StructuredChartCommand[] | null {
  const result = StructuredChartCommandArraySchema.safeParse(commands);

  if (!result.success) {
    console.warn('[chartCommandUtils] Structured command validation failed', result.error.format());
    return null;
  }

  return result.data as StructuredChartCommand[];
}

export function validateChartObjectsPayload(
  payload: ChartObjectsPayload,
): ChartObjectsPayload | null {
  const result = ChartObjectsPayloadSchema.safeParse(payload);

  if (!result.success) {
    console.warn('[chartCommandUtils] Chart objects validation failed', result.error.format());
    return null;
  }

  return result.data as ChartObjectsPayload;
}
