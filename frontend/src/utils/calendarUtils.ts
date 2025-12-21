/**
 * Utility functions for Economic Calendar variants
 */

export interface EconomicEvent {
  id: string;
  title: string;
  currency: string;
  impact: 'high' | 'medium' | 'low';
  datetime: string;
  datetime_utc: string;
  datetime_local: string;
  forecast?: string | null;
  previous?: string | null;
  actual?: string | null;
}

/**
 * Determine if calendar should auto-expand to show preview
 * Logic: If today has 2 or fewer events, show tomorrow preview
 */
export function shouldAutoExpand(todayEvents: EconomicEvent[]): boolean {
  return todayEvents.length <= 2;
}

/**
 * Format countdown timer for upcoming events
 * Examples:
 * - "in 9h 45m" (future)
 * - "in 30m" (soon)
 * - "2h ago" (past)
 * - "now" (happening)
 */
export function formatCountdown(eventTime: string): string {
  const now = new Date();
  const event = new Date(eventTime);
  const diffMs = event.getTime() - now.getTime();
  const absDiffMs = Math.abs(diffMs);

  // Less than 1 minute
  if (absDiffMs < 60 * 1000) {
    return 'now';
  }

  const hours = Math.floor(absDiffMs / (1000 * 60 * 60));
  const minutes = Math.floor((absDiffMs % (1000 * 60 * 60)) / (1000 * 60));

  if (diffMs < 0) {
    // Past event
    if (hours > 0) {
      return `${hours}h ago`;
    }
    return `${minutes}m ago`;
  } else {
    // Future event
    if (hours > 0) {
      return `in ${hours}h ${minutes}m`;
    }
    return `in ${minutes}m`;
  }
}

/**
 * Get impact emoji for visual clarity
 */
export function getImpactEmoji(impact: string): string {
  switch (impact.toLowerCase()) {
    case 'high':
      return '🔴';
    case 'medium':
      return '🟡';
    case 'low':
      return '⚪';
    default:
      return '⚫';
  }
}

/**
 * Get impact color class for styling
 */
export function getImpactColorClass(impact: string): string {
  switch (impact.toLowerCase()) {
    case 'high':
      return 'impact-high';
    case 'medium':
      return 'impact-medium';
    case 'low':
      return 'impact-low';
    default:
      return 'impact-unknown';
  }
}

/**
 * Format forecast/previous/actual values for display
 * Returns null if no data available
 */
export function formatEventMetrics(event: EconomicEvent): string | null {
  const parts: string[] = [];

  if (event.forecast) {
    parts.push(`Forecast: ${event.forecast}`);
  }
  if (event.previous) {
    parts.push(`Previous: ${event.previous}`);
  }
  if (event.actual) {
    parts.push(`Actual: ${event.actual}`);
  }

  return parts.length > 0 ? parts.join(' | ') : null;
}

/**
 * Group events by date
 */
export function groupEventsByDate(events: EconomicEvent[]): Record<string, EconomicEvent[]> {
  const grouped: Record<string, EconomicEvent[]> = {};

  events.forEach((event) => {
    const date = new Date(event.datetime_utc).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });

    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(event);
  });

  return grouped;
}

/**
 * Get relative time label
 * Examples: "Today", "Tomorrow", "Monday", "Dec 5"
 */
export function getRelativeTimeLabel(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);

  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  const diffDays = Math.floor((eventDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  if (diffDays === -1) return 'Yesterday';
  if (diffDays > 1 && diffDays <= 7) {
    return date.toLocaleDateString('en-US', { weekday: 'long' });
  }

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Sort events by datetime (ascending)
 */
export function sortEventsByTime(events: EconomicEvent[]): EconomicEvent[] {
  return [...events].sort((a, b) => {
    return new Date(a.datetime_utc).getTime() - new Date(b.datetime_utc).getTime();
  });
}

/**
 * Filter events by time period
 */
export function filterEventsByPeriod(
  events: EconomicEvent[],
  period: 'today' | 'tomorrow' | 'this_week' | 'next_week'
): EconomicEvent[] {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  return events.filter((event) => {
    const eventDate = new Date(event.datetime_utc);
    const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
    const diffDays = Math.floor((eventDay.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    switch (period) {
      case 'today':
        return diffDays === 0;
      case 'tomorrow':
        return diffDays === 1;
      case 'this_week':
        return diffDays >= 0 && diffDays < 7;
      case 'next_week':
        return diffDays >= 7 && diffDays < 14;
      default:
        return true;
    }
  });
}

/**
 * Get summary text for week events
 * Example: "Mon: NFP, CPI | Wed: FOMC | Fri: GDP"
 */
export function getWeekSummary(events: EconomicEvent[]): string {
  const grouped = groupEventsByDate(events);
  const summaries: string[] = [];

  Object.entries(grouped).forEach(([date, dateEvents]) => {
    const day = new Date(dateEvents[0].datetime_utc).toLocaleDateString('en-US', {
      weekday: 'short',
    });
    const titles = dateEvents.map((e) => e.title.split(' ')[0]).slice(0, 2); // First 2 events
    summaries.push(`${day}: ${titles.join(', ')}`);
  });

  return summaries.join(' | ');
}

/**
 * Calculate time until next high-impact event
 */
export function getNextHighImpactEvent(events: EconomicEvent[]): {
  event: EconomicEvent;
  countdown: string;
} | null {
  const now = new Date();
  const upcoming = events
    .filter((e) => e.impact === 'high' && new Date(e.datetime_utc) > now)
    .sort((a, b) => new Date(a.datetime_utc).getTime() - new Date(b.datetime_utc).getTime());

  if (upcoming.length === 0) return null;

  return {
    event: upcoming[0],
    countdown: formatCountdown(upcoming[0].datetime_utc),
  };
}

/**
 * Format time for display (24h or 12h based on locale)
 */
export function formatEventTime(dateStr: string, use24Hour = false): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: !use24Hour,
  });
}

/**
 * Determine if event is happening soon (within next hour)
 */
export function isEventSoon(dateStr: string): boolean {
  const now = new Date();
  const event = new Date(dateStr);
  const diffMs = event.getTime() - now.getTime();
  return diffMs > 0 && diffMs < 60 * 60 * 1000; // Within 1 hour
}

/**
 * Get market impact description
 */
export function getImpactDescription(impact: string): string {
  switch (impact.toLowerCase()) {
    case 'high':
      return 'High Impact - Market Moving';
    case 'medium':
      return 'Medium Impact - Watch Closely';
    case 'low':
      return 'Low Impact - Informational';
    default:
      return 'Unknown Impact';
  }
}
