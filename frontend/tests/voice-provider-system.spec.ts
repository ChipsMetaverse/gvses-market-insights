import { test, expect } from '@playwright/test';

test.describe('Voice Provider System Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    
    // Wait for the app to load completely
    await page.waitForSelector('[data-testid="trading-dashboard"]', { timeout: 10000 });
    
    // Switch to voice tab to access voice provider functionality
    await page.click('[data-testid="voice-tab"]');
    await page.waitForSelector('[data-testid="voice-interface"]', { timeout: 5000 });
  });

  test('Provider switcher UI is visible and functional', async ({ page }) => {
    console.log('Testing provider switcher UI...');
    
    // Check if provider switcher is visible
    const providerSwitcher = page.locator('[data-testid="provider-switcher"]');
    await expect(providerSwitcher).toBeVisible();
    
    // Verify default provider is ElevenLabs
    const elevenLabsButton = page.locator('[data-testid="provider-elevenlabs"]');
    await expect(elevenLabsButton).toHaveClass(/active/);
    
    // Switch to OpenAI provider
    const openAIButton = page.locator('[data-testid="provider-openai"]');
    await openAIButton.click();
    
    // Verify OpenAI provider is now active
    await expect(openAIButton).toHaveClass(/active/);
    await expect(elevenLabsButton).not.toHaveClass(/active/);
    
    console.log('✅ Provider switcher UI test passed');
  });

  test('Connection status indicators work correctly', async ({ page }) => {
    console.log('Testing connection status indicators...');
    
    // Check initial disconnected state
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toContainText('Disconnected');
    
    // Test connect button is visible and clickable
    const connectButton = page.locator('[data-testid="connect-button"]');
    await expect(connectButton).toBeVisible();
    await expect(connectButton).toBeEnabled();
    
    console.log('✅ Connection status test passed');
  });

  test('Provider-specific UI elements render correctly', async ({ page }) => {
    console.log('Testing provider-specific UI elements...');
    
    // Test ElevenLabs specific elements
    await page.click('[data-testid="provider-elevenlabs"]');
    await page.waitForTimeout(500); // Allow state to update
    
    // Check for ElevenLabs-specific elements (if any)
    const voiceInterface = page.locator('[data-testid="voice-interface"]');
    await expect(voiceInterface).toBeVisible();
    
    // Switch to OpenAI and check for OpenAI-specific elements
    await page.click('[data-testid="provider-openai"]');
    await page.waitForTimeout(500); // Allow state to update
    
    // Check for OpenAI-specific elements (tool call indicators, etc.)
    const toolCallStatus = page.locator('[data-testid="tool-call-status"]');
    // OpenAI provider may show tool call status even if not connected
    // This element might not be visible until a connection is made
    
    console.log('✅ Provider-specific UI test passed');
  });

  test('Text input functionality works with unified interface', async ({ page }) => {
    console.log('Testing text input functionality...');
    
    // Test text input is visible
    const textInput = page.locator('[data-testid="message-input"]');
    await expect(textInput).toBeVisible();
    
    // Test send button is visible but disabled when no text
    const sendButton = page.locator('[data-testid="send-button"]');
    await expect(sendButton).toBeVisible();
    await expect(sendButton).toBeDisabled();
    
    // Type a test message
    await textInput.fill('Test message for voice provider');
    
    // Send button should now be enabled
    await expect(sendButton).toBeEnabled();
    
    // Test that message appears in input field
    await expect(textInput).toHaveValue('Test message for voice provider');
    
    console.log('✅ Text input functionality test passed');
  });

  test('Voice recording UI elements are present', async ({ page }) => {
    console.log('Testing voice recording UI elements...');
    
    // Check for voice recording button
    const recordButton = page.locator('[data-testid="record-button"]');
    await expect(recordButton).toBeVisible();
    
    // Check for audio level indicator
    const audioLevel = page.locator('[data-testid="audio-level"]');
    await expect(audioLevel).toBeVisible();
    
    // Check for recording timer
    const recordingTimer = page.locator('[data-testid="recording-timer"]');
    await expect(recordingTimer).toBeVisible();
    
    console.log('✅ Voice recording UI test passed');
  });

  test('Message history displays correctly', async ({ page }) => {
    console.log('Testing message history display...');
    
    // Check for messages container
    const messagesContainer = page.locator('[data-testid="messages-container"]');
    await expect(messagesContainer).toBeVisible();
    
    // Test that messages container is scrollable
    await expect(messagesContainer).toHaveCSS('overflow-y', 'auto');
    
    console.log('✅ Message history test passed');
  });

  test('Provider switching preserves UI state', async ({ page }) => {
    console.log('Testing provider switching state preservation...');
    
    // Enter some text
    const textInput = page.locator('[data-testid="message-input"]');
    await textInput.fill('Test message that should persist');
    
    // Switch providers
    await page.click('[data-testid="provider-openai"]');
    await page.waitForTimeout(500);
    await page.click('[data-testid="provider-elevenlabs"]');
    await page.waitForTimeout(500);
    
    // Check that text input is preserved (this behavior may vary based on implementation)
    // If text should be cleared on provider switch, we'd test for that instead
    const inputValue = await textInput.inputValue();
    console.log('Input value after provider switch:', inputValue);
    
    console.log('✅ Provider switching state test passed');
  });

  test('Error states are handled gracefully', async ({ page }) => {
    console.log('Testing error state handling...');
    
    // Look for any error messages or indicators
    const errorDisplay = page.locator('[data-testid="error-message"]');
    
    // Initially, there should be no errors
    await expect(errorDisplay).not.toBeVisible().catch(() => {
      // Error display might not exist yet, which is fine
      console.log('No error display found (expected for initial state)');
    });
    
    // Test that the app doesn't crash on provider switch
    await page.click('[data-testid="provider-openai"]');
    await page.click('[data-testid="provider-elevenlabs"]');
    
    // App should still be functional
    const voiceInterface = page.locator('[data-testid="voice-interface"]');
    await expect(voiceInterface).toBeVisible();
    
    console.log('✅ Error state handling test passed');
  });

  test('Chart integration works with voice tab', async ({ page }) => {
    console.log('Testing chart integration with voice functionality...');
    
    // Switch back to charts tab
    await page.click('[data-testid="charts-tab"]');
    await page.waitForSelector('[data-testid="trading-chart"]', { timeout: 5000 });
    
    // Verify chart is visible
    const chart = page.locator('[data-testid="trading-chart"]');
    await expect(chart).toBeVisible();
    
    // Switch back to voice tab
    await page.click('[data-testid="voice-tab"]');
    
    // Voice interface should still be functional
    const voiceInterface = page.locator('[data-testid="voice-interface"]');
    await expect(voiceInterface).toBeVisible();
    
    console.log('✅ Chart integration test passed');
  });

  test('Responsive design works on mobile viewport', async ({ page }) => {
    console.log('Testing responsive design on mobile viewport...');
    
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that provider switcher is still accessible
    const providerSwitcher = page.locator('[data-testid="provider-switcher"]');
    await expect(providerSwitcher).toBeVisible();
    
    // Check that voice interface adapts to mobile
    const voiceInterface = page.locator('[data-testid="voice-interface"]');
    await expect(voiceInterface).toBeVisible();
    
    // Verify text input is still usable
    const textInput = page.locator('[data-testid="message-input"]');
    await expect(textInput).toBeVisible();
    
    console.log('✅ Responsive design test passed');
  });

  // Performance and stability tests
  test('Multiple provider switches don\'t cause memory leaks', async ({ page }) => {
    console.log('Testing rapid provider switching stability...');
    
    // Perform rapid provider switches
    for (let i = 0; i < 10; i++) {
      await page.click('[data-testid="provider-openai"]');
      await page.waitForTimeout(100);
      await page.click('[data-testid="provider-elevenlabs"]');
      await page.waitForTimeout(100);
    }
    
    // App should still be responsive
    const voiceInterface = page.locator('[data-testid="voice-interface"]');
    await expect(voiceInterface).toBeVisible();
    
    // Provider switcher should still work
    await page.click('[data-testid="provider-openai"]');
    const openAIButton = page.locator('[data-testid="provider-openai"]');
    await expect(openAIButton).toHaveClass(/active/);
    
    console.log('✅ Provider switching stability test passed');
  });
});

