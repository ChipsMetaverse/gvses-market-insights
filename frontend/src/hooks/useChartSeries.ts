/**
 * useChartSeries - Hook for managing chart series lifecycle
 * Provides utilities for adding, updating, and removing indicator series
 */

import { useRef, useCallback } from 'react';
import { IChartApi, ISeriesApi, LineData, Time, SeriesType, LineSeries, HistogramSeries, AreaSeries } from 'lightweight-charts';
import { ChartDataPoint } from '../utils/indicatorDataFormatter';

export interface SeriesManager {
  chart: IChartApi | null;
  series: Map<string, ISeriesApi<SeriesType>>;
}

export interface SeriesConfig {
  type: 'line' | 'histogram' | 'area';
  color?: string;
  lineWidth?: number;
  priceScaleId?: 'left' | 'right';
  visible?: boolean;
  title?: string;
}

export function useChartSeries(chart: IChartApi | null) {
  const seriesMapRef = useRef<Map<string, ISeriesApi<SeriesType>>>(new Map());
  
  /**
   * Add or update a line series on the chart
   */
  const addOrUpdateSeries = useCallback((
    id: string,
    data: ChartDataPoint[],
    config: SeriesConfig = { type: 'line' }
  ): ISeriesApi<SeriesType> | null => {
    if (!chart) return null;
    
    let series = seriesMapRef.current.get(id);
    
    // Create new series if it doesn't exist
    if (!series) {
      const seriesOptions: any = {
        color: config.color || '#2962FF',
        lineWidth: config.lineWidth || 2,
        crosshairMarkerVisible: true,
        priceScaleId: config.priceScaleId || 'right',
        visible: config.visible !== false,
        title: config.title || id
      };
      
      // Create series based on type - Using v5 API with addSeries
      switch (config.type) {
        case 'histogram':
          series = chart.addSeries(HistogramSeries, {
            ...seriesOptions,
            priceFormat: {
              type: 'volume'
            }
          });
          break;
          
        case 'area':
          series = chart.addSeries(AreaSeries, {
            ...seriesOptions,
            lineWidth: config.lineWidth || 2,
            topColor: config.color ? `${config.color}33` : 'rgba(41, 98, 255, 0.2)',
            bottomColor: config.color ? `${config.color}05` : 'rgba(41, 98, 255, 0.05)'
          });
          break;
          
        case 'line':
        default:
          series = chart.addSeries(LineSeries, seriesOptions);
          break;
      }
      
      seriesMapRef.current.set(id, series);
    }
    
    // Update series data
    if (data && data.length > 0) {
      try {
        series.setData(data as LineData[]);
      } catch (error) {
        console.error(`Error updating series ${id}:`, error);
      }
    }
    
    return series;
  }, [chart]);
  
  /**
   * Remove a series from the chart
   */
  const removeSeries = useCallback((id: string): boolean => {
    if (!chart) return false;
    
    const series = seriesMapRef.current.get(id);
    if (!series) return false;
    
    try {
      chart.removeSeries(series);
      seriesMapRef.current.delete(id);
      return true;
    } catch (error) {
      console.error(`Error removing series ${id}:`, error);
      return false;
    }
  }, [chart]);
  
  /**
   * Update series visibility
   */
  const setSeriesVisibility = useCallback((id: string, visible: boolean): void => {
    const series = seriesMapRef.current.get(id);
    if (!series) return;
    
    series.applyOptions({ visible });
  }, []);
  
  /**
   * Update series color
   */
  const setSeriesColor = useCallback((id: string, color: string): void => {
    const series = seriesMapRef.current.get(id);
    if (!series) return;
    
    series.applyOptions({ color });
  }, []);
  
  /**
   * Get a specific series by ID
   */
  const getSeries = useCallback((id: string): ISeriesApi<SeriesType> | undefined => {
    return seriesMapRef.current.get(id);
  }, []);
  
  /**
   * Remove all series
   */
  const removeAllSeries = useCallback((): void => {
    if (!chart) return;
    
    seriesMapRef.current.forEach((series, id) => {
      try {
        chart.removeSeries(series);
      } catch (error) {
        console.error(`Error removing series ${id}:`, error);
      }
    });
    
    seriesMapRef.current.clear();
  }, [chart]);
  
  /**
   * Batch update multiple series
   */
  const batchUpdateSeries = useCallback((
    updates: Array<{ id: string; data: ChartDataPoint[]; config?: SeriesConfig }>
  ): void => {
    updates.forEach(({ id, data, config }) => {
      addOrUpdateSeries(id, data, config);
    });
  }, [addOrUpdateSeries]);
  
  /**
   * Add price lines (for support/resistance, fibonacci levels)
   */
  const addPriceLine = useCallback((
    seriesId: string,
    price: number,
    options: {
      color?: string;
      lineWidth?: number;
      lineStyle?: number;
      title?: string;
      axisLabelVisible?: boolean;
    } = {}
  ): any => {
    const series = seriesMapRef.current.get(seriesId);
    if (!series) return null;
    
    return series.createPriceLine({
      price,
      color: options.color || 'rgba(128, 128, 128, 0.5)',
      lineWidth: options.lineWidth || 1,
      lineStyle: options.lineStyle || 2, // Dashed
      axisLabelVisible: options.axisLabelVisible !== false,
      title: options.title || ''
    });
  }, []);
  
  /**
   * Get all active series IDs
   */
  const getActiveSeriesIds = useCallback((): string[] => {
    return Array.from(seriesMapRef.current.keys());
  }, []);
  
  /**
   * Check if a series exists
   */
  const hasSeries = useCallback((id: string): boolean => {
    return seriesMapRef.current.has(id);
  }, []);
  
  return {
    // Core functions
    addOrUpdateSeries,
    removeSeries,
    removeAllSeries,
    
    // Series management
    getSeries,
    hasSeries,
    getActiveSeriesIds,
    
    // Updates
    setSeriesVisibility,
    setSeriesColor,
    batchUpdateSeries,
    
    // Price lines
    addPriceLine,
    
    // Direct access to series map (use carefully)
    seriesMap: seriesMapRef.current
  };
}