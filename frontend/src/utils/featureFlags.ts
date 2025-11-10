/**
 * Feature Flags Configuration
 * ============================
 *
 * Centralized feature flag management for experimental features.
 *
 * Phase 1: Structured Chart Command Migration
 */

/**
 * Prefer structured chart commands over legacy string commands.
 *
 * When enabled:
 * - Structured commands processed first
 * - Legacy commands ignored if structured commands present
 * - Enables cleaner, type-safe command handling
 *
 * When disabled (default):
 * - Hybrid mode: both formats processed
 * - Backward compatible with existing integrations
 *
 * @default false
 */
export const PREFER_STRUCTURED_CHART_COMMANDS =
  import.meta.env.VITE_PREFER_STRUCTURED_CHART_COMMANDS === 'true';

/**
 * Enable structured chart objects payload (ChartCommandPayloadV2 wiring).
 * When enabled, frontend will consume chart_objects first.
 */
export const ENABLE_STRUCTURED_CHART_OBJECTS =
  import.meta.env.VITE_ENABLE_STRUCTURED_CHART_OBJECTS === 'true';

/**
 * Feature flag for debugging - logs feature flag states on startup
 */
export const DEBUG_FEATURE_FLAGS =
  import.meta.env.VITE_DEBUG_FEATURE_FLAGS === 'true';

// Log feature flag states in development
if (DEBUG_FEATURE_FLAGS && import.meta.env.DEV) {
  console.log('[Feature Flags] Configuration:', {
    PREFER_STRUCTURED_CHART_COMMANDS,
    ENABLE_STRUCTURED_CHART_OBJECTS,
    DEBUG_FEATURE_FLAGS,
  });
}
