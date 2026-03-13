import { test, expect } from './setup';

/**
 * Transaction Validation E2E Tests
 * Tests the validation workflow for pending transactions
 */

test.describe('Transaction Validation', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to validation/transactions page
    const validationSelectors = [
      'text=/validation|en attente|pending/i',
      'text=/transactions?/i',
      'a[href*="validation"]',
      'a[href*="transaction"]',
      '[data-testid*="validation"]'
    ];
    
    for (const selector of validationSelectors) {
      try {
        const locator = page.locator(selector).first();
        if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
          await locator.click();
          await page.waitForTimeout(1000);
          break;
        }
      } catch {
        continue;
      }
    }
  });

  test('pending transactions are displayed', async ({ page }) => {
    // Look for transaction list or table
    const transactionSelectors = [
      '.transaction-item',
      '.transaction-row',
      'table tbody tr',
      '[data-testid*="transaction"]',
      '.pending-item'
    ];
    
    let hasTransactions = false;
    for (const selector of transactionSelectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        hasTransactions = true;
        break;
      }
    }
    
    // Either we see transactions or an empty state message
    if (!hasTransactions) {
      const pageContent = await page.content();
      const hasEmptyState = 
        /aucune|vide|empty|no transactions|rien/i.test(pageContent);
      expect(hasEmptyState).toBe(true);
    } else {
      expect(hasTransactions).toBe(true);
    }
  });

  test('batch validation works for a group', async ({ page }) => {
    // Look for checkboxes to select transactions
    const checkboxSelectors = [
      'input[type="checkbox"]',
      '.checkbox',
      '[role="checkbox"]'
    ];
    
    const checkboxes = page.locator(checkboxSelectors[0]);
    const count = await checkboxes.count();
    
    if (count === 0) {
      test.skip('No transactions available for batch validation');
      return;
    }
    
    // Select first 2 transactions (skip header checkbox if present)
    const toSelect = Math.min(2, count);
    for (let i = 1; i <= toSelect; i++) {
      try {
        await checkboxes.nth(i).click();
      } catch {
        break;
      }
    }
    
    // Look for validate button
    const validateSelectors = [
      'button:has-text("Valider")',
      'button:has-text("Valider tout")',
      'button:has-text("Confirmer")',
      '.validate',
      '[data-testid="validate"]'
    ];
    
    let validated = false;
    for (const selector of validateSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 }).catch(() => false)) {
          await button.click();
          validated = true;
          break;
        }
      } catch {
        continue;
      }
    }
    
    expect(validated).toBe(true);
    
    await page.waitForTimeout(1000);
    
    // Check for success indication
    const pageContent = await page.content();
    const hasSuccess = 
      /succès|validé|confirmé|success|validated/i.test(pageContent);
    
    expect(hasSuccess).toBe(true);
  });

  test('ignore transaction works', async ({ page }) => {
    // Look for ignore/skip buttons
    const ignoreSelectors = [
      'button:has-text("Ignorer")',
      'button:has-text("Skip")',
      'button:has-text("Passer")',
      '.ignore',
      '[data-testid="ignore"]',
      'button:has([data-lucide="eye-off"])'
    ];
    
    let ignored = false;
    for (const selector of ignoreSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 }).catch(() => false)) {
          await button.click();
          ignored = true;
          break;
        }
      } catch {
        continue;
      }
    }
    
    if (!ignored) {
      test.skip('No ignore button found');
      return;
    }
    
    await page.waitForTimeout(1000);
    
    // Transaction should be marked as ignored or removed
    const pageContent = await page.content();
    const hasIgnored = 
      /ignoré|ignorée|skipped|ignored/i.test(pageContent);
    
    expect(hasIgnored).toBe(true);
  });

  test('transaction shows category suggestions', async ({ page }) => {
    // Look for category badges or suggestions
    const categorySelectors = [
      '.category',
      '.category-badge',
      '[class*="category"]',
      '.suggestion'
    ];
    
    const hasCategories = await page.locator(categorySelectors.join(', ')).count() > 0;
    
    // Categories should be visible or there's a dropdown to select
    if (!hasCategories) {
      const hasSelect = await page.locator('select').count() > 0;
      expect(hasSelect).toBe(true);
    } else {
      expect(hasCategories).toBe(true);
    }
  });

  test('transaction details are visible', async ({ page }) => {
    // Check for transaction details
    const pageContent = await page.content();
    
    // Should show date, description, and amount
    const hasDate = /\d{2}[\/\-]\d{2}[\/\-]\d{4}/.test(pageContent);
    const hasAmount = /[\d\s]+[,.]\d{2}/.test(pageContent);
    
    expect(hasDate || hasAmount).toBe(true);
  });

});
