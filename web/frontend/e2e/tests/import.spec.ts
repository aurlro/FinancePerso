import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Import CSV E2E Tests (PR #10)
 * 
 * Tests the CSV import functionality:
 * - Upload CSV file
 * - Map columns
 * - Preview data
 * - Import transactions
 */

test.describe('Import CSV', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('test@example.com');
    await page.getByLabel(/password|mot de passe/i).fill('password123');
    await page.getByRole('button', { name: /connexion|login/i }).click();
    
    // Navigate to import page
    await page.getByRole('link', { name: /import|importer/i }).click();
    await expect(page.getByRole('heading', { name: /import|importer/i })).toBeVisible();
  });

  test('should display import form', async ({ page }) => {
    // Check import form elements
    await expect(page.getByText(/fichier csv|csv file/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sélectionner|browse|choose/i })).toBeVisible();
    await expect(page.getByRole('combobox', { name: /compte|account/i })).toBeVisible();
  });

  test('should upload CSV file', async ({ page }) => {
    // Create test CSV content
    const csvContent = `Date;Libelle;Montant
2024-03-15;Supermarche;-45.20
2024-03-16;Salaire;2500.00
2024-03-17;Essence;-60.00`;
    
    // Write to temp file
    const tempFile = path.join(__dirname, '../temp_test.csv');
    fs.writeFileSync(tempFile, csvContent);
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(tempFile);
    
    // Clean up
    fs.unlinkSync(tempFile);
    
    // Check that preview or mapping step appears
    await expect(page.getByText(/aperçu|preview|mapping|colonnes/i)).toBeVisible();
  });

  test('should map CSV columns', async ({ page }) => {
    // Upload test file first
    const csvContent = `Date;Description;Amount
2024-03-15;Supermarket;-45.20
2024-03-16;Salary;2500.00`;
    
    const tempFile = path.join(__dirname, '../temp_test.csv');
    fs.writeFileSync(tempFile, csvContent);
    
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Wait for mapping interface
    await page.waitForSelector('select, [data-testid="column-mapping"]', { timeout: 5000 });
    
    // Map columns if needed
    const dateMapping = page.locator('select').filter({ hasText: /date/i });
    if (await dateMapping.isVisible().catch(() => false)) {
      await dateMapping.selectOption('Date');
    }
    
    const amountMapping = page.locator('select').filter({ hasText: /montant|amount/i });
    if (await amountMapping.isVisible().catch(() => false)) {
      await amountMapping.selectOption('Amount');
    }
  });

  test('should preview transactions before import', async ({ page }) => {
    // Upload and map file
    const csvContent = `Date;Libelle;Montant
2024-03-15;Supermarche;-45.20`;
    
    const tempFile = path.join(__dirname, '../temp_test.csv');
    fs.writeFileSync(tempFile, csvContent);
    
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Wait for preview
    await expect(page.getByText(/aperçu|preview|transactions à importer/i)).toBeVisible();
    
    // Check preview data
    await expect(page.getByText(/supermarche/i)).toBeVisible();
    await expect(page.getByText(/-45\.20|45\.20/)).toBeVisible();
  });

  test('should import transactions successfully', async ({ page }) => {
    // Upload file
    const csvContent = `Date;Libelle;Montant
2024-03-15;Test Import;-25.50
2024-03-16;Test Salaire;1500.00`;
    
    const tempFile = path.join(__dirname, '../temp_test.csv');
    fs.writeFileSync(tempFile, csvContent);
    
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Select account if required
    const accountSelect = page.getByRole('combobox', { name: /compte|account/i });
    if (await accountSelect.isVisible().catch(() => false)) {
      await accountSelect.selectOption({ index: 1 });
    }
    
    // Click import button
    await page.getByRole('button', { name: /importer|import|confirmer/i }).click();
    
    // Check success message
    await expect(page.getByText(/succès|success|importé|imported/i)).toBeVisible();
    
    // Check summary
    await expect(page.getByText(/2|imported|transactions/)).toBeVisible();
  });

  test('should detect duplicates', async ({ page }) => {
    // Upload file with potential duplicates
    const csvContent = `Date;Libelle;Montant
2024-03-15;Duplicate Test;-30.00`;
    
    const tempFile = path.join(__dirname, '../temp_test.csv');
    fs.writeFileSync(tempFile, csvContent);
    
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Import once
    await page.getByRole('button', { name: /importer|import|confirmer/i }).click();
    await expect(page.getByText(/succès|success/i)).toBeVisible();
    
    // Try to import same file again
    fs.writeFileSync(tempFile, csvContent);
    await page.goto('/import');
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Check duplicate detection
    await expect(page.getByText(/doublon|duplicate|déjà importé/i)).toBeVisible();
  });

  test('should handle invalid CSV format', async ({ page }) => {
    // Upload invalid file
    const invalidContent = `This is not a valid CSV
Just some random text`;
    
    const tempFile = path.join(__dirname, '../temp_test.txt');
    fs.writeFileSync(tempFile, invalidContent);
    
    await page.locator('input[type="file"]').setInputFiles(tempFile);
    fs.unlinkSync(tempFile);
    
    // Check error message
    await expect(page.getByText(/erreur|error|invalide|invalid/i)).toBeVisible();
  });

});
