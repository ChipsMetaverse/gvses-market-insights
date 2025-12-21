import axios from 'axios';

import { getApiUrl } from '../utils/apiConfig';
import type {
  ForexCalendarEvent,
  ForexCalendarResponse,
  ForexImpact,
  ForexTimePeriod,
} from '../types/forex';

interface CalendarQuery {
  timePeriod?: ForexTimePeriod;
  start?: string;
  end?: string;
  impact?: ForexImpact | `${ForexImpact},${ForexImpact}`;
}

type CachedEntry = {
  timestamp: number;
  response: ForexCalendarResponse;
};

const CACHE_TTL_MS = 10_000; // 10 seconds per integration plan

class ForexDataService {
  private cache = new Map<string, CachedEntry>();

  private buildCacheKey(params: CalendarQuery): string {
    return JSON.stringify({ ...params, timePeriod: params.timePeriod ?? 'today' });
  }

  private normalizeResponse(data: ForexCalendarResponse): ForexCalendarResponse {
    const sortedEvents: ForexCalendarEvent[] = [...(data.events ?? [])];
    sortedEvents.sort((a, b) => new Date(a.datetime_utc).getTime() - new Date(b.datetime_utc).getTime());

    return {
      ...data,
      events: sortedEvents,
      count: sortedEvents.length,
    };
  }

  private getCached(key: string): ForexCalendarResponse | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    if (Date.now() - cached.timestamp > CACHE_TTL_MS) {
      this.cache.delete(key);
      return null;
    }

    return cached.response;
  }

  private setCache(key: string, response: ForexCalendarResponse): void {
    this.cache.set(key, {
      timestamp: Date.now(),
      response,
    });
  }

  async getCalendar(params: CalendarQuery = {}): Promise<ForexCalendarResponse> {
    const key = this.buildCacheKey(params);
    const cached = this.getCached(key);
    if (cached) {
      return cached;
    }

    const apiUrl = getApiUrl();
    const response = await axios.get<ForexCalendarResponse>(`${apiUrl}/api/forex/calendar`, {
      params: {
        time_period: params.timePeriod ?? 'today',
        start: params.start,
        end: params.end,
        impact: params.impact,
      },
    });

    const normalized = this.normalizeResponse(response.data);
    this.setCache(key, normalized);
    return normalized;
  }

  async getToday(): Promise<ForexCalendarResponse> {
    return this.getCalendar({ timePeriod: 'today' });
  }

  async getWeek(): Promise<ForexCalendarResponse> {
    return this.getCalendar({ timePeriod: 'this_week' });
  }
}

export const forexDataService = new ForexDataService();
