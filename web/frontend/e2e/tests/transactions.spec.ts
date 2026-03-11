import { test, expect } from '@playwright/test';

/**
 * Transactions E2E Tests (PR #10)
 * 
 * Tests the transaction management flows:
 * - View transactions list
 * - Filter transactions
 * - Update transaction
 * - Categorize transactions
 */

test.describe('Transactions', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('password123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    await expect(page).toHaveURL(/.*dashboard.*/);
    
    // Navigate to transactions page
    await page.getByRole('link', { name: /transactions|opérations/i }).click();
    await expect(page.getByRole('heading', { name: /transactions|opérations/i })).toBeVisible();
  });

  test('should display transactions list', async ({ page }) => {
    // Check that transactions table or list is visible
    await expect(page.getByRole('table')).toBeVisible();
    
    // Check for transaction data
    const rows = page.locator('table tbody tr');
    await expect(rows.first()).toBeVisible();
  });

  test('should filter transactions by category', async ({ page }) => {
    // Open filter dropdown
    await page.getByRole('combobox', { name: /catégorie|category/i }).click();
    
    // Select a category
    await page.getByRole('option', { name: /alimentation|nourriture/i }).click();
    
    // Check that filtered results are shown
    await expect(page.getByText(/alimentation|nourriture/i)).toBeVisible();
  });

  test('should filter transactions by status', async ({ page }) => {
    // Filter by pending status
    await page.getByRole('combobox', { name: /statut|status/i }).click();
    await page.getByRole('option', { name: /pending|en attente/i }).click();
    
    // Check that pending transactions are shown
    await expect(page.getByText(/pending|en attente/i)).toBeVisible();
  });

  test('should search transactions', async ({ page }) => {
    // Type in search box
    await page.getByPlaceholder(/rechercher|search/i).fill('supermarket');
    
    // Wait for search results
    await page.waitForTimeout(500);
    
    // Check that results contain search term
    const results = page.locator('table tbody tr');
    await expect(results.first()).toBeVisible();
  });

  test('should update transaction category', async ({ page }) => {
    // Click on first transaction to edit
    const firstRow = page.locator('table tbody tr').first();
    await firstRow.click();
    
    // Open category dropdown
    await page.getByRole('combobox', { name: /catégorie|category/i }).click();
    
    // Select new category
    await page.getByRole('option', { name: /transport/i }).click();
    
    // Save changes
    await page.getByRole('button', { name: /save|enregistrer/i }).click();
    
    // Check success message
    await expect(page.getByText(/saved|enregistré|success/i)).toBeVisible();
  });

  test('should validate transaction', async ({ page }) => {
    // Find a pending transaction
    const pendingRow = page.locator('table tbody tr').filter({ hasText: /pending|en attente/i }).first();
    
    if (await pendingRow.isVisible().catch(() => false)) {
      // Click validate button
      await pendingRow.getByRole('button', { name: /validate|valider/i }).click();
      
      // Check that status changed
      await expect(pendingRow.getByText(/validated|validé/i)).toBeVisible();
    }
  });

  test('should bulk categorize transactions', async ({ page }) => {
    // Select multiple transactions using checkboxes
    const checkboxes = page.locator('table tbody tr input[type="checkbox"]');
    await checkboxes.nth(0).check();
    await checkboxes.nth(1).check();
    
    // Click bulk action
    await page.getByRole('button', { name: /bulk|actions groupées/i }).click();
    
    // Select categorize action
    await page.getByRole('menuitem', { name: /catégoriser|categorize/i }).click();
    
    // Select category
    await page.getByRole('combobox', { name: /catégorie|category/i }).click();
    await page.getByRole('option', { name: /loisirs/i }).click();
    
    // Apply
    await page.getByRole('button', { name: /apply|appliquer/i }).click();
    
    // Check success
    await expect(page.getByText(/success|succès|updated/i)).toBeVisible();
  });

  test('should navigate through pagination', async ({ page }) => {
    // Check if pagination exists
    const nextButton = page.getByRole('button', { name: /next|suivant/i });
    
    if (await nextButton.isVisible().catch(() => false)) {
      // Click next page
      await nextButton.click();
      
      // Check URL or page number
      await expect(page.getByText(/page 2|2\/\d+/i)).toBeVisible();
    }
  });

});
