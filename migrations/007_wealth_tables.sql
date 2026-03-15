-- Migration: Tables pour la gestion du patrimoine
-- Created: 2026-03-14

-- Table des actifs
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- real_estate, savings, investment, etc.
    value REAL NOT NULL DEFAULT 0,
    acquisition_date DATE,
    category TEXT DEFAULT 'Autre',
    notes TEXT,
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE
);

-- Index sur les actifs
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);

-- Table des objectifs d'épargne
CREATE TABLE IF NOT EXISTS savings_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    current_amount REAL DEFAULT 0,
    deadline DATE,
    category TEXT DEFAULT 'Général',
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE
);

-- Index sur les objectifs
CREATE INDEX IF NOT EXISTS idx_savings_goals_deadline ON savings_goals(deadline);

-- Table des dividendes
CREATE TABLE IF NOT EXISTS dividends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    amount REAL NOT NULL,
    date_received DATE NOT NULL,
    source TEXT,
    created_at DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Index sur les dividendes
CREATE INDEX IF NOT EXISTS idx_dividends_date ON dividends(date_received);
CREATE INDEX IF NOT EXISTS idx_dividends_asset ON dividends(asset_id);

-- Table des biens immobiliers
CREATE TABLE IF NOT EXISTS real_estate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    purchase_price REAL NOT NULL,
    current_value REAL NOT NULL,
    mortgage_remaining REAL DEFAULT 0,
    purchase_date DATE,
    notes TEXT,
    created_at DATE DEFAULT CURRENT_DATE,
    updated_at DATE
);

-- Index sur l'immobilier
CREATE INDEX IF NOT EXISTS idx_real_estate_value ON real_estate(current_value);

-- Table de l'historique du patrimoine
CREATE TABLE IF NOT EXISTS wealth_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_wealth REAL NOT NULL,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index sur l'historique
CREATE INDEX IF NOT EXISTS idx_wealth_history_date ON wealth_history(snapshot_date);

-- Table du cache IA
CREATE TABLE IF NOT EXISTS ai_cache (
    cache_key TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    provider TEXT NOT NULL,
    timestamp REAL NOT NULL,
    ttl INTEGER NOT NULL DEFAULT 86400,
    hit_count INTEGER DEFAULT 1
);

-- Index sur le cache
CREATE INDEX IF NOT EXISTS idx_ai_cache_timestamp ON ai_cache(timestamp);

-- Table des performances de requêtes (optionnelle)
CREATE TABLE IF NOT EXISTS query_performance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_pattern TEXT NOT NULL,
    execution_time REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT
);

CREATE INDEX IF NOT EXISTS idx_query_perf_timestamp ON query_performance_log(timestamp);
