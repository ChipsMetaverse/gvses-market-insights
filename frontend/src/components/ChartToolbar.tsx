import { useState, useRef, useEffect } from 'react'
import './ChartToolbar.css'

export interface ChartToolbarProps {
  onIndicatorToggle?: (indicator: string) => void
  onDrawingToolSelect?: (tool: string) => void
  onTimeframeChange?: (timeframe: string) => void
}

export function ChartToolbar({
  onIndicatorToggle,
  onDrawingToolSelect,
  onTimeframeChange
}: ChartToolbarProps) {
  const [activeDrawingTool, setActiveDrawingTool] = useState<string | null>(null)
  const [showIndicators, setShowIndicators] = useState(false)
  const [showDrawingTools, setShowDrawingTools] = useState(false)
  
  // Refs for auto-hide functionality
  const drawingToolsRef = useRef<HTMLDivElement>(null)
  const indicatorsRef = useRef<HTMLDivElement>(null)
  const drawingButtonRef = useRef<HTMLButtonElement>(null)
  const indicatorsButtonRef = useRef<HTMLButtonElement>(null)

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

  const handleDrawingToolClick = (toolId: string) => {
    const newTool = activeDrawingTool === toolId ? null : toolId
    setActiveDrawingTool(newTool)
    onDrawingToolSelect?.(newTool || 'none')
  }

  // Auto-hide functionality
  useEffect(() => {
    const handleMouseLeave = (panelType: 'drawing' | 'indicators') => {
      return (event: MouseEvent) => {
        const currentTarget = event.currentTarget as HTMLElement
        const relatedTarget = event.relatedTarget as HTMLElement
        
        // Don't hide if mouse moved to the related button or is still within the panel
        if (panelType === 'drawing') {
          if (relatedTarget && (
            drawingButtonRef.current?.contains(relatedTarget) ||
            currentTarget.contains(relatedTarget)
          )) {
            return
          }
          setShowDrawingTools(false)
        } else if (panelType === 'indicators') {
          if (relatedTarget && (
            indicatorsButtonRef.current?.contains(relatedTarget) ||
            currentTarget.contains(relatedTarget)
          )) {
            return
          }
          setShowIndicators(false)
        }
      }
    }

    // Attach mouse leave events
    const drawingPanel = drawingToolsRef.current
    const indicatorsPanel = indicatorsRef.current
    const cleanupFunctions: (() => void)[] = []
    
    if (drawingPanel && showDrawingTools) {
      const drawingLeaveHandler = handleMouseLeave('drawing')
      drawingPanel.addEventListener('mouseleave', drawingLeaveHandler)
      cleanupFunctions.push(() => drawingPanel.removeEventListener('mouseleave', drawingLeaveHandler))
    }
    
    if (indicatorsPanel && showIndicators) {
      const indicatorsLeaveHandler = handleMouseLeave('indicators')
      indicatorsPanel.addEventListener('mouseleave', indicatorsLeaveHandler)
      cleanupFunctions.push(() => indicatorsPanel.removeEventListener('mouseleave', indicatorsLeaveHandler))
    }

    // Return cleanup function that removes all event listeners
    return () => {
      cleanupFunctions.forEach(cleanup => cleanup())
    }
  }, [showDrawingTools, showIndicators])

  return (
    <div className="chart-toolbar">
      {/* Drawing Tools */}
      <div className="toolbar-section">
        <button
          ref={drawingButtonRef}
          className={`toolbar-button ${showDrawingTools ? 'active' : ''}`}
          onClick={() => setShowDrawingTools(!showDrawingTools)}
          title="Drawing Tools"
        >
          <span className="button-icon">✏️</span>
          <span className="button-label">Draw</span>
        </button>
        {showDrawingTools && (
          <div ref={drawingToolsRef} className="toolbar-dropdown-panel drawing-tools-panel">
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
          ref={indicatorsButtonRef}
          className={`toolbar-button ${showIndicators ? 'active' : ''}`}
          onClick={() => setShowIndicators(!showIndicators)}
          title="Indicators"
        >
          <span className="button-icon">📊</span>
          <span className="button-label">Indicators</span>
        </button>
        {showIndicators && (
          <div ref={indicatorsRef} className="toolbar-dropdown-panel indicators-panel">
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
