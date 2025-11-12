/**
 * Chart Command Poller
 * Polls the backend for chart control commands from Agent Builder HTTP actions
 * and executes them on the frontend chart.
 */

export interface ChartCommand {
  type: 'symbol' | 'timeframe' | 'indicator' | 'style' | 'snapshot';
  value: string;
  enabled?: boolean;
  metadata?: any;
}

export interface BackendCommand {
  id: string;
  type: string;
  data: any;
  timestamp: string;
  status: string;
}

export class ChartCommandPoller {
  private interval: NodeJS.Timeout | null = null;
  private isPolling = false;
  private pollIntervalMs: number;
  private onCommand: (command: ChartCommand) => void;
  private apiBaseUrl: string;

  constructor(
    onCommand: (command: ChartCommand) => void,
    pollIntervalMs = 1000,
    apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  ) {
    this.onCommand = onCommand;
    this.pollIntervalMs = pollIntervalMs;
    this.apiBaseUrl = apiBaseUrl;
  }

  /**
   * Start polling for chart commands
   */
  start() {
    if (this.isPolling) {
      console.log('[ChartPoller] Already polling');
      return;
    }

    console.log('[ChartPoller] Starting command polling');
    this.isPolling = true;

    // Immediate first poll
    this.poll();

    // Set up interval
    this.interval = setInterval(() => {
      this.poll();
    }, this.pollIntervalMs);
  }

  /**
   * Stop polling
   */
  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.isPolling = false;
    console.log('[ChartPoller] Stopped polling');
  }

  /**
   * Single poll cycle
   */
  private async poll() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/chart/commands`);

      if (!response.ok) {
        console.error('[ChartPoller] Failed to fetch commands:', response.status);
        return;
      }

      const data = await response.json();

      // Process pending commands
      if (data.commands && Array.isArray(data.commands)) {
        for (const command of data.commands) {
          if (command.status === 'pending') {
            await this.processCommand(command);
          }
        }
      }
    } catch (error) {
      console.error('[ChartPoller] Error polling commands:', error);
    }
  }

  /**
   * Process a single backend command
   */
  private async processCommand(command: BackendCommand) {
    console.log('[ChartPoller] Processing command:', command);

    try {
      // Convert backend command to frontend chart command
      const chartCommand = this.convertCommand(command);

      if (chartCommand) {
        // Execute command via callback
        this.onCommand(chartCommand);

        // Acknowledge command to backend
        await this.acknowledgeCommand(command.id);
      }
    } catch (error) {
      console.error('[ChartPoller] Error processing command:', command.id, error);
    }
  }

  /**
   * Convert backend command format to frontend chart command
   */
  private convertCommand(backendCommand: BackendCommand): ChartCommand | null {
    switch (backendCommand.type) {
      case 'symbol_change':
        return {
          type: 'symbol',
          value: backendCommand.data.symbol,
          metadata: {
            previousSymbol: backendCommand.data.previous_symbol
          }
        };

      case 'timeframe_change':
        return {
          type: 'timeframe',
          value: backendCommand.data.timeframe,
          metadata: {
            previousTimeframe: backendCommand.data.previous_timeframe
          }
        };

      case 'indicator_toggle':
        return {
          type: 'indicator',
          value: backendCommand.data.indicator,
          enabled: backendCommand.data.enabled,
          metadata: {
            requestedIndicator: backendCommand.data.requested_indicator,
            previousState: backendCommand.data.previous_state
          }
        };

      case 'style_change':
        return {
          type: 'style',
          value: backendCommand.data.style,
          metadata: {
            previousStyle: backendCommand.data.previous_style
          }
        };

      case 'capture_snapshot':
        return {
          type: 'snapshot',
          value: 'capture',
          metadata: backendCommand.data
        };

      default:
        console.warn('[ChartPoller] Unknown command type:', backendCommand.type);
        return null;
    }
  }

  /**
   * Acknowledge command has been processed
   */
  private async acknowledgeCommand(commandId: string) {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/api/chart/commands/${commandId}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        console.log('[ChartPoller] Acknowledged command:', commandId);
      } else {
        console.error('[ChartPoller] Failed to acknowledge command:', commandId);
      }
    } catch (error) {
      console.error('[ChartPoller] Error acknowledging command:', commandId, error);
    }
  }

  /**
   * Check if currently polling
   */
  isActive(): boolean {
    return this.isPolling;
  }
}
