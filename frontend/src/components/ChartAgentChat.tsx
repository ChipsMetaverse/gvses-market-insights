import React, { useState, useEffect } from 'react';

// Safely import ChatKit with error handling
let ChatKit: any = null;
let useChatKit: any = null;

try {
  const chatkitModule = require('@openai/chatkit-react');
  ChatKit = chatkitModule.ChatKit;
  useChatKit = chatkitModule.useChatKit;
} catch (error) {
  console.warn('ChatKit not available:', error);
}

interface ChartAgentChatProps {
  className?: string;
}

export function ChartAgentChat({ className = "h-[600px] w-[320px]" }: ChartAgentChatProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [control, setControl] = useState<any>(null);

  useEffect(() => {
    if (!ChatKit || !useChatKit) {
      setError('ChatKit library not available');
      setIsLoading(false);
      return;
    }

    try {
      // Initialize ChatKit
      const initializeChatKit = async () => {
        try {
          const { control: chatControl } = useChatKit({
            api: {
              async getClientSecret(existing) {
                // If we have an existing secret, try to refresh it
                if (existing) {
                  try {
                    const backendUrl = import.meta.env.VITE_API_URL || 'https://g-vses.fly.dev';
                    const res = await fetch(`${backendUrl}/api/chatkit/session`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        device_id: localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`
                      }),
                    });

                    if (!res.ok) {
                      throw new Error(`Session refresh failed: ${res.status}`);
                    }

                    const { client_secret } = await res.json();
                    return client_secret;
                  } catch (error) {
                    console.warn('Session refresh failed, creating new session:', error);
                    // Fall through to create new session
                  }
                }

                // Create a new session
                const deviceId = localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`;
                localStorage.setItem('chatkit_device_id', deviceId);

                try {
                  const backendUrl = import.meta.env.VITE_API_URL || 'https://g-vses.fly.dev';
                  const res = await fetch(`${backendUrl}/api/chatkit/session`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      device_id: deviceId
                    }),
                  });

                  if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error(`Session creation failed: ${res.status} - ${errorText}`);
                  }

                  const { client_secret } = await res.json();
                  console.log('ChatKit session created successfully');
                  return client_secret;
                } catch (error) {
                  console.error('Failed to create ChatKit session:', error);
                  throw error;
                }
              },
            },
          });

          setControl(chatControl);
          setIsLoading(false);
        } catch (err) {
          console.error('ChatKit initialization error:', err);
          setError(err instanceof Error ? err.message : 'Failed to initialize ChatKit');
          setIsLoading(false);
        }
      };

      // Only initialize if we have the required components
      if (useChatKit) {
        initializeChatKit();
      }
    } catch (err) {
      console.error('ChatKit setup error:', err);
      setError(err instanceof Error ? err.message : 'ChatKit setup failed');
      setIsLoading(false);
    }
  }, []);

  if (error) {
    return (
      <div className="chart-agent-chat">
        <div className="mb-2 text-sm font-medium text-red-600">
          Chart Control Assistant - Error
        </div>
        <div className="border rounded-lg p-4 bg-red-50 border-red-200">
          <p className="text-sm text-red-700">Failed to load ChatKit:</p>
          <p className="text-xs text-red-600 mt-1">{error}</p>
          <p className="text-xs text-gray-500 mt-2">
            The chart control agent will load once the ChatKit connection is established.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="chart-agent-chat">
        <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          Chart Control Assistant
        </div>
        <div className="border rounded-lg p-4 bg-gray-50">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Loading ChatKit...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-agent-chat">
      <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
        Chart Control Assistant
      </div>
      <div className="border rounded-lg overflow-hidden shadow-sm">
        {control && ChatKit ? (
          <ChatKit 
            control={control} 
            className={className}
            style={{
              colorScheme: 'light',
              backgroundColor: '#ffffff',
              fontFamily: 'system-ui, -apple-system, sans-serif'
            }}
          />
        ) : (
          <div className="p-4 bg-yellow-50 border-yellow-200">
            <p className="text-sm text-yellow-700">ChatKit control not available</p>
          </div>
        )}
      </div>
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        Try: "Change chart to AAPL", "Set timeframe to 1h", "Enable RSI indicator"
      </div>
    </div>
  );
}