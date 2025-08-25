import React from 'react';
import { StrategicInsights as StrategicInsightsType, StrategyCode } from '../types/dashboard';

interface StrategicInsightsProps {
  data: StrategicInsightsType;
  onSelectStrategy?: (strategy_code: StrategyCode) => void;
}

export const StrategicInsights: React.FC<StrategicInsightsProps> = ({ data, onSelectStrategy }) => {
  return (
    <div className="card" data-testid="strategic-insights">
      <div className="card-header">
        <h3 className="card-title">Strategic Insights</h3>
        <div style={{ display: 'flex', gap: '16px', fontSize: '14px' }}>
          {data.iv_rank !== undefined && (
            <div>
              <span style={{ color: 'var(--text-muted)' }}>IV Rank: </span>
              <span style={{ fontWeight: '600' }}>{data.iv_rank.toFixed(1)}%</span>
            </div>
          )}
          {data.iv_percentile !== undefined && (
            <div>
              <span style={{ color: 'var(--text-muted)' }}>IV %ile: </span>
              <span style={{ fontWeight: '600' }}>{data.iv_percentile.toFixed(1)}%</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="strategies-list">
        {data.items.map((strategy, index) => (
          <div 
            key={index} 
            className="strategy-card"
            onClick={() => onSelectStrategy?.(strategy.strategy_code)}
            style={{ cursor: onSelectStrategy ? 'pointer' : 'default' }}
          >
            <div className="strategy-header">
              <div className="strategy-title">{strategy.title}</div>
              <div className="strategy-tags">
                {strategy.tags?.map((tag, i) => (
                  <span key={i} className="strategy-tag">{tag}</span>
                ))}
              </div>
            </div>
            
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: '8px 0' }}>
              {strategy.rationale}
            </p>
            
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                Recommended Legs:
              </div>
              <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
                {strategy.recommended_legs.map((leg, i) => (
                  <div key={i} style={{ marginBottom: '2px' }}>
                    {leg.action} {leg.quantity} {leg.right} @ ${leg.strike} exp {leg.expiry}
                  </div>
                ))}
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13px' }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Net: </span>
                <span style={{ 
                  fontWeight: '600',
                  color: strategy.net_debit_credit > 0 ? 'var(--accent-primary)' : 'var(--accent-secondary)'
                }}>
                  ${Math.abs(strategy.net_debit_credit).toFixed(0)} {strategy.net_debit_credit > 0 ? 'Debit' : 'Credit'}
                </span>
              </div>
              
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Max Profit: </span>
                <span style={{ fontWeight: '600', color: 'var(--accent-secondary)' }}>
                  {strategy.max_profit_text || `$${strategy.max_profit?.toFixed(0) || '—'}`}
                </span>
              </div>
              
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Max Loss: </span>
                <span style={{ fontWeight: '600', color: 'var(--accent-danger)' }}>
                  {strategy.max_loss_text || `$${strategy.max_loss?.toFixed(0) || '—'}`}
                </span>
              </div>
              
              {strategy.probability_of_profit_pct !== undefined && (
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>PoP: </span>
                  <span style={{ fontWeight: '600' }}>
                    {strategy.probability_of_profit_pct.toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
            
            {strategy.breakevens && strategy.breakevens.length > 0 && (
              <div style={{ marginTop: '8px', fontSize: '12px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Breakeven: </span>
                <span>{strategy.breakevens.map(be => `$${be.toFixed(2)}`).join(', ')}</span>
              </div>
            )}
            
            {(strategy.greeks_delta !== undefined || strategy.greeks_theta !== undefined) && (
              <div style={{ marginTop: '8px', display: 'flex', gap: '12px', fontSize: '11px' }}>
                {strategy.greeks_delta !== undefined && (
                  <span className="badge neutral">Δ {strategy.greeks_delta.toFixed(2)}</span>
                )}
                {strategy.greeks_gamma !== undefined && (
                  <span className="badge neutral">Γ {strategy.greeks_gamma.toFixed(3)}</span>
                )}
                {strategy.greeks_theta !== undefined && (
                  <span className="badge neutral">Θ {strategy.greeks_theta.toFixed(2)}</span>
                )}
                {strategy.greeks_vega !== undefined && (
                  <span className="badge neutral">V {strategy.greeks_vega.toFixed(2)}</span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};