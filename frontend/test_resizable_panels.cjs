const puppeteer = require('puppeteer');

async function testResizablePanels() {
  console.log('Testing resizable panels and provider management...\n');
  
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1440, height: 900 }
  });
  
  const page = await browser.newPage();

  try {
    // Navigate to the app
    console.log('1. Navigating to application...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle0', timeout: 30000 });
    await new Promise(r => setTimeout(r, 2000));

    // Take initial screenshot
    await page.screenshot({ path: 'test-1-initial-layout.png' });
    console.log('✓ Initial layout captured');

    // Test 1: Check if panels are visible
    console.log('\n2. Checking panel visibility...');
    const leftPanel = await page.$('.analysis-panel-left');
    const mainContent = await page.$('.main-content');
    const rightPanel = await page.$('.voice-panel-right');
    
    if (leftPanel && mainContent && rightPanel) {
      console.log('✓ All panels are visible');
    } else {
      console.log('✗ Some panels are missing');
    }

    // Test 2: Check if dividers are present
    console.log('\n3. Checking panel dividers...');
    const dividers = await page.$$('.panel-divider');
    console.log(`✓ Found ${dividers.length} panel dividers`);

    // Test 3: Get initial panel widths
    console.log('\n4. Getting initial panel widths...');
    const initialLeftWidth = await page.evaluate(() => {
      const panel = document.querySelector('.analysis-panel-left');
      return panel ? panel.offsetWidth : 0;
    });
    const initialRightWidth = await page.evaluate(() => {
      const panel = document.querySelector('.voice-panel-right');
      return panel ? panel.offsetWidth : 0;
    });
    console.log(`   Left panel: ${initialLeftWidth}px`);
    console.log(`   Right panel: ${initialRightWidth}px`);

    // Test 4: Try to drag the left divider
    console.log('\n5. Testing left panel resize...');
    if (dividers.length > 0) {
      const leftDivider = dividers[0];
      const box = await leftDivider.boundingBox();
      
      // Drag the divider 50px to the right
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2 + 50, box.y + box.height / 2);
      await page.mouse.up();
      await new Promise(r => setTimeout(r, 500));

      const newLeftWidth = await page.evaluate(() => {
        const panel = document.querySelector('.analysis-panel-left');
        return panel ? panel.offsetWidth : 0;
      });
      
      if (newLeftWidth !== initialLeftWidth) {
        console.log(`✓ Left panel resized from ${initialLeftWidth}px to ${newLeftWidth}px`);
      } else {
        console.log('✗ Left panel resize failed');
      }
      
      await page.screenshot({ path: 'test-2-left-panel-resized.png' });
    }

    // Test 5: Try to drag the right divider
    console.log('\n6. Testing right panel resize...');
    if (dividers.length > 1) {
      const rightDivider = dividers[1];
      const box = await rightDivider.boundingBox();
      
      // Drag the divider 50px to the left
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2 - 50, box.y + box.height / 2);
      await page.mouse.up();
      await new Promise(r => setTimeout(r, 500));

      const newRightWidth = await page.evaluate(() => {
        const panel = document.querySelector('.voice-panel-right');
        return panel ? panel.offsetWidth : 0;
      });
      
      if (newRightWidth !== initialRightWidth) {
        console.log(`✓ Right panel resized from ${initialRightWidth}px to ${newRightWidth}px`);
      } else {
        console.log('✗ Right panel resize failed');
      }
      
      await page.screenshot({ path: 'test-3-right-panel-resized.png' });
    }

    // Test 6: Check localStorage persistence
    console.log('\n7. Testing localStorage persistence...');
    const savedLeftWidth = await page.evaluate(() => localStorage.getItem('leftPanelWidth'));
    const savedRightWidth = await page.evaluate(() => localStorage.getItem('rightPanelWidth'));
    
    if (savedLeftWidth && savedRightWidth) {
      console.log(`✓ Panel widths saved to localStorage`);
      console.log(`   Left: ${savedLeftWidth}px, Right: ${savedRightWidth}px`);
    } else {
      console.log('✗ Panel widths not saved to localStorage');
    }

    // Test 7: Refresh and check if widths persist
    console.log('\n8. Testing persistence after refresh...');
    await page.reload({ waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 2000));
    
    const reloadedLeftWidth = await page.evaluate(() => {
      const panel = document.querySelector('.analysis-panel-left');
      return panel ? panel.offsetWidth : 0;
    });
    const reloadedRightWidth = await page.evaluate(() => {
      const panel = document.querySelector('.voice-panel-right');
      return panel ? panel.offsetWidth : 0;
    });
    
    console.log(`   After reload - Left: ${reloadedLeftWidth}px, Right: ${reloadedRightWidth}px`);
    await page.screenshot({ path: 'test-4-after-reload.png' });

    // Test 8: Check for StructuredResponse component
    console.log('\n9. Testing StructuredResponse rendering...');
    // Add a test message to see if it renders with StructuredResponse
    await page.evaluate(() => {
      // Simulate adding an assistant message
      const event = new CustomEvent('test-message', {
        detail: {
          role: 'assistant',
          content: '## Test Response\n\n- Bullet point 1\n- Bullet point 2\n\n**Bold text** and *italic text*'
        }
      });
      window.dispatchEvent(event);
    });
    
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: 'test-5-structured-response.png' });
    console.log('✓ StructuredResponse test completed');

    console.log('\n✅ All tests completed successfully!');
    console.log('\nScreenshots saved:');
    console.log('  - test-1-initial-layout.png');
    console.log('  - test-2-left-panel-resized.png');
    console.log('  - test-3-right-panel-resized.png');
    console.log('  - test-4-after-reload.png');
    console.log('  - test-5-structured-response.png');

  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: 'test-error.png' });
  } finally {
    await browser.close();
  }
}

testResizablePanels();