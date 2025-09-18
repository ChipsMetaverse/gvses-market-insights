const { chromium } = require('playwright');

async function testUIDebug() {
  console.log('🔍 UI Debug - Finding Elements...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5174');
    console.log('✅ Application loaded');
    await page.waitForTimeout(3000);
    
    // Debug: Find all elements that might be tabs
    const tabDebug = await page.evaluate(() => {
      const elements = Array.from(document.querySelectorAll('*'));
      const tabElements = elements.filter(el => {
        const text = (el.textContent || '').toLowerCase();
        const classes = el.className || '';
        const id = el.id || '';
        const dataAttrs = Array.from(el.attributes).map(attr => `${attr.name}="${attr.value}"`);
        
        return (
          text.includes('voice') || 
          classes.includes('tab') || 
          classes.includes('voice') ||
          id.includes('voice') ||
          dataAttrs.some(attr => attr.includes('voice') || attr.includes('tab'))
        );
      });
      
      return tabElements.map(el => ({
        tagName: el.tagName,
        text: (el.textContent || '').substring(0, 50),
        className: el.className,
        id: el.id,
        dataAttrs: Array.from(el.attributes).map(attr => `${attr.name}="${attr.value}"`),
        isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
      }));
    });
    
    console.log('\n📊 Tab-related elements found:');
    tabDebug.forEach((el, i) => {
      console.log(`${i + 1}. ${el.tagName}: "${el.text}"`);
      console.log(`   Class: ${el.className}`);
      console.log(`   ID: ${el.id}`);
      console.log(`   Attributes: ${el.dataAttrs.join(', ')}`);
      console.log(`   Visible: ${el.isVisible}`);
      console.log('');
    });
    
    // Debug: Find all select elements
    const selectDebug = await page.evaluate(() => {
      const selects = Array.from(document.querySelectorAll('select'));
      return selects.map(select => ({
        className: select.className,
        id: select.id,
        dataAttrs: Array.from(select.attributes).map(attr => `${attr.name}="${attr.value}"`),
        options: Array.from(select.options).map(opt => ({ value: opt.value, text: opt.text })),
        isVisible: select.offsetWidth > 0 && select.offsetHeight > 0
      }));
    });
    
    console.log('\n📋 Select elements found:');
    selectDebug.forEach((el, i) => {
      console.log(`${i + 1}. Select Element:`);
      console.log(`   Class: ${el.className}`);
      console.log(`   ID: ${el.id}`);
      console.log(`   Attributes: ${el.dataAttrs.join(', ')}`);
      console.log(`   Options: ${el.options.map(opt => `${opt.value}="${opt.text}"`).join(', ')}`);
      console.log(`   Visible: ${el.isVisible}`);
      console.log('');
    });
    
    // Debug: Find all buttons
    const buttonDebug = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.map(btn => ({
        text: (btn.textContent || '').substring(0, 30),
        className: btn.className,
        id: btn.id,
        dataAttrs: Array.from(btn.attributes).map(attr => `${attr.name}="${attr.value}"`),
        isVisible: btn.offsetWidth > 0 && btn.offsetHeight > 0
      }));
    });
    
    console.log('\n🔘 Button elements found:');
    buttonDebug.forEach((el, i) => {
      console.log(`${i + 1}. "${el.text}"`);
      console.log(`   Class: ${el.className}`);
      console.log(`   ID: ${el.id}`);
      console.log(`   Attributes: ${el.dataAttrs.join(', ')}`);
      console.log(`   Visible: ${el.isVisible}`);
      console.log('');
    });
    
    // Take screenshot for visual inspection
    await page.screenshot({ 
      path: 'ui-debug-elements.png', 
      fullPage: true 
    });
    console.log('📸 Screenshot saved: ui-debug-elements.png');
    
  } catch (error) {
    console.error('❌ Debug test failed:', error);
  } finally {
    await page.waitForTimeout(2000);
    await browser.close();
  }
}

testUIDebug().catch(console.error);