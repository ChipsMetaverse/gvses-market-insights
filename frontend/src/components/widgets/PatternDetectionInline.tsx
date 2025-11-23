import React from 'react';
import { Activity } from 'lucide-react';

interface Pattern {
  name: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  category: string;
  confidence: number;
  description?: string;
}

interface PatternDetectionInlineProps {
  data: {
    patterns: Pattern[];
    symbol?: string;
  };
}

export function PatternDetectionInline({ data }: PatternDetectionInlineProps) {
  const getSignalColor = (signal: Pattern['signal']) => {
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

  const getCategoryColor = (category: string) => {
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

  if (!data.patterns || data.patterns.length === 0) {
    return (
      <div className="my-2 border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <Activity className="w-4 h-4 text-blue-600" />
          <h4 className="text-sm font-semibold text-gray-900">Pattern Detection</h4>
        </div>
        <p className="text-xs text-gray-500">No patterns detected for {data.symbol || 'this symbol'}.</p>
      </div>
    );
  }

  return (
    <div className="my-2 border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <Activity className="w-4 h-4 text-blue-600" />
        <h4 className="text-sm font-semibold text-gray-900">Pattern Detection</h4>
        {data.symbol && (
          <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
            {data.symbol}
          </span>
        )}
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {data.patterns.slice(0, 10).map((pattern, index) => (
          <div
            key={index}
            className="flex items-start gap-2 p-2 rounded border border-gray-200 bg-gray-50"
          >
            {/* Accent Bar */}
            <div className={`w-1 h-full ${getCategoryColor(pattern.category)} rounded-full flex-shrink-0`} />

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-gray-900 truncate">{pattern.name}</span>
                <span
                  className={`text-xs font-bold px-1.5 py-0.5 rounded border flex-shrink-0 ${getSignalColor(pattern.signal)}`}
                >
                  {pattern.signal}
                </span>
              </div>

              {/* Category & Confidence */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-gray-600">{pattern.category}</span>
                <span className="text-xs font-semibold text-gray-700">{pattern.confidence}%</span>
              </div>

              {/* Confidence Bar */}
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all ${
                    pattern.confidence >= 70
                      ? 'bg-green-500'
                      : pattern.confidence >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                  }`}
                  style={{ width: `${pattern.confidence}%` }}
                />
              </div>

              {/* Description if available */}
              {pattern.description && (
                <p className="text-xs text-gray-500 mt-1">{pattern.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {data.patterns.length > 10 && (
        <div className="mt-2 pt-2 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Showing 10 of {data.patterns.length} patterns
          </p>
        </div>
      )}
    </div>
  );
}
