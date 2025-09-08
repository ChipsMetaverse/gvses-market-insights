/**
 * Voice Command Helper Component
 * Provides visual feedback for voice commands with history and suggestions
 */

import React, { useState, useEffect } from 'react';
import { enhancedChartControl, EnhancedChartCommand } from '../services/enhancedChartControlService';
import './VoiceCommandHelper.css';

interface VoiceCommandHelperProps {
  isVisible?: boolean;
  position?: 'left' | 'right' | 'bottom';
  maxHeight?: number;
}

export const VoiceCommandHelper: React.FC<VoiceCommandHelperProps> = ({
  isVisible = true,
  position = 'right',
  maxHeight = 400
}) => {
  const [commandHistory, setCommandHistory] = useState<EnhancedChartCommand[]>([]);
  const [context, setContext] = useState<any>({});
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchInput, setSearchInput] = useState('');

  // Update history and context periodically
  useEffect(() => {
    const updateState = () => {
      setCommandHistory(enhancedChartControl.getHistory());
      setContext(enhancedChartControl.getContext());
    };

    updateState();
    const interval = setInterval(updateState, 1000);
    return () => clearInterval(interval);
  }, []);

  // Get suggestions as user types
  useEffect(() => {
    const getSuggestions = async () => {
      if (searchInput.length >= 2) {
        const newSuggestions = await enhancedChartControl.getSuggestions(searchInput);
        setSuggestions(newSuggestions);
      } else {
        setSuggestions([]);
      }
    };

    const debounceTimer = setTimeout(getSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchInput]);

  const handleUndo = async () => {
    await enhancedChartControl.undo();
  };

  const handleRedo = async () => {
    await enhancedChartControl.redo();
  };

  const handleSuggestionClick = async (suggestion: string) => {
    await enhancedChartControl.processEnhancedResponse(suggestion);
    setSearchInput('');
    setSuggestions([]);
  };

  const formatCommand = (cmd: EnhancedChartCommand) => {
    const icons: { [key: string]: string } = {
      symbol: '📊',
      timeframe: '⏱️',
      indicator: '📈',
      zoom: '🔍',
      scroll: '📅',
      style: '🎨',
      reset: '🔄',
      crosshair: '➕'
    };

    return (
      <div className="command-history-item" key={cmd.timestamp}>
        <span className="command-icon">{icons[cmd.type] || '▶️'}</span>
        <span className="command-type">{cmd.type}</span>
        <span className="command-value">{typeof cmd.value === 'object' ? JSON.stringify(cmd.value) : cmd.value}</span>
        {cmd.confidence && (
          <span className="command-confidence" title="Confidence">
            {Math.round(cmd.confidence * 100)}%
          </span>
        )}
      </div>
    );
  };

  const exampleCommands = [
    { category: 'Navigation', commands: [
      'Show me Microsoft',
      'Display Apple chart',
      'Go back to previous stock',
      'Switch to Tesla'
    ]},
    { category: 'Timeframes', commands: [
      'Show last month',
      'Display year to date',
      'Zoom to this week',
      'View 5 day chart'
    ]},
    { category: 'Multi-Commands', commands: [
      'Show Apple and zoom to 1 month',
      'Display Tesla with RSI indicator',
      'Switch to Microsoft then add moving average',
      'Show NVDA and change to line chart'
    ]},
    { category: 'Analysis', commands: [
      'Add moving average',
      'Show RSI indicator',
      'Display volume bars',
      'Add Bollinger bands'
    ]},
    { category: 'Chart Controls', commands: [
      'Zoom in more',
      'Reset the view',
      'Switch to candlestick chart',
      'Toggle crosshair'
    ]}
  ];

  if (!isVisible) return null;

  return (
    <div className={`voice-command-helper ${position} ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="helper-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="helper-title">🎤 Voice Commands</span>
        <span className="helper-toggle">{isExpanded ? '▼' : '▲'}</span>
      </div>

      {isExpanded && (
        <div className="helper-content" style={{ maxHeight }}>
          {/* Context Status */}
          <div className="context-status">
            <div className="status-row">
              <span className="status-label">Current:</span>
              <span className="status-value">{context.currentSymbol} / {context.currentTimeframe}</span>
            </div>
            <div className="status-row">
              <span className="status-label">Commands:</span>
              <span className="status-value">{context.sessionCommands || 0} this session</span>
            </div>
            <div className="history-controls">
              <button 
                onClick={handleUndo} 
                disabled={!context.canUndo}
                title="Undo last command"
              >
                ↶ Undo
              </button>
              <button 
                onClick={handleRedo} 
                disabled={!context.canRedo}
                title="Redo command"
              >
                ↷ Redo
              </button>
            </div>
          </div>

          {/* Search/Suggestions */}
          <div className="command-search">
            <input
              type="text"
              placeholder="Type a command or company name..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="search-input"
            />
            {suggestions.length > 0 && (
              <div className="suggestions-dropdown">
                {suggestions.map((suggestion, idx) => (
                  <div
                    key={idx}
                    className="suggestion-item"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Command History */}
          {commandHistory.length > 0 && (
            <div className="command-history">
              <h4>Recent Commands</h4>
              <div className="history-list">
                {commandHistory.slice(-5).reverse().map(formatCommand)}
              </div>
            </div>
          )}

          {/* Example Commands */}
          <div className="example-commands">
            <h4>Try Saying...</h4>
            {exampleCommands.map((category) => (
              <details key={category.category} className="command-category">
                <summary>{category.category}</summary>
                <div className="command-list">
                  {category.commands.map((cmd, idx) => (
                    <div 
                      key={idx} 
                      className="example-command"
                      onClick={() => handleSuggestionClick(cmd)}
                    >
                      "{cmd}"
                    </div>
                  ))}
                </div>
              </details>
            ))}
          </div>

          {/* Tips */}
          <div className="voice-tips">
            <h4>💡 Pro Tips</h4>
            <ul>
              <li>Say company names naturally: "Show me Microsoft"</li>
              <li>Combine commands: "Display Apple and zoom to 1 month"</li>
              <li>Use relative commands: "Go back" or "Zoom in more"</li>
              <li>Navigate by time: "Show last earnings" or "Go to yesterday"</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};