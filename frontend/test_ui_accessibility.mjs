/**
 * Playwright Accessibility Test for Polished UI/UX
 * Verifies WCAG compliance and civil engineering UI principles
 */

import { chromium } from 'playwright';

// Color codes for output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m'
};

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
    console.log(`${colors.green}✅ ${message}${colors.reset}`);
}

function logError(message) {
    console.log(`${colors.red}❌ ${message}${colors.reset}`);
}

function logWarning(message) {
    console.log(`${colors.yellow}⚠️  ${message}${colors.reset}`);
}

function logSection(message) {
    console.log(`\n${colors.bright}${colors.blue}${'='.repeat(60)}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${message}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${'='.repeat(60)}${colors.reset}\n`);
}

async function testButtonSizes(page) {
    logSection('TESTING BUTTON SIZES (44x44px minimum)');
    
    const buttons = await page.$$('button');
    let passCount = 0;
    let failCount = 0;
    let failedButtons = [];
    
    for (const button of buttons) {
        const box = await button.boundingBox();
        if (box) {
            if (box.width >= 44 && box.height >= 44) {
                passCount++;
            } else {
                failCount++;
                const text = await button.textContent();
                failedButtons.push({
                    text: text?.trim() || 'unnamed',
                    width: box.width,
                    height: box.height
                });
            }
        }
    }
    
    if (failCount === 0) {
        logSuccess(`All ${passCount} buttons meet 44x44px minimum size requirement`);
    } else {
        logError(`${failCount} buttons below minimum size:`);
        failedButtons.forEach(btn => {
            log(`  - "${btn.text}": ${btn.width}x${btn.height}px`, colors.red);
        });
    }
    
    return { pass: failCount === 0, passCount, failCount };
}

async function testAriaLabels(page) {
    logSection('TESTING ARIA LABELS');
    
    const interactiveElements = await page.$$('button, a, input, select, textarea');
    let labeledCount = 0;
    let unlabeledCount = 0;
    let unlabeledElements = [];
    
    for (const element of interactiveElements) {
        const ariaLabel = await element.getAttribute('aria-label');
        const ariaLabelledBy = await element.getAttribute('aria-labelledby');
        const text = await element.textContent();
        const title = await element.getAttribute('title');
        const tagName = await element.evaluate(el => el.tagName.toLowerCase());
        
        // Check if element has accessible label
        if (ariaLabel || ariaLabelledBy || (text && text.trim()) || title) {
            labeledCount++;
        } else {
            unlabeledCount++;
            const className = await element.getAttribute('class');
            unlabeledElements.push({
                tag: tagName,
                class: className || 'no-class'
            });
        }
    }
    
    if (unlabeledCount === 0) {
        logSuccess(`All ${labeledCount} interactive elements have accessible labels`);
    } else {
        logWarning(`${unlabeledCount} elements missing accessible labels:`);
        unlabeledElements.forEach(el => {
            log(`  - <${el.tag}> with class: ${el.class}`, colors.yellow);
        });
    }
    
    return { pass: unlabeledCount === 0, labeledCount, unlabeledCount };
}

async function testColorPalette(page) {
    logSection('TESTING COLOR PALETTE CONSOLIDATION');
    
    const colors = await page.evaluate(() => {
        const allElements = document.querySelectorAll('*');
        const colorSet = new Set();
        
        allElements.forEach(el => {
            const style = window.getComputedStyle(el);
            if (style.color) colorSet.add(style.color);
            if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                colorSet.add(style.backgroundColor);
            }
        });
        
        return Array.from(colorSet);
    });
    
    const uniqueColorCount = colors.length;
    
    if (uniqueColorCount <= 10) {
        logSuccess(`Color palette consolidated to ${uniqueColorCount} colors (target: 8-10)`);
    } else if (uniqueColorCount <= 15) {
        logWarning(`Color palette has ${uniqueColorCount} colors (target: 8-10)`);
    } else {
        logError(`Color palette has ${uniqueColorCount} colors (target: 8-10)`);
    }
    
    return { pass: uniqueColorCount <= 15, colorCount: uniqueColorCount };
}

async function testFocusIndicators(page) {
    logSection('TESTING FOCUS INDICATORS');
    
    const focusableElements = await page.$$('button, a, input, select, textarea');
    let goodFocusCount = 0;
    let missingFocusCount = 0;
    let missingFocusElements = [];
    
    for (const element of focusableElements.slice(0, 10)) { // Test first 10 for speed
        await element.focus();
        
        const hasFocusStyle = await element.evaluate(el => {
            const style = window.getComputedStyle(el);
            return style.outline !== 'none' || 
                   style.boxShadow !== 'none' || 
                   style.borderColor !== window.getComputedStyle(el, ':not(:focus)').borderColor;
        });
        
        if (hasFocusStyle) {
            goodFocusCount++;
        } else {
            missingFocusCount++;
            const text = await element.textContent();
            missingFocusElements.push(text?.trim() || 'unnamed');
        }
    }
    
    if (missingFocusCount === 0) {
        logSuccess(`All tested elements have proper focus indicators`);
    } else {
        logWarning(`${missingFocusCount} elements missing focus indicators`);
    }
    
    return { pass: missingFocusCount === 0, goodFocusCount, missingFocusCount };
}

