/**
 * useIndicatorState - Main hook for managing technical indicator data and state
 * Provides interface for fetching, caching, and updating indicator configurations
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useIndicatorContext, useCachedIndicatorData } from '../contexts/IndicatorContext';
import { IndicatorDataFormatter, IndicatorApiResponse } from '../utils/indicatorDataFormatter';
import axios from 'axios';
import { useDebounce } from './useDebounce';
import { getApiUrl } from '../utils/apiConfig';

const API_URL = getApiUrl();

export interface UseIndicatorStateOptions {
  autoFetch?: boolean;
  debounceMs?: number;
  cacheEnabled?: boolean;
}

export interface IndicatorDataState {
  data: any | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useIndicatorState(options: UseIndicatorStateOptions = {}) {
  const {
    autoFetch = true,
    debounceMs = 300,
    cacheEnabled = true
  } = options;
  
  const { state, dispatch } = useIndicatorContext();
  const abortControllerRef = useRef<AbortController | null>(null);
  const [dataState, setDataState] = useState<IndicatorDataState>({
    data: null,
    loading: false,
    error: null,
    lastUpdated: null
  });
  
  // Debounce symbol changes to avoid excessive API calls
  const debouncedSymbol = useDebounce(state.symbol, debounceMs);
  
  // Generate cache key for current state
  const getCacheKey = useCallback(() => {
    const enabledIndicators = Object.entries(state.indicators)
      .filter(([_, config]) => {
        if ('enabled' in config) return config.enabled;
        // Handle moving averages separately
        if ('ma20' in config) {
          return config.ma20.enabled || config.ma50.enabled || config.ma200.enabled;
        }
        return false;
      })
      .map(([name]) => name)
      .join('-');
    
    return `${state.symbol}-${state.timeframe}-${enabledIndicators}`;
  }, [state.symbol, state.timeframe, state.indicators]);
  
  // Check cache for existing data
  const cachedData = useCachedIndicatorData(getCacheKey());
  
  // Fetch indicator data from API
  const fetchIndicatorData = useCallback(async (signal?: AbortSignal) => {
    // Build list of enabled indicators
    const requestedIndicators: string[] = [];
    
    // Check moving averages
    const { movingAverages } = state.indicators;
    if (movingAverages.ma20.enabled || movingAverages.ma50.enabled || movingAverages.ma200.enabled) {
      requestedIndicators.push('moving_averages');
    }
    
    // Check other indicators
    if (state.indicators.bollingerBands.enabled) {
      requestedIndicators.push('bollinger');
    }
    if (state.indicators.rsi.enabled) {
      requestedIndicators.push('rsi');
    }
    if (state.indicators.macd.enabled) {
      requestedIndicators.push('macd');
    }
    if (state.indicators.fibonacci.enabled) {
      requestedIndicators.push('fibonacci');
    }
    if (state.indicators.supportResistance.enabled) {
      requestedIndicators.push('support_resistance');
    }
    
    // Skip if no indicators enabled
    if (requestedIndicators.length === 0) {
      setDataState({
        data: null,
        loading: false,
        error: null,
        lastUpdated: null
      });
      return null;
    }
    
    // Set loading state
    dispatch({ type: 'SET_LOADING', payload: { indicator: 'all', loading: true } });
    setDataState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await axios.get<IndicatorApiResponse>(
        `${API_URL}/api/technical-indicators`,
        {
          params: {
            symbol: state.symbol,
            indicators: requestedIndicators.join(','),
            // Map timeframe to days for API
            days: timeframeToDays(state.timeframe)
          },
          signal
        }
      );
      
      // Format the response data
      const formattedData = IndicatorDataFormatter.formatIndicatorResponse(response.data);
      
      // Cache the data if caching is enabled
      if (cacheEnabled) {
        const cacheKey = getCacheKey();
        dispatch({
          type: 'SET_INDICATOR_DATA',
          payload: {
            key: cacheKey,
            data: formattedData,
            ttl: 30000 // 30 seconds TTL
          }
        });
      }
      
      setDataState({
        data: formattedData,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
      
      dispatch({ type: 'SET_LOADING', payload: { indicator: 'all', loading: false } });
      return formattedData;
      
    } catch (error: any) {
      const isCanceled = axios.isCancel(error) || error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError' || error?.name === 'AbortError';

      dispatch({ type: 'SET_LOADING', payload: { indicator: 'all', loading: false } });

      if (isCanceled) {
        setDataState(prev => ({
          ...prev,
          loading: false
        }));
        return null;
      }

      const errorMessage = axios.isAxiosError(error)
        ? error.message
        : 'Failed to fetch indicator data';
      
      dispatch({ type: 'SET_ERROR', payload: { indicator: 'all', error: errorMessage } });
      setDataState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
      
      throw error;
    }
  }, [state.symbol, state.timeframe, state.indicators, dispatch, cacheEnabled, getCacheKey]);
  
  // Refetch data (bypasses cache)
  const refetch = useCallback(async () => {
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    try {
      return await fetchIndicatorData(abortControllerRef.current.signal);
    } catch (error: any) {
      const isCanceled = axios.isCancel(error) || error?.name === 'AbortError' || error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED';
      if (!isCanceled) {
        console.error('Failed to refetch indicator data:', error);
      }
      return null;
    }
  }, [fetchIndicatorData]);
  
  // Toggle indicator visibility
  const toggleIndicator = useCallback((indicator: string, subIndicator?: string) => {
    dispatch({ type: 'TOGGLE_INDICATOR', payload: { indicator, subIndicator } });
  }, [dispatch]);
  
  // Update indicator configuration
  const updateIndicatorConfig = useCallback((indicator: string, config: any) => {
    dispatch({ type: 'UPDATE_INDICATOR_CONFIG', payload: { indicator, config } });
  }, [dispatch]);
  
  // Set oscillator pane visibility and type
  const setOscillatorPane = useCallback((show: boolean, type?: 'rsi' | 'macd' | 'stochastic') => {
    dispatch({ type: 'SET_OSCILLATOR_PANE', payload: { show, type } });
  }, [dispatch]);
  
  // Clear all cache
  const clearCache = useCallback(() => {
    dispatch({ type: 'CLEAR_CACHE' });
  }, [dispatch]);
  
  // Reset to default settings
  const resetToDefaults = useCallback(() => {
    dispatch({ type: 'RESET_TO_DEFAULTS' });
  }, [dispatch]);
  
  // Auto-fetch on symbol/timeframe/indicator changes
  useEffect(() => {
    if (!autoFetch) return;
    
    // Use cached data if available
    if (cachedData && cacheEnabled) {
      setDataState({
        data: cachedData,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
      return;
    }
    
    // Fetch fresh data
    const controller = new AbortController();
    abortControllerRef.current = controller;
    
    fetchIndicatorData(controller.signal).catch((error: any) => {
      const isCanceled = axios.isCancel(error) || error?.name === 'AbortError' || error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED';
      if (!isCanceled) {
        console.error('Auto-fetch failed:', error);
      }
    });
    
    return () => {
      controller.abort();
    };
  }, [debouncedSymbol, state.timeframe, state.indicators, autoFetch, cacheEnabled, cachedData, fetchIndicatorData]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  return {
    // State
    state: {
      ...dataState,
      symbol: state.symbol,
      timeframe: state.timeframe,
      indicators: state.indicators,
      ui: state.ui,
      isOscillatorVisible: state.ui.showOscillatorPane,
      selectedOscillator: state.ui.selectedOscillator
    },
    
    // Actions
    actions: {
      refetch,
      toggleIndicator,
      updateIndicatorConfig,
      setOscillatorPane,
      clearCache,
      resetToDefaults,
      setSymbol: (symbol: string) => dispatch({ type: 'SET_SYMBOL', payload: symbol }),
      setTimeframe: (timeframe: string) => dispatch({ type: 'SET_TIMEFRAME', payload: timeframe }),
      setAutoRefresh: (enabled: boolean) => dispatch({ type: 'SET_AUTO_REFRESH', payload: enabled }),
      setRefreshInterval: (ms: number) => dispatch({ type: 'SET_REFRESH_INTERVAL', payload: ms })
    }
  };
}

// Helper function to convert timeframe to days
function timeframeToDays(timeframe: string): number {
  const map: { [key: string]: number } = {
    // Intraday - request sufficient data for technical indicators (minimum 200 days for MA200)
    '10S': 200, '30S': 200, '1m': 200, '3m': 200, '5m': 200,
    '10m': 200, '15m': 200, '30m': 200,
    // Hours - request 200 days for indicators
    '1H': 200, '2H': 200, '3H': 200, '4H': 200, '6H': 200, '8H': 200, '12H': 200,
    // Days - request sufficient data for indicators (minimum 200 for MA200)
    '1D': 200, '2D': 200, '3D': 200, '5D': 200, '1W': 200,
    // Months
    '1M': 200, '3M': 200, '6M': 200,
    // Years - Multi-year support
    '1Y': 365, '2Y': 730, '3Y': 1095, '5Y': 1825,
    // Special
    'YTD': Math.max(200, Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 1).getTime()) / (1000 * 60 * 60 * 24))),
    'MAX': 3650 // 10 years
  };
  return map[timeframe] || 200;
}

