import { test, expect } from '@playwright/test';

test.describe('ChatKit voice integration (stubbed)', () => {
  test('requests ChatKit session and renders assistant shell without errors', async ({ page }) => {
    let chatKitSessionHits = 0;
    let realtimeSessionHits = 0;

    await page.addInitScript(() => {
      const navigatorAny = navigator as any;
      navigatorAny.mediaDevices = navigatorAny.mediaDevices || {};
      navigatorAny.mediaDevices.getUserMedia = async () => new MediaStream();

      class MockWebSocket {
        url: string;
        readyState = 1;
        listeners: Record<string, ((event: any) => void)[]> = {};

        constructor(url: string) {
          this.url = url;
          setTimeout(() => {
            (this.listeners.open || []).forEach((listener) => listener({ type: 'open' }));
          }, 0);
        }

        addEventListener(type: string, listener: (event: any) => void) {
          this.listeners[type] = this.listeners[type] || [];
          this.listeners[type].push(listener);
        }

        removeEventListener(type: string, listener: (event: any) => void) {
          this.listeners[type] = (this.listeners[type] || []).filter((fn) => fn !== listener);
        }

        send() {}

        close() {
          this.readyState = 3;
          (this.listeners.close || []).forEach((listener) => listener({ type: 'close' }));
        }
      }

      (window as any).WebSocket = MockWebSocket;
    });

    await page.route('**/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          openai_relay: { active: true },
        }),
      });
    });

    await page.route('**/api/chatkit/session', async (route) => {
      chatKitSessionHits += 1;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          client_secret: {
            value: 'stubbed-chatkit-secret',
          },
        }),
      });
    });

    await page.route('**/openai/realtime/session', async (route) => {
      realtimeSessionHits += 1;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          session_id: 'session_stub',
          ws_url: 'wss://example.com/realtime-stub',
          api_key: 'stubbed-api-key',
          client_secret: { value: 'stubbed-api-key' },
        }),
      });
    });

    await page.route('**/api/agent/orchestrate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          text: 'Stubbed agent response for testing',
          chart_commands: ['LOAD:AAPL'],
          tools_used: [],
        }),
      });
    });

    await page.goto('/');

    await expect(page.locator('text=AI Trading Assistant')).toBeVisible();

    await page.waitForFunction(() => window.localStorage.getItem('chatkit_device_id') !== null);

    expect(chatKitSessionHits).toBeGreaterThan(0);

    await expect(page.locator('text=AI Assistant - Error')).toHaveCount(0);

    await page.getByTitle('Connect voice').click();

    expect(realtimeSessionHits).toBeGreaterThan(0);

    await expect(page.locator('text=Connected')).toBeVisible();
  });
});
