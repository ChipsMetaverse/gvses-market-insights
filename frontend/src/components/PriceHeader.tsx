import React from 'react';
import { PriceHeader as PriceHeaderType } from '../types/dashboard';

interface PriceHeaderProps {
  data: PriceHeaderType;
}

export const PriceHeader: React.FC<PriceHeaderProps> = ({ data }) => {
  const isPositive = data.change_pct >= 0;
  
  return (
    <div className="price-header" data-testid="price-header">
      <div className="price-header-left">
        <div>
          <div className="price-header-company">{data.company_name}</div>
          <div className="price-header-symbol">{data.symbol} • {data.exchange}</div>
        </div>
        <div>
          <div className="price-header-price">{data.last_price_formatted}</div>
          <div className={`price-header-change ${isPositive ? 'positive' : 'negative'}`}>
            <span>{isPositive ? '▲' : '▼'}</span>
            <span>{data.change_abs_formatted}</span>
            <span>({data.change_pct_formatted})</span>
          </div>
        </div>
      </div>
      
      <div className="price-header-right">
        <div className={`badge ${data.is_market_open ? 'bullish' : 'neutral'}`}>
          {data.is_market_open ? 'Market Open' : 'Market Closed'}
        </div>
      </div>
    </div>
  );
};