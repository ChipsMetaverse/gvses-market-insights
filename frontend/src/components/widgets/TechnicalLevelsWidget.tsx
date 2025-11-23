import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, TrendingUp, TrendingDown, Target } from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';

interface TechnicalLevelsWidgetProps {
  symbol?: string;
  onClose?: () => void;
  onAction?: (action: WidgetAction) => void;
}

type WidgetAction =
  | { type: 'levels.refresh' }
  | { type: 'chart.highlightLevel'; payload: { level: 'sellHigh' | 'buyLow' | 'btd'; price: number } };

interface TechnicalLevels {
  sell_high_level: number;
  buy_low_level: number;
  btd_level: number;
}

export function TechnicalLevelsWidget({ symbol = 'TSLA', onClose, onAction }: TechnicalLevelsWidgetProps) {
  const [levels, setLevels] = useState<TechnicalLevels | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightedLevel, setHighlightedLevel] = useState<string | null>(null);

  const fetchLevels = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!opts?.silent) {
        setIsLoading(true);
      }
      setError(null);

      try {
        const response = await marketDataService.getTechnicalLevels(symbol);
        setLevels(response);

        // Notify parent of refresh action
        onAction?.({ type: 'levels.refresh' });
      } catch (err) {
        console.error('Failed to load technical levels', err);
        setError('Unable to load technical levels. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [symbol, onAction]
  );

  useEffect(() => {
    fetchLevels();
  }, [fetchLevels]);

  const handleLevelClick = (level: 'sellHigh' | 'buyLow' | 'btd', price: number) => {
    setHighlightedLevel(level);
    onAction?.({
      type: 'chart.highlightLevel',
      payload: { level, price },
    });

    // Clear highlight after 3 seconds
    setTimeout(() => setHighlightedLevel(null), 3000);
  };

  const handleRefresh = () => {
    fetchLevels({ silent: true });
  };

  const levelData = [
    {
      id: 'sellHigh' as const,
      label: 'Sell High',
      tooltip: 'Resistance level - Consider taking profits near this price',
      value: levels?.sell_high_level,
      icon: TrendingDown,
      color: 'red',
      bgColor: 'bg-red-500',
      textColor: 'text-red-600',
      borderColor: 'border-red-500',
      hoverBg: 'hover:bg-red-50',
      activeBg: 'bg-red-50',
    },
    {
      id: 'buyLow' as const,
      label: 'Buy Low',
      tooltip: 'Support level - Potential buying opportunity',
      value: levels?.buy_low_level,
      icon: TrendingUp,
      color: 'green',
      bgColor: 'bg-green-500',
      textColor: 'text-green-600',
      borderColor: 'border-green-500',
      hoverBg: 'hover:bg-green-50',
      activeBg: 'bg-green-50',
    },
    {
      id: 'btd' as const,
      label: 'BTD',
      tooltip: 'Buy The Dip - Aggressive entry level',
      value: levels?.btd_level,
      icon: Target,
      color: 'blue',
      bgColor: 'bg-blue-500',
      textColor: 'text-blue-600',
      borderColor: 'border-blue-500',
      hoverBg: 'hover:bg-blue-50',
      activeBg: 'bg-blue-50',
    },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900">Technical Levels</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded">
                {symbol}
              </span>
              <span className="text-sm text-gray-500">Support & Resistance analysis</span>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            aria-label="Refresh technical levels"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Levels List */}
        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {isLoading && !error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mb-4" />
              <p className="text-sm text-gray-600">Calculating technical levels…</p>
            </div>
          ) : (
            <div className="space-y-3">
              {levelData.map((levelInfo) => {
                const Icon = levelInfo.icon;
                const isHighlighted = highlightedLevel === levelInfo.id;

                return (
                  <button
                    key={levelInfo.id}
                    onClick={() =>
                      levelInfo.value && handleLevelClick(levelInfo.id, levelInfo.value)
                    }
                    disabled={!levelInfo.value}
                    className={`w-full flex items-center gap-4 p-4 rounded-lg border-2 transition-all ${
                      isHighlighted
                        ? `${levelInfo.borderColor} ${levelInfo.activeBg}`
                        : `border-gray-200 ${levelInfo.hoverBg}`
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                    title={levelInfo.tooltip}
                  >
                    {/* Color Indicator */}
                    <div className={`w-4 h-4 rounded-full ${levelInfo.bgColor} flex-shrink-0`} />

                    {/* Icon */}
                    <Icon className={`w-5 h-5 ${levelInfo.textColor} flex-shrink-0`} />

                    {/* Label */}
                    <div className="flex-1 text-left">
                      <div className="font-semibold text-gray-900">{levelInfo.label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{levelInfo.tooltip}</div>
                    </div>

                    {/* Price */}
                    <div className={`text-2xl font-bold ${levelInfo.textColor}`}>
                      {levelInfo.value ? `$${levelInfo.value.toFixed(2)}` : 'N/A'}
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Help Text */}
          {!isLoading && !error && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-900">
                <span className="font-semibold">💡 Tip:</span> Click any level to highlight it on the
                chart
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        {levels && (
          <div className="px-6 py-4 border-t bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>Based on 30-day price action</span>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>Live calculation</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
