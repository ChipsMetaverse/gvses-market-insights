import { test, expect } from '@playwright/test';

test('Voice Pipeline Diagnostic Investigation', async ({ page }) => {
  // Enable console logging
  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type()}]`, msg.text());
  });

  // Navigate to diagnostic page
  await page.goto('http://localhost:5175/voice-diagnostic.html');

  // Verify page loaded with new version
  const title = await page.title();
  console.log('Page title:', title);

  const pageLoadTime = await page.locator('#pageLoadTime').textContent();
  console.log('Page load time:', pageLoadTime);

  // Run diagnostic
  console.log('\n=== Running Full Diagnostic ===\n');
  await page.click('#runBtn');

  // Wait for diagnostic to complete (max 30 seconds)
  await page.waitForSelector('#summary', { state: 'visible', timeout: 30000 });

  // Get all result items
  const results = await page.locator('.result-item').all();
  console.log(`\nTotal stages: ${results.length}\n`);

  for (let i = 0; i < results.length; i++) {
    const result = results[i];
    const stage = await result.locator('.result-stage').textContent();
    const name = await result.locator('.result-name').textContent();
    const status = await result.locator('.result-status').textContent();
    const message = await result.locator('.result-message').textContent();
    const duration = await result.locator('.result-duration').textContent();

    console.log(`${status} ${stage}: ${name}`);
    console.log(`   Message: ${message}`);
    console.log(`   Duration: ${duration}\n`);
  }

  // Check summary
  const summary = await page.locator('#summary').innerHTML();
  console.log('=== Summary ===');
  console.log(summary);

  // Take screenshot
  await page.screenshot({ path: 'diagnostic-results.png', fullPage: true });
  console.log('\nScreenshot saved: diagnostic-results.png');
});

test('Agent Orchestrator Endpoint Direct Test', async ({ page }) => {
  // Test the /ask endpoint directly
  console.log('\n=== Testing /ask Endpoint ===\n');

  const response = await page.evaluate(async () => {
    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'ping', conversation_history: [] })
    });
    return {
      status: res.status,
      ok: res.ok,
      data: await res.json()
    };
  });

  console.log('Status:', response.status);
  console.log('OK:', response.ok);
  console.log('Response data:', JSON.stringify(response.data, null, 2));
  console.log('\nChecking for "text" field:', 'text' in response.data);
  console.log('Checking for "response" field:', 'response' in response.data);

  // The diagnostic expects "text" but backend returns "response"
  if ('response' in response.data && !('text' in response.data)) {
    console.log('\n⚠️  ISSUE FOUND: Backend returns "response" field, but diagnostic expects "text" field');
  }
});
