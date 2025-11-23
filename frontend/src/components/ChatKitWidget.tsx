import { useEffect, useState } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { API_BASE_URL } from '../utils/apiConfig';

/**
 * ChatKit Widget Component
 *
 * Integrates OpenAI ChatKit with G'sves agent for visual widget rendering.
 * Replaces raw JSON responses with rendered market widgets (charts, news, calendars, etc.)
 */
export function ChatKitWidget() {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        try {
          // Reuse existing session if available
          if (existing) {
            return existing;
          }

          // Create new ChatKit session
          const response = await fetch(`${API_BASE_URL}/api/chatkit/session`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              user_id: `user_${Date.now()}`,
              device_id: `device_${Date.now()}`
            })
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Session creation failed: ${response.status}`);
          }

          const data = await response.json();
          setIsLoading(false);
          return data.client_secret;

        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to create ChatKit session';
          console.error('ChatKit session error:', errorMessage);
          setError(errorMessage);
          setIsLoading(false);
          throw err;
        }
      }
    }
  });

  useEffect(() => {
    // Log when component mounts
    console.log('ChatKitWidget mounted - initializing session...');
  }, []);

  if (error) {
    return (
      <div className="chatkit-error-container p-4 border border-red-300 rounded-lg bg-red-50">
        <h3 className="text-red-700 font-semibold mb-2">ChatKit Error</h3>
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="chatkit-loading-container p-4 border border-gray-300 rounded-lg bg-gray-50">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Initializing ChatKit...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="chatkit-container">
      <ChatKit
        control={control}
        className="h-[600px] w-full rounded-lg shadow-lg border border-gray-200"
      />
    </div>
  );
}

export default ChatKitWidget;
