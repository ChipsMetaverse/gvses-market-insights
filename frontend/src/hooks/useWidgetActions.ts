import { useCallback } from 'react';
import type { WidgetAction } from '../components/widgets';

interface ChartAPI {
  highlightLevel: (level: string, price: number) => void;
  togglePattern: (patternId: string, visible: boolean) => void;
  setTimeframe: (timeframe: string) => void;
  setChartType: (type: string) => void;
  setDrawingTool: (tool: string) => void;
  clearAllDrawings: () => void;
  toggleIndicator: (name: string) => void;
}

interface UseWidgetActionsOptions {
  chartRef?: React.RefObject<ChartAPI>;
  onRefresh?: () => void;
  onFullscreen?: () => void;
  onClose?: () => void;
}

export function useWidgetActions({
  chartRef,
  onRefresh,
  onFullscreen,
  onClose,
}: UseWidgetActionsOptions = {}) {
  const handleAction = useCallback(
    (action: WidgetAction) => {
      console.log('[WidgetActions] Handling action:', action);

      switch (action.type) {
        // Economic Calendar Actions
        case 'calendar.refresh':
          console.log('[Calendar] Refreshing with period:', action.payload.period);
          onRefresh?.();
          break;

        case 'calendar.setPeriod':
          console.log('[Calendar] Setting period to:', action.payload.value);
          break;

        // Market News Actions
        case 'news.refresh':
          console.log('[News] Refreshing news feed');
          onRefresh?.();
          break;

        case 'news.setSource':
          console.log('[News] Setting source to:', action.payload.value);
          break;

        case 'browser.openUrl':
          console.log('[Browser] Opening URL:', action.payload.url);
          window.open(action.payload.url, '_blank', 'noopener,noreferrer');
          break;

        // Technical Levels Actions
        case 'levels.refresh':
          console.log('[Levels] Refreshing technical levels');
          onRefresh?.();
          break;

        case 'chart.highlightLevel':
          console.log(
            '[Chart] Highlighting level:',
            action.payload.level,
            'at price:',
            action.payload.price
          );
          if (chartRef?.current) {
            chartRef.current.highlightLevel(action.payload.level, action.payload.price);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        // Pattern Detection Actions
        case 'patterns.refresh':
          console.log('[Patterns] Refreshing pattern detection');
          onRefresh?.();
          break;

        case 'patterns.toggleVisibility':
          console.log(
            '[Patterns] Toggling pattern:',
            action.payload.patternId,
            'visible:',
            action.payload.visible
          );
          if (chartRef?.current) {
            chartRef.current.togglePattern(action.payload.patternId, action.payload.visible);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'patterns.filterCategory':
          console.log('[Patterns] Filtering by category:', action.payload.category);
          break;

        // Trading Chart Actions
        case 'chart.setTimeframe':
          console.log('[Chart] Setting timeframe to:', action.payload.value);
          if (chartRef?.current) {
            chartRef.current.setTimeframe(action.payload.value);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'chart.setType':
          console.log('[Chart] Setting chart type to:', action.payload.value);
          if (chartRef?.current) {
            chartRef.current.setChartType(action.payload.value);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'chart.activateDrawingTool':
          console.log('[Chart] Activating drawing tool:', action.payload.value);
          if (chartRef?.current) {
            chartRef.current.setDrawingTool(action.payload.value);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'chart.clearDrawings':
          console.log('[Chart] Clearing all drawings');
          if (chartRef?.current) {
            chartRef.current.clearAllDrawings();
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'chart.toggleIndicator':
          console.log('[Chart] Toggling indicator:', action.payload.name);
          if (chartRef?.current) {
            chartRef.current.toggleIndicator(action.payload.name);
          } else {
            console.warn('[Chart] Chart ref not available');
          }
          break;

        case 'chart.fullscreen':
          console.log('[Chart] Entering fullscreen mode');
          onFullscreen?.();
          break;

        case 'chart.close':
          console.log('[Chart] Closing widget');
          onClose?.();
          break;

        default:
          console.warn('[WidgetActions] Unhandled action type:', (action as any).type);
      }
    },
    [chartRef, onRefresh, onFullscreen, onClose]
  );

  return {
    handleAction,
  };
}
