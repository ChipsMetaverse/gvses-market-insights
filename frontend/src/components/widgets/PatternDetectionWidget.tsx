import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Eye, EyeOff, Activity } from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';

interface PatternDetectionWidgetProps {
  symbol?: string;
  onClose?: () => void;
  onAction?: (action: WidgetAction) => void;
}

type PatternCategory = 'Reversal' | 'Continuation' | 'Neutral';

type WidgetAction =
  | { type: 'patterns.refresh' }
  | { type: 'patterns.toggleVisibility'; payload: { patternId: string; visible: boolean } }
  | { type: 'patterns.filterCategory'; payload: { category: PatternCategory | 'all' } };

interface ChartPattern {
  id: string;
  name: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  category: PatternCategory;
  confidence: number;
  visible: boolean;
}

export function PatternDetectionWidget({
  symbol = 'TSLA',
  onClose,
  onAction,
}: PatternDetectionWidgetProps) {
  const [showAllPatterns, setShowAllPatterns] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<PatternCategory | 'all'>('all');
  const [patterns, setPatterns] = useState<ChartPattern[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!opts?.silent) {
        setIsLoading(true);
      }
      setError(null);

      try {
        const response = await marketDataService.getPatternDetection(symbol);

        // Transform API response to ChartPattern format
        const detectedPatterns: ChartPattern[] =
          response.patterns?.map((pattern: any, index: number) => ({
            id: pattern.id || `pattern-${index}`,
            name: pattern.name,
            signal: pattern.signal,
            category: pattern.category,
            confidence: pattern.confidence,
            visible: showAllPatterns,
          })) || [];

        setPatterns(detectedPatterns);

        // Notify parent of refresh action
        onAction?.({ type: 'patterns.refresh' });
      } catch (err) {
        console.error('Failed to load pattern detection', err);
        setError('Unable to load chart patterns. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [symbol, showAllPatterns, onAction]
  );

  useEffect(() => {
    fetchPatterns();
  }, [fetchPatterns]);

  const handleShowAllToggle = () => {
    const newShowAll = !showAllPatterns;
    setShowAllPatterns(newShowAll);

    // Update all patterns visibility
    setPatterns((prev) =>
      prev.map((pattern) => ({
        ...pattern,
        visible: newShowAll,
      }))
    );
  };

  const handlePatternToggle = (patternId: string) => {
    setPatterns((prev) =>
      prev.map((pattern) => {
        if (pattern.id === patternId) {
          const newVisible = !pattern.visible;
          onAction?.({
            type: 'patterns.toggleVisibility',
            payload: { patternId, visible: newVisible },
          });
          return { ...pattern, visible: newVisible };
        }
        return pattern;
      })
    );
  };

  const handleCategoryFilter = (category: PatternCategory | 'all') => {
    setSelectedCategory(category);
    onAction?.({
      type: 'patterns.filterCategory',
      payload: { category },
    });
  };

  const handleRefresh = () => {
    fetchPatterns({ silent: true });
  };

  const filteredPatterns =
    selectedCategory === 'all'
      ? patterns
      : patterns.filter((p) => p.category === selectedCategory);

  const getCategoryColor = (category: PatternCategory) => {
    switch (category) {
      case 'Reversal':
        return 'text-red-600 bg-red-100';
      case 'Continuation':
        return 'text-blue-600 bg-blue-100';
      case 'Neutral':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSignalColor = (signal: ChartPattern['signal']) => {
    switch (signal) {
      case 'BULLISH':
        return 'text-green-700 bg-green-100 border-green-300';
      case 'BEARISH':
        return 'text-red-700 bg-red-100 border-red-300';
      case 'NEUTRAL':
        return 'text-gray-700 bg-gray-100 border-gray-300';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  const getAccentBarColor = (category: PatternCategory) => {
    switch (category) {
      case 'Reversal':
        return 'bg-red-500';
      case 'Continuation':
        return 'bg-blue-500';
      case 'Neutral':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b">
          <Activity className="w-6 h-6 text-blue-600" />
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900">Pattern Detection</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded">
                {symbol}
              </span>
              <span className="text-sm text-gray-500">AI-powered technical analysis</span>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            aria-label="Refresh pattern detection"
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

        {/* Filters */}
        <div className="px-6 py-4 border-b bg-gray-50 space-y-3">
          {/* Show All Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showAllPatterns}
              onChange={handleShowAllToggle}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">Show All Patterns</span>
          </label>

          {/* Category Filters */}
          <div className="flex gap-2">
            <button
              onClick={() => handleCategoryFilter('all')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => handleCategoryFilter('Reversal')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedCategory === 'Reversal'
                  ? 'bg-red-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              Reversal
            </button>
            <button
              onClick={() => handleCategoryFilter('Continuation')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedCategory === 'Continuation'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              Continuation
            </button>
            <button
              onClick={() => handleCategoryFilter('Neutral')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedCategory === 'Neutral'
                  ? 'bg-gray-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              Neutral
            </button>
          </div>
        </div>

        {/* Patterns List */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {isLoading && !error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mb-4" />
              <p className="text-sm text-gray-600">Analyzing chart patterns…</p>
            </div>
          ) : filteredPatterns.length === 0 ? (
            <div className="text-center py-16">
              <Activity className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-sm text-gray-600">
                No {selectedCategory !== 'all' && selectedCategory} patterns detected for {symbol}.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredPatterns.map((pattern) => (
                <button
                  key={pattern.id}
                  onClick={() => handlePatternToggle(pattern.id)}
                  className={`w-full flex items-start gap-4 p-4 rounded-lg border-2 transition-all ${
                    pattern.visible
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-gray-200 bg-gray-50 opacity-60'
                  } hover:shadow-md`}
                >
                  {/* Accent Bar */}
                  <div className={`w-1 h-full ${getAccentBarColor(pattern.category)} rounded-full`} />

                  {/* Visibility Icon */}
                  {pattern.visible ? (
                    <Eye className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <EyeOff className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                  )}

                  {/* Content */}
                  <div className="flex-1 text-left">
                    {/* Header */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-gray-900">{pattern.name}</span>
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded border ${getSignalColor(pattern.signal)}`}
                      >
                        {pattern.signal}
                      </span>
                    </div>

                    {/* Category & Confidence */}
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded ${getCategoryColor(pattern.category)}`}>
                        {pattern.category}
                      </span>
                      <span className="text-sm font-semibold text-gray-700">{pattern.confidence}%</span>
                    </div>

                    {/* Confidence Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          pattern.confidence >= 70
                            ? 'bg-green-500'
                            : pattern.confidence >= 50
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                        }`}
                        style={{ width: `${pattern.confidence}%` }}
                      />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {patterns.length > 0 && (
          <div className="px-6 py-4 border-t bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>
                {filteredPatterns.length} {filteredPatterns.length === 1 ? 'pattern' : 'patterns'} detected
              </span>
              <span className="flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full" />
                {patterns.filter((p) => p.visible).length} visible on chart
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
