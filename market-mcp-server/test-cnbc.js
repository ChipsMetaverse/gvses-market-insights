import NodeCache from 'node-cache';
import CNBCIntegration from './cnbc-integration.js';

async function testCNBC() {
  console.log('Testing CNBC Integration...\n');
  
  const cache = new NodeCache({ stdTTL: 60 });
  const cnbc = new CNBCIntegration(cache);
  
  // Test 1: Get CNBC Quote
  console.log('1. Testing CNBC Quote for AAPL:');
  try {
    const quote = await cnbc.getCNBCQuote('AAPL');
    if (quote) {
      console.log('✅ CNBC Quote:', {
        symbol: quote.symbol,
        price: quote.price,
        change: quote.change,
        changePercent: quote.changePercent,
        source: quote.source
      });
    } else {
      console.log('⚠️ CNBC quote returned null (may need to check endpoint)');
    }
  } catch (error) {
    console.log('❌ CNBC quote failed:', error.message);
  }
  
  // Test 2: Get CNBC News
  console.log('\n2. Testing CNBC News:');
  try {
    const news = await cnbc.getCNBCNews('markets', 3);
    if (news && news.length > 0) {
      console.log(`✅ Found ${news.length} CNBC articles:`);
      news.forEach((article, i) => {
        console.log(`   ${i + 1}. ${article.title}`);
        console.log(`      URL: ${article.url}`);
      });
    } else {
      console.log('⚠️ No CNBC news articles found');
    }
  } catch (error) {
    console.log('❌ CNBC news failed:', error.message);
  }
  
  // Test 3: Get Pre-Market Movers
  console.log('\n3. Testing CNBC Pre-Market Movers:');
  try {
    const movers = await cnbc.getCNBCPreMarket();
    console.log('✅ Pre-Market Movers:');
    console.log(`   Gainers: ${movers.gainers.length} stocks`);
    console.log(`   Losers: ${movers.losers.length} stocks`);
    console.log(`   Most Active: ${movers.active.length} stocks`);
  } catch (error) {
    console.log('❌ Pre-market movers failed:', error.message);
  }
  
  // Test 4: Get Market Sentiment
  console.log('\n4. Testing CNBC Market Sentiment:');
  try {
    const sentiment = await cnbc.getCNBCSentiment();
    if (sentiment) {
      console.log('✅ Market Sentiment:', {
        headline: sentiment.headline || 'N/A',
        keyPoints: sentiment.keyPoints ? sentiment.keyPoints.length : 0
      });
    } else {
      console.log('⚠️ No sentiment data available');
    }
  } catch (error) {
    console.log('❌ Market sentiment failed:', error.message);
  }
  
  console.log('\n✨ CNBC Integration Test Complete!');
}

testCNBC().catch(console.error);