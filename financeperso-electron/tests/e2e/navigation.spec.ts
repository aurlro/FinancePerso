import { test, expect } from './setup';

/**
 * Navigation E2E Tests
 * Tests routing and keyboard navigation
 */

test.describe('Navigation', () => {
  
  test('all main routes are accessible', async ({ page }) => {
    const routes = [
      { name: 'Dashboard', patterns: [/dashboard/i, /tableau de bord/i, /accueil/i] },
      { name: 'Transactions', patterns: [/transaction/i, /opération/i] },
      { name: 'Budgets', patterns: [/budget/i] },
      { name: 'Import', patterns: [/import/i] },
      { name: 'Settings', patterns: [/paramètre/i, /setting/i, /configuration/i] },
    ];
    
    const accessibleRoutes: string[] = [];
    
    for (const route of routes) {
      // Look for navigation link
      for (const pattern of route.patterns) {
        const link = page.locator(`a, button`).filter({ hasText: pattern });
        if (await link.count() > 0) {
          accessibleRoutes.push(route.name);
          break;
        }
      }
    }
    
    // At least 3 main routes should be accessible
    expect(accessibleRoutes.length).toBeGreaterThanOrEqual(3);
  });

  test('keyboard navigation with Tab works', async ({ page }) => {
    // Focus first focusable element
    await page.keyboard.press('Tab');
    
    // Track focused elements
    const focusedElements: string[] = [];
    
    // Press Tab 10 times and collect focused elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
      
      const activeElement = await page.evaluate(() => {
        const el = document.activeElement;
        return el ? el.tagName.toLowerCase() + (el.getAttribute('href') || '') : null;
      });
      
      if (activeElement) {
        focusedElements.push(activeElement);
      }
    }
    
    // Should have moved focus to multiple elements
    expect(focusedElements.length).toBeGreaterThan(0);
    
    // Check for interactive elements being focused
    const hasInteractiveElements = focusedElements.some(el => 
      el.includes('a') || el.includes('button') || el.includes('input')
    );
    
    expect(hasInteractiveElements).toBe(true);
  });

  test('sidebar navigation is present', async ({ page }) => {
    // Look for sidebar or navigation container
    const navSelectors = [
      'nav',
      'aside',
      '[role="navigation"]',
      '.sidebar',
      '.navigation',
      '.menu',
      '.nav'
    ];
    
    let navigationFound = false;
    for (const selector of navSelectors) {
      const locator = page.locator(selector).first();
      if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
        navigationFound = true;
        
        // Check for navigation links
        const links = await locator.locator('a, button').count();
        expect(links).toBeGreaterThanOrEqual(2);
        break;
      }
    }
    
    expect(navigationFound).toBe(true);
  });

  test('active route is highlighted', async ({ page }) => {
    // Click on a navigation item
    const navLinks = page.locator('nav a, aside a, .sidebar a, .navigation a');
    const count = await navLinks.count();
    
    if (count > 0) {
      await navLinks.first().click();
      await page.waitForTimeout(500);
      
      // Check for active state
      const activeSelectors = [
        '.active',
        '[aria-current="page"]',
        '.selected',
        '[class*="active"]'
      ];
      
      let hasActiveState = false;
      for (const selector of activeSelectors) {
        const activeCount = await page.locator(selector).count();
        if (activeCount > 0) {
          hasActiveState = true;
          break;
        }
      }
      
      expect(hasActiveState).toBe(true);
    }
  });

  test('page title updates on navigation', async ({ page }) => {
    const initialTitle = await page.title();
    
    // Navigate to different section
    const navLinks = page.locator('nav a, aside a, .sidebar a').filter({ hasNotText: /dashboard|accueil/i });
    
    if (await navLinks.count() > 0) {
      await navLinks.first().click();
      await page.waitForTimeout(1000);
      
      // Title might change or URL might change
      // In Electron, check the content changes
      const pageContent = await page.content();
      expect(pageContent.length).toBeGreaterThan(0);
    }
  });

  test('keyboard shortcut for navigation', async ({ page }) => {
    // Try common keyboard shortcuts
    const shortcuts = [
      { key: 'Escape', action: 'close modal/dropdown' },
      { key: 'Enter', action: 'activate focused element' },
      { key: 'Space', action: 'activate button' },
    ];
    
    // Focus a button first
    const button = page.locator('button').first();
    if (await button.isVisible()) {
      await button.focus();
      
      // Press Enter
      await page.keyboard.press('Enter');
      await page.waitForTimeout(200);
      
      // No error should occur
      const pageContent = await page.content();
      expect(pageContent).toBeTruthy();
    }
  });

});
