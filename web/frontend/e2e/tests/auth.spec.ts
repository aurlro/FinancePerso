import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests (PR #10)
 * 
 * Tests the critical authentication flows:
 * - Login
 * - Registration
 * - Logout
 * - Protected routes
 */

test.describe('Authentication', () => {
  
  test.beforeEach(async ({ page }) => {
    // Go to home page before each test
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    // Check that login form elements are visible
    await expect(page.getByRole('heading', { name: /connexion|login/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password|mot de passe/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /connexion|login|sign in/i })).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Fill in login form
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('password123');
    
    // Click login button
    await page.getByRole('button', { name: /connexion|login|sign in/i }).click();
    
    // Wait for navigation to dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
    
    // Check that user is logged in (avatar or user menu visible)
    await expect(page.getByText(/dashboard|tableau de bord/i)).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Fill in wrong credentials
    await page.getByLabel(/email/i).fill('wrong@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('wrongpassword');
    
    // Click login button
    await page.getByRole('button', { name: /connexion|login|sign in/i }).click();
    
    // Check error message
    await expect(page.getByText(/invalid|incorrect|erreur|échec/i)).toBeVisible();
    
    // Should stay on login page
    await expect(page).toHaveURL(/.*login|auth.*/);
  });

  test('should navigate to registration page', async ({ page }) => {
    // Click on register link
    await page.getByRole('link', { name: /register|inscription|créer un compte/i }).click();
    
    // Check registration form
    await expect(page.getByRole('heading', { name: /inscription|register|sign up/i })).toBeVisible();
    await expect(page.getByLabel(/name|nom/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password|mot de passe/i)).toBeVisible();
  });

  test('should register new user', async ({ page }) => {
    // Navigate to registration
    await page.getByRole('link', { name: /register|inscription|créer un compte/i }).click();
    
    // Fill registration form
    const timestamp = Date.now();
    await page.getByLabel(/name|nom/i).fill(`Test User ${timestamp}`);
    await page.getByLabel(/email/i).fill(`test${timestamp}@example.com`);
    await page.getByLabel(/password|mot de passe/i).fill('Password123!');
    
    // Submit form
    await page.getByRole('button', { name: /register|inscription|sign up|créer/i }).click();
    
    // Should redirect to dashboard or login
    await expect(page).toHaveURL(/.*(dashboard|login|auth).*/);
  });

  test('should logout successfully', async ({ page }) => {
    // First login
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('password123');
    await page.getByRole('button', { name: /connexion|login|sign in/i }).click();
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
    
    // Click logout
    await page.getByRole('button', { name: /logout|déconnexion/i }).click();
    
    // Should redirect to login
    await expect(page).toHaveURL(/.*login|auth.*/);
    
    // Login form should be visible again
    await expect(page.getByRole('heading', { name: /connexion|login/i })).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access dashboard directly without login
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*login|auth.*/);
  });

});
