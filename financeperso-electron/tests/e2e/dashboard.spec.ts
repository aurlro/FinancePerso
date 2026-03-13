import { test, expect } from './setup';

/**
 * Dashboard E2E Tests
 * Tests the dashboard functionality including KPIs, charts, and navigation
 */

test.describe('Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard if not already there
    await page.waitForLoadState('networkidle');
  });

  test('dashboard displays 3 KPIs', async ({ page }) => {
    // Look for common KPI indicators
    const kpiPatterns = [
      /revenu|revenue|income/i,
      /dépense|expense|spending/i,
      /solde|balance|total/i,
      /épargne|savings/i
    ];
    
    let foundKPIs = 0;
    const pageContent = await page.content();
    
    for (const pattern of kpiPatterns) {
      if (pattern.test(pageContent)) {
        foundKPIs++;
      }
    }
    
    // Should find at least 3 KPI indicators
    expect(foundKPIs).toBeGreaterThanOrEqual(3);
    
    // Look for numeric values that could be KPIs
    const kpiCards = await page.locator('.kpi, .metric, .stat, [class*="card"]').count();
    expect(kpiCards).toBeGreaterThanOrEqual(3);
  });

  test('navigation to transactions works', async ({ page }) => {
    // Try to find and click a transactions link/button
    const transactionSelectors = [
      'text=/transactions?/i',
      'a[href*="transaction"]',
      'button:has-text("Transaction")',
      '[data-testid*="transaction"]'
    ];
    
    let clicked = false;
    for (const selector of transactionSelectors) {
      try {
        const locator = page.locator(selector).first();
        if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
          await locator.click();
          clicked = true;
          break;
        }
      } catch {
        continue;
      }
    }
    
    expect(clicked).toBe(true);
    
    // Wait for navigation
    await page.waitForTimeout(1000);
    
    // Verify we're on transactions page
    const url = await page.url();
    const content = await page.content();
    const onTransactionsPage = 
      url.includes('transaction') || 
      /transaction|opération|débit|crédit/i.test(content);
    
    expect(onTransactionsPage).toBe(true);
  });

  test('charts are loaded (canvas or svg present)', async ({ page }) => {
    // Look for chart containers
    const chartSelectors = [
      'canvas', // Canvas-based charts (Chart.js, Recharts canvas)
      'svg',    // SVG-based charts (D3, Recharts SVG)
      '.recharts-wrapper',
      '.chart',
      '[class*="chart"]'
    ];
    
    let chartsFound = false;
    for (const selector of chartSelectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        chartsFound = true;
        break;
      }
    }
    
    expect(chartsFound).toBe(true);
  });

  test('screenshot of dashboard', async ({ page }) => {
    // Ensure dashboard is fully loaded
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Take screenshot
    await page.screenshot({ 
      path: 'test-results/screenshots/dashboard-full.png',
      fullPage: true 
    });
    
    // Verify screenshot was created (file exists check happens outside this test)
    const fs = require('fs');
    expect(fs.existsSync('test-results/screenshots/dashboard-full.png')).toBe(true);
  });

  test('dashboard shows current period', async ({ page }) => {
    // Check for date/period indicators
    const pageContent = await page.content();
    const currentYear = new Date().getFullYear().toString();
    const currentMonth = new Date().toLocaleString('fr-FR', { month: 'long' });
    
    // Should show current year or month
    const hasPeriodInfo = 
      pageContent.includes(currentYear) ||
      pageContent.toLowerCase().includes(currentMonth.toLowerCase()) ||
      /(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)/i.test(pageContent);
    
    expect(hasPeriodInfo).toBe(true);
  });

});
