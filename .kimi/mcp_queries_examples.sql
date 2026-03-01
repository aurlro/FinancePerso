-- ============================================
-- EXEMPLES DE REQUÊTES MCP SQLITE - FinancePerso
-- ============================================
-- Ces requêtes peuvent être exécutées via le serveur MCP SQLite
-- Schéma: label (pas description), category_validated (pas category), status

-- 1. Stats rapides sur les transactions
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_depenses,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_revenus,
    ROUND(SUM(amount), 2) as balance
FROM transactions
WHERE status = 'validated';

-- 2. Top 10 des catégories de dépenses (mois courant)
SELECT 
    category_validated as categorie,
    COUNT(*) as nb_transactions,
    ROUND(SUM(ABS(amount)), 2) as total_depense
FROM transactions
WHERE amount < 0
    AND status = 'validated'
    AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
GROUP BY category_validated
ORDER BY total_depense DESC
LIMIT 10;

-- 3. Transactions récentes (30 derniers jours)
SELECT 
    date,
    label,
    ROUND(amount, 2) as montant,
    category_validated as categorie,
    member
FROM transactions
WHERE date >= date('now', '-30 days')
    AND status = 'validated'
ORDER BY date DESC
LIMIT 20;

-- 4. Évolution mensuelle (12 derniers mois)
SELECT 
    strftime('%Y-%m', date) as mois,
    ROUND(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 2) as depenses,
    ROUND(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 2) as revenus,
    ROUND(SUM(amount), 2) as solde
FROM transactions
WHERE status = 'validated'
    AND date >= date('now', '-12 months')
GROUP BY strftime('%Y-%m', date)
ORDER BY mois DESC;

-- 5. Dépenses par membre du foyer
SELECT 
    COALESCE(member, 'Anonyme') as membre,
    COUNT(*) as nb_transactions,
    ROUND(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 2) as total_depenses
FROM transactions
WHERE status = 'validated'
GROUP BY member
ORDER BY total_depenses DESC;

-- 6. Recherche par mot-clé (ex: Amazon)
SELECT 
    date,
    label,
    ROUND(amount, 2) as montant,
    category_validated as categorie
FROM transactions
WHERE label LIKE '%Amazon%'
    AND status = 'validated'
ORDER BY date DESC
LIMIT 20;

-- 7. Top 10 plus grosses dépenses
SELECT 
    date,
    label,
    ROUND(ABS(amount), 2) as montant,
    category_validated as categorie
FROM transactions
WHERE amount < 0 AND status = 'validated'
ORDER BY ABS(amount) DESC
LIMIT 10;

-- 8. Transactions sans catégorie
SELECT 
    date,
    label,
    ROUND(amount, 2) as montant
FROM transactions
WHERE (category_validated IS NULL OR category_validated = '') 
    AND status = 'validated'
ORDER BY date DESC
LIMIT 20;

-- 9. Stats par compte
SELECT 
    COALESCE(account_label, 'Compte Principal') as compte,
    COUNT(*) as nb_transactions,
    ROUND(SUM(amount), 2) as solde
FROM transactions
WHERE status = 'validated'
GROUP BY account_label
ORDER BY solde DESC;

-- 10. Analyse des notes/beneficiaires
SELECT 
    notes,
    beneficiary,
    COUNT(*) as occurrences
FROM transactions
WHERE (notes IS NOT NULL AND notes != '') 
   OR (beneficiary IS NOT NULL AND beneficiary != '')
GROUP BY notes, beneficiary
ORDER BY occurrences DESC
LIMIT 10;
