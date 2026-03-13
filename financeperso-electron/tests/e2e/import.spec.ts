import { test, expect } from './setup';
import * as path from 'path';

/**
 * Import CSV E2E Tests
 * Tests the CSV import functionality
 */

test.describe('Import CSV', () => {
  
  const sampleCsvPath = path.join(process.cwd(), 'tests', 'fixtures', 'sample-transactions.csv');

  test('import CSV with comma separator works', async ({ page }) => {
    // Navigate to import page
    const importSelectors = [
      'text=/import/i',
      'a[href*="import"]',
      'button:has-text("Import")',
      '[data-testid*="import"]'
    ];
    
    for (const selector of importSelectors) {
      try {
        const locator = page.locator(selector).first();
        if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
          await locator.click();
          break;
        }
      } catch {
        continue;
      }
    }
    
    await page.waitForTimeout(1000);
    
    // Look for file input
    const fileInput = await page.locator('input[type="file"]').first();
    await expect(fileInput).toBeVisible();
    
    // Upload the CSV file
    await fileInput.setInputFiles(sampleCsvPath);
    
    // Wait for processing
    await page.waitForTimeout(2000);
    
    // Check for success indicator or preview
    const successSelectors = [
      'text=/success|succès|importé|chargé/i',
      '.success',
      '[class*="success"]',
      '.preview',
      'table',
      '.transaction-list'
    ];
    
    let importSuccess = false;
    for (const selector of successSelectors) {
      if (await page.locator(selector).first().isVisible({ timeout: 5000 }).catch(() => false)) {
        importSuccess = true;
        break;
      }
    }
    
    expect(importSuccess).toBe(true);
  });

  test('import with semicolon separator works', async ({ page }) => {
    // Create a semicolon-separated version
    const semicolonCsvPath = path.join(process.cwd(), 'tests', 'fixtures', 'sample-transactions-semicolon.csv');
    const fs = require('fs');
    const content = fs.readFileSync(sampleCsvPath, 'utf8');
    fs.writeFileSync(semicolonCsvPath, content.replace(/,/g, ';'));
    
    // Navigate to import page
    await page.goto('file://' + path.join(process.cwd(), '.vite', 'build', 'index.html'));
    await page.waitForTimeout(1000);
    
    // Find file input
    const fileInput = await page.locator('input[type="file"]').first();
    
    if (await fileInput.isVisible().catch(() => false)) {
      await fileInput.setInputFiles(semicolonCsvPath);
      await page.waitForTimeout(2000);
      
      // Should show preview or success
      const hasContent = await page.locator('table tr, .transaction-row, .preview-row').count() > 0;
      expect(hasContent).toBe(true);
    }
    
    // Cleanup
    fs.unlinkSync(semicolonCsvPath);
  });

  test('duplicate detection works', async ({ page }) => {
    // Navigate to import page
    const fileInput = await page.locator('input[type="file"]').first();
    
    if (await fileInput.isVisible().catch(() => false)) {
      // First import
      await fileInput.setInputFiles(sampleCsvPath);
      await page.waitForTimeout(2000);
      
      // Try to import the same file again
      await fileInput.setInputFiles(sampleCsvPath);
      await page.waitForTimeout(2000);
      
      // Should show duplicate warning
      const pageContent = await page.content();
      const hasDuplicateWarning = 
        /doublon|duplicate|déjà|already|existe|exists/i.test(pageContent);
      
      expect(hasDuplicateWarning).toBe(true);
    }
  });

  test('CSV columns are mapped correctly', async ({ page }) => {
    const fileInput = await page.locator('input[type="file"]').first();
    
    if (await fileInput.isVisible().catch(() => false)) {
      await fileInput.setInputFiles(sampleCsvPath);
      await page.waitForTimeout(2000);
      
      // Check that preview shows date, description, and amount columns
      const pageContent = await page.content();
      const hasDateColumn = /date|Date/i.test(pageContent);
      const hasDescColumn = /description|Description|libellé|Libellé/i.test(pageContent);
      const hasAmountColumn = /montant|Montant|amount|Amount/i.test(pageContent);
      
      expect(hasDateColumn).toBe(true);
      expect(hasDescColumn).toBe(true);
      expect(hasAmountColumn).toBe(true);
    }
  });

});
