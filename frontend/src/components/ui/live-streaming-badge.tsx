// Live Streaming Badge - Compact indicator for real-time data status
// Shows connection state and update frequency

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { Activity, CircleDot } from 'lucide-react';
import { streamingDataService } from '@/services/streamingDataService.browser';

export interface LiveStreamingBadgeProps {
  className?: string;
}

export function LiveStreamingBadge({ className }: LiveStreamingBadgeProps) {
  const [isLive, setIsLive] = useState(false);
  const [updateCount, setUpdateCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    let updateTimer: number;

    const handleUpdate = () => {
      setIsLive(true);
      setUpdateCount(prev => prev + 1);
      setLastUpdate(new Date());
      
      // Reset live indicator after 5 seconds of no updates
      if (updateTimer) clearTimeout(updateTimer);
      updateTimer = setTimeout(() => {
        setIsLive(false);
      }, 5000);
    };

    const handleConnect = () => {
      setIsLive(true);
    };

    const handleDisconnect = () => {
      setIsLive(false);
      if (updateTimer) clearTimeout(updateTimer);
    };

    // Subscribe to events
    streamingDataService.on('priceUpdate', handleUpdate);
    streamingDataService.on('providerConnected', handleConnect);
    streamingDataService.on('providerDisconnected', handleDisconnect);

    // Check initial status
    const status = streamingDataService.getStatus();
    setIsLive(status.some(s => s.connected));

    return () => {
      streamingDataService.off('priceUpdate', handleUpdate);
      streamingDataService.off('providerConnected', handleConnect);
      streamingDataService.off('providerDisconnected', handleDisconnect);
      if (updateTimer) clearTimeout(updateTimer);
    };
  }, []);

  if (!isLive && updateCount === 0) {
    return null; // Don't show anything if never connected
  }

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium transition-all",
        isLive
          ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400"
          : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
        className
      )}
    >
      {isLive ? (
        <>
          <CircleDot className="h-3 w-3 animate-pulse" />
          <span>LIVE</span>
        </>
      ) : (
        <>
          <Activity className="h-3 w-3" />
          <span>OFFLINE</span>
        </>
      )}
    </div>
  );
}