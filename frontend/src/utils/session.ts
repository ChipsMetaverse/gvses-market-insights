/**
 * Session ID utility for chart command polling
 * Generates and persists a unique session identifier for this browser tab/window
 */

const SESSION_KEY = "chart-session-id";

/**
 * Get or create a session ID for this tab
 * Stored in sessionStorage (per-tab isolation)
 */
export function getSessionId(): string {
  let sid = sessionStorage.getItem(SESSION_KEY);
  if (!sid) {
    sid = `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    sessionStorage.setItem(SESSION_KEY, sid);
  }
  return sid;
}

/**
 * Clear the session ID (useful for testing)
 */
export function clearSessionId(): void {
  sessionStorage.removeItem(SESSION_KEY);
}
