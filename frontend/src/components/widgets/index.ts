// Widget Components
export { EconomicCalendarWidget } from './EconomicCalendarWidget';
export { MarketNewsFeedWidget } from './MarketNewsFeedWidget';
export { TechnicalLevelsWidget } from './TechnicalLevelsWidget';
export { PatternDetectionWidget } from './PatternDetectionWidget';
export { TradingChartDisplayWidget } from './TradingChartDisplayWidget';

// Widget Types
export type WidgetType =
  | 'economic-calendar'
  | 'market-news'
  | 'technical-levels'
  | 'pattern-detection'
  | 'trading-chart';

// Widget Action Types
export type WidgetAction =
  // Economic Calendar Actions
  | { type: 'calendar.refresh'; payload: { period: string; impact: 'high' } }
  | { type: 'calendar.setPeriod'; payload: { value: string } }
  // Market News Actions
  | { type: 'news.refresh' }
  | { type: 'news.setSource'; payload: { value: 'all' | 'cnbc' | 'yahoo' } }
  | { type: 'browser.openUrl'; payload: { url: string } }
  // Technical Levels Actions
  | { type: 'levels.refresh' }
  | { type: 'chart.highlightLevel'; payload: { level: 'sellHigh' | 'buyLow' | 'btd'; price: number } }
  // Pattern Detection Actions
  | { type: 'patterns.refresh' }
  | { type: 'patterns.toggleVisibility'; payload: { patternId: string; visible: boolean } }
  | { type: 'patterns.filterCategory'; payload: { category: string } }
  // Trading Chart Actions
  | { type: 'chart.setTimeframe'; payload: { value: string } }
  | { type: 'chart.setType'; payload: { value: string } }
  | { type: 'chart.activateDrawingTool'; payload: { value: string } }
  | { type: 'chart.clearDrawings' }
  | { type: 'chart.toggleIndicator'; payload: { name: string } }
  | { type: 'chart.fullscreen' }
  | { type: 'chart.close' };
