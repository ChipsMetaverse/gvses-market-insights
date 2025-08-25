import React from 'react';
import { TechnicalOverview } from '../types/dashboard';

interface TechnicalOverviewCardProps {
  data: TechnicalOverview;
}

export const TechnicalOverviewCard: React.FC<TechnicalOverviewCardProps> = ({ data }) => {
  const getBadgeClass = (rating: string) => {
    switch (rating) {
      case 'Bullish':
        return 'bullish';
      case 'Bearish':
        return 'bearish';
      default:
        return 'neutral';
    }
  };
  
  return (
    <div className="card" data-testid="technical-overview">
      <div className="card-header">
        <h3 className="card-title">Technical Overview</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${getBadgeClass(data.rating)}`}>
            {data.rating}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Score: {data.rating_score > 0 ? '+' : ''}{data.rating_score}
          </span>
        </div>
      </div>
      
      <div className="technical-content">
        {data.notes && data.notes.length > 0 && (
          <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)' }}>
            {data.notes.map((note, index) => (
              <li key={index} style={{ marginBottom: '4px', fontSize: '14px' }}>
                {note}
              </li>
            ))}
          </ul>
        )}
        
        {data.macd && (
          <div style={{ marginTop: '16px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
              MACD ({data.macd.fast_period}, {data.macd.slow_period}, {data.macd.signal_period})
            </div>
            <div style={{ display: 'flex', gap: '16px', fontSize: '14px' }}>
              {data.macd.last_macd !== undefined && (
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>MACD: </span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                    {data.macd.last_macd.toFixed(2)}
                  </span>
                </div>
              )}
              {data.macd.last_signal !== undefined && (
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Signal: </span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                    {data.macd.last_signal.toFixed(2)}
                  </span>
                </div>
              )}
              {data.macd.last_histogram !== undefined && (
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Histogram: </span>
                  <span 
                    style={{ 
                      color: data.macd.last_histogram >= 0 ? 'var(--accent-secondary)' : 'var(--accent-danger)', 
                      fontWeight: '600' 
                    }}
                  >
                    {data.macd.last_histogram.toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};