async function testHoverStates(page) {
    logSection('TESTING HOVER STATES');
    
    const hoverableElements = await page.$$('button, a, .stock-card, .news-item');
    let goodHoverCount = 0;
    let missingHoverCount = 0;
    
    for (const element of hoverableElements.slice(0, 10)) { // Test first 10 for speed
        const initialStyle = await element.evaluate(el => {
            const style = window.getComputedStyle(el);
            return {
                background: style.backgroundColor,
                transform: style.transform,
                boxShadow: style.boxShadow
            };
        });
        
        await element.hover();
        await page.waitForTimeout(100);
        
        const hoverStyle = await element.evaluate(el => {
            const style = window.getComputedStyle(el);
            return {
                background: style.backgroundColor,
                transform: style.transform,
                boxShadow: style.boxShadow
            };
        });
        
        const hasHoverEffect = 
            initialStyle.background !== hoverStyle.background ||
            initialStyle.transform !== hoverStyle.transform ||
            initialStyle.boxShadow !== hoverStyle.boxShadow;
        
        if (hasHoverEffect) {
            goodHoverCount++;
        } else {
            missingHoverCount++;
        }
    }
    
    if (missingHoverCount === 0) {
        logSuccess(`All tested elements have hover effects`);
    } else {
        logWarning(`${missingHoverCount} elements missing hover effects`);
    }
    
    return { pass: missingHoverCount <= 2, goodHoverCount, missingHoverCount };
}

async function testGridAlignment(page) {
    logSection('TESTING 8px GRID ALIGNMENT');
    
    const gridMetrics = await page.evaluate(() => {
        const panels = document.querySelectorAll('.insights-panel, .content-main, .analysis-panel');
        const alignmentIssues = [];
        
        panels.forEach(panel => {
            const rect = panel.getBoundingClientRect();
            const style = window.getComputedStyle(panel);
            const padding = parseInt(style.paddingLeft);
            
            // Check if dimensions are multiples of 8
            if (rect.width % 8 !== 0) {
                alignmentIssues.push(`Panel width ${rect.width}px not aligned to 8px grid`);
            }
            if (padding % 8 !== 0) {
                alignmentIssues.push(`Panel padding ${padding}px not aligned to 8px grid`);
            }
        });
        
        return alignmentIssues;
    });
    
    if (gridMetrics.length === 0) {
        logSuccess('All panels aligned to 8px grid system');
    } else {
        logWarning('Grid alignment issues found:');
        gridMetrics.forEach(issue => log(`  - ${issue}`, colors.yellow));
    }
    
    return { pass: gridMetrics.length === 0, issues: gridMetrics };
}

async function testWhitespaceRatio(page) {
    logSection('TESTING WHITESPACE RATIO');
    
    const whitespaceMetrics = await page.evaluate(() => {
        const viewport = { width: window.innerWidth, height: window.innerHeight };
        const panels = document.querySelectorAll('.panel, .card, [class*="panel"], [class*="card"]');
        
        const totalArea = viewport.width * viewport.height;
        let contentArea = 0;
        
        panels.forEach(panel => {
            const rect = panel.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                contentArea += rect.width * rect.height;
            }
        });
        
        const whitespaceRatio = ((totalArea - contentArea) / totalArea * 100);
        return { ratio: whitespaceRatio.toFixed(2), totalArea, contentArea };
    });
    
    const ratio = parseFloat(whitespaceMetrics.ratio);
    
    if (ratio >= 30 && ratio <= 40) {
        logSuccess(`Whitespace ratio: ${ratio}% (optimal: 30-40%)`);
    } else if (ratio >= 25 && ratio <= 45) {
        logWarning(`Whitespace ratio: ${ratio}% (target: 30-40%)`);
    } else {
        logError(`Whitespace ratio: ${ratio}% (target: 30-40%)`);
    }
    
    return { pass: ratio >= 25 && ratio <= 45, ratio };
}

async function main() {
    log('\n' + '='.repeat(60), colors.bright + colors.magenta);
    log('ACCESSIBILITY & UI POLISH VERIFICATION', colors.bright + colors.magenta);
    log('Civil Engineering Principles Applied', colors.bright + colors.magenta);
    log('='.repeat(60) + '\n', colors.bright + colors.magenta);
    
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
    });
    
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    try {
        // Navigate to the app
        await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
        await page.waitForTimeout(3000);
        
        // Run all tests
        const results = {
            buttonSizes: await testButtonSizes(page),
            ariaLabels: await testAriaLabels(page),
            colorPalette: await testColorPalette(page),
            focusIndicators: await testFocusIndicators(page),
            hoverStates: await testHoverStates(page),
            gridAlignment: await testGridAlignment(page),
            whitespaceRatio: await testWhitespaceRatio(page)
        };
        
        // Summary
        logSection('TEST SUMMARY');
        
        let totalPass = 0;
        let totalFail = 0;
        
        Object.entries(results).forEach(([test, result]) => {
            if (result.pass) {
                logSuccess(`${test}: PASSED`);
                totalPass++;
            } else {
                logError(`${test}: NEEDS IMPROVEMENT`);
                totalFail++;
            }
        });
        
        log('\n' + '='.repeat(60), colors.bright);
        if (totalFail === 0) {
            log('🎉 ALL ACCESSIBILITY TESTS PASSED!', colors.bright + colors.green);
        } else {
            log(`📊 Results: ${totalPass} passed, ${totalFail} need improvement`, colors.bright + colors.yellow);
        }
        log('='.repeat(60) + '\n', colors.bright);
        
        // Take final screenshot
        await page.screenshot({ path: 'accessibility-test-complete.png', fullPage: true });
        log('📸 Test screenshot saved: accessibility-test-complete.png', colors.cyan);
        
    } catch (error) {
        console.error('Test failed:', error);
    } finally {
        await page.waitForTimeout(3000);
        await browser.close();
    }
}

main().catch(console.error);