import { useState } from 'react'
import './ChartToolbar.css'

export interface ChartToolbarProps {
  onIndicatorToggle?: (indicator: string) => void
  onDrawingToolSelect?: (tool: string) => void
  onChartTypeChange?: (type: string) => void
  onTimeframeChange?: (timeframe: string) => void
}

export function ChartToolbar({
  onIndicatorToggle,
  onDrawingToolSelect,
  onChartTypeChange,
  onTimeframeChange
}: ChartToolbarProps) {
  const [activeDrawingTool, setActiveDrawingTool] = useState<string | null>(null)
  const [chartType, setChartType] = useState('candlestick')
  const [showIndicators, setShowIndicators] = useState(false)
  const [showDrawingTools, setShowDrawingTools] = useState(false)

  const drawingTools = [
    { id: 'trendline', icon: '📈', label: 'Trend Line' },
    { id: 'horizontal', icon: '━', label: 'Horizontal Line' },
    { id: 'vertical', icon: '┃', label: 'Vertical Line' },
    { id: 'rectangle', icon: '▭', label: 'Rectangle' },
    { id: 'fibonacci', icon: 'φ', label: 'Fibonacci Retracement' },
    { id: 'text', icon: 'A', label: 'Text' },
  ]

  const indicators = [
    { id: 'ma', label: 'Moving Averages' },
    { id: 'bollinger', label: 'Bollinger Bands' },
    { id: 'rsi', label: 'RSI' },
    { id: 'macd', label: 'MACD' },
    { id: 'volume', label: 'Volume' },
    { id: 'stochastic', label: 'Stochastic' },
  ]

  const chartTypes = [
    { id: 'candlestick', icon: '📊', label: 'Candlestick' },
    { id: 'line', icon: '📉', label: 'Line' },
    { id: 'area', icon: '📈', label: 'Area' },
    { id: 'bars', icon: '▅', label: 'Bars' },
  ]

  const handleDrawingToolClick = (toolId: string) => {
    const newTool = activeDrawingTool === toolId ? null : toolId
    setActiveDrawingTool(newTool)
    onDrawingToolSelect?.(newTool || 'none')
  }

  const handleChartTypeClick = (typeId: string) => {
    setChartType(typeId)
    onChartTypeChange?.(typeId)
  }

  return (
    <div className="chart-toolbar">
      {/* Chart Type Selector */}
      <div className="toolbar-section">
        <div className="toolbar-dropdown">
          <button className="toolbar-button chart-type-button">
            <span className="button-icon">{chartTypes.find(t => t.id === chartType)?.icon}</span>
            <span className="button-label">{chartTypes.find(t => t.id === chartType)?.label}</span>
            <span className="dropdown-arrow">▼</span>
          </button>
          <div className="dropdown-menu chart-type-menu">
            {chartTypes.map(type => (
              <button
                key={type.id}
                className={`dropdown-item ${chartType === type.id ? 'active' : ''}`}
                onClick={() => handleChartTypeClick(type.id)}
              >
                <span className="item-icon">{type.icon}</span>
                <span>{type.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="toolbar-divider" />

      {/* Drawing Tools */}
      <div className="toolbar-section">
        <button
          className={`toolbar-button ${showDrawingTools ? 'active' : ''}`}
          onClick={() => setShowDrawingTools(!showDrawingTools)}
          title="Drawing Tools"
        >
          <span className="button-icon">✏️</span>
          <span className="button-label">Draw</span>
        </button>
        {showDrawingTools && (
          <div className="toolbar-dropdown-panel drawing-tools-panel">
            <div className="panel-header">Drawing Tools</div>
            <div className="tool-grid">
              {drawingTools.map(tool => (
                <button
                  key={tool.id}
                  className={`tool-button ${activeDrawingTool === tool.id ? 'active' : ''}`}
                  onClick={() => handleDrawingToolClick(tool.id)}
                  title={tool.label}
                >
                  <span className="tool-icon">{tool.icon}</span>
                  <span className="tool-label">{tool.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="toolbar-divider" />

      {/* Indicators */}
      <div className="toolbar-section">
        <button
          className={`toolbar-button ${showIndicators ? 'active' : ''}`}
          onClick={() => setShowIndicators(!showIndicators)}
          title="Indicators"
        >
          <span className="button-icon">📊</span>
          <span className="button-label">Indicators</span>
        </button>
        {showIndicators && (
          <div className="toolbar-dropdown-panel indicators-panel">
            <div className="panel-header">Technical Indicators</div>
            <div className="indicator-list">
              {indicators.map(indicator => (
                <button
                  key={indicator.id}
                  className="indicator-item"
                  onClick={() => onIndicatorToggle?.(indicator.id)}
                >
                  <span className="indicator-checkbox">☐</span>
                  <span>{indicator.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="toolbar-divider" />

      {/* Quick Actions */}
      <div className="toolbar-section toolbar-actions">
        <button className="toolbar-button" title="Zoom In">
          <span className="button-icon">🔍+</span>
        </button>
        <button className="toolbar-button" title="Zoom Out">
          <span className="button-icon">🔍-</span>
        </button>
        <button className="toolbar-button" title="Fit Content">
          <span className="button-icon">⊞</span>
        </button>
        <button className="toolbar-button" title="Screenshot">
          <span className="button-icon">📷</span>
        </button>
        <button className="toolbar-button" title="Settings">
          <span className="button-icon">⚙️</span>
        </button>
      </div>
    </div>
  )
}
