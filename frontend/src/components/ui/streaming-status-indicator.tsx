// Streaming Status Indicator - Shows real-time data connection status
// Visual feedback for WebSocket connections and streaming updates

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { Activity, Loader2, Pause, Play, AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { Badge } from './badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './tooltip';
import { Button } from './button';
import { streamingDataService, StreamingProvider } from '@/services/streamingDataService.browser';

export interface StreamingStatusProps {
  className?: string;
  showDetails?: boolean;
  onToggleStreaming?: (enabled: boolean) => void;
}

interface ProviderStatus {
  provider: StreamingProvider;
  isConnected: boolean;
  symbolCount: number;
  lastUpdate?: Date;
  error?: string;
}

export function StreamingStatusIndicator({ 
  className, 
  showDetails = false,
  onToggleStreaming 
}: StreamingStatusProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [activeSymbols, setActiveSymbols] = useState<string[]>([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [updateCount, setUpdateCount] = useState(0);

  useEffect(() => {
    // Set up event listeners
    const handleConnectionChange = ({ provider, connected }: any) => {
      setProviders(prev => {
        const existing = prev.find(p => p.provider === provider);
        if (existing) {
          return prev.map(p => 
            p.provider === provider 
              ? { ...p, isConnected: connected, error: connected ? undefined : p.error }
              : p
          );
        }
        return [...prev, { provider, isConnected: connected, symbolCount: 0 }];
      });
      
      // Update overall streaming status
      setIsStreaming(connected || providers.some(p => p.isConnected));
      setIsConnecting(false);
    };

    const handlePriceUpdate = ({ symbol }: any) => {
      setUpdateCount(prev => prev + 1);
      
      // Update last update time for connected providers
      setProviders(prev => prev.map(p => 
        p.isConnected ? { ...p, lastUpdate: new Date() } : p
      ));
    };

    const handleError = ({ provider, error }: any) => {
      setProviders(prev => prev.map(p => 
        p.provider === provider 
          ? { ...p, error: error.message, isConnected: false }
          : p
      ));
      setIsConnecting(false);
    };

    const handleSymbolsChange = ({ symbols }: any) => {
      setActiveSymbols(symbols);
      
      // Update symbol count per provider
      const providerSymbols = streamingDataService.getActiveProviders();
      setProviders(prev => prev.map(p => ({
        ...p,
        symbolCount: providerSymbols[p.provider]?.length || 0
      })));
    };

    // Subscribe to events
    streamingDataService.on('providerConnected', handleConnectionChange);
    streamingDataService.on('providerDisconnected', handleConnectionChange);
    streamingDataService.on('priceUpdate', handlePriceUpdate);
    streamingDataService.on('providerError', handleError);
    streamingDataService.on('symbolsChanged', handleSymbolsChange);

    // Get initial state
    const status = streamingDataService.getConnectionStatus();
    const initialProviders: ProviderStatus[] = [];
    
    Object.entries(status).forEach(([provider, data]) => {
      initialProviders.push({
        provider: provider as StreamingProvider,
        isConnected: data.connected,
        symbolCount: data.symbols?.length || 0,
        lastUpdate: data.lastUpdate ? new Date(data.lastUpdate) : undefined,
        error: data.error
      });
    });
    
    setProviders(initialProviders);
    setIsStreaming(initialProviders.some(p => p.isConnected));
    setActiveSymbols(streamingDataService.getSubscribedSymbols());

    // Cleanup
    return () => {
      streamingDataService.off('providerConnected', handleConnectionChange);
      streamingDataService.off('providerDisconnected', handleConnectionChange);
      streamingDataService.off('priceUpdate', handlePriceUpdate);
      streamingDataService.off('providerError', handleError);
      streamingDataService.off('symbolsChanged', handleSymbolsChange);
    };
  }, []);

  const handleToggle = () => {
    if (onToggleStreaming) {
      const newState = !isStreaming;
      setIsConnecting(newState);
      onToggleStreaming(newState);
    }
  };

  const connectedCount = providers.filter(p => p.isConnected).length;
  const totalSymbols = providers.reduce((sum, p) => sum + p.symbolCount, 0);

  // Simple indicator
  if (!showDetails) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className={cn("flex items-center gap-2", className)}>
              <div className="relative">
                {isConnecting ? (
                  <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
                ) : isStreaming ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-muted-foreground" />
                )}
                {isStreaming && (
                  <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                )}
              </div>
              <span className="text-sm text-muted-foreground">
                {isConnecting ? 'Connecting...' : isStreaming ? 'Live' : 'Offline'}
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <div className="space-y-1 text-xs">
              <p className="font-medium">
                {isStreaming 
                  ? `Streaming ${totalSymbols} symbol${totalSymbols !== 1 ? 's' : ''}`
                  : 'No active streams'}
              </p>
              {connectedCount > 0 && (
                <p className="text-muted-foreground">
                  {connectedCount} provider{connectedCount !== 1 ? 's' : ''} connected
                </p>
              )}
              {updateCount > 0 && (
                <p className="text-muted-foreground">
                  {updateCount} update{updateCount !== 1 ? 's' : ''} received
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Detailed indicator
  return (
    <div className={cn("space-y-3", className)}>
      {/* Header with toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isConnecting ? (
            <Loader2 className="h-5 w-5 animate-spin text-yellow-500" />
          ) : isStreaming ? (
            <Activity className="h-5 w-5 text-green-500 animate-pulse" />
          ) : (
            <WifiOff className="h-5 w-5 text-muted-foreground" />
          )}
          <span className="font-medium">
            Real-Time Data
          </span>
        </div>
        {onToggleStreaming && (
          <Button
            size="sm"
            variant={isStreaming ? "ghost" : "outline"}
            onClick={handleToggle}
            disabled={isConnecting}
          >
            {isStreaming ? (
              <>
                <Pause className="h-3 w-3 mr-1" />
                Pause
              </>
            ) : (
              <>
                <Play className="h-3 w-3 mr-1" />
                Start
              </>
            )}
          </Button>
        )}
      </div>

      {/* Provider status */}
      {providers.length > 0 && (
        <div className="space-y-2">
          {providers.map(provider => (
            <div key={provider.provider} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={cn(
                  "h-2 w-2 rounded-full",
                  provider.isConnected ? "bg-green-500" : "bg-gray-300"
                )} />
                <span className="text-sm">{provider.provider}</span>
              </div>
              <div className="flex items-center gap-2">
                {provider.symbolCount > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    {provider.symbolCount} symbol{provider.symbolCount !== 1 ? 's' : ''}
                  </Badge>
                )}
                {provider.error && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <AlertCircle className="h-3 w-3 text-red-500" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="text-xs">{provider.error}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Active symbols */}
      {activeSymbols.length > 0 && (
        <div>
          <p className="text-xs text-muted-foreground mb-1">Streaming:</p>
          <div className="flex flex-wrap gap-1">
            {activeSymbols.slice(0, 5).map(symbol => (
              <Badge key={symbol} variant="outline" className="text-xs">
                {symbol}
              </Badge>
            ))}
            {activeSymbols.length > 5 && (
              <Badge variant="outline" className="text-xs">
                +{activeSymbols.length - 5} more
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* Update counter */}
      {updateCount > 0 && (
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Updates received:</span>
          <span className="font-mono">{updateCount.toLocaleString()}</span>
        </div>
      )}
    </div>
  );
}