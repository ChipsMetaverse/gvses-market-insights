import { test, expect } from '@playwright/test';

const STREAM_BUTTON = '[data-testid="start-news-stream"]';
const STOP_BUTTON = '[data-testid="stop-news-stream"]';
const LIVE_INDICATOR = '[data-testid="news-stream-indicator"]';
const NEWS_LIST_ITEMS = '[data-testid="news-stream-item"]';
const CONSOLE_LOG_TEXT = 'Streaming event received';

// Helper to wait for console message containing specific text
async function waitForConsoleMessage(page, text, timeout = 15000) {
  return new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      page.off('console', handler);
      reject(new Error(`Console message '${text}' not received within ${timeout}ms`));
    }, timeout);

    const handler = (msg: any) => {
      if (msg.type() === 'log' && msg.text().includes(text)) {
        clearTimeout(timer);
        page.off('console', handler);
        resolve();
      }
    };

    page.on('console', handler);
  });
}

test.describe('Streaming market news', () => {
  test('starts SSE stream, renders live updates, and stops cleanly', async ({ page }) => {
    await page.goto('/');

    // Ensure stream button is visible
    const startButton = page.locator(STREAM_BUTTON);
    await expect(startButton).toBeVisible();

    // Attach console watcher before starting stream
    const consolePromise = waitForConsoleMessage(page, CONSOLE_LOG_TEXT, 20000);

    // Start the stream
    await startButton.click();

    // Verify UI state switched to active streaming
    await expect(page.locator(STOP_BUTTON)).toBeVisible();
    await expect(page.locator(LIVE_INDICATOR)).toContainText('Live streaming');

    // Wait for at least one console log confirming an event
    await consolePromise;

    // Wait for at least one news item to render
    await expect(page.locator(NEWS_LIST_ITEMS)).toHaveCountGreaterThan(0, { timeout: 20000 });

    // Stop the stream
    await page.locator(STOP_BUTTON).click();

    // Verify UI returns to idle state
    await expect(page.locator(STREAM_BUTTON)).toBeVisible();
    await expect(page.locator(LIVE_INDICATOR)).not.toBeVisible({ timeout: 5000 });
  });
});
