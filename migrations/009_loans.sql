-- ============================================
-- Migration 009: Gestion des Emprunts
-- Description: Tables pour le suivi des prêts et emprunts
-- Date: 2026-02-28
-- ============================================

-- Table des emprunts (prêts immobiliers, consommation, etc.)
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- Nom de l'emprunt (ex: "Prêt Maison")
    lender TEXT,                           -- Organisme prêteur (ex: "Banque Populaire")
    
    -- Montants
    principal_amount REAL NOT NULL,        -- Capital emprunté initial
    total_amount REAL,                     -- Montant total à rembourser (avec intérêts)
    remaining_capital REAL,                -- Capital restant dû
    paid_capital REAL DEFAULT 0,           -- Capital déjà remboursé
    paid_interest REAL DEFAULT 0,          -- Intérêts déjà payés
    
    -- Taux et durée
    interest_rate REAL,                    -- Taux d'intérêt annuel (ex: 2.5 pour 2.5%)
    monthly_payment REAL NOT NULL,         -- Mensualité
    total_duration_months INTEGER,         -- Durée totale en mois
    remaining_months INTEGER,              -- Mois restants
    
    -- Dates
    start_date TEXT,                       -- Date de début (YYYY-MM-DD)
    end_date TEXT,                         -- Date de fin prévue
    
    -- Attribuition
    member_id INTEGER,                     -- Membre concerné (NULL = commun)
    account_type TEXT DEFAULT 'JOINT' CHECK (account_type IN ('PERSONAL_A', 'PERSONAL_B', 'JOINT')),
    
    -- Métadonnées
    is_active BOOLEAN DEFAULT 1,           -- Emprunt en cours ou clôturé
    notes TEXT,                            -- Notes libres
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE SET NULL
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_active ON loans(is_active);
CREATE INDEX IF NOT EXISTS idx_loans_type ON loans(account_type);

-- Trigger pour updated_at
CREATE TRIGGER IF NOT EXISTS trg_loans_updated
AFTER UPDATE ON loans
BEGIN
    UPDATE loans SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Table de liaison transactions <-> emprunts
-- Permet de lier une transaction (mensualité) à un emprunt spécifique
CREATE TABLE IF NOT EXISTS loan_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    amount_breakdown TEXT,                 -- JSON: {"capital": 400, "interest": 100, "insurance": 50}
    period TEXT,                           -- Période concernée (ex: "2024-02")
    is_auto_detected BOOLEAN DEFAULT 0,    -- Détecté automatiquement ou manuel
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    UNIQUE(loan_id, transaction_id)
);

CREATE INDEX IF NOT EXISTS idx_loan_tx_loan ON loan_transactions(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_tx_transaction ON loan_transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_loan_tx_period ON loan_transactions(period);

-- Vue pour obtenir les statistiques des emprunts
CREATE VIEW IF NOT EXISTS v_loan_summary AS
SELECT 
    l.*,
    CASE 
        WHEN l.total_amount > 0 THEN ROUND((l.paid_capital / l.principal_amount) * 100, 2)
        ELSE 0 
    END as repayment_progress_pct,
    CASE 
        WHEN l.remaining_months > 0 THEN l.remaining_months
        WHEN l.total_duration_months > 0 THEN l.total_duration_months - 
            (CAST((julianday('now') - julianday(l.start_date)) / 30 AS INTEGER))
        ELSE 0
    END as calculated_remaining_months,
    m.name as member_name
FROM loans l
LEFT JOIN members m ON l.member_id = m.id
WHERE l.is_active = 1;

-- ============================================
-- DONNÉES DE TEST (optionnel, pour développement)
-- ============================================
-- INSERT INTO loans (name, lender, principal_amount, interest_rate, monthly_payment, total_duration_months, account_type)
-- VALUES ('Prêt Immobilier', 'Banque Pop', 250000, 2.5, 1200, 240, 'JOINT');
