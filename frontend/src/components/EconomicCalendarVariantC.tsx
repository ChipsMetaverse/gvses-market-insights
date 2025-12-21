/**
 * Economic Calendar - Variant C: Calendar Timeline Only
 *
 * Features:
 * - Horizontal calendar timeline with event markers
 * - Real-time economic event data
 * - Compact, professional layout
 * - No technical analysis sections (handled by parent component)
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { forexDataService } from '../services/forexDataService';
import {
  formatCountdown,
  getImpactEmoji,
  sortEventsByTime,
} from '../utils/calendarUtils';
import type {
  ForexCalendarEvent,
  ForexCalendarResponse,
} from '../types/forex';
import './EconomicCalendar.css';
import './EconomicCalendarVariantC.css';

interface EventMarker {
  id: string;
  event: ForexCalendarEvent;
  timestamp: number;
  xPosition: number; // Percentage position on timeline
}

interface GroupedMarker {
  id: string;
  events: ForexCalendarEvent[];
  xPosition: number;
  timestamp: number;
}

export const EconomicCalendarVariantC: React.FC = () => {
  // Forex Calendar State
  const [calendar, setCalendar] = useState<ForexCalendarResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [hoveredEvent, setHoveredEvent] = useState<ForexCalendarEvent | null>(null);
  const [hoveredGroup, setHoveredGroup] = useState<GroupedMarker | null>(null);

  // Hover timeout for smooth UX
  const hoverTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  // Fetch Forex Calendar (economic events)
  const fetchCalendar = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await forexDataService.getCalendar({
        timePeriod: 'this_week',
        impact: 'high',
      });
      setCalendar(response);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to load Forex calendar', err);
      setError('Unable to load calendar');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch calendar on mount
  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  // Cleanup hover timeout on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

  // Handle marker hover with smooth transitions
  const handleMarkerEnter = (group: GroupedMarker) => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    setHoveredGroup(group);
    setHoveredEvent(group.events[0]);
  };

  const handleMarkerLeave = () => {
    // Delay hiding to allow mouse to move to tooltip
    hoverTimeoutRef.current = setTimeout(() => {
      setHoveredGroup(null);
      setHoveredEvent(null);
    }, 150); // 150ms grace period
  };

  const handleTooltipEnter = () => {
    // Cancel any pending hide timeout when entering tooltip
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
  };

  const handleTooltipLeave = () => {
    // Immediately hide when leaving tooltip
    setHoveredGroup(null);
    setHoveredEvent(null);
  };

  // Calculate event markers with positions on timeline (7-day view)
  const eventMarkers = useMemo<EventMarker[]>(() => {
    if (!calendar?.events) return [];

    const sorted = sortEventsByTime(calendar.events);
    const now = Date.now();
    const dayInMs = 24 * 60 * 60 * 1000;
    const viewStart = now - dayInMs; // 1 day before
    const viewEnd = now + (6 * dayInMs); // 6 days after (week view)
    const viewRangeMs = viewEnd - viewStart;

    return sorted
      .filter(event => {
        const eventTime = new Date(event.datetime_utc).getTime();
        return eventTime >= viewStart && eventTime <= viewEnd;
      })
      .map(event => {
        const eventTime = new Date(event.datetime_utc).getTime();
        const relativePosition = (eventTime - viewStart) / viewRangeMs;
        const xPosition = relativePosition * 100;

        return {
          id: event.id,
          event,
          timestamp: eventTime,
          xPosition: Math.max(0, Math.min(100, xPosition)),
        };
      });
  }, [calendar]);

  // Group nearby markers to prevent overlapping (within 3% of timeline = ~5 hours)
  const groupedMarkers = useMemo<GroupedMarker[]>(() => {
    if (eventMarkers.length === 0) return [];

    const GROUPING_THRESHOLD = 3; // 3% of timeline width
    const groups: GroupedMarker[] = [];
    const sorted = [...eventMarkers].sort((a, b) => a.xPosition - b.xPosition);

    let currentGroup: EventMarker[] = [sorted[0]];
    let groupStart = sorted[0].xPosition;

    for (let i = 1; i < sorted.length; i++) {
      const marker = sorted[i];
      const distance = Math.abs(marker.xPosition - groupStart);

      if (distance <= GROUPING_THRESHOLD) {
        // Add to current group
        currentGroup.push(marker);
      } else {
        // Finalize current group and start new one
        const avgPosition = currentGroup.reduce((sum, m) => sum + m.xPosition, 0) / currentGroup.length;
        groups.push({
          id: `group-${groups.length}`,
          events: currentGroup.map(m => m.event),
          xPosition: avgPosition,
          timestamp: currentGroup[0].timestamp,
        });
        currentGroup = [marker];
        groupStart = marker.xPosition;
      }
    }

    // Add final group
    if (currentGroup.length > 0) {
      const avgPosition = currentGroup.reduce((sum, m) => sum + m.xPosition, 0) / currentGroup.length;
      groups.push({
        id: `group-${groups.length}`,
        events: currentGroup.map(m => m.event),
        xPosition: avgPosition,
        timestamp: currentGroup[0].timestamp,
      });
    }

    return groups;
  }, [eventMarkers]);

  // Calculate dates for timeline
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const sixDaysLater = new Date(now);
  sixDaysLater.setDate(sixDaysLater.getDate() + 6);

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="economic-calendar-variant-c">
        <div className="loading-state">Loading economic calendar...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="economic-calendar-variant-c">
        <div className="error-state">{error}</div>
      </div>
    );
  }

  return (
    <div className="economic-calendar-variant-c">
      {/* Calendar Timeline */}
      <div className="calendar-timeline-section">
        <div className="timeline-axis">
          {/* Timeline labels at top */}
          <div className="timeline-labels">
            <span className="label-start">{formatDate(yesterday)}</span>
            <span className="label-now">{formatDate(now)}</span>
            <span className="label-end">{formatDate(sixDaysLater)}</span>
            <span className="event-count-badge">{eventMarkers.length} events</span>
            <button onClick={fetchCalendar} className="refresh-btn-inline" title="Refresh">⟳</button>
          </div>

          {/* Current time indicator (14.3% = 1 day out of 7 days) */}
          <div className="current-time-line" style={{ left: '14.3%' }}>
            <div className="time-line-marker"></div>
          </div>

          {/* Event markers on timeline - now using grouped markers */}
          <div className="event-markers-layer">
            {groupedMarkers.map(group => (
              <GroupedEventMarker
                key={group.id}
                group={group}
                isHovered={hoveredGroup?.id === group.id}
                onMouseEnter={() => handleMarkerEnter(group)}
                onMouseLeave={handleMarkerLeave}
              />
            ))}
          </div>

          {/* Hover Tooltip - stays open when mouse is over it */}
          {hoveredGroup && (
            <GroupedTooltip
              events={hoveredGroup.events}
              xPosition={hoveredGroup.xPosition}
              onMouseEnter={handleTooltipEnter}
              onMouseLeave={handleTooltipLeave}
            />
          )}
        </div>
      </div>

      {lastUpdated && (
        <p className="calendar-updated" aria-live="polite">
          Updated {lastUpdated.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
        </p>
      )}
    </div>
  );
};