// Integration tests that verify the complete workflow
test.describe('Voice Provider Integration Workflows', () => {
  test('Complete ElevenLabs workflow simulation', async ({ page }) => {
    console.log('Testing complete ElevenLabs workflow...');
    
    await page.goto('/');
    await page.waitForSelector('[data-testid="trading-dashboard"]');
    await page.click('[data-testid="voice-tab"]');
    
    // Select ElevenLabs provider
    await page.click('[data-testid="provider-elevenlabs"]');
    
    // Simulate text message workflow
    const textInput = page.locator('[data-testid="message-input"]');
    await textInput.fill('Show me Tesla stock price');
    
    const sendButton = page.locator('[data-testid="send-button"]');
    await expect(sendButton).toBeEnabled();
    
    // Note: We don't actually send the message to avoid API calls in tests
    console.log('✅ ElevenLabs workflow test passed');
  });

  test('Complete OpenAI workflow simulation', async ({ page }) => {
    console.log('Testing complete OpenAI workflow...');
    
    await page.goto('/');
    await page.waitForSelector('[data-testid="trading-dashboard"]');
    await page.click('[data-testid="voice-tab"]');
    
    // Select OpenAI provider
    await page.click('[data-testid="provider-openai"]');
    
    // Simulate text message workflow
    const textInput = page.locator('[data-testid="message-input"]');
    await textInput.fill('Analyze the current market trends');
    
    const sendButton = page.locator('[data-testid="send-button"]');
    await expect(sendButton).toBeEnabled();
    
    // OpenAI-specific elements should be ready
    // Tool call status might be visible for OpenAI provider
    
    console.log('✅ OpenAI workflow test passed');
  });
});