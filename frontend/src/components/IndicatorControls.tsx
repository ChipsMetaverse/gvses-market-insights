/**
 * IndicatorControls - UI component for managing technical indicator settings
 * Provides toggles, configuration options, and quick presets
 */

import React, { useState } from 'react';
import { useIndicatorState } from '../hooks/useIndicatorState';
import './IndicatorControls.css';

export function IndicatorControls() {
  const { state, actions } = useIndicatorState();
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'overlays' | 'oscillators' | 'patterns'>('overlays');
  
  // Quick presets for common indicator combinations
  const applyPreset = (preset: 'basic' | 'advanced' | 'daytrading' | 'swing') => {
    actions.resetToDefaults();
    
    switch (preset) {
      case 'basic':
        actions.toggleIndicator('movingAverages', 'ma20');
        actions.toggleIndicator('movingAverages', 'ma50');
        break;
        
      case 'advanced':
        actions.toggleIndicator('movingAverages', 'ma20');
        actions.toggleIndicator('movingAverages', 'ma50');
        actions.toggleIndicator('movingAverages', 'ma200');
        actions.toggleIndicator('bollingerBands');
        actions.toggleIndicator('rsi');
        actions.setOscillatorPane(true, 'rsi');
        break;
        
      case 'daytrading':
        actions.toggleIndicator('movingAverages', 'ma20');
        actions.toggleIndicator('bollingerBands');
        actions.toggleIndicator('macd');
        actions.toggleIndicator('rsi');
        actions.setOscillatorPane(true, 'macd');
        break;
        
      case 'swing':
        actions.toggleIndicator('movingAverages', 'ma50');
        actions.toggleIndicator('movingAverages', 'ma200');
        actions.toggleIndicator('fibonacci');
        actions.toggleIndicator('supportResistance');
        break;
    }
  };
  
  return (
    <div className={`indicator-controls ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* Header */}
      <div className="indicator-controls-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>Technical Indicators</h3>
        <div className="header-actions">
          {state.loading && <span className="loading-indicator">⟳</span>}
          <button className="toggle-btn">
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>
      
      {/* Quick Actions Bar */}
      <div className="quick-actions">
        <button 
          className="quick-action-btn"
          onClick={() => actions.refetch()}
          disabled={state.loading}
        >
          Refresh
        </button>
        <button 
          className="quick-action-btn"
          onClick={() => actions.clearCache()}
        >
          Clear Cache
        </button>
        <button 
          className={`quick-action-btn ${state.ui.autoRefresh ? 'active' : ''}`}
          onClick={() => actions.setAutoRefresh(!state.ui.autoRefresh)}
        >
          Auto-Refresh
        </button>
      </div>
      
      {/* Expanded Controls */}
      {isExpanded && (
        <div className="indicator-controls-body">
          {/* Presets */}
          <div className="presets-section">
            <h4>Quick Presets</h4>
            <div className="preset-buttons">
              <button onClick={() => applyPreset('basic')} className="preset-btn">
                Basic
              </button>
              <button onClick={() => applyPreset('advanced')} className="preset-btn">
                Advanced
              </button>
              <button onClick={() => applyPreset('daytrading')} className="preset-btn">
                Day Trading
              </button>
              <button onClick={() => applyPreset('swing')} className="preset-btn">
                Swing Trading
              </button>
            </div>
          </div>
          
          {/* Tabs */}
          <div className="indicator-tabs">
            <button 
              className={`tab ${activeTab === 'overlays' ? 'active' : ''}`}
              onClick={() => setActiveTab('overlays')}
            >
              Overlays
            </button>
            <button 
              className={`tab ${activeTab === 'oscillators' ? 'active' : ''}`}
              onClick={() => setActiveTab('oscillators')}
            >
              Oscillators
            </button>
            <button 
              className={`tab ${activeTab === 'patterns' ? 'active' : ''}`}
              onClick={() => setActiveTab('patterns')}
            >
              Patterns
            </button>
          </div>
          
          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'overlays' && (
              <div className="indicators-list">
                {/* Moving Averages */}
                <div className="indicator-group">
                  <h5>Moving Averages</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.movingAverages.ma20.enabled}
                      onChange={() => actions.toggleIndicator('movingAverages', 'ma20')}
                    />
                    <span>MA 20</span>
                  </label>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.movingAverages.ma50.enabled}
                      onChange={() => actions.toggleIndicator('movingAverages', 'ma50')}
                    />
                    <span>MA 50</span>
                  </label>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.movingAverages.ma200.enabled}
                      onChange={() => actions.toggleIndicator('movingAverages', 'ma200')}
                    />
                    <span>MA 200</span>
                  </label>
                </div>
                
                {/* Bollinger Bands */}
                <div className="indicator-group">
                  <h5>Bollinger Bands</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.bollingerBands.enabled}
                      onChange={() => actions.toggleIndicator('bollingerBands')}
                    />
                    <span>Enabled</span>
                  </label>
                  {state.indicators.bollingerBands.enabled && (
                    <div className="indicator-config">
                      <label>
                        Period:
                        <input
                          type="number"
                          value={state.indicators.bollingerBands.period}
                          onChange={(e) => actions.updateIndicatorConfig('bollingerBands', {
                            period: parseInt(e.target.value)
                          })}
                          min="10"
                          max="50"
                        />
                      </label>
                    </div>
                  )}
                </div>
                
                {/* Fibonacci */}
                <div className="indicator-group">
                  <h5>Fibonacci Retracement</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.fibonacci.enabled}
                      onChange={() => actions.toggleIndicator('fibonacci')}
                    />
                    <span>Enabled</span>
                  </label>
                </div>
                
                {/* Support/Resistance */}
                <div className="indicator-group">
                  <h5>Support & Resistance</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.supportResistance.enabled}
                      onChange={() => actions.toggleIndicator('supportResistance')}
                    />
                    <span>Enabled</span>
                  </label>
                </div>
              </div>
            )}
            
            {activeTab === 'oscillators' && (
              <div className="indicators-list">
                {/* RSI */}
                <div className="indicator-group">
                  <h5>RSI (Relative Strength Index)</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.rsi.enabled}
                      onChange={() => {
                        actions.toggleIndicator('rsi');
                        if (!state.indicators.rsi.enabled) {
                          actions.setOscillatorPane(true, 'rsi');
                        }
                      }}
                    />
                    <span>Enabled</span>
                  </label>
                  {state.indicators.rsi.enabled && (
                    <div className="indicator-config">
                      <label>
                        Period:
                        <input
                          type="number"
                          value={state.indicators.rsi.period}
                          onChange={(e) => actions.updateIndicatorConfig('rsi', {
                            period: parseInt(e.target.value)
                          })}
                          min="5"
                          max="30"
                        />
                      </label>
                      <label>
                        Overbought:
                        <input
                          type="number"
                          value={state.indicators.rsi.overbought}
                          onChange={(e) => actions.updateIndicatorConfig('rsi', {
                            overbought: parseInt(e.target.value)
                          })}
                          min="60"
                          max="90"
                        />
                      </label>
                      <label>
                        Oversold:
                        <input
                          type="number"
                          value={state.indicators.rsi.oversold}
                          onChange={(e) => actions.updateIndicatorConfig('rsi', {
                            oversold: parseInt(e.target.value)
                          })}
                          min="10"
                          max="40"
                        />
                      </label>
                    </div>
                  )}
                </div>
                
                {/* MACD */}
                <div className="indicator-group">
                  <h5>MACD</h5>
                  <label className="indicator-toggle">
                    <input
                      type="checkbox"
                      checked={state.indicators.macd.enabled}
                      onChange={() => {
                        actions.toggleIndicator('macd');
                        if (!state.indicators.macd.enabled) {
                          actions.setOscillatorPane(true, 'macd');
                        }
                      }}
                    />
                    <span>Enabled</span>
                  </label>
                  {state.indicators.macd.enabled && (
                    <div className="indicator-config">
                      <label>
                        Fast Period:
                        <input
                          type="number"
                          value={state.indicators.macd.fastPeriod}
                          onChange={(e) => actions.updateIndicatorConfig('macd', {
                            fastPeriod: parseInt(e.target.value)
                          })}
                          min="5"
                          max="20"
                        />
                      </label>
                      <label>
                        Slow Period:
                        <input
                          type="number"
                          value={state.indicators.macd.slowPeriod}
                          onChange={(e) => actions.updateIndicatorConfig('macd', {
                            slowPeriod: parseInt(e.target.value)
                          })}
                          min="20"
                          max="40"
                        />
                      </label>
                      <label>
                        Signal Period:
                        <input
                          type="number"
                          value={state.indicators.macd.signalPeriod}
                          onChange={(e) => actions.updateIndicatorConfig('macd', {
                            signalPeriod: parseInt(e.target.value)
                          })}
                          min="5"
                          max="15"
                        />
                      </label>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {activeTab === 'patterns' && (
              <div className="indicators-list">
                <p className="coming-soon">Pattern recognition coming soon...</p>
              </div>
            )}
          </div>
          
          {/* Status Bar */}
          <div className="status-bar">
            {state.error && (
              <div className="error-message">
                Error: {state.error}
              </div>
            )}
            {state.lastUpdated && (
              <div className="last-updated">
                Last updated: {state.lastUpdated.toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}