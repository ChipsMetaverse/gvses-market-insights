import { test, expect } from '@playwright/test'

const API_BASE = process.env.API_BASE || 'http://localhost:8000'

test.describe('Agent Orchestrator API', () => {
  test('orchestrate returns text response shape', async ({ request }) => {
    const res = await request.post(`${API_BASE}/api/agent/orchestrate`, {
      data: {
        query: 'Say hello and include today\'s date briefly.',
        stream: false,
        session_id: `test_${Date.now()}`
      }
    })
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(typeof body.text).toBe('string')
    expect(body.timestamp).toBeTruthy()
    // tools_used may be empty if caching or minimal prompt; only assert shape
    expect(Array.isArray(body.tools_used)).toBeTruthy()
  })
})

