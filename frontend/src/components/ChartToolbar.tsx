import React from 'react';
import type { Tool } from '../drawings/ToolboxManager';
import './ChartToolbar.css';

export interface ChartToolbarProps {
  setTool?: (tool: Tool) => void;
  onTimeframeChange?: (timeframe: string) => void;
}

export function ChartToolbar({ setTool, onTimeframeChange }: ChartToolbarProps) {
  if (!setTool) {
    return <div className="chart-toolbar">{/* Chart toolbar - indicators removed */}</div>;
  }

  return (
    <div className="chart-toolbar" style={{ display: 'flex', gap: 8, padding: '4px 8px', borderBottom: '1px solid #e5e7eb' }}>
      <button onClick={() => setTool('trendline')} title="Trendline (Alt+T)" style={{ cursor: 'pointer', padding: '4px 8px', border: '1px solid #ccc', borderRadius: '4px', background: '#fff' }}>
        ↗️ Trendline
      </button>
      <button onClick={() => setTool('ray')} title="Ray (Alt+R)" style={{ cursor: 'pointer', padding: '4px 8px', border: '1px solid #ccc', borderRadius: '4px', background: '#fff' }}>
        ➡️ Ray
      </button>
      <button onClick={() => setTool('horizontal')} title="Horizontal (Alt+H)" style={{ cursor: 'pointer', padding: '4px 8px', border: '1px solid #ccc', borderRadius: '4px', background: '#fff' }}>
        — Horizontal
      </button>
      <button onClick={() => setTool('none')} title="Exit (Esc)" style={{ cursor: 'pointer', padding: '4px 8px', border: '1px solid #ccc', borderRadius: '4px', background: '#fff' }}>
        ✕ Cancel
      </button>
    </div>
  );
}
