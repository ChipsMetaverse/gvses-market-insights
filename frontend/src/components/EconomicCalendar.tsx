import React, { useCallback, useEffect, useMemo, useState } from 'react';

import { forexDataService } from '../services/forexDataService';
import type {
  ForexCalendarEvent,
  ForexCalendarResponse,
  ForexImpact,
  ForexTimePeriod,
} from '../types/forex';
import './EconomicCalendar.css';

type ImpactFilter = ForexImpact | 'all';

const PERIOD_OPTIONS: Array<{ label: string; value: ForexTimePeriod }> = [
  { label: 'Today', value: 'today' },
  { label: 'Tomorrow', value: 'tomorrow' },
  { label: 'This Week', value: 'this_week' },
  { label: 'Next Week', value: 'next_week' },
];

const IMPACT_OPTIONS: Array<{ label: string; value: ImpactFilter; emoji: string }> = [
  { label: 'All', value: 'all', emoji: '🌐' },
  { label: 'High', value: 'high', emoji: '🔴' },
  { label: 'Medium', value: 'medium', emoji: '🟡' },
  { label: 'Low', value: 'low', emoji: '🟢' },
];

interface GroupedEvents {
  date: string;
  events: ForexCalendarEvent[];
}

/**
 * Economic Calendar Component
 * - Simple event list grouped by date
 * - Period and impact filters
 * - Clean timeline layout
 */
export const EconomicCalendar: React.FC = () => {
  const [timePeriod, setTimePeriod] = useState<ForexTimePeriod>('today');
  const [impact] = useState<ImpactFilter>('high'); // Fixed impact filter for high-impact events
  const [calendar, setCalendar] = useState<ForexCalendarResponse | null>(null);
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
        const impactFilter = impact === 'all' ? undefined : impact;
        const response = await forexDataService.getCalendar({
          timePeriod,
          impact: impactFilter,
        });
        setCalendar(response);
        setLastUpdated(new Date());
      } catch (err) {
        console.error('Failed to load Forex calendar', err);
        setError('Unable to load economic calendar. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [impact, timePeriod]
  );

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  const groupedEvents: GroupedEvents[] = useMemo(() => {
    if (!calendar?.events?.length) {
      return [];
    }

    const groups = new Map<string, ForexCalendarEvent[]>();
    calendar.events.forEach((event) => {
      const dateKey = new Date(event.datetime_utc).toLocaleDateString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });
      const existing = groups.get(dateKey) ?? [];
      existing.push(event);
      groups.set(dateKey, existing);
    });

    return Array.from(groups.entries()).map(([date, events]) => ({
      date,
      events,
    }));
  }, [calendar]);

  const handleRefresh = () => {
    fetchCalendar({ silent: true });
  };

  return (
    <section className="economic-calendar" aria-labelledby="economic-calendar-title">
      <div className="calendar-header">
        <div>
          <h3 id="economic-calendar-title">Economic Calendar</h3>
          <p className="calendar-subtitle">
            Stay ahead of high-impact macro events.
          </p>
        </div>
        <div className="calendar-actions">
          <button
            type="button"
            className="calendar-refresh"
            onClick={handleRefresh}
            aria-label="Refresh economic calendar"
          >
            ⟳ Refresh
          </button>
        </div>
      </div>

      <div className="calendar-filters" role="group" aria-label="Economic calendar filters">
        <div className="filter-section">
          <span className="filter-label">Period</span>
          <div className="filter-pills">
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`pill ${timePeriod === option.value ? 'pill--active' : ''}`}
                onClick={() => setTimePeriod(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="calendar-error" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="calendar-loading" role="status">
          <span className="spinner" aria-hidden="true" />
          Loading macro events…
        </div>
      ) : (
        <div className="calendar-timeline" aria-live="polite">
          {groupedEvents.length === 0 ? (
            <div className="calendar-empty">No events for the selected filters.</div>
          ) : (
            groupedEvents.map((group) => (
              <section key={group.date} className="timeline-day">
                <header className="timeline-day__header">
                  <h4>{group.date}</h4>
                </header>
                <ol className="timeline-day__list">
                  {group.events.map((event) => {
                    const eventTime = new Date(event.datetime_utc);
                    const timeLabel = eventTime.toLocaleTimeString(undefined, {
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    });
                    return (
                      <li key={event.id} className="timeline-event">
                        <div className="timeline-event__indicator" data-impact={event.impact} />
                        <div className="timeline-event__time">
                          <span>{timeLabel}</span>
                          <span className="timeline-event__currency">{event.currency}</span>
                        </div>
                        <div className="timeline-event__content">
                          <div className="timeline-event__title" title={event.title}>
                            {event.title}
                          </div>
                          <div className="timeline-event__metrics">
                            {event.actual && (
                              <span className="metric Tag--actual" aria-label="Actual value">
                                Actual: {event.actual}
                              </span>
                            )}
                            {event.forecast && (
                              <span className="metric" aria-label="Forecast value">
                                Forecast: {event.forecast}
                              </span>
                            )}
                            {event.previous && (
                              <span className="metric" aria-label="Previous value">
                                Previous: {event.previous}
                              </span>
                            )}
                            {event.revised && (
                              <span className="metric" aria-label="Revised value">
                                Revised: {event.revised}
                              </span>
                            )}
                          </div>
                          {event.detail_url && (
                            <a
                              className="timeline-event__link"
                              href={event.detail_url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              View details ↗
                            </a>
                          )}
                          {event.notes && (
                            <p className="timeline-event__notes">{event.notes}</p>
                          )}
                        </div>
                      </li>
                    );
                  })}
                </ol>
              </section>
            ))
          )}
        </div>
      )}

      {lastUpdated && (
        <p className="calendar-updated" aria-live="polite">
          Updated {lastUpdated.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
        </p>
      )}
    </section>
  );
};
