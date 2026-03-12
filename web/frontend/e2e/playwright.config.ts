import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration (PR #10)
 * 
 * Run tests:
 *   npx playwright test
 * 
 * Run tests in headed mode:
 *   npx playwright test --headed
 * 
 * Run specific test:
 *   npx playwright test auth.spec.ts
 * 
 * Debug mode:
 *   npx playwright test --debug
 */

export default defineConfig({
  testDir: './tests',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use */
  reporter: 'html',
  
  /* Shared settings for all the projects below */
  use: {
    /* Base URL to use in actions like `await page.goto('/')` */
    baseURL: process.env.FRONTEND_URL || 'http://localhost:8080',
    
    /* API URL for backend requests */
    apiBaseURL: process.env.API_URL || 'http://localhost:8000/api',
    
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video recording */
    video: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    /* Test against mobile viewports */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* Run local dev server before starting the tests */
  webServer: [
    {
      command: 'cd .. && python web/api/start_api.py',
      url: 'http://localhost:8000/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 30000,
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:8080',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
  ],
});