/**
 * Grouped Event Marker Component - Shows count badge when multiple events grouped
 */
interface GroupedEventMarkerProps {
  group: GroupedMarker;
  isHovered: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

const GroupedEventMarker: React.FC<GroupedEventMarkerProps> = ({
  group,
  isHovered,
  onMouseEnter,
  onMouseLeave,
}) => {
  const isPast = group.timestamp < Date.now();
  const isGroup = group.events.length > 1;

  return (
    <div
      className={`event-marker grouped ${isPast ? 'past' : 'future'} ${
        isHovered ? 'hovered' : ''
      }`}
      style={{ left: `${group.xPosition}%` }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      title={isGroup ? `${group.events.length} events` : group.events[0].title}
    >
      <div className="marker-icon">
        {isGroup ? (
          <span className="event-count">{group.events.length}</span>
        ) : (
          <span className="event-dot">🔴</span>
        )}
      </div>
      <div className="marker-line"></div>
    </div>
  );
};

/**
 * Grouped Tooltip Component - Shows all events in a group
 */
interface GroupedTooltipProps {
  events: ForexCalendarEvent[];
  xPosition: number;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

const GroupedTooltip: React.FC<GroupedTooltipProps> = ({
  events,
  xPosition,
  onMouseEnter,
  onMouseLeave
}) => {
  if (!events || events.length === 0) return null;

  return (
    <div
      className="event-tooltip grouped"
      style={{
        left: `${xPosition}%`,
        transform: xPosition > 80 ? 'translateX(-100%)' : 'translateX(0)',
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {events.length > 1 && (
        <div className="tooltip-group-header">
          {events.length} events
        </div>
      )}
      <div className="tooltip-events-list">
        {events.map((event, idx) => {
        const time = new Date(event.datetime_utc).toLocaleString('en-US', {
          weekday: 'short',
          hour: '2-digit',
          minute: '2-digit',
        });
        const countdown = formatCountdown(event.datetime_utc);

        return (
          <div key={event.id} className={`tooltip-event ${idx > 0 ? 'tooltip-divider' : ''}`}>
            <div className="tooltip-header">
              <span className="tooltip-emoji">{getImpactEmoji(event.impact)}</span>
              <span className="tooltip-currency">{event.currency}</span>
              <span className="tooltip-time">{time}</span>
            </div>
            <div className="tooltip-title">{event.title}</div>
            {idx === 0 && <div className="tooltip-countdown">{countdown}</div>}

            {/* Show all event metrics like in detailed list */}
            <div className="tooltip-metrics-container">
              {event.actual && (
                <div className="tooltip-metrics">
                  <span className="metric-label">Actual:</span>
                  <span className="metric-value metric-value--actual">{event.actual}</span>
                </div>
              )}
              {event.forecast && (
                <div className="tooltip-metrics">
                  <span className="metric-label">Forecast:</span>
                  <span className="metric-value">{event.forecast}</span>
                </div>
              )}
              {event.previous && (
                <div className="tooltip-metrics">
                  <span className="metric-label">Previous:</span>
                  <span className="metric-value">{event.previous}</span>
                </div>
              )}
              {event.revised && (
                <div className="tooltip-metrics">
                  <span className="metric-label">Revised:</span>
                  <span className="metric-value">{event.revised}</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
      </div>
    </div>
  );
};
