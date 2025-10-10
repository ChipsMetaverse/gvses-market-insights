import { test, expect } from '@playwright/test';

test.describe('Voice Assistant Flow', () => {
  test('should complete full voice→agent→TTS flow', async ({ page }) => {
    // Open test page
    await page.goto('http://localhost:8000/test_voice_flow.html');

    console.log('\n🧪 Testing Complete Voice Assistant Flow\n');

    // Test 1: Direct agent orchestrator call
    console.log('📋 Test 1: Agent Orchestrator Endpoint');
    await page.click('button:has-text("Test Agent Orchestrator")');
    await page.waitForTimeout(2000);

    const agentResult = await page.locator('#agent-result').textContent();
    console.log('Agent Result:', agentResult);

    if (agentResult?.includes('couldn\'t generate')) {
      console.error('❌ FOUND THE ISSUE: Agent orchestrator returning error response!');
      console.error('This is why users see "I couldn\'t generate a response"');
    } else if (agentResult?.includes('✅ Valid response received')) {
      console.log('✅ Agent orchestrator working correctly');
    }

    // Test 2: OpenAI session
    console.log('\n📋 Test 2: OpenAI Session Creation');
    await page.click('button:has-text("Test OpenAI Session")');
    await page.waitForTimeout(1000);

    const openaiResult = await page.locator('#openai-result').textContent();
    console.log('OpenAI Result:', openaiResult);

    // Test 3: Complete flow
    console.log('\n📋 Test 3: Complete Voice Flow (Simulated)');
    await page.click('button:has-text("Test Complete Flow")');
    await page.waitForTimeout(3000);

    const flowResult = await page.locator('#flow-result').textContent();
    console.log('Flow Result:', flowResult);

    if (flowResult?.includes('COMPLETE FLOW SUCCESSFUL')) {
      console.log('\n✅ ALL TESTS PASSED - Voice assistant should work!');
    } else if (flowResult?.includes('couldn\'t generate')) {
      console.error('\n❌ ISSUE CONFIRMED: Agent returning error responses');
      console.error('   This explains the user\'s "I couldn\'t generate a response" errors');
    } else {
      console.warn('\n⚠️ Test incomplete or failed');
    }

    // Take screenshot for debugging
    await page.screenshot({ path: 'test-voice-flow-results.png', fullPage: true });
    console.log('\n📸 Screenshot saved: test-voice-flow-results.png');
  });
});
