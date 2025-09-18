import { test, expect } from '@playwright/test'

const APP_BASE = process.env.APP_BASE || 'http://localhost:5173'
const API_BASE = process.env.API_BASE || 'http://localhost:8000'

test.describe('ProviderTest - OpenAI Realtime (voice-only)', () => {
  test('switch to OpenAI Realtime and connect via relay session', async ({ page }) => {
    // Navigate to ProviderTest harness view
    await page.goto(`${APP_BASE}/?provider-test`)

    // Intercept the session POST to verify the flow
    const sessionPromise = page.waitForResponse((resp) =>
      resp.url().includes('/openai/realtime/session') && resp.status() === 200
    )

    // Find the OpenAI Realtime row and click Switch
    const realtimeRow = page.locator('div', { hasText: 'openai-realtime' })
    await expect(realtimeRow).toBeVisible()
    await realtimeRow.getByRole('button', { name: /switch/i }).click()

    // Expect the session endpoint to be called and succeed
    const sessionRes = await sessionPromise
    const sessionJson = await sessionRes.json()
    expect(sessionJson.session_id).toBeTruthy()
    expect(typeof sessionJson.ws_url).toBe('string')

    // Wait briefly for connection status to update
    const statusLocator = page.locator('text=/Status:\s*(Connected|Connecting|Disconnected)/i').first()
    await expect(statusLocator).toBeVisible()

    // The component shows a color-coded status; allow a few seconds to connect
    await expect(page.getByText(/Connected/i)).toBeVisible({ timeout: 8000 })

    // Voice controls should be enabled when connected
    const startVoice = page.getByRole('button', { name: /Start Voice/i })
    await expect(startVoice).toBeEnabled()
  })
})

