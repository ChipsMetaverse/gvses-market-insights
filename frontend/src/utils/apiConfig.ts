/**
 * API Configuration Utilities
 * Standardized API URL handling across the application
 */

/**
 * Get the base API URL for backend services
 * Prioritizes VITE_API_URL environment variable, then falls back to
 * window.location with proper port detection for localhost
 */
export function getApiUrl(): string {
  // First check for environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Build from window.location
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  const host = window.location.hostname;
  
  // Add :8000 for localhost AND 127.0.0.1
  const port = (host === 'localhost' || host === '127.0.0.1') ? ':8000' : '';
  
  return `${protocol}//${host}${port}`;
}

/**
 * Get WebSocket URL for real-time connections
 * Converts HTTP to WS protocol while maintaining the same host/port
 */
export function getWebSocketUrl(): string {
  const apiUrl = getApiUrl();
  return apiUrl.replace(/^http/, 'ws');
}

/**
 * Check if the API is healthy
 * @returns Promise<boolean> true if API is healthy, false otherwise
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${getApiUrl()}/health`);
    if (response.ok) {
      const data = await response.json();
      return data.status === 'healthy' || data.openai_relay_operational === true;
    }
    return false;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
}

/**
 * Get health status for specific services
 * @returns Promise with detailed health information
 */
export async function getDetailedHealth(): Promise<{
  apiHealthy: boolean;
  openaiRelayOperational: boolean;
  agentAvailable: boolean;
  marketDataAvailable: boolean;
}> {
  try {
    const response = await fetch(`${getApiUrl()}/health`);
    if (response.ok) {
      const data = await response.json();
      return {
        apiHealthy: data.status === 'healthy',
        openaiRelayOperational: data.openai_relay_operational === true,
        agentAvailable: data.agent_available !== false,
        marketDataAvailable: data.market_data_available !== false
      };
    }
    return {
      apiHealthy: false,
      openaiRelayOperational: false,
      agentAvailable: false,
      marketDataAvailable: false
    };
  } catch (error) {
    console.error('Detailed health check failed:', error);
    return {
      apiHealthy: false,
      openaiRelayOperational: false,
      agentAvailable: false,
      marketDataAvailable: false
    };
  }
}