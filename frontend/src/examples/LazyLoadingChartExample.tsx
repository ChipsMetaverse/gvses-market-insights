/**
 * LazyLoadingChartExample - Complete Example Implementation
 *
 * Demonstrates all features of the lazy loading chart:
 * - Initial data loading
 * - Automatic lazy loading on scroll
 * - Loading states and indicators
 * - Cache performance monitoring
 * - Error handling
 * - Manual controls
 *
 * Usage:
 *   import { LazyLoadingChartExample } from './examples/LazyLoadingChartExample'
 *
 *   function App() {
 *     return <LazyLoadingChartExample />
 *   }
 */

import { useState } from 'react'
import { TradingChartLazy } from '../components/TradingChartLazy'
import { useInfiniteChartData } from '../hooks/useInfiniteChartData'

export function LazyLoadingChartExample() {
  const [symbol, setSymbol] = useState('AAPL')
  const [interval, setInterval] = useState('1d')
  const [showCacheInfo, setShowCacheInfo] = useState(false)

  // Access hook for manual controls (optional)
  const chartHook = useInfiniteChartData({
    symbol,
    interval,
    initialDays: 60,
    enabled: true,
  })

  return (
    <div style={{ padding: '20px', fontFamily: 'system-ui, sans-serif' }}>
      <h1>Lazy Loading Chart Example</h1>

      {/* Controls */}
      <div
        style={{
          marginBottom: '20px',
          padding: '15px',
          background: '#f9fafb',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
        }}
      >
        <h3 style={{ marginTop: 0 }}>Controls</h3>

        {/* Symbol Selector */}
        <div style={{ marginBottom: '10px' }}>
          <label style={{ marginRight: '10px', fontWeight: '500' }}>
            Symbol:
          </label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
            }}
          >
            <option value="AAPL">AAPL - Apple</option>
            <option value="TSLA">TSLA - Tesla</option>
            <option value="NVDA">NVDA - NVIDIA</option>
            <option value="MSFT">MSFT - Microsoft</option>
            <option value="GOOGL">GOOGL - Google</option>
            <option value="AMZN">AMZN - Amazon</option>
          </select>
        </div>

        {/* Interval Selector */}
        <div style={{ marginBottom: '10px' }}>
          <label style={{ marginRight: '10px', fontWeight: '500' }}>
            Interval:
          </label>
          <select
            value={interval}
            onChange={(e) => setInterval(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
            }}
          >
            <option value="5m">5 Minutes</option>
            <option value="15m">15 Minutes</option>
            <option value="30m">30 Minutes</option>
            <option value="1h">1 Hour</option>
            <option value="1d">Daily</option>
            <option value="1wk">Weekly</option>
          </select>
        </div>

        {/* Debug Toggle */}
        <div style={{ marginBottom: '10px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showCacheInfo}
              onChange={(e) => setShowCacheInfo(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            <span>Show cache performance info</span>
          </label>
        </div>

        {/* Manual Actions */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button
            onClick={chartHook.refresh}
            disabled={chartHook.isLoading}
            style={{
              padding: '8px 16px',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
              background: 'white',
              cursor: chartHook.isLoading ? 'not-allowed' : 'pointer',
              opacity: chartHook.isLoading ? 0.6 : 1,
            }}
          >
            🔄 Refresh
          </button>

          <button
            onClick={chartHook.loadMore}
            disabled={chartHook.isLoading || chartHook.isLoadingMore || !chartHook.hasMore}
            style={{
              padding: '8px 16px',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
              background: 'white',
              cursor:
                chartHook.isLoading || chartHook.isLoadingMore || !chartHook.hasMore
                  ? 'not-allowed'
                  : 'pointer',
              opacity:
                chartHook.isLoading || chartHook.isLoadingMore || !chartHook.hasMore ? 0.6 : 1,
            }}
          >
            ⬅️ Load More
          </button>

          <button
            onClick={chartHook.reset}
            style={{
              padding: '8px 16px',
              borderRadius: '4px',
              border: '1px solid #d1d5db',
              background: 'white',
              cursor: 'pointer',
            }}
          >
            ↺ Reset
          </button>
        </div>
      </div>

      {/* Stats */}
      <div
        style={{
          marginBottom: '20px',
          padding: '15px',
          background: '#eff6ff',
          borderRadius: '8px',
          border: '1px solid #dbeafe',
        }}
      >
        <h3 style={{ marginTop: 0, color: '#1e40af' }}>Chart Statistics</h3>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Loaded Candles
            </div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e40af' }}>
              {chartHook.data.length.toLocaleString()}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Date Range
            </div>
            <div style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
              {chartHook.oldestDate?.toLocaleDateString() || 'N/A'}
              <br />→ {chartHook.newestDate?.toLocaleDateString() || 'N/A'}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
              Cache Performance
            </div>
            <div style={{ fontSize: '14px', fontWeight: '500' }}>
              {chartHook.cacheInfo.tier === 'memory' && (
                <span style={{ color: '#10b981' }}>⚡ Memory ({chartHook.cacheInfo.duration_ms}ms)</span>
              )}
              {chartHook.cacheInfo.tier === 'database' && (
                <span style={{ color: '#3b82f6' }}>💾 Database ({chartHook.cacheInfo.duration_ms}ms)</span>
              )}
              {chartHook.cacheInfo.tier === 'api' && (
                <span style={{ color: '#f59e0b' }}>🌐 API ({chartHook.cacheInfo.duration_ms}ms)</span>
              )}
              {!chartHook.cacheInfo.tier && <span style={{ color: '#9ca3af' }}>N/A</span>}
            </div>
          </div>
        </div>

        {chartHook.error && (
          <div
            style={{
              marginTop: '15px',
              padding: '10px',
              background: '#fee2e2',
              border: '1px solid #fecaca',
              borderRadius: '4px',
              color: '#991b1b',
            }}
          >
            ❌ {chartHook.error}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div
        style={{
          marginBottom: '20px',
          padding: '15px',
          background: '#fef3c7',
          borderRadius: '8px',
          border: '1px solid #fde68a',
        }}
      >
        <h3 style={{ marginTop: 0, color: '#92400e' }}>💡 How to Test Lazy Loading</h3>
        <ol style={{ margin: 0, paddingLeft: '20px', color: '#78350f' }}>
          <li>
            <strong>Initial Load:</strong> Watch the center loading spinner appear briefly
          </li>
          <li>
            <strong>Pan Left:</strong> Click and drag the chart to the right (or use mouse wheel)
          </li>
          <li>
            <strong>Watch Badge:</strong> When you get close to the left edge, a blue "Loading older data..." badge appears
          </li>
          <li>
            <strong>See Integration:</strong> New candles appear smoothly on the left side
          </li>
          <li>
            <strong>Performance:</strong> Enable cache info to see how fast data loads
          </li>
        </ol>
      </div>

      {/* Chart */}
      <div
        style={{
          height: '500px',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          overflow: 'hidden',
          background: 'white',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }}
      >
        <TradingChartLazy
          symbol={symbol}
          interval={interval}
          initialDays={60}
          enableLazyLoading={true}
          showCacheInfo={showCacheInfo}
        />
      </div>

      {/* Footer */}
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#6b7280' }}>
        <strong>Performance Expectations:</strong>
        <ul style={{ margin: '10px 0', paddingLeft: '20px' }}>
          <li>Initial load (cold): ~500ms (API fetch + database store)</li>
          <li>Initial load (cached): ~50-200ms (database hit)</li>
          <li>Lazy load: ~50-200ms (pre-warmed database)</li>
          <li>API call reduction: 99% (1000 views → ~10 API calls)</li>
        </ul>
      </div>
    </div>
  )
}

export default LazyLoadingChartExample
