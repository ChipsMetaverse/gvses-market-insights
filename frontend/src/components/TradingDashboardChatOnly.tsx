import React, { useState, useEffect, useRef } from 'react';
import { TradingChart } from './TradingChart';
import { TimeRangeSelector } from './TimeRangeSelector';
import { RealtimeChatKit } from './RealtimeChatKit';
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';
import './TradingDashboardSimple.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  provider?: string;
}

// Helper functions for timeframe conversion
const timeframeToDays = (timeframe: string): { fetch: number; display: number } => {
  const map: Record<string, { fetch: number; display: number }> = {
    '1D': { fetch: 1, display: 1 },
    '5D': { fetch: 5, display: 5 },
    '1M': { fetch: 30, display: 30 },
    '3M': { fetch: 90, display: 90 },
    '6M': { fetch: 180, display: 180 },
    '1Y': { fetch: 365, display: 365 },
    '2Y': { fetch: 730, display: 730 },
    '3Y': { fetch: 1095, display: 1095 },
    'YTD': { fetch: 365, display: 365 },
    'MAX': { fetch: 3650, display: 3650 },
  };
  return map[timeframe] || map['1D'];
};

const timeframeToInterval = (timeframe: string): string => {
  const map: Record<string, string> = {
    '1D': '15m',
    '5D': '30m',
    '1M': '1h',
    '3M': '1d',
    '6M': '1d',
    '1Y': '1d',
    '2Y': '1wk',
    '3Y': '1wk',
    'YTD': '1d',
    'MAX': '1wk',
  };
  return map[timeframe] || '1d';
};

export function TradingDashboardChatOnly() {
  const [selectedSymbol, setSelectedSymbol] = useState('TSLA');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');
  const [messages, setMessages] = useState<Message[]>([]);
  const chartRef = useRef<any>(null);

  return (
    <div className="trading-dashboard-simple" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header className="dashboard-header-with-tickers header-container" style={{ flexShrink: 0, padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>G'sves AI Trading Assistant</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: '#666' }}>Symbol:</span>
            <input
              type="text"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
              style={{
                padding: '0.25rem 0.5rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '0.875rem',
                width: '80px'
              }}
              placeholder="Symbol"
            />
          </div>
        </div>
      </header>

      {/* Main Content - Split Layout */}
      <main style={{ flex: 1, overflow: 'hidden', padding: '1rem', display: 'flex', gap: '1rem' }}>
        {/* Left Side - Chart */}
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          {/* Timeframe Selector */}
          <TimeRangeSelector
            selected={selectedTimeframe}
            options={['1D', '5D', '1M', '3M', '6M', '1Y', 'YTD', 'MAX']}
            onChange={(range) => setSelectedTimeframe(range)}
            showAdvancedMenu={true}
          />
          <div className="chart-wrapper" style={{ flex: 1, minHeight: 0 }}>
            <TradingChart
              symbol={selectedSymbol}
              days={timeframeToDays(selectedTimeframe).fetch}
              displayDays={timeframeToDays(selectedTimeframe).display}
              interval={timeframeToInterval(selectedTimeframe)}
              onChartReady={(chart: any) => {
                chartRef.current = chart;
                chartControlService.setChartRef(chart);
                enhancedChartControl.setChartRef(chart);
                console.log('Chart ready with trendline support');
              }}
            />
          </div>
        </div>

        {/* Right Side - ChatKit */}
        <div style={{ width: '400px', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <RealtimeChatKit
            symbol={selectedSymbol}
            timeframe={selectedTimeframe}
            onMessage={(message) => {
              console.log('Chat message:', message);
              setMessages((prev) => [...prev, message]);
            }}
            onChartCommand={(command) => {
              console.log('Chart command received:', command);
              // Chart commands are handled by the chartControlService
            }}
          />
        </div>
      </main>
    </div>
  );
}
