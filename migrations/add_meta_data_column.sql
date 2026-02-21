-- Migration: Ajout du champ meta_data à la table transactions
-- =============================================================
-- Ce champ stocke les métadonnées de catégorisation au format JSON
-- 
-- Date: 2024-01-15
-- Version: 2.0

-- Vérifier si la colonne existe déjà
SELECT CASE 
    WHEN COUNT(*) = 0 THEN 'Column does not exist - will add'
    ELSE 'Column already exists - skipping'
END as migration_status
FROM pragma_table_info('transactions')
WHERE name = 'meta_data';

-- Ajouter la colonne meta_data si elle n'existe pas
ALTER TABLE transactions ADD COLUMN meta_data TEXT;

-- Mettre à jour les transactions existantes avec des métadonnées par défaut
UPDATE transactions 
SET meta_data = json_object(
    'categorization', json_object(
        'method', 'LEGACY',
        'confidence_score', 1.0,
        'timestamp', datetime('now'),
        'version', '1.0'
    ),
    'migrated', true
)
WHERE meta_data IS NULL 
AND category_validated IS NOT NULL;

-- Vérification
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN meta_data IS NOT NULL THEN 1 ELSE 0 END) as with_metadata,
    SUM(CASE WHEN meta_data IS NULL THEN 1 ELSE 0 END) as without_metadata
FROM transactions;
