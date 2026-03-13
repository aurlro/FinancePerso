import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';

/**
 * Playwright configuration for FinancePerso Electron app E2E tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  /* Run tests in files in parallel */
  fullyParallel: false, // Electron tests should run sequentially
  
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI */
  workers: 1, // Electron tests must be single worker
  
  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['list'],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],
  
  /* Shared settings for all the projects below */
  use: {
    /* Maximum time each action such as `click()` can take */
    actionTimeout: 15000,
    
    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video recording - off by default, can be enabled with USE_VIDEO=1 */
    video: process.env.USE_VIDEO ? 'on-first-retry' : 'off',
  },

  /* Configure projects for major desktop browsers */
  projects: [
    {
      name: 'electron',
      use: {
        // Electron-specific options
        browserName: 'chromium',
      },
    },
  ],

  /* Folder for test artifacts such as screenshots, videos, traces */
  outputDir: 'test-results/',
  
  /* Run local dev server before starting the tests */
  webServer: process.env.SKIP_WEBSERVER ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
  
  /* Global setup and teardown */
  globalSetup: require.resolve('./tests/e2e/global-setup'),
  globalTeardown: require.resolve('./tests/e2e/global-teardown'),
});
