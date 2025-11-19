import React, { useState } from 'react';
import {
  Maximize2,
  X,
  BarChart3,
  TrendingUp,
  Image,
  Edit3,
  Minus,
  Move,
  Trash2,
} from 'lucide-react';
import { TradingChart } from '../TradingChart';
import type { Tool } from '../../drawings/ToolboxManager';

interface TradingChartDisplayWidgetProps {
  symbol?: string;
  currentPrice?: number;
  priceChange?: number;
  percentChange?: number;
  onClose?: () => void;
  onAction?: (action: WidgetAction) => void;
}

type Timeframe = '1D' | '5D' | '1M' | '3M' | '6M' | '1Y' | '5Y' | 'All';
type ChartType = 'candlestick' | 'line' | 'area';
type Indicator = 'volume' | 'sma' | 'ema' | 'rsi' | 'macd';

type WidgetAction =
  | { type: 'chart.setTimeframe'; payload: { value: Timeframe } }
  | { type: 'chart.setType'; payload: { value: ChartType } }
  | { type: 'chart.activateDrawingTool'; payload: { value: Tool } }
  | { type: 'chart.clearDrawings' }
  | { type: 'chart.toggleIndicator'; payload: { name: Indicator } }
  | { type: 'chart.fullscreen' }
  | { type: 'chart.close' };

const TIMEFRAME_OPTIONS: Timeframe[] = ['1D', '5D', '1M', '3M', '6M', '1Y', '5Y', 'All'];

// Helper functions for timeframe conversion
const timeframeToDays = (timeframe: Timeframe): number => {
  const map: Record<Timeframe, number> = {
    '1D': 1,
    '5D': 5,
    '1M': 30,
    '3M': 90,
    '6M': 180,
    '1Y': 365,
    '5Y': 1825,
    'All': 3650,
  };
  return map[timeframe] || 90;
};

const timeframeToInterval = (timeframe: Timeframe): string => {
  const map: Record<Timeframe, string> = {
    '1D': '15m',
    '5D': '30m',
    '1M': '1h',
    '3M': '1d',
    '6M': '1d',
    '1Y': '1d',
    '5Y': '1wk',
    'All': '1wk',
  };
  return map[timeframe] || '1d';
};

