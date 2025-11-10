/**
 * API Configuration Utilities
 * Standardized API URL handling across the application
 */

const DEFAULT_FALLBACK_URL = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';
const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', 'host.docker.internal']);

const normalizeUrlForEnvironment = (url: string | null | undefined): string | null => {
  if (!url) {
    return null;
  }

  if (typeof window === 'undefined') {
    return url;
  }

  try {
    const win = window as ApiWindow;
    const { hostname, protocol } = win.location;

    if (!hostname) {
      return url;
    }

    const parsed = new URL(url);

    // Align protocol with current origin when possible
    if (protocol === 'https:' && parsed.protocol !== 'https:') {
      parsed.protocol = 'https:';
    }

    // When running behind Docker desktop, replace localhost with host.docker.internal
    if (hostname === 'host.docker.internal' && LOCAL_HOSTS.has(parsed.hostname)) {
      parsed.hostname = hostname;
    }

    return parsed.toString().replace(/\/$/, '');
  } catch (error) {
    console.warn('Failed to normalize API URL for environment', error);
    return url;
  }
};

type ApiResolver = () => string;

type ApiGlobal = typeof globalThis & {
  __API_URL__?: string;
  __apiUrlResolver__?: ApiResolver;
  getApiUrl?: ApiResolver;
};

type ApiWindow = Window & {
  __API_URL__?: string;
  getApiUrl?: ApiResolver;
};

const globalScope = globalThis as ApiGlobal;

const persistUrl = (url: string): string => {
  if (!url) {
    return DEFAULT_FALLBACK_URL;
  }

  const normalized = normalizeUrlForEnvironment(url) ?? url;

  globalScope.__API_URL__ = normalized;

  if (typeof window !== 'undefined') {
    const win = window as ApiWindow;
    win.__API_URL__ = normalized;
    if (typeof win.getApiUrl !== 'function') {
      win.getApiUrl = getApiUrl;
    }
  }

  if (typeof globalScope.getApiUrl !== 'function') {
    globalScope.getApiUrl = getApiUrl;
  }

  return normalized;
};

const tryEnvApiUrl = (): string | null => {
  try {
    const value = (import.meta as any)?.env?.VITE_API_URL;
    if (typeof value === 'string' && value.length > 0) {
      return normalizeUrlForEnvironment(value) ?? value;
    }
    return null;
  } catch (error) {
    console.warn('Unable to read VITE_API_URL from import.meta', error);
    return null;
  }
};

const tryCustomResolver = (): string | null => {
  const candidates: Array<ApiResolver | string | undefined> = [];

  if (typeof globalScope.__apiUrlResolver__ === 'function') {
    candidates.push(globalScope.__apiUrlResolver__);
  }

  if (typeof window !== 'undefined') {
    const win = window as ApiWindow;
    if (typeof win.getApiUrl === 'function' && win.getApiUrl !== getApiUrl) {
      candidates.push(win.getApiUrl);
    }
    if (typeof win.__API_URL__ === 'string') {
      candidates.push(win.__API_URL__);
    }
  }

  if (typeof globalScope.getApiUrl === 'function' && globalScope.getApiUrl !== getApiUrl) {
    candidates.push(globalScope.getApiUrl);
  }

  if (typeof globalScope.__API_URL__ === 'string') {
    candidates.push(globalScope.__API_URL__);
  }

  for (const resolver of candidates) {
    if (!resolver) continue;
    try {
      if (typeof resolver === 'string' && resolver.length > 0) {
        return resolver;
      }
      if (typeof resolver === 'function') {
        const value = resolver();
        if (typeof value === 'string' && value.length > 0) {
          return value;
        }
      }
    } catch (error) {
      console.warn('Custom API URL resolver failed', error);
    }
  }

  return null;
};

const tryLocationApiUrl = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }

  const win = window as ApiWindow;
  const { protocol, hostname, port } = win.location;

  const normalizedProtocol = protocol === 'https:' ? 'https:' : 'http:';

  if (LOCAL_HOSTS.has(hostname)) {
    return `${normalizedProtocol}//${hostname}:8000`;
  }

  // Production: separate frontend and backend apps
  if (hostname === 'gvses-market-insights.fly.dev') {
    return 'https://gvses-market-insights-api.fly.dev';
  }

  const inferredPort = port ? `:${port}` : '';
  return `${normalizedProtocol}//${hostname}${inferredPort}`;
};

/**
 * Get the base API URL for backend services
 * Prioritizes environment variables, global overrides, then window location.
 */
export function getApiUrl(): string {
  try {
    const envUrl = tryEnvApiUrl();
    if (envUrl) {
      return persistUrl(envUrl);
    }

    const customUrl = tryCustomResolver();
    if (customUrl) {
      return persistUrl(customUrl);
    }

    const locationUrl = tryLocationApiUrl();
    if (locationUrl) {
      return persistUrl(locationUrl);
    }
  } catch (error) {
    console.error('Failed to resolve API URL, falling back to default', error);
  }

  return persistUrl(DEFAULT_FALLBACK_URL);
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

export default getApiUrl;
