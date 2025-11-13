import { useEffect, useRef } from "react";
import { fetchChartCommands, ChartCommandEnvelope } from "../services/chartCommandService";

export function useChartCommandPolling(opts: {
  sessionId: string;
  onCommands: (cmds: ChartCommandEnvelope[]) => void;
  enabled?: boolean;
  intervalMs?: number;
}) {
  const { sessionId, onCommands, enabled = true, intervalMs = 2000 } = opts;
  const cursorRef = useRef<number | undefined>(undefined);
  const timerRef = useRef<number | null>(null);
  const backoffRef = useRef<number>(intervalMs);

  useEffect(() => {
    if (!enabled) return;
    let aborted = false;

    const tick = async () => {
      const ctl = new AbortController();
      try {
        const { commands, cursor } = await fetchChartCommands({
          cursor: cursorRef.current,
          sessionId,
          limit: 100,
          signal: ctl.signal,
        });
        if (aborted) return;
        if (commands.length) onCommands(commands);
        cursorRef.current = cursor;
        backoffRef.current = intervalMs; // reset on success
      } catch {
        backoffRef.current = Math.min(backoffRef.current * 2, 30000); // backoff to 30s max
      } finally {
        if (!aborted) timerRef.current = window.setTimeout(tick, backoffRef.current);
      }
      return () => ctl.abort();
    };

    timerRef.current = window.setTimeout(tick, backoffRef.current);
    return () => {
      aborted = true;
      if (timerRef.current) window.clearTimeout(timerRef.current);
      timerRef.current = null;
    };
  }, [enabled, intervalMs, sessionId, onCommands]);
}
