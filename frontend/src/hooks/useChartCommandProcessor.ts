/**
 * Chart Command Processor Hook
 * Polls the Chart Control API for commands and executes them via the chart control service.
 */

import { useEffect, useRef, useCallback } from 'react';
import { chartControlService } from '../services/chartControlService';
import { marketDataService } from '../services/marketDataService';

interface ChartCommand {
  id: string;
  type: 'symbol_change' | 'timeframe_change' | 'indicator_toggle' | 'capture_snapshot' | 'style_change';
  data: any;
  timestamp: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

interface UseChartCommandProcessorOptions {
  enabled?: boolean;
  pollingInterval?: number; // milliseconds
  onCommandExecuted?: (command: ChartCommand, success: boolean, message: string) => void;
  onError?: (error: string) => void;
}

export function useChartCommandProcessor(options: UseChartCommandProcessorOptions = {}) {
  const {
    enabled = true,
    pollingInterval = 1000, // Poll every 1 second
    onCommandExecuted,
    onError
  } = options;

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const processingRef = useRef<boolean>(false);
  const lastProcessedRef = useRef<string>('');

  const acknowledgeCommand = useCallback(async (commandId: string) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL || window.location.origin}/api/chart/commands/${commandId}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Failed to acknowledge command:', error);
    }
  }, []);

  const executeCommand = useCallback(async (command: ChartCommand) => {
    let success = false;
    let message = '';

    try {
      switch (command.type) {
        case 'symbol_change':
          const symbol = command.data.symbol;
          if (symbol) {
            // Trigger symbol change via chartControlService
            const chartCommand = {
              type: 'symbol' as const,
              value: symbol,
              metadata: { 
                assetType: 'stock' as const,
                source: 'mcp_api' 
              },
              timestamp: Date.now()
            };
            
            success = chartControlService.executeCommand(chartCommand);
            message = success ? `Chart symbol changed to ${symbol}` : 'Failed to change symbol';
          }
          break;

        case 'timeframe_change':
          const timeframe = command.data.timeframe;
          if (timeframe) {
            const chartCommand = {
              type: 'timeframe' as const,
              value: timeframe,
              timestamp: Date.now()
            };
            
            success = chartControlService.executeCommand(chartCommand);
            message = success ? `Timeframe changed to ${timeframe}` : 'Failed to change timeframe';
          }
          break;

        case 'indicator_toggle':
          const { indicator, enabled } = command.data;
          if (indicator !== undefined && enabled !== undefined) {
            const chartCommand = {
              type: 'indicator' as const,
              value: { name: indicator, enabled },
              timestamp: Date.now()
            };
            
            success = chartControlService.executeCommand(chartCommand);
            const action = enabled ? 'enabled' : 'disabled';
            message = success ? `${indicator} indicator ${action}` : `Failed to ${enabled ? 'enable' : 'disable'} ${indicator}`;
          }
          break;

        case 'capture_snapshot':
          // For now, just acknowledge the command
          // TODO: Implement actual screenshot functionality
          success = true;
          message = 'Chart snapshot capture initiated (frontend implementation pending)';
          break;

        case 'style_change':
          const style = command.data.style;
          if (style) {
            const chartCommand = {
              type: 'style' as const,
              value: style,
              timestamp: Date.now()
            };
            
            success = chartControlService.executeCommand(chartCommand);
            message = success ? `Chart style changed to ${style}` : 'Failed to change style';
          }
          break;

        default:
          message = `Unknown command type: ${command.type}`;
          break;
      }

      // Call the callback with results
      if (onCommandExecuted) {
        onCommandExecuted(command, success, message);
      }

      // Log the command execution
      console.log(`Chart Command ${command.id}: ${message} (${success ? 'Success' : 'Failed'})`);

      return success;

    } catch (error: any) {
      const errorMessage = `Error executing command ${command.id}: ${error.message}`;
      console.error(errorMessage);
      
      if (onError) {
        onError(errorMessage);
      }
      
      if (onCommandExecuted) {
        onCommandExecuted(command, false, errorMessage);
      }
      
      return false;
    }
  }, [onCommandExecuted, onError]);

  const pollCommands = useCallback(async () => {
    if (processingRef.current) {
      return; // Skip if already processing
    }

    processingRef.current = true;

    try {
      // Get pending commands from the Chart Control API
      const response = await fetch(`${import.meta.env.VITE_API_URL || window.location.origin}/api/chart/commands`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const commands: ChartCommand[] = data.commands || [];

      // Process new commands
      for (const command of commands) {
        // Skip already processed commands
        if (command.id === lastProcessedRef.current) {
          continue;
        }

        console.log(`Processing chart command: ${command.type}`, command.data);

        // Execute the command
        const success = await executeCommand(command);

        // Acknowledge the command (remove it from the queue)
        await acknowledgeCommand(command.id);

        // Update last processed ID
        lastProcessedRef.current = command.id;

        // Break after processing one command to avoid overwhelming the UI
        break;
      }

    } catch (error: any) {
      const errorMessage = `Chart command polling error: ${error.message}`;
      console.error(errorMessage);
      
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      processingRef.current = false;
    }
  }, [executeCommand, acknowledgeCommand, onError]);

  // Start/stop polling
  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Start polling
    intervalRef.current = setInterval(pollCommands, pollingInterval);

    // Initial poll
    pollCommands();

    // Cleanup on unmount or when disabled
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, pollingInterval, pollCommands]);

  // Manual poll function
  const manualPoll = useCallback(() => {
    pollCommands();
  }, [pollCommands]);

  // Status
  const isProcessing = processingRef.current;

  return {
    isProcessing,
    manualPoll,
    lastProcessedCommand: lastProcessedRef.current
  };
}