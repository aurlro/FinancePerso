-- ============================================
-- Migration 008: Couple Edition
-- Description: Tables pour la gestion couple avec confidentialité
-- Date: 2026-02-28
-- ============================================

-- Table de mapping Carte → Membre
-- Permet d'attribuer automatiquement une transaction à un membre
-- selon le suffixe de la carte utilisée
CREATE TABLE IF NOT EXISTS card_member_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_suffix TEXT UNIQUE NOT NULL,  -- Les 4 derniers chiffres: "1234"
    member_id INTEGER,                 -- NULL = carte jointe/inconnue
    account_type TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (account_type IN ('PERSONAL_A', 'PERSONAL_B', 'JOINT', 'UNKNOWN')),
    label TEXT,                        -- Libellé lisible: "CB Perso Aurélien"
    is_active BOOLEAN DEFAULT 1,       -- Permet de désactiver sans supprimer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE SET NULL
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_card_member_suffix ON card_member_mappings(card_suffix);
CREATE INDEX IF NOT EXISTS idx_card_member_type ON card_member_mappings(account_type);
CREATE INDEX IF NOT EXISTS idx_card_member_active ON card_member_mappings(is_active);

-- Trigger pour mettre à jour updated_at
CREATE TRIGGER IF NOT EXISTS trg_card_member_mappings_updated
AFTER UPDATE ON card_member_mappings
BEGIN
    UPDATE card_member_mappings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Table des paramètres couple
-- Stocke la configuration globale du mode couple
CREATE TABLE IF NOT EXISTS couple_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton: une seule ligne
    member_a_id INTEGER,                    -- Référence vers members (ex: Aurélien)
    member_b_id INTEGER,                    -- Référence vers members (ex: Elise)
    current_user_id INTEGER,                -- Qui utilise l'app actuellement
    joint_account_labels TEXT DEFAULT '[]', -- JSON: ["COMPTE JOINT", "LIVRET COMMUN"]
    show_partner_details BOOLEAN DEFAULT 0, -- Pour debug/test, normalement 0
    transfer_detection_days INTEGER DEFAULT 3, -- Fenêtre de détection des virements
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_a_id) REFERENCES members(id) ON DELETE SET NULL,
    FOREIGN KEY (member_b_id) REFERENCES members(id) ON DELETE SET NULL,
    FOREIGN KEY (current_user_id) REFERENCES members(id) ON DELETE SET NULL
);

-- Trigger pour updated_at
CREATE TRIGGER IF NOT EXISTS trg_couple_settings_updated
AFTER UPDATE ON couple_settings
BEGIN
    UPDATE couple_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Table des virements internes détectés
-- Permet de tracker et valider les virements entre comptes
CREATE TABLE IF NOT EXISTS detected_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_transaction_id INTEGER NOT NULL,
    to_transaction_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,                 -- NULL = en attente de validation
    is_validated BOOLEAN DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (from_transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (to_transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    UNIQUE(from_transaction_id, to_transaction_id)
);

CREATE INDEX IF NOT EXISTS idx_transfers_from ON detected_transfers(from_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to ON detected_transfers(to_transaction_id);
CREATE INDEX IF NOT EXISTS idx_transfers_validated ON detected_transfers(is_validated);

-- ============================================
-- DONNÉES INITIALES
-- ============================================

-- Créer la ligne de configuration couple si elle n'existe pas
INSERT OR IGNORE INTO couple_settings (id) VALUES (1);

-- ============================================
-- MIGRATION DES DONNÉES EXISTANTES
-- ============================================

-- Détecter automatiquement les cartes existantes et les marquer comme UNKNOWN
INSERT OR IGNORE INTO card_member_mappings (card_suffix, account_type, label)
SELECT DISTINCT 
    card_suffix,
    'UNKNOWN',
    'Carte ****' || card_suffix || ' (à configurer)'
FROM transactions
WHERE card_suffix IS NOT NULL 
  AND card_suffix != ''
  AND card_suffix NOT IN (SELECT card_suffix FROM card_member_mappings);

-- ============================================
-- VUES UTILITAIRES
-- ============================================

-- Vue pour obtenir les transactions avec leur propriétaire
CREATE VIEW IF NOT EXISTS v_transactions_with_owner AS
SELECT 
    t.*,
    COALESCE(cm.account_type, 'UNKNOWN') as owner_type,
    cm.member_id as owner_member_id,
    CASE 
        WHEN cs.current_user_id IS NULL THEN 'UNKNOWN'
        WHEN cm.member_id = cs.current_user_id THEN 'ME'
        WHEN cm.member_id IS NOT NULL THEN 'PARTNER'
        WHEN cm.account_type = 'JOINT' THEN 'JOINT'
        ELSE 'UNKNOWN'
    END as visibility_role
FROM transactions t
LEFT JOIN card_member_mappings cm ON t.card_suffix = cm.card_suffix AND cm.is_active = 1
CROSS JOIN couple_settings cs
WHERE t.status = 'validated';
