import React from 'react';
import { RealtimeChatKit } from './RealtimeChatKit';
import './TradingDashboardSimple.css';

/**
 * ChatKit-only dashboard for logged-in users and demo mode
 * Charts are displayed via ChatKit widgets, not as a permanent sidebar
 */
export function TradingDashboardChatOnly() {
  return (
    <div className="trading-dashboard-simple" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header className="dashboard-header-with-tickers header-container" style={{ flexShrink: 0, padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>G'sves AI Trading Assistant</h1>
        </div>
      </header>

      {/* Main Content - ChatKit Only */}
      <main style={{ flex: 1, overflow: 'hidden', padding: '1rem', display: 'flex', justifyContent: 'center' }}>
        {/* ChatKit Full Width */}
        <div style={{ width: '100%', maxWidth: '1200px', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <RealtimeChatKit
            symbol="TSLA"
            timeframe="3M"
            onMessage={(message) => {
              console.log('Chat message:', message);
            }}
            onChartCommand={(command) => {
              console.log('Chart command received:', command);
            }}
          />
        </div>
      </main>
    </div>
  );
}
