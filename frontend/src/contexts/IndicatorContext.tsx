/**
 * IndicatorContext - Centralized state management for technical indicators
 * Manages indicator configurations, visibility, and data caching
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { ChartDataPoint } from '../utils/indicatorDataFormatter';

// Indicator configuration types
export interface IndicatorConfig {
  enabled: boolean;
  period?: number;
  color?: string;
  lineWidth?: number;
  showInMainChart?: boolean;
  showInOscillator?: boolean;
}

export interface MovingAveragesConfig {
  ma20: IndicatorConfig;
  ma50: IndicatorConfig;
  ma200: IndicatorConfig;
}

export interface BollingerBandsConfig extends IndicatorConfig {
  standardDeviations?: number;
}

export interface RSIConfig extends IndicatorConfig {
  overbought?: number;
  oversold?: number;
}

export interface MACDConfig extends IndicatorConfig {
  fastPeriod?: number;
  slowPeriod?: number;
  signalPeriod?: number;
}

export interface FibonacciConfig extends IndicatorConfig {
  levels?: number[];
  autoDetectSwings?: boolean;
}

export interface SupportResistanceConfig extends IndicatorConfig {
  sensitivity?: number;
  maxLevels?: number;
}

// Main state interface
export interface IndicatorState {
  // Current symbol and timeframe
  symbol: string;
  timeframe: string;
  
  // Indicator configurations
  indicators: {
    movingAverages: MovingAveragesConfig;
    bollingerBands: BollingerBandsConfig;
    rsi: RSIConfig;
    macd: MACDConfig;
    fibonacci: FibonacciConfig;
    supportResistance: SupportResistanceConfig;
  };
  
  // Cached indicator data
  cache: {
    [key: string]: {
      data: any;
      timestamp: number;
      ttl: number;
    };
  };
  
  // UI state
  ui: {
    showOscillatorPane: boolean;
    selectedOscillator: 'rsi' | 'macd' | 'stochastic' | null;
    isPanelCollapsed: boolean;
    autoRefresh: boolean;
    refreshInterval: number; // milliseconds
  };
  
  // Loading states
  loading: {
    [indicatorType: string]: boolean;
  };
  
  // Error states
  errors: {
    [indicatorType: string]: string | null;
  };
}

// Action types
export type IndicatorAction =
  | { type: 'SET_SYMBOL'; payload: string }
  | { type: 'SET_TIMEFRAME'; payload: string }
  | { type: 'TOGGLE_INDICATOR'; payload: { indicator: string; subIndicator?: string } }
  | { type: 'UPDATE_INDICATOR_CONFIG'; payload: { indicator: string; config: Partial<IndicatorConfig> } }
  | { type: 'SET_INDICATOR_DATA'; payload: { key: string; data: any; ttl?: number } }
  | { type: 'CLEAR_CACHE'; payload?: string }
  | { type: 'SET_OSCILLATOR_PANE'; payload: { show: boolean; type?: 'rsi' | 'macd' | 'stochastic' } }
  | { type: 'SET_AUTO_REFRESH'; payload: boolean }
  | { type: 'SET_REFRESH_INTERVAL'; payload: number }
  | { type: 'SET_LOADING'; payload: { indicator: string; loading: boolean } }
  | { type: 'SET_ERROR'; payload: { indicator: string; error: string | null } }
  | { type: 'BATCH_UPDATE'; payload: Partial<IndicatorState> }
  | { type: 'RESET_TO_DEFAULTS' }
  | { type: 'HYDRATE_FROM_STORAGE'; payload: Partial<IndicatorState> };

// Default state
const defaultState: IndicatorState = {
  symbol: 'AAPL',
  timeframe: '1D',
  indicators: {
    movingAverages: {
      ma20: { enabled: true, color: '#2962FF', lineWidth: 2, showInMainChart: true },
      ma50: { enabled: false, color: '#FF6B35', lineWidth: 2, showInMainChart: true },
      ma200: { enabled: false, color: '#4CAF50', lineWidth: 2, showInMainChart: true }
    },
    bollingerBands: {
      enabled: false,
      period: 20,
      standardDeviations: 2,
      color: '#9C27B0',
      lineWidth: 1,
      showInMainChart: true
    },
    rsi: {
      enabled: false,
      period: 14,
      overbought: 70,
      oversold: 30,
      color: '#FF9800',
      showInOscillator: true
    },
    macd: {
      enabled: false,
      fastPeriod: 12,
      slowPeriod: 26,
      signalPeriod: 9,
      color: '#00BCD4',
      showInOscillator: true
    },
    fibonacci: {
      enabled: false,
      autoDetectSwings: true,
      showInMainChart: true
    },
    supportResistance: {
      enabled: false,
      sensitivity: 0.5,
      maxLevels: 5,
      showInMainChart: true
    }
  },
  cache: {},
  ui: {
    showOscillatorPane: false,
    selectedOscillator: null,
    isPanelCollapsed: false,
    autoRefresh: true,
    refreshInterval: 30000 // 30 seconds
  },
  loading: {},
  errors: {}
};

// Reducer
function indicatorReducer(state: IndicatorState, action: IndicatorAction): IndicatorState {
  switch (action.type) {
    case 'SET_SYMBOL':
      return {
        ...state,
        symbol: action.payload,
        cache: {} // Clear cache on symbol change
      };
      
    case 'SET_TIMEFRAME':
      return {
        ...state,
        timeframe: action.payload,
        cache: {} // Clear cache on timeframe change
      };
      
    case 'TOGGLE_INDICATOR': {
      const { indicator, subIndicator } = action.payload;
      
      if (subIndicator && indicator === 'movingAverages') {
        return {
          ...state,
          indicators: {
            ...state.indicators,
            movingAverages: {
              ...state.indicators.movingAverages,
              [subIndicator]: {
                ...state.indicators.movingAverages[subIndicator as keyof MovingAveragesConfig],
                enabled: !state.indicators.movingAverages[subIndicator as keyof MovingAveragesConfig].enabled
              }
            }
          }
        };
      }
      
      const indicatorConfig = state.indicators[indicator as keyof typeof state.indicators];
      if ('enabled' in indicatorConfig) {
        return {
          ...state,
          indicators: {
            ...state.indicators,
            [indicator]: {
              ...indicatorConfig,
              enabled: !indicatorConfig.enabled
            }
          }
        };
      }
      
      return state;
    }
    
    case 'UPDATE_INDICATOR_CONFIG': {
      const { indicator, config } = action.payload;
      return {
        ...state,
        indicators: {
          ...state.indicators,
          [indicator]: {
            ...state.indicators[indicator as keyof typeof state.indicators],
            ...config
          }
        }
      };
    }
    
    case 'SET_INDICATOR_DATA': {
      const { key, data, ttl = 30000 } = action.payload;
      return {
        ...state,
        cache: {
          ...state.cache,
          [key]: {
            data,
            timestamp: Date.now(),
            ttl
          }
        }
      };
    }
    
    case 'CLEAR_CACHE':
      if (action.payload) {
        const { [action.payload]: _, ...restCache } = state.cache;
        return { ...state, cache: restCache };
      }
      return { ...state, cache: {} };
      
    case 'SET_OSCILLATOR_PANE':
      return {
        ...state,
        ui: {
          ...state.ui,
          showOscillatorPane: action.payload.show,
          selectedOscillator: action.payload.type || state.ui.selectedOscillator
        }
      };
      
    case 'SET_AUTO_REFRESH':
      return {
        ...state,
        ui: {
          ...state.ui,
          autoRefresh: action.payload
        }
      };
      
    case 'SET_REFRESH_INTERVAL':
      return {
        ...state,
        ui: {
          ...state.ui,
          refreshInterval: action.payload
        }
      };
      
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.indicator]: action.payload.loading
        }
      };
      
    case 'SET_ERROR':
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.indicator]: action.payload.error
        }
      };
      
    case 'BATCH_UPDATE':
      return {
        ...state,
        ...action.payload
      };
      
    case 'RESET_TO_DEFAULTS':
      return defaultState;
      
    case 'HYDRATE_FROM_STORAGE':
      return {
        ...state,
        ...action.payload,
        cache: {}, // Don't restore cache from storage
        loading: {}, // Reset loading states
        errors: {} // Reset error states
      };
      
    default:
      return state;
  }
}

// Context
const IndicatorContext = createContext<{
  state: IndicatorState;
  dispatch: React.Dispatch<IndicatorAction>;
} | null>(null);

// Provider component
export function IndicatorProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(indicatorReducer, defaultState);
  
  // Persist state to localStorage
  useEffect(() => {
    const persistableState = {
      symbol: state.symbol,
      timeframe: state.timeframe,
      indicators: state.indicators,
      ui: state.ui
    };
    localStorage.setItem('indicatorSettings', JSON.stringify(persistableState));
  }, [state.symbol, state.timeframe, state.indicators, state.ui]);
  
  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('indicatorSettings');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        dispatch({ type: 'HYDRATE_FROM_STORAGE', payload: parsed });
      } catch (error) {
        console.error('Failed to hydrate indicator settings:', error);
      }
    }
  }, []);
  
  // Auto-refresh logic
  useEffect(() => {
    if (!state.ui.autoRefresh) return;
    
    const interval = setInterval(() => {
      // Clear stale cache entries
      const now = Date.now();
      const keysToRemove: string[] = [];
      
      Object.entries(state.cache).forEach(([key, entry]) => {
        if (now - entry.timestamp > entry.ttl) {
          keysToRemove.push(key);
        }
      });
      
      keysToRemove.forEach(key => {
        dispatch({ type: 'CLEAR_CACHE', payload: key });
      });
    }, state.ui.refreshInterval);
    
    return () => clearInterval(interval);
  }, [state.ui.autoRefresh, state.ui.refreshInterval, state.cache]);
  
  return (
    <IndicatorContext.Provider value={{ state, dispatch }}>
      {children}
    </IndicatorContext.Provider>
  );
}

// Hook to use the context
export function useIndicatorContext() {
  const context = useContext(IndicatorContext);
  if (!context) {
    throw new Error('useIndicatorContext must be used within an IndicatorProvider');
  }
  return context;
}

// Helper hook for cache management
export function useCachedIndicatorData(key: string) {
  const { state } = useIndicatorContext();
  const cached = state.cache[key];
  
  if (!cached) return null;
  
  const isStale = Date.now() - cached.timestamp > cached.ttl;
  return isStale ? null : cached.data;
}

// Helper hook for checking if indicator is enabled
export function useIsIndicatorEnabled(indicator: string, subIndicator?: string): boolean {
  const { state } = useIndicatorContext();
  
  if (subIndicator && indicator === 'movingAverages') {
    return state.indicators.movingAverages[subIndicator as keyof MovingAveragesConfig].enabled;
  }
  
  const indicatorConfig = state.indicators[indicator as keyof typeof state.indicators];
  return 'enabled' in indicatorConfig ? indicatorConfig.enabled : false;
}