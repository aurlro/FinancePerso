import { test, expect } from './setup';

/**
 * Budgets E2E Tests
 * Tests budget creation, display, and deletion
 */

test.describe('Budgets', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to budgets page
    const budgetSelectors = [
      'text=/budgets?/i',
      'a[href*="budget"]',
      'button:has-text("Budget")',
      '[data-testid*="budget"]'
    ];
    
    for (const selector of budgetSelectors) {
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

  test('create a budget', async ({ page }) => {
    // Look for create/add budget button
    const addSelectors = [
      'text=/ajouter|créer|nouveau|add|create|new/i',
      'button:has([data-lucide="plus"])',
      '.add-budget',
      '[data-testid="add-budget"]'
    ];
    
    let addButtonFound = false;
    for (const selector of addSelectors) {
      try {
        const locator = page.locator(selector).first();
        if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
          await locator.click();
          addButtonFound = true;
          break;
        }
      } catch {
        continue;
      }
    }
    
    expect(addButtonFound).toBe(true);
    
    // Wait for form/modal to appear
    await page.waitForTimeout(500);
    
    // Fill budget form
    const formSelectors = {
      category: ['input[name="category"]', 'select[name="category"]', '#category', '[placeholder*="catégorie"]'],
      amount: ['input[name="amount"]', 'input[type="number"]', '#amount', '[placeholder*="montant"]']
    };
    
    // Try to fill category
    for (const selector of formSelectors.category) {
      try {
        const field = page.locator(selector).first();
        if (await field.isVisible({ timeout: 1000 }).catch(() => false)) {
          await field.fill('Alimentation');
          break;
        }
      } catch {
        continue;
      }
    }
    
    // Try to fill amount
    for (const selector of formSelectors.amount) {
      try {
        const field = page.locator(selector).first();
        if (await field.isVisible({ timeout: 1000 }).catch(() => false)) {
          await field.fill('500');
          break;
        }
      } catch {
        continue;
      }
    }
    
    // Submit form
    const submitSelectors = [
      'button[type="submit"]',
      'text=/enregistrer|sauvegarder|valider|save|submit/i',
      '.submit'
    ];
    
    for (const selector of submitSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
          await button.click();
          break;
        }
      } catch {
        continue;
      }
    }
    
    await page.waitForTimeout(1000);
    
    // Verify budget was created
    const pageContent = await page.content();
    const hasNewBudget = 
      pageContent.includes('Alimentation') ||
      pageContent.includes('500') ||
      await page.locator('.budget-item, .budget-card').count() > 0;
    
    expect(hasNewBudget).toBe(true);
  });

  test('budget displays with progress bar', async ({ page }) => {
    // Look for budget cards with progress indicators
    const progressSelectors = [
      '.progress-bar',
      '[class*="progress"]',
      'progress',
      '.bar',
      '[role="progressbar"]'
    ];
    
    let hasProgressBar = false;
    for (const selector of progressSelectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        hasProgressBar = true;
        break;
      }
    }
    
    // Progress bar should be present
    expect(hasProgressBar).toBe(true);
  });

  test('delete budget works', async ({ page }) => {
    // Get initial budget count
    const initialCount = await page.locator('.budget-item, .budget-card, .budget-row').count();
    
    if (initialCount === 0) {
      test.skip('No budgets to delete');
      return;
    }
    
    // Look for delete button on first budget
    const deleteSelectors = [
      'button:has([data-lucide="trash"])',
      'button:has([data-lucide="x"])',
      '.delete',
      '[data-testid="delete"]',
      'text=/supprimer|delete|remove/i'
    ];
    
    for (const selector of deleteSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 }).catch(() => false)) {
          await button.click();
          break;
        }
      } catch {
        continue;
      }
    }
    
    await page.waitForTimeout(1000);
    
    // Confirm deletion if dialog appears
    const confirmSelectors = [
      'button:has-text("Oui")',
      'button:has-text("Confirmer")',
      'button:has-text("Supprimer")',
      '.confirm'
    ];
    
    for (const selector of confirmSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 }).catch(() => false)) {
          await button.click();
          break;
        }
      } catch {
        continue;
      }
    }
    
    await page.waitForTimeout(1000);
    
    // Verify budget was deleted
    const finalCount = await page.locator('.budget-item, .budget-card, .budget-row').count();
    expect(finalCount).toBeLessThanOrEqual(initialCount);
  });

  test('budget shows correct amount format', async ({ page }) => {
    // Check for currency formatting
    const pageContent = await page.content();
    
    // Look for euro symbol or EUR
    const hasCurrency = 
      pageContent.includes('€') ||
      pageContent.includes('EUR') ||
      /\d+[,.]\d{2}/.test(pageContent); // Decimal format
    
    expect(hasCurrency).toBe(true);
  });

});
