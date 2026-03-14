import { test, expect } from '@playwright/test';

test.describe('Assistant IA Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('#/assistant');
  });

  test('affiche la page assistant avec le titre', async ({ page }) => {
    await expect(page.getByText('Assistant IA')).toBeVisible();
    await expect(page.getByText('Posez-moi vos questions sur vos finances')).toBeVisible();
  });

  test('affiche le message de bienvenue initial', async ({ page }) => {
    await expect(page.getByText('Bienvenue sur votre Assistant IA')).toBeVisible();
    await expect(page.getByText('Analyser mes dépenses')).toBeVisible();
    await expect(page.getByText('Trouver des économies')).toBeVisible();
  });

  test('permet d\'envoyer un message', async ({ page }) => {
    const input = page.getByPlaceholder('Posez votre question');
    await input.fill('Combien ai-je dépensé ce mois-ci ?');
    
    const sendButton = page.getByRole('button', { name: /envoyer/i });
    await sendButton.click();
    
    // Vérifie que le message utilisateur apparaît
    await expect(page.getByText('Combien ai-je dépensé ce mois-ci ?')).toBeVisible();
  });

  test('affiche les suggestions rapides', async ({ page }) => {
    await expect(page.getByText('💰 Analyser mes dépenses')).toBeVisible();
    await expect(page.getByText('💡 Trouver des économies')).toBeVisible();
    await expect(page.getByText('📊 Expliquer mon budget')).toBeVisible();
  });

  test('permet de créer une nouvelle conversation', async ({ page }) => {
    // Clique sur le bouton nouvelle conversation (visible sur desktop)
    const newChatButton = page.getByRole('button', { name: /nouvelle conversation/i });
    if (await newChatButton.isVisible().catch(() => false)) {
      await newChatButton.click();
      // La nouvelle conversation devrait avoir le titre par défaut
      await expect(page.getByText('Nouvelle conversation')).toBeVisible();
    }
  });

  test('vérifie la présence de l\'avatar IA', async ({ page }) => {
    // Vérifie que l'emoji robot est présent
    await expect(page.locator('text=🤖').first()).toBeVisible();
  });
});
