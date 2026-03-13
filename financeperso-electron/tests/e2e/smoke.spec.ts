import { test, expect } from './setup';

/**
 * Smoke tests - Basic app functionality
 * Tests that the app starts and renders correctly
 */

test.describe('Smoke Tests', () => {
  
  test('app starts without error', async ({ page }) => {
    // Verify the app root element exists
    const root = await page.locator('#root');
    await expect(root).toBeVisible();
    
    // Take screenshot of initial load
    await page.screenshot({ path: 'test-results/screenshots/smoke-app-start.png' });
  });

  test('app title is correct', async ({ page }) => {
    // Wait for the title to be set
    await page.waitForTimeout(500);
    
    // Get the page title (Electron window title)
    const title = await page.title();
    
    // App should have FinancePerso in the title
    expect(title.toLowerCase()).toContain('finance');
  });

  test('no console errors on startup', async ({ page }) => {
    const consoleErrors: string[] = [];
    
    // Listen for console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Wait a bit for any startup errors
    await page.waitForTimeout(2000);
    
    // Check for critical errors (ignore React dev warnings)
    const criticalErrors = consoleErrors.filter(err => 
      !err.includes('React') && 
      !err.includes('StrictMode') &&
      !err.includes('devTools')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('main navigation is visible', async ({ page }) => {
    // Look for navigation elements
    const navSelectors = [
      'nav',
      '[role="navigation"]',
      '.sidebar',
      '.navigation',
      '.menu'
    ];
    
    let navigationFound = false;
    for (const selector of navSelectors) {
      if (await page.locator(selector).isVisible().catch(() => false)) {
        navigationFound = true;
        break;
      }
    }
    
    expect(navigationFound).toBe(true);
  });

});
