import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import { forexDataService } from '../../services/forexDataService';
import type { ForexCalendarEvent, ForexTimePeriod } from '../../types/forex';

interface EconomicCalendarWidgetProps {
  onClose?: () => void;
  onAction?: (action: WidgetAction) => void;
}

type WidgetAction =
  | { type: 'calendar.refresh'; payload: { period: ForexTimePeriod; impact: 'high' } }
  | { type: 'calendar.setPeriod'; payload: { value: ForexTimePeriod } };

const PERIOD_OPTIONS: Array<{ label: string; value: ForexTimePeriod }> = [
  { label: 'Today', value: 'today' },
  { label: 'Tomorrow', value: 'tomorrow' },
  { label: 'This Week', value: 'week' },
  { label: 'Next Week', value: 'next-week' },
];

export function EconomicCalendarWidget({ onClose, onAction }: EconomicCalendarWidgetProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<ForexTimePeriod>('today');
  const [events, setEvents] = useState<ForexCalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchCalendar = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!opts?.silent) {
        setIsLoading(true);
      }
      setError(null);

      try {
        const response = await forexDataService.getCalendar({
          timePeriod: selectedPeriod,
          impact: 'high', // Always high-impact only
        });
        setEvents(response.events || []);
        setLastUpdated(new Date());

        // Notify parent of refresh action
        onAction?.({
          type: 'calendar.refresh',
          payload: { period: selectedPeriod, impact: 'high' },
        });
      } catch (err) {
        console.error('Failed to load Forex calendar', err);
        setError('Unable to load economic calendar. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [selectedPeriod, onAction]
  );

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  const handlePeriodChange = (period: ForexTimePeriod) => {
    setSelectedPeriod(period);
    onAction?.({
      type: 'calendar.setPeriod',
      payload: { value: period },
    });
  };

  const handleRefresh = () => {
    fetchCalendar({ silent: true });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900">Economic Calendar</h3>
            <p className="text-sm text-gray-500 mt-1">ForexFactory events • High-impact only</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
            aria-label="Refresh economic calendar"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="ml-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Period Filters */}
        <div className="px-6 py-4 border-b">
          <div className="flex gap-2">
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => handlePeriodChange(option.value)}
                className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                  selectedPeriod === option.value
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Events List */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {isLoading && !error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mb-4" />
              <p className="text-sm text-gray-600">Loading macro events…</p>
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-sm text-gray-600">No high-impact events for the selected period.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {events.map((event) => {
                const eventTime = new Date(event.datetime_utc);
                const timeLabel = eventTime.toLocaleTimeString(undefined, {
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false,
                });

                return (
                  <div
                    key={event.id}
                    className="flex gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    {/* Impact Indicator */}
                    <div className="flex-shrink-0">
                      <div className="w-1 h-full bg-red-500 rounded-full" />
                    </div>

                    {/* Time & Currency */}
                    <div className="flex-shrink-0 text-sm">
                      <div className="font-semibold text-gray-900">{timeLabel}</div>
                      <div className="text-xs text-gray-500 mt-1">{event.currency}</div>
                    </div>

                    {/* Event Content */}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 mb-2">{event.title}</div>

                      {/* Metrics */}
                      <div className="flex flex-wrap gap-2 text-xs">
                        {event.actual && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded font-medium">
                            Actual: {event.actual}
                          </span>
                        )}
                        {event.forecast && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded">
                            Forecast: {event.forecast}
                          </span>
                        )}
                        {event.previous && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded">
                            Previous: {event.previous}
                          </span>
                        )}
                        {event.revised && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                            Revised: {event.revised}
                          </span>
                        )}
                      </div>

                      {/* Detail Link */}
                      {event.detail_url && (
                        <a
                          href={event.detail_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 mt-2 text-xs text-blue-600 hover:text-blue-800"
                        >
                          View details
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                            />
                          </svg>
                        </a>
                      )}

                      {/* Notes */}
                      {event.notes && (
                        <p className="mt-2 text-xs text-gray-600">{event.notes}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        {lastUpdated && (
          <div className="px-6 py-4 border-t bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>
                Updated {lastUpdated.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
              </span>
              <span className="flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-red-500 rounded-full" />
                High-impact events only
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