export function TradingChartDisplayWidget({
  symbol = 'TSLA',
  currentPrice = 242.84,
  priceChange = 12.5,
  percentChange = 4.23,
  onClose,
  onAction,
}: TradingChartDisplayWidgetProps) {
  const [timeframe, setTimeframe] = useState<Timeframe>('3M'); // Default to 3 months as requested
  const [chartType, setChartType] = useState<ChartType>('candlestick');
  const [activeDrawingTool, setActiveDrawingTool] = useState<Tool>('none');
  const [indicators, setIndicators] = useState<Record<Indicator, boolean>>({
    volume: true,
    sma: false,
    ema: false,
    rsi: false,
    macd: false,
  });

  const isPositive = priceChange >= 0;

  const handleTimeframeChange = (tf: Timeframe) => {
    setTimeframe(tf);
    onAction?.({
      type: 'chart.setTimeframe',
      payload: { value: tf },
    });
  };

  const handleChartTypeChange = (type: ChartType) => {
    setChartType(type);
    onAction?.({
      type: 'chart.setType',
      payload: { value: type },
    });
  };

  const handleDrawingToolActivate = (tool: Tool) => {
    setActiveDrawingTool(tool);
    onAction?.({
      type: 'chart.activateDrawingTool',
      payload: { value: tool },
    });
  };

  const handleClearDrawings = () => {
    onAction?.({ type: 'chart.clearDrawings' });
  };

  const handleIndicatorToggle = (indicator: Indicator) => {
    setIndicators((prev) => {
      const newIndicators = { ...prev, [indicator]: !prev[indicator] };
      onAction?.({
        type: 'chart.toggleIndicator',
        payload: { name: indicator },
      });
      return newIndicators;
    });
  };

  const handleFullscreen = () => {
    onAction?.({ type: 'chart.fullscreen' });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 border-b">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-blue-600 bg-blue-100 px-3 py-1.5 rounded-lg">
              {symbol}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-3xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              ${currentPrice.toFixed(2)}
            </span>
            <span className={`text-lg font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}
              {priceChange.toFixed(2)} ({isPositive ? '+' : ''}
              {percentChange.toFixed(2)}%)
            </span>
          </div>
          <div className="flex-1" />
          <button
            onClick={handleFullscreen}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Fullscreen"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Chart Controls */}
        <div className="flex items-center gap-4 px-4 py-3 border-b bg-gray-50 overflow-x-auto">
          {/* Timeframe Buttons */}
          <div className="flex gap-1">
            {TIMEFRAME_OPTIONS.map((tf) => (
              <button
                key={tf}
                onClick={() => handleTimeframeChange(tf)}
                className={`px-3 py-1.5 text-sm font-medium rounded-full transition-all ${
                  timeframe === tf
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <div className="h-6 w-px bg-gray-300" />

          {/* Drawing Tools */}
          <div className="flex gap-1">
            <button
              onClick={() => handleDrawingToolActivate('trendline')}
              className={`p-2 rounded-lg transition-colors ${
                activeDrawingTool === 'trendline'
                  ? 'bg-blue-100 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
              aria-label="Trendline"
              title="Trendline (Alt+T)"
            >
              <TrendingUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDrawingToolActivate('ray')}
              className={`p-2 rounded-lg transition-colors ${
                activeDrawingTool === 'ray' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
              }`}
              aria-label="Ray"
              title="Ray (Alt+R)"
            >
              <Move className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDrawingToolActivate('horizontal')}
              className={`p-2 rounded-lg transition-colors ${
                activeDrawingTool === 'horizontal'
                  ? 'bg-blue-100 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
              aria-label="Horizontal line"
              title="Horizontal (Alt+H)"
            >
              <Minus className="w-4 h-4" />
            </button>
            <button
              onClick={handleClearDrawings}
              className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Clear All Drawings"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>

          <div className="h-6 w-px bg-gray-300" />

          {/* Chart Type Buttons */}
          <div className="flex gap-1">
            <button
              onClick={() => handleChartTypeChange('candlestick')}
              className={`px-3 py-1.5 text-sm font-medium rounded-full flex items-center gap-1.5 transition-all ${
                chartType === 'candlestick'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Candle
            </button>
            <button
              onClick={() => handleChartTypeChange('line')}
              className={`px-3 py-1.5 text-sm font-medium rounded-full flex items-center gap-1.5 transition-all ${
                chartType === 'line'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              Line
            </button>
            <button
              onClick={() => handleChartTypeChange('area')}
              className={`px-3 py-1.5 text-sm font-medium rounded-full flex items-center gap-1.5 transition-all ${
                chartType === 'area'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              <Image className="w-4 h-4" />
              Area
            </button>
          </div>
        </div>

        {/* Chart Display Area */}
        <div className="flex-1 relative min-h-[400px] bg-gray-50">
          <TradingChart
            symbol={symbol}
            days={timeframeToDays(timeframe)}
            displayDays={timeframeToDays(timeframe)}
            interval={timeframeToInterval(timeframe)}
            onChartReady={(chart: any) => {
              // Chart ready with trendline support
              console.log('Widget chart ready with trendlines');
            }}
          />
        </div>

        {/* Indicator Toggles */}
        <div className="px-4 py-3 border-t bg-gray-50">
          <div className="flex gap-2">
            {(Object.keys(indicators) as Indicator[]).map((indicator) => (
              <button
                key={indicator}
                onClick={() => handleIndicatorToggle(indicator)}
                className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                  indicators[indicator]
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {indicator.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
