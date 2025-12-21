/**
 * ChartLoadingIndicator - Visual Loading States for Chart Data
 *
 * Displays loading indicators for:
 * - Initial data load (center overlay)
 * - Lazy loading more data (top-left badge)
 * - Cache performance info (optional)
 */

import React from 'react'
import './ChartLoadingIndicator.css'

export interface ChartLoadingIndicatorProps {
  isLoading: boolean
  isLoadingMore: boolean
  cacheInfo?: {
    tier: 'memory' | 'database' | 'api' | null
    duration_ms: number | null
  }
  showCacheInfo?: boolean
}

export function ChartLoadingIndicator({
  isLoading,
  isLoadingMore,
  cacheInfo,
  showCacheInfo = false,
}: ChartLoadingIndicatorProps) {
  // Don't render anything if nothing is loading
  if (!isLoading && !isLoadingMore && !showCacheInfo) {
    return null
  }

  return (
    <>
      {/* Initial loading overlay (center) */}
      {isLoading && (
        <div className="chart-loading-overlay">
          <div className="chart-loading-spinner">
            <div className="spinner"></div>
            <p className="loading-text">Loading chart data...</p>
          </div>
        </div>
      )}

      {/* Lazy loading badge (top-left) */}
      {isLoadingMore && (
        <div className="chart-loading-badge">
          <div className="badge-spinner"></div>
          <span className="badge-text">Loading older data...</span>
        </div>
      )}

      {/* Cache info (development/debug) */}
      {showCacheInfo && cacheInfo && cacheInfo.tier && (
        <div className="chart-cache-info">
          <span className={`cache-tier tier-${cacheInfo.tier}`}>
            {cacheInfo.tier === 'memory' && '⚡ Memory'}
            {cacheInfo.tier === 'database' && '💾 Database'}
            {cacheInfo.tier === 'api' && '🌐 API'}
          </span>
          {cacheInfo.duration_ms !== null && (
            <span className="cache-duration">
              {cacheInfo.duration_ms < 1000
                ? `${Math.round(cacheInfo.duration_ms)}ms`
                : `${(cacheInfo.duration_ms / 1000).toFixed(2)}s`}
            </span>
          )}
        </div>
      )}
    </>
  )
}

export default ChartLoadingIndicator
