/**
 * Chart Command Type Definitions
 * Discriminated unions for type-safe chart command payloads
 *
 * Phase 1: Chart Command Hardening - Enhanced Type Safety
 */

export interface StructuredChartCommand {
  type: string;
  payload?: Record<string, any>;
  description?: string | null;
  legacy?: string | null;
  timestamp?: string;
}

/**
 * Legacy chart command format (string-based)
 * Examples: "LOAD:TSLA", "TIMEFRAME:1D", "INDICATOR:RSI"
 */
export type LegacyChartCommand = string;

/**
 * Normalized chart command payload
 * Contains both legacy and structured formats for backwards compatibility
 */
export interface ChartCommandPayload {
  /** Legacy string-based commands (e.g., ["LOAD:TSLA", "INDICATOR:RSI"]) */
  legacy: LegacyChartCommand[];
  /** Structured command objects with typed payloads */
  structured: StructuredChartCommand[];
  /** Optional response text from agent */
  responseText?: string;
  /** Optional structured chart objects payload (Phase 1 migration) */
  objects?: ChartObjectsPayload | null;
}

/**
 * Overlay configuration contained within ChartObjectsPayload
 */
export interface ChartCommandOverlayConfig {
  name: string;
  type?: string | null;
  params?: Record<string, unknown>;
}

/**
 * Indicator configuration contained within ChartObjectsPayload
 */
export interface ChartCommandIndicatorConfig {
  name: string;
  enabled?: boolean | null;
  params?: Record<string, unknown>;
}

/**
 * Chart objects payload emitted by the backend when structured chart objects are enabled
 */
export interface ChartObjectsPayload {
  version: '2.0';
  symbol?: string | null;
  timeframe?: string | null;
  overlays: ChartCommandOverlayConfig[];
  indicators: ChartCommandIndicatorConfig[];
  commands: StructuredChartCommand[];
  notes?: string | null;
}

/**
 * Type guard to check if a command is a LoadCommand
 */
export function isLoadCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'load';
}

/**
 * Type guard to check if a command is a TimeframeCommand
 */
export function isTimeframeCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'timeframe';
}

/**
 * Type guard to check if a command is an IndicatorCommand
 */
export function isIndicatorCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'indicator';
}

/**
 * Type guard to check if a command is a DrawingCommand
 */
export function isDrawingCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'drawing';
}

/**
 * Type guard to check if a command is a ZoomCommand
 */
export function isZoomCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'zoom';
}

/**
 * Type guard to check if a command is a ScrollCommand
 */
export function isScrollCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'scroll';
}

/**
 * Type guard to check if a command is a StyleCommand
 */
export function isStyleCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'style';
}

/**
 * Type guard to check if a command is a ResetCommand
 */
export function isResetCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'reset';
}

/**
 * Type guard to check if a command is a CrosshairCommand
 */
export function isCrosshairCommand(cmd: StructuredChartCommand): boolean {
  return cmd.type === 'crosshair';
}

/**
 * Example usage of discriminated unions with type narrowing:
 *
 * ```typescript
 * function processCommand(cmd: StructuredChartCommand) {
 *   switch (cmd.type) {
 *     case 'load':
 *       // TypeScript knows cmd is LoadCommand here
 *       console.log('Loading symbol:', cmd.payload.symbol);
 *       break;
 *     case 'indicator':
 *       // TypeScript knows cmd is IndicatorCommand here
 *       console.log('Toggling indicator:', cmd.payload.name, cmd.payload.enabled);
 *       break;
 *     case 'timeframe':
 *       // TypeScript knows cmd is TimeframeCommand here
 *       console.log('Changing timeframe to:', cmd.payload.interval);
 *       break;
 *     // ... other cases
 *   }
 * }
 *
 * // Type guards
 * if (isLoadCommand(cmd)) {
 *   console.log(cmd.payload.symbol); // TypeScript knows this is valid
 * }
 * ```
 */
