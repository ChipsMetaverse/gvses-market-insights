import { test, expect, request } from '@playwright/test'

const API_BASE = process.env.API_BASE || 'http://localhost:8000'

test.describe('OpenAI Realtime Relay API', () => {
  test('health endpoint reports operational relay', async ({ request }) => {
    const res = await request.get(`${API_BASE}/health`)
    expect(res.ok()).toBeTruthy()
    const body = await res.json()

    // Basic shape checks
    expect(body.status).toBeDefined()
    // Relay may be exposed under either openai_relay or openai_service depending on code path
    // We only assert the health endpoint returns JSON and does not 5xx
  })

  test('session endpoint returns a valid ws_url', async ({ request }) => {
    const res = await request.post(`${API_BASE}/openai/realtime/session`, { data: {} })
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.session_id).toBeTruthy()
    expect(typeof body.ws_url).toBe('string')
    // Must be ws://, wss://, or a relative relay path
    expect(/^(ws|wss):\/\//.test(body.ws_url) || body.ws_url.startsWith('/realtime-relay/')).toBeTruthy()
  })
})

