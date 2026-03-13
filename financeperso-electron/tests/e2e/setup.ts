import { test as base, electron, ElectronApplication, Page } from '@playwright/test';
import * as path from 'path';

/**
 * Helper functions and fixtures for Electron E2E tests
 */

/**
 * Launch Electron app in test mode
 * @returns ElectronApplication instance
 */
export async function launchElectronApp(): Promise<ElectronApplication> {
  // Get the path to the Electron executable
  const electronPath = require('electron');
  
  // Path to the main process entry point
  const mainPath = path.join(process.cwd(), '.vite', 'build', 'main.js');
  
  // Launch Electron app
  const electronApp = await electron.launch({
    args: [mainPath],
    env: {
      ...process.env,
      NODE_ENV: 'test',
      ELECTRON_IS_TEST: 'true',
      ELECTRON_IS_DEV: 'true',
    },
  });

  return electronApp;
}

/**
 * Wait for the renderer process to be ready
 * @param page - Playwright Page instance
 */
export async function waitForRenderer(page: Page): Promise<void> {
  // Wait for the app to be fully loaded
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
  
  // Wait for React to mount the app
  await page.waitForSelector('#root', { timeout: 30000 });
  
  // Additional wait for any async initialization
  await page.waitForTimeout(500);
}

/**
 * Get the first BrowserWindow
 * @param electronApp - ElectronApplication instance
 * @returns Page instance
 */
export async function getFirstWindow(electronApp: ElectronApplication): Promise<Page> {
  const page = await electronApp.firstWindow();
  await waitForRenderer(page);
  return page;
}

/**
 * Custom test fixture with Electron app
 */
export type TestFixtures = {
  electronApp: ElectronApplication;
  page: Page;
};

/**
 * Extended test with Electron fixtures
 */
export const test = base.extend<TestFixtures>({
  electronApp: [async ({}, use) => {
    const electronApp = await launchElectronApp();
    await use(electronApp);
    await electronApp.close();
  }, { scope: 'test' }],
  
  page: [async ({ electronApp }, use) => {
    const page = await getFirstWindow(electronApp);
    await use(page);
  }, { scope: 'test' }],
});

/**
 * Take a named screenshot
 * @param page - Playwright Page
 * @param name - Screenshot name
 */
export async function takeScreenshot(page: Page, name: string): Promise<void> {
  await page.screenshot({ 
    path: `test-results/screenshots/${name}.png`,
    fullPage: true 
  });
}

/**
 * Check if element exists on page
 * @param page - Playwright Page
 * @param selector - CSS selector or text
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Safe click with retry
 * @param page - Playwright Page
 * @param selector - Element selector
 */
export async function safeClick(page: Page, selector: string): Promise<void> {
  await page.waitForSelector(selector, { timeout: 10000 });
  await page.click(selector);
}

export { expect } from '@playwright/test';
