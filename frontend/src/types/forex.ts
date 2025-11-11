export type ForexImpact = 'high' | 'medium' | 'low' | 'holiday';

export type ForexTimePeriod =
  | 'today'
  | 'tomorrow'
  | 'week'
  | 'next-week'
  | 'custom';

export interface ForexCalendarEvent {
  id: string;
  title: string;
  currency: string;
  impact: ForexImpact;
  timestamp: string;
  previous?: string | null;
  forecast?: string | null;
  actual?: string | null;
  detail_url?: string | null;
  notes?: string | null;
  revised?: string | null;
}

export interface ForexCalendarResponse {
  time_period: ForexTimePeriod;
  start?: string | null;
  end?: string | null;
  impact_filter?: string | null;
  count: number;
  events: ForexCalendarEvent[];
}
