import React, { useState, useEffect } from 'react';
import './DebugWidget.css';

interface DebugLog {
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success';
  category: string;
  message: string;
}

interface DebugWidgetProps {
  isConnected: boolean;
  isLoading: boolean;
  voiceProvider: string;
  openAIConnected?: boolean;
  agentVoiceConnected?: boolean;
  realtimeSDKConnected?: boolean;
  isBetaMode?: boolean;
}

export const DebugWidget: React.FC<DebugWidgetProps> = ({
  isConnected,
  isLoading,
  voiceProvider,
  openAIConnected,
  agentVoiceConnected,
  realtimeSDKConnected,
  isBetaMode
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [logs, setLogs] = useState<DebugLog[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showAllLogs, setShowAllLogs] = useState(true); // Default to showing ALL logs

  // Intercept console logs
  useEffect(() => {
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;
    const pendingLogs: DebugLog[] = [];
    let flushScheduled = false;

    const flushLogs = () => {
      if (pendingLogs.length > 0) {
        const logsToAdd = [...pendingLogs];
        pendingLogs.length = 0;

        setLogs(prev => {
          const updated = [...prev, ...logsToAdd];
          // Keep last 500 logs (increased for better debugging)
          return updated.slice(-500);
        });
      }
      flushScheduled = false;
    };

    const addLog = (level: 'info' | 'warn' | 'error' | 'success', category: string, ...args: any[]) => {
      const message = args.map(arg =>
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ');

      const log: DebugLog = {
        timestamp: new Date().toLocaleTimeString(),
        level,
        category,
        message
      };

      pendingLogs.push(log);

      // Batch updates using queueMicrotask
      if (!flushScheduled) {
        flushScheduled = true;
        queueMicrotask(flushLogs);
      }
    };

    console.log = (...args: any[]) => {
      originalLog(...args);
      const message = args.join(' ');

      let category = 'General';
      let level: 'info' | 'success' = 'info';

      if (message.includes('🚨')) category = 'DEBUG';
      else if (message.includes('[TTS')) category = 'TTS';
      else if (message.includes('[AGENT')) category = 'Agent';
      else if (message.includes('OpenAI') || message.includes('OPENAI')) category = 'OpenAI';
      else if (message.includes('connected') || message.includes('✅')) {
        category = 'Connection';
        level = 'success';
      }

      addLog(level, category, ...args);
    };

    console.warn = (...args: any[]) => {
      originalWarn(...args);
      addLog('warn', 'Warning', ...args);
    };

    console.error = (...args: any[]) => {
      originalError(...args);
      addLog('error', 'Error', ...args);
    };

    return () => {
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
    };
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && isExpanded) {
      const logsContainer = document.querySelector('.debug-logs-container');
      if (logsContainer) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
      }
    }
  }, [logs, autoScroll, isExpanded]);

  const clearLogs = () => setLogs([]);

  // Show all logs or filtered logs based on toggle
  const displayLogs = showAllLogs ? logs : logs.filter(log =>
    log.category === 'DEBUG' ||
    log.category === 'TTS' ||
    log.category === 'Agent' ||
    log.category === 'OpenAI' ||
    log.category === 'Connection' ||
    log.level === 'error'
  );

  return (
    <div className={`debug-widget ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="debug-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="debug-title">
          <span className="debug-icon">🔧</span>
          <span>Debug Tools</span>
          {!isExpanded && (
            <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '●' : '○'}
            </span>
          )}
        </div>
        <button className="toggle-btn">{isExpanded ? '−' : '+'}</button>
      </div>

      {isExpanded && (
        <div className="debug-content">
          {/* Status Panel */}
          <div className="debug-section">
            <h4>System Status</h4>
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">Provider:</span>
                <span className="status-value">
                  {voiceProvider}
                  {isBetaMode && <span style={{color: '#ff6b35', fontSize: '0.8em', marginLeft: '4px'}}>🧪 BETA</span>}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Connected:</span>
                <span className={`status-value ${isConnected ? 'connected' : 'disconnected'}`}>
                  {isConnected ? '✅ Yes' : '❌ No'}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Loading:</span>
                <span className="status-value">{isLoading ? '⏳ Yes' : 'No'}</span>
              </div>
              {voiceProvider === 'agent' && (
                <>
                  <div className="status-item">
                    <span className="status-label">OpenAI Connected:</span>
                    <span className={`status-value ${openAIConnected ? 'connected' : 'disconnected'}`}>
                      {openAIConnected ? '✅ Yes' : '❌ No'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Agent Voice State:</span>
                    <span className={`status-value ${agentVoiceConnected ? 'connected' : 'disconnected'}`}>
                      {agentVoiceConnected ? '✅ Connected' : '❌ Disconnected'}
                    </span>
                  </div>
                </>
              )}
              {voiceProvider === 'realtime-sdk' && (
                <div className="status-item">
                  <span className="status-label">Realtime SDK:</span>
                  <span className={`status-value ${realtimeSDKConnected ? 'connected' : 'disconnected'}`}>
                    {realtimeSDKConnected ? '✅ Connected' : '❌ Disconnected'}
                    <span style={{color: '#00ff88', fontSize: '0.8em', marginLeft: '4px'}}>Direct OpenAI + Agents SDK</span>
                  </span>
                </div>
              )}
            </div>

            {/* Test Instructions */}
            <div style={{ marginTop: '12px', padding: '12px', background: '#1a1a1a', borderRadius: '6px', border: '1px solid #333' }}>
              <h5 style={{ margin: '0 0 8px 0', color: '#00d4ff', fontSize: '11px' }}>🧪 TTS Test Procedure:</h5>
              <ol style={{ margin: 0, paddingLeft: '20px', fontSize: '10px', color: '#888', lineHeight: '1.6' }}>
                <li>Click "Clear" button below</li>
                <li>Click microphone 🎙️ (bottom-right)</li>
                <li>Wait for "Connected: ✅ Yes"</li>
                <li>Say: "What is Apple stock price?"</li>
                <li>Wait 10 seconds</li>
                <li>Look for [TTS] logs below</li>
              </ol>
            </div>
          </div>

          {/* Logs Panel */}
          <div className="debug-section">
            <div className="logs-header">
              <h4>Live Logs ({displayLogs.length}{showAllLogs ? ' - ALL' : ' - FILTERED'})</h4>
              <div className="logs-controls">
                <label className="auto-scroll-toggle">
                  <input
                    type="checkbox"
                    checked={showAllLogs}
                    onChange={(e) => setShowAllLogs(e.target.checked)}
                  />
                  Show All
                </label>
                <label className="auto-scroll-toggle">
                  <input
                    type="checkbox"
                    checked={autoScroll}
                    onChange={(e) => setAutoScroll(e.target.checked)}
                  />
                  Auto-scroll
                </label>
                <button onClick={clearLogs} className="clear-btn">Clear</button>
              </div>
            </div>
            <div className="debug-logs-container">
              {displayLogs.length === 0 ? (
                <div className="no-logs">No logs yet. Interact with the voice system to see diagnostics.</div>
              ) : (
                displayLogs.map((log, index) => (
                  <div key={index} className={`log-entry log-${log.level}`}>
                    <span className="log-timestamp">{log.timestamp}</span>
                    <span className={`log-category category-${log.category.toLowerCase()}`}>
                      {log.category}
                    </span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
