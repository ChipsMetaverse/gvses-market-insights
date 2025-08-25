import React from 'react';
import { MarketSnapshot as MarketSnapshotType } from '../types/dashboard';

interface MarketSnapshotProps {
  data: MarketSnapshotType;
}

export const MarketSnapshot: React.FC<MarketSnapshotProps> = ({ data }) => {
  return (
    <div className="card" data-testid="market-snapshot">
      <div className="card-header">
        <h3 className="card-title">Market Snapshot</h3>
      </div>
      <div className="market-snapshot">
        <div className="market-snapshot-item">
          <div className="market-snapshot-label">Open</div>
          <div className="market-snapshot-value">${data.open_price.toFixed(2)}</div>
        </div>
        
        <div className="market-snapshot-item">
          <div className="market-snapshot-label">Day Range</div>
          <div className="market-snapshot-value">
            ${data.day_low.toFixed(2)} - ${data.day_high.toFixed(2)}
          </div>
        </div>
        
        <div className="market-snapshot-item">
          <div className="market-snapshot-label">Previous Close</div>
          <div className="market-snapshot-value">${data.prev_close.toFixed(2)}</div>
        </div>
        
        <div className="market-snapshot-item">
          <div className="market-snapshot-label">Volume</div>
          <div className="market-snapshot-value">{data.volume_formatted}</div>
        </div>
        
        {data.avg_volume_3m && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">Avg Volume (3M)</div>
            <div className="market-snapshot-value">{data.avg_volume_3m_formatted}</div>
          </div>
        )}
        
        {data.market_cap_formatted && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">Market Cap</div>
            <div className="market-snapshot-value">{data.market_cap_formatted}</div>
          </div>
        )}
        
        {data.pe_ttm_formatted && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">P/E Ratio (TTM)</div>
            <div className="market-snapshot-value">{data.pe_ttm_formatted}</div>
          </div>
        )}
        
        {data.dividend_yield_pct_formatted && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">Dividend Yield</div>
            <div className="market-snapshot-value">{data.dividend_yield_pct_formatted}</div>
          </div>
        )}
        
        {data.beta !== undefined && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">Beta</div>
            <div className="market-snapshot-value">{data.beta.toFixed(2)}</div>
          </div>
        )}
        
        {data.week52_range_formatted && (
          <div className="market-snapshot-item">
            <div className="market-snapshot-label">52 Week Range</div>
            <div className="market-snapshot-value">{data.week52_range_formatted}</div>
          </div>
        )}
      </div>
    </div>
  );
};