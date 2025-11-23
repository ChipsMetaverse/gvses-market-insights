import React from 'react';
import { TrendingUp, TrendingDown, Target } from 'lucide-react';

interface TechnicalLevelsInlineProps {
  data: {
    sell_high_level?: number;
    buy_low_level?: number;
    btd_level?: number;
    symbol?: string;
  };
}

export function TechnicalLevelsInline({ data }: TechnicalLevelsInlineProps) {
  const levels = [
    {
      label: 'Sell High',
      value: data.sell_high_level,
      icon: TrendingDown,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
    },
    {
      label: 'Buy Low',
      value: data.buy_low_level,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
    },
    {
      label: 'BTD',
      value: data.btd_level,
      icon: Target,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
  ];

  return (
    <div className="my-2 border border-gray-200 rounded-lg p-3 bg-white shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-1 h-4 bg-blue-500 rounded"></div>
        <h4 className="text-sm font-semibold text-gray-900">Technical Levels</h4>
        {data.symbol && (
          <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
            {data.symbol}
          </span>
        )}
      </div>

      <div className="space-y-2">
        {levels.map((level) => {
          const Icon = level.icon;
          return (
            <div
              key={level.label}
              className={`flex items-center gap-2 p-2 rounded border ${level.borderColor} ${level.bgColor}`}
            >
              <Icon className={`w-4 h-4 ${level.color} flex-shrink-0`} />
              <span className="text-xs font-medium text-gray-700 flex-1">{level.label}</span>
              <span className={`text-sm font-bold ${level.color}`}>
                {level.value ? `$${level.value.toFixed(2)}` : 'N/A'}
              </span>
            </div>
          );
        })}
      </div>

      <div className="mt-2 pt-2 border-t border-gray-100">
        <p className="text-xs text-gray-500">Based on 30-day price action</p>
      </div>
    </div>
  );
}
