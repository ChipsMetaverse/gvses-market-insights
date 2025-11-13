export type ChartCommandType = "change_symbol" | "set_timeframe" | "toggle_indicator" | "highlight_pattern";

export interface ChartCommand {
  type: ChartCommandType;
  payload: Record<string, unknown>;
  description?: string;
  legacy?: string | null;
}

export interface ChartCommandEnvelope {
  seq: number;
  timestamp: number;
  command: ChartCommand;
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function fetchChartCommands(params: {
  cursor?: number;
  sessionId?: string;
  signal?: AbortSignal;
  limit?: number;
} = {}): Promise<{ commands: ChartCommandEnvelope[]; cursor: number }> {
  const u = new URL("/api/chart-commands", API_BASE || window.location.origin);
  if (params.cursor !== undefined) u.searchParams.set("cursor", String(params.cursor));
  if (params.sessionId) u.searchParams.set("sessionId", params.sessionId);
  if (params.limit) u.searchParams.set("limit", String(params.limit));
  const res = await fetch(u.toString(), { headers: { Accept: "application/json" }, signal: params.signal });
  if (!res.ok) throw new Error(`chart-commands ${res.status}: ${await res.text()}`);
  return res.json();
}
