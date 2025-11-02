const playwright = require('playwright');

async function finalTrendlineTest() {
  console.log('🎯 FINAL TRENDLINE VERIFICATION TEST');
  console.log('='.repeat(70));
  
  const browser = await playwright.chromium.launch({ 
    headless: false,
    args: ['--no-sandbox']
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('\n📍 Loading application...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'final_before.png', fullPage: true });
    console.log('📸 Before: final_before.png');
    
    console.log('\n💬 Sending query: "Draw a trendline for AAPL"');
    const result = await page.evaluate(async () => {
      const response = await fetch('http://localhost:8000/api/agent/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'Draw a trendline for AAPL' })
      });
      const data = await response.json();
      
      const trendlines = (data.chart_commands || []).filter(cmd => 
        cmd.includes('TRENDLINE')
      );
      
      console.log('[TEST] Trendline commands:', trendlines);
      
      if (window.enhancedChartControl) {
        await window.enhancedChartControl.processEnhancedResponse(data.chart_commands.join(' '));
      }
      
      return {
        trendlines,
        total_commands: data.chart_commands.length
      };
    });
    
    console.log('\n📊 Trendline Commands Generated:');
    result.trendlines.forEach((cmd, i) => {
      const parts = cmd.split(':');
      if (parts.length >= 5) {
        console.log(`   ${i + 1}. Price: $${parts[1]} @ ${parts[2]} → $${parts[3]} @ ${parts[4]}`);
        console.log(`      Timestamp range: ${parts[2]} to ${parts[4]}`);
      } else {
        console.log(`   ${i + 1}. ${cmd} (incomplete)`);
      }
    });
    
    console.log('\n⏳ Waiting for rendering (5 seconds)...');
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: 'final_after.png', fullPage: true });
    console.log('📸 After: final_after.png');
    
    console.log('\n' + '='.repeat(70));
    console.log('✅ TEST COMPLETE');
    console.log('='.repeat(70));
    console.log('\n📖 VERIFICATION:');
    console.log('   Compare final_before.png and final_after.png');
    console.log('   Look for:');
    console.log('   - Diagonal blue line connecting two price points');
    console.log('   - Line should span across visible chart data');
    console.log('   - Line should NOT be at the edge of the chart');
    
    console.log('\n👁️  Browser staying open for 30 seconds for inspection...');
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

finalTrendlineTest();
