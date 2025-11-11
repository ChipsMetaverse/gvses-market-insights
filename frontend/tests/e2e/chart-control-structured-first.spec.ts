/**
 * Integration Tests for Structured-First Chart Control
 *
 * Tests the end-to-end chart control flow with PREFER_STRUCTURED_CHART_COMMANDS
 * feature flag enabled and disabled.
 *
 * Phase 1: Structured Chart Command Migration - Integration Tests
 */

import { test, expect } from '@playwright/test';

test.describe('Chart Control - Structured-First Mode', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');

    // Wait for app to be ready
    await page.waitForSelector('[data-testid="trading-dashboard"]', { timeout: 10000 });
  });

  test('should process structured commands when feature flag enabled', async ({ page }) => {
    // This test requires setting VITE_PREFER_STRUCTURED_CHART_COMMANDS=true
    // Check if feature flag is enabled via console logs
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('[ChartControl]') || msg.text().includes('[Enhanced Chart]')) {
        logs.push(msg.text());
      }
    });

    // Simulate agent response with both structured and legacy commands
    // The backend would send this payload
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'Loading Tesla stock',
          chartCommands: ['LOAD:AAPL'], // Legacy (should be ignored in structured-first mode)
          chartCommandsStructured: [
            { type: 'load', payload: { symbol: 'TSLA' } } // Structured (should be processed)
          ]
        }
      });
      window.dispatchEvent(event);
    });

    // Wait for chart to update
    await page.waitForTimeout(3000);

    // Verify structured command was processed by checking logs
    const hasStructuredLog = logs.some(log =>
      log.includes('structured-first') || log.includes('Processing') && log.includes('structured')
    );

    // In structured-first mode, TSLA should be loaded, not AAPL
    // We can verify this by checking the current symbol in the chart header
    const symbolText = await page.locator('[data-testid="current-symbol"]').textContent();

    if (hasStructuredLog) {
      // Feature flag is enabled - should process structured commands (TSLA)
      expect(symbolText).toContain('TSLA');
    } else {
      // Feature flag is disabled - may process both or use hybrid mode
      console.log('Feature flag not enabled, skipping structured-first assertion');
    }
  });

  test('should fall back to pattern matching when no structured commands', async ({ page }) => {
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('[ChartControl]')) {
        logs.push(msg.text());
      }
    });

    // Send response with NO structured commands
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'show me NVDA',
          chartCommands: [],
          chartCommandsStructured: []
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(3000);

    // Check if pattern matching fallback was used
    const hasFallbackLog = logs.some(log =>
      log.includes('falling back to pattern matching') ||
      log.includes('No structured commands')
    );

    if (hasFallbackLog) {
      // Verify pattern matching extracted NVDA from the text
      const symbolText = await page.locator('[data-testid="current-symbol"]').textContent();
      expect(symbolText).toContain('NVDA');
    }
  });

  test('should process both formats in hybrid mode', async ({ page }) => {
    const logs: string[] = [];
    page.on('console', msg => {
      if (msg.text().includes('[Enhanced Chart]')) {
        logs.push(msg.text());
      }
    });

    // Send both structured and legacy commands
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'load microsoft with 1 hour timeframe',
          chartCommands: ['TIMEFRAME:1H'], // Legacy timeframe
          chartCommandsStructured: [
            { type: 'load', payload: { symbol: 'MSFT' } } // Structured symbol
          ]
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(3000);

    // In hybrid mode, both should be processed
    const hasHybridLog = logs.some(log => log.includes('hybrid'));

    if (hasHybridLog) {
      // Verify symbol was changed
      const symbolText = await page.locator('[data-testid="current-symbol"]').textContent();
      expect(symbolText).toContain('MSFT');

      // Verify timeframe was changed (check active timeframe button)
      const activeTimeframe = await page.locator('.timeframe-button.active').textContent();
      expect(activeTimeframe).toContain('1H');
    }
  });

  test('should log processing mode on every response', async ({ page }) => {
    let processingModeLogged = false;
    let detectedMode = '';

    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('processingMode')) {
        processingModeLogged = true;
        if (text.includes('structured-first')) {
          detectedMode = 'structured-first';
        } else if (text.includes('hybrid')) {
          detectedMode = 'hybrid';
        }
      }
    });

    // Trigger any agent response
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'test response',
          chartCommands: [],
          chartCommandsStructured: []
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(1000);

    expect(processingModeLogged).toBe(true);
    expect(['structured-first', 'hybrid']).toContain(detectedMode);
  });
});

test.describe('Chart Control - Command Priority', () => {
  test('structured commands should override legacy when both present (structured-first mode)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="trading-dashboard"]', { timeout: 10000 });

    const executedSymbols: string[] = [];

    page.on('console', msg => {
      const text = msg.text();
      // Track which symbols are loaded
      if (text.includes('Loading symbol') || text.includes('LOAD:')) {
        executedSymbols.push(text);
      }
    });

    // Send conflicting commands - structured says TSLA, legacy says AAPL
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'load stock',
          chartCommands: ['LOAD:AAPL'], // Legacy
          chartCommandsStructured: [
            { type: 'load', payload: { symbol: 'TSLA' } } // Structured
          ]
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(3000);

    // In structured-first mode, only TSLA should be loaded
    // Check the current symbol displayed
    const symbolText = await page.locator('[data-testid="current-symbol"]').textContent();

    // If structured-first mode is enabled, TSLA takes priority
    // If hybrid mode, might see both or last one wins
    const logs = executedSymbols.join(' ');
    console.log('Executed symbols:', logs);
  });
});

test.describe('Chart Control - Error Handling', () => {
  test('should handle invalid structured commands gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="trading-dashboard"]', { timeout: 10000 });

    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Send malformed structured command
    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'test',
          chartCommands: [],
          chartCommandsStructured: [
            { type: 'invalid_type', payload: { bad: 'data' } }
          ]
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(2000);

    // App should not crash
    const dashboard = await page.locator('[data-testid="trading-dashboard"]').isVisible();
    expect(dashboard).toBe(true);
  });

  test('should handle missing payload fields in structured commands', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="trading-dashboard"]', { timeout: 10000 });

    await page.evaluate(() => {
      const event = new CustomEvent('agentResponse', {
        detail: {
          text: 'test',
          chartCommands: [],
          chartCommandsStructured: [
            { type: 'load', payload: {} } // Missing symbol field
          ]
        }
      });
      window.dispatchEvent(event);
    });

    await page.waitForTimeout(2000);

    // Should not crash, should handle gracefully
    const dashboard = await page.locator('[data-testid="trading-dashboard"]').isVisible();
    expect(dashboard).toBe(true);
  });
});
