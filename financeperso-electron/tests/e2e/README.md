# E2E Tests for FinancePerso Electron

This directory contains the end-to-end (E2E) test suite for FinancePerso Electron application using Playwright.

## Structure

```
tests/
├── e2e/
│   ├── setup.ts              # Test fixtures and helpers
│   ├── global-setup.ts       # Global test setup
│   ├── global-teardown.ts    # Global test teardown
│   ├── smoke.spec.ts         # Smoke tests (basic functionality)
│   ├── dashboard.spec.ts     # Dashboard tests
│   ├── import.spec.ts        # CSV import tests
│   ├── budgets.spec.ts       # Budget management tests
│   ├── validation.spec.ts    # Transaction validation tests
│   └── navigation.spec.ts    # Navigation tests
└── fixtures/
    └── sample-transactions.csv  # Sample data for tests
```

## Running Tests

### Prerequisites

```bash
# Install dependencies (including Playwright)
npm install

# Install Playwright browsers
npx playwright install
```

### Run All Tests

```bash
npm run test:e2e
```

### Run Tests with UI Mode

```bash
npm run test:e2e:ui
```

### Run Tests in Debug Mode

```bash
npm run test:e2e:debug
```

### Run Tests in Headed Mode (see browser)

```bash
npm run test:e2e:headed
```

### Run Only Smoke Tests

```bash
npm run test:e2e:smoke
```

## Test Categories

### Smoke Tests (`smoke.spec.ts`)
- App starts without error
- Correct window title
- No console errors on startup
- Navigation is visible

### Dashboard Tests (`dashboard.spec.ts`)
- Dashboard displays 3 KPIs
- Navigation to transactions works
- Charts are loaded (canvas or SVG)
- Screenshot of dashboard
- Current period is shown

### Import Tests (`import.spec.ts`)
- Import CSV with comma separator
- Import with semicolon separator
- Duplicate detection
- Column mapping verification

### Budgets Tests (`budgets.spec.ts`)
- Create a budget
- Budget displays with progress bar
- Delete budget works
- Correct amount format

### Validation Tests (`validation.spec.ts`)
- Pending transactions displayed
- Batch validation works
- Ignore transaction works
- Category suggestions shown
- Transaction details visible

### Navigation Tests (`navigation.spec.ts`)
- All main routes accessible
- Keyboard navigation with Tab
- Sidebar navigation present
- Active route highlighted
- Keyboard shortcuts work

## Configuration

The test configuration is in `playwright.config.ts`:
- Tests run on desktop only (no mobile)
- Screenshots on failure
- Video recording optional (set `USE_VIDEO=1`)
- Single worker (required for Electron)

## Environment Variables

- `CI`: Set automatically in CI environment
- `NODE_ENV`: Set to 'test' during tests
- `ELECTRON_IS_TEST`: Set to 'true' for test mode
- `USE_VIDEO`: Set to '1' to enable video recording
- `SKIP_WEBSERVER`: Set to skip starting the dev server

## Artifacts

Test artifacts are saved to:
- Screenshots: `test-results/screenshots/`
- Videos: `test-results/` (if enabled)
- HTML Report: `test-results/html-report/`
- JUnit XML: `test-results/junit.xml`

## CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

Tested on: Ubuntu, macOS, and Windows.

## Writing New Tests

Use the custom test fixture with Electron support:

```typescript
import { test, expect } from './setup';

test('my test', async ({ page, electronApp }) => {
  // page is the Electron renderer page
  // electronApp is the Electron application instance
  
  await page.click('button');
  await expect(page.locator('.result')).toHaveText('Success');
});
```

## Helpers

- `takeScreenshot(page, name)` - Take a named screenshot
- `elementExists(page, selector)` - Check if element exists
- `safeClick(page, selector)` - Click with retry
- `waitForRenderer(page)` - Wait for app to be ready
