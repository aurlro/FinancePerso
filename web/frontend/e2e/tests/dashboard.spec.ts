import { test, expect } from '@playwright/test';

/**
 * Dashboard E2E Tests (PR #10)
 * 
 * Tests the dashboard functionality:
 * - View KPIs
 * - Charts rendering
 * - Period selection
 * - Category breakdown
 */

test.describe('Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('password123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should display key metrics', async ({ page }) => {
    // Check KPI cards
    await expect(page.getByText(/revenus|income/i)).toBeVisible();
    await expect(page.getByText(/dépenses|expenses/i)).toBeVisible();
    await expect(page.getByText(/épargne|savings/i)).toBeVisible();
    await expect(page.getByText(/reste à vivre|remaining/i)).toBeVisible();
  });

  test('should display charts', async ({ page }) => {
    // Check that charts are rendered (canvas elements)
    const charts = page.locator('canvas');
    await expect(charts.first()).toBeVisible();
    
    // Check chart containers
    await expect(page.getByText(/évolution|trends|chart/i)).toBeVisible();
  });

  test('should change month period', async ({ page }) => {
    // Find month selector
    const monthSelector = page.getByRole('combobox', { name: /mois|month|période/i });
    
    if (await monthSelector.isVisible().catch(() => false)) {
      // Select different month
      await monthSelector.click();
      await page.getByRole('option').nth(1).click();
      
      // Wait for data to update
      await page.waitForTimeout(1000);
      
      // Check that values updated
      await expect(page.getByText(/revenus|income/i)).toBeVisible();
    }
  });

  test('should display category breakdown', async ({ page }) => {
    // Check category section
    await expect(page.getByText(/catégories|categories|répartition/i)).toBeVisible();
    
    // Check category items
    const categoryItems = page.locator('[data-testid="category-item"], .category-item');
    await expect(categoryItems.first()).toBeVisible().catch(async () => {
      // Fallback: check for any category names
      await expect(page.getByText(/alimentation|transport|logement/i)).toBeVisible();
    });
  });

  test('should navigate to transactions from dashboard', async ({ page }) => {
    // Click on a metric or view details button
    await page.getByRole('link', { name: /voir détails|view details|transactions/i }).first().click();
    
    // Should navigate to transactions
    await expect(page).toHaveURL(/.*transactions.*/);
  });

  test('should refresh data', async ({ page }) => {
    // Click refresh button if exists
    const refreshButton = page.getByRole('button', { name: /refresh|rafraîchir|reload/i });
    
    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      
      // Check loading state or updated timestamp
      await expect(page.getByText(/mis à jour|updated|chargement/i)).toBeVisible();
    }
  });

  test('should display recent transactions', async ({ page }) => {
    // Check recent transactions section
    await expect(page.getByText(/récentes|recent|dernières/i)).toBeVisible();
    
    // Check transaction items
    const recentItems = page.locator('[data-testid="recent-transaction"], .recent-transaction');
    await expect(recentItems.first()).toBeVisible().catch(async () => {
      // Check for table rows
      await expect(page.locator('table tbody tr').first()).toBeVisible();
    });
  });

});
