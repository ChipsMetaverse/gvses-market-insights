/**
 * Sentiment Progress Bar Component
 *
 * Displays a 0-100 sentiment score with color-coded visual feedback.
 * Inspired by StockWisp's sentiment scoring UI.
 *
 * Score Ranges:
 * - 0-20: Very Bearish (Red)
 * - 21-40: Bearish (Dark Orange)
 * - 41-60: Neutral (Orange)
 * - 61-80: Bullish (Light Green)
 * - 81-100: Very Bullish (Green)
 */

import React from 'react';
import './SentimentProgressBar.css';

export interface SentimentData {
  score: number;
  label: string;
  color: string;
  components?: {
    price_momentum: number;
    technical: number;
    news_sentiment: number;
    volume_trend: number;
  };
  timestamp?: string;
}

interface SentimentProgressBarProps {
  sentiment: SentimentData;
  showComponents?: boolean;
  compact?: boolean;
}

const SentimentProgressBar: React.FC<SentimentProgressBarProps> = ({
  sentiment,
  showComponents = false,
  compact = false
}) => {
  const { score, label, color, components } = sentiment;

  // Ensure score is within 0-100 range
  const normalizedScore = Math.max(0, Math.min(100, score));

  return (
    <div className={`sentiment-progress-bar ${compact ? 'compact' : ''}`}>
      {/* Header with Score and Label */}
      <div className="sentiment-header">
        <span className="sentiment-label" style={{ color }}>
          {label}
        </span>
        <span className="sentiment-score" style={{ color }}>
          {normalizedScore}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: `${normalizedScore}%`,
              backgroundColor: color
            }}
          />
        </div>

        {/* Scale Markers */}
        {!compact && (
          <div className="progress-bar-markers">
            <span className="marker marker-0">0</span>
            <span className="marker marker-50">50</span>
            <span className="marker marker-100">100</span>
          </div>
        )}
      </div>

      {/* Component Breakdown (Optional) */}
      {showComponents && components && !compact && (
        <div className="sentiment-components">
          <div className="component">
            <span className="component-label">Price Momentum</span>
            <span className="component-value">{components.price_momentum}</span>
          </div>
          <div className="component">
            <span className="component-label">Technical</span>
            <span className="component-value">{components.technical}</span>
          </div>
          <div className="component">
            <span className="component-label">News</span>
            <span className="component-value">{components.news_sentiment}</span>
          </div>
          <div className="component">
            <span className="component-label">Volume</span>
            <span className="component-value">{components.volume_trend}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SentimentProgressBar;
