// Playwright verification for agent chart_commands and company info intent
// Prereqs:
// - Backend running at http://localhost:8000
// - Frontend dev server running at http://localhost:5174 (vite)

const { chromium } = require('playwright');

async function orchestrate(query) {
  const res = await fetch('http://localhost:8000/api/agent/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!res.ok) {
    throw new Error(`orchestrate failed: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

function pickCommands(payload) {
  const cmds = payload.chart_commands || (payload.data && payload.data.chart_commands) || [];
  return Array.isArray(cmds) ? cmds : [];
}

(async () => {
  console.log('\n🧪 Verifying agent behavior with Playwright');
  console.log('-----------------------------------------');

  // Launch headless browser and load the app (sanity of UI readiness)
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  try {
    await page.goto('http://localhost:5174', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);
    console.log('✅ Frontend reachable');
  } catch (e) {
    console.error('❌ Frontend not reachable at http://localhost:5174');
    await browser.close();
    process.exit(1);
  }

  let failures = 0;

  // Case 1: "show me the 4hr chart for META"
  try {
    const q1 = 'show me the 4hr chart for META';
    const r1 = await orchestrate(q1);
    const cmds1 = pickCommands(r1);
    const hasMeta = cmds1.some(c => /\bCHART:MET(A)?\b/.test(c));
    const hasH4 = cmds1.some(c => c === 'TIMEFRAME:H4');
    console.log('\n[Q1] chart_commands:', cmds1);
    if (!hasMeta || !hasH4) {
      console.error('❌ Q1 failed: expected CHART:META and TIMEFRAME:H4');
      failures++;
    } else {
      console.log('✅ Q1 passed: META + H4 timeframe');
    }
  } catch (e) {
    console.error('❌ Q1 error:', e.message);
    failures++;
  }

  // Case 2: "What is PLTR?" (company info + chart sync)
  try {
    const q2 = 'What is PLTR?';
    const r2 = await orchestrate(q2);
    const cmds2 = pickCommands(r2);
    const hasPltr = cmds2.some(c => c === 'CHART:PLTR');
    const text2 = (r2.text || '').toLowerCase();
    const mentionsPalantir = text2.includes('palantir');
    console.log('\n[Q2] text preview:', (r2.text || '').slice(0, 140));
    console.log('[Q2] chart_commands:', cmds2);
    if (!hasPltr || !mentionsPalantir) {
      console.error('❌ Q2 failed: expected CHART:PLTR and descriptive text mentioning Palantir');
      failures++;
    } else {
      console.log('✅ Q2 passed: company info + chart sync');
    }
  } catch (e) {
    console.error('❌ Q2 error:', e.message);
    failures++;
  }

  // Case 3: "Show PLTR chart" (chart-only path)
  try {
    const q3 = 'Show PLTR chart';
    const r3 = await orchestrate(q3);
    const cmds3 = pickCommands(r3);
    const hasPltr = cmds3.some(c => c === 'CHART:PLTR');
    console.log('\n[Q3] chart_commands:', cmds3);
    if (!hasPltr) {
      console.error('❌ Q3 failed: expected CHART:PLTR');
      failures++;
    } else {
      console.log('✅ Q3 passed: chart-only path emits CHART:PLTR');
    }
  } catch (e) {
    console.error('❌ Q3 error:', e.message);
    failures++;
  }

  await browser.close();

  console.log('\n-----------------------------------------');
  if (failures > 0) {
    console.error(`❌ Verification failed with ${failures} failing case(s)`);
    process.exit(2);
  } else {
    console.log('✅ All verification cases passed');
    process.exit(0);
  }
})();

