import { rm } from 'fs/promises';
import * as path from 'path';

/**
 * Global setup for E2E tests
 * - Cleans up previous test results
 * - Sets up test environment
 */
async function globalSetup() {
  console.log('🚀 Starting E2E test suite setup...');
  
  // Clean up test results from previous runs
  try {
    await rm(path.join(process.cwd(), 'test-results'), { recursive: true, force: true });
    console.log('✅ Cleaned up previous test results');
  } catch {
    // Directory might not exist, that's fine
  }
  
  // Set environment variables for testing
  process.env.NODE_ENV = 'test';
  process.env.ELECTRON_IS_TEST = 'true';
  
  console.log('✅ Global setup complete');
}

export default globalSetup;
