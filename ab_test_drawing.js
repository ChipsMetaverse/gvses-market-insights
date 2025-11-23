const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  
  // Test A: StackOverflow Approach (Line Series)
  console.log('\n=== TEST A: StackOverflow Line Series Approach ===');
  const pageA = await browser.newPage();
  await pageA.goto('http://localhost:5174/demo');
  await pageA.waitForTimeout(4000);
  
  const resultA = await pageA.evaluate(() => {
    const chart = window.chartRef?.current;
    if (!chart) return { success: false, error: 'Chart not found' };
    
    // StackOverflow approach: Create line series with 2 points
    try {
      const lineSeries = chart.addLineSeries({
        color: '#FF0000',
        lineWidth: 2,
        lastValueVisible: false,
        priceLineVisible: false
      });
      
      // Add 2 data points to create a "trendline"
      lineSeries.setData([
        { time: 1731283200, value: 395 },
        { time: 1731542400, value: 415 }
      ]);
      
      return {
        success: true,
        method: 'StackOverflow Line Series',
        color: 'red',
        points: 2
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  });
  
  console.log('Result A:', JSON.stringify(resultA, null, 2));
  await pageA.waitForTimeout(2000);
  await pageA.screenshot({ path: 'test-a-stackoverflow.png' });
  console.log('Screenshot A saved: test-a-stackoverflow.png');
  
  // Test B: Our ISeriesPrimitive Approach
  console.log('\n=== TEST B: ISeriesPrimitive Approach ===');
  const pageB = await browser.newPage();
  await pageB.goto('http://localhost:5174/demo');
  await pageB.waitForTimeout(4000);
  
  const resultB = await pageB.evaluate(() => {
    const primitive = window.enhancedChartControl?.drawingPrimitive;
    if (!primitive) return { success: false, error: 'DrawingPrimitive not found' };
    
    try {
      const id = primitive.addTrendline(395, 1731283200, 415, 1731542400);
      primitive.forceUpdate();
      
      return {
        success: true,
        method: 'ISeriesPrimitive',
        id: id,
        count: primitive.getDrawings().length
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  });
  
  console.log('Result B:', JSON.stringify(resultB, null, 2));
  await pageB.waitForTimeout(2000);
  await pageB.screenshot({ path: 'test-b-primitive.png' });
  console.log('Screenshot B saved: test-b-primitive.png');
  
  // Test C: StackOverflow on same page as current implementation
  console.log('\n=== TEST C: Both Methods Together ===');
  const pageC = await browser.newPage();
  await pageC.goto('http://localhost:5174/demo');
  await pageC.waitForTimeout(4000);
  
  const resultC = await pageC.evaluate(() => {
    const results = { stackoverflow: null, primitive: null };
    
    // Try StackOverflow approach
    try {
      const chart = window.chartRef?.current;
      if (chart) {
        const lineSeries = chart.addLineSeries({
          color: '#FF0000',
          lineWidth: 3,
          lastValueVisible: false,
          priceLineVisible: false
        });
        lineSeries.setData([
          { time: 1731283200, value: 390 },
          { time: 1731542400, value: 405 }
        ]);
        results.stackoverflow = { success: true, color: 'red' };
      } else {
        results.stackoverflow = { success: false, error: 'Chart not found' };
      }
    } catch (error) {
      results.stackoverflow = { success: false, error: error.message };
    }
    
    // Try ISeriesPrimitive approach
    try {
      const primitive = window.enhancedChartControl?.drawingPrimitive;
      if (primitive) {
        const id = primitive.addTrendline(400, 1731283200, 420, 1731542400);
        primitive.forceUpdate();
        results.primitive = { success: true, id, color: 'blue' };
      } else {
        results.primitive = { success: false, error: 'Primitive not found' };
      }
    } catch (error) {
      results.primitive = { success: false, error: error.message };
    }
    
    return results;
  });
  
  console.log('Result C:', JSON.stringify(resultC, null, 2));
  await pageC.waitForTimeout(2000);
  await pageC.screenshot({ path: 'test-c-both.png' });
  console.log('Screenshot C saved: test-c-both.png');
  
  console.log('\n=== A/B Test Complete ===');
  console.log('Compare screenshots to see which method renders correctly');
  
  await browser.close();
})();
