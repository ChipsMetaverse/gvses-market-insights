"use client"

import { TrendingUp, TrendingDown } from 'lucide-react'
import type { MarketData } from '../types'

interface MarketInsightsProps {
  marketData: MarketData[]
  currentSymbol: string
  onSymbolChange: (symbol: string) => void
}

export function MarketInsights({ marketData, currentSymbol, onSymbolChange }: MarketInsightsProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Market Insights</h3>
      <div className="space-y-3">
        {marketData.map((stock, index) => (
          <div
            key={index}
            className={`space-y-2 p-3 rounded-lg cursor-pointer transition-colors ${
              currentSymbol === stock.symbol ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 hover:bg-gray-100'
            }`}
            onClick={() => onSymbolChange(stock.symbol)}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-black">{stock.symbol}</span>
              <span
                className={`px-2 py-0.5 text-xs rounded ${
                  stock.signal === 'LTB'
                    ? 'bg-blue-100 text-blue-800'
                    : stock.signal === 'ST'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-green-100 text-green-800'
                }`}
              >
                {stock.signal}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-black">${stock.price}</span>
              <div className={`text-xs flex items-center ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {stock.change >= 0 ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-1" />
                )}
                {Math.abs(stock.change)}%
              </div>
            </div>
            <p className="text-xs text-gray-600">{stock.analysis}</p>
          </div>
        ))}
      </div>
    </div>
  )
}