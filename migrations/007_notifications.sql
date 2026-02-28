-- Migration 007: Système de notifications unifié v3.0
-- Crée une table dédiée pour les notifications avec persistance DB

-- Table principale des notifications
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    level TEXT NOT NULL CHECK (level IN ('critical', 'warning', 'info', 'success', 'achievement')),
    type TEXT NOT NULL,
    title TEXT,
    message TEXT NOT NULL,
    icon TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Catégorisation
    category TEXT,
    source TEXT,  -- Module qui a créé la notification
    
    -- Actions possibles (JSON array)
    actions_json TEXT CHECK (json_valid(actions_json)),
    
    -- Métadonnées additionnelles (JSON object)
    metadata_json TEXT CHECK (json_valid(metadata_json)),
    
    -- Pour futur multi-utilisateur
    user_id INTEGER DEFAULT 1,
    
    -- Pour déduplication
    dedup_key TEXT,
    
    -- Statut
    is_read BOOLEAN DEFAULT 0,
    is_dismissed BOOLEAN DEFAULT 0,
    is_pinned BOOLEAN DEFAULT 0
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
    ON notifications(user_id, is_read, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_type 
    ON notifications(type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_category 
    ON notifications(category, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_dedup 
    ON notifications(dedup_key, created_at);

CREATE INDEX IF NOT EXISTS idx_notifications_expires 
    ON notifications(expires_at) WHERE expires_at IS NOT NULL;

-- Table des préférences de notification par utilisateur
CREATE TABLE IF NOT EXISTS notification_preferences (
    user_id INTEGER DEFAULT 1 PRIMARY KEY,
    
    -- Notifications activées par niveau
    critical_enabled BOOLEAN DEFAULT 1,
    warning_enabled BOOLEAN DEFAULT 1,
    info_enabled BOOLEAN DEFAULT 1,
    success_enabled BOOLEAN DEFAULT 1,
    achievement_enabled BOOLEAN DEFAULT 1,
    
    -- Notifications activées par type (JSON object)
    type_preferences_json TEXT DEFAULT '{}' CHECK (json_valid(type_preferences_json)),
    
    -- Canaux
    desktop_enabled BOOLEAN DEFAULT 1,
    email_enabled BOOLEAN DEFAULT 0,
    sms_enabled BOOLEAN DEFAULT 0,
    
    -- Email configuration
    email_address TEXT,
    
    -- Seuils
    budget_warning_threshold INTEGER DEFAULT 80,  -- %
    budget_critical_threshold INTEGER DEFAULT 100, -- %
    
    -- Fréquences
    daily_digest_enabled BOOLEAN DEFAULT 1,
    weekly_summary_enabled BOOLEAN DEFAULT 1,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des préférences par défaut
INSERT OR IGNORE INTO notification_preferences (user_id) VALUES (1);

-- Table pour l'historique des envois (dédublication)
CREATE TABLE IF NOT EXISTS notification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedup_key TEXT NOT NULL UNIQUE,
    notification_id TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue pour notifications actives (non lues, non expirées)
CREATE VIEW IF NOT EXISTS v_notifications_active AS
SELECT 
    n.*,
    CASE 
        WHEN n.level = 'critical' THEN 1
        WHEN n.level = 'warning' THEN 2
        WHEN n.level = 'info' THEN 3
        WHEN n.level = 'success' THEN 4
        WHEN n.level = 'achievement' THEN 5
    END as priority
FROM notifications n
WHERE n.is_dismissed = 0
    AND (n.expires_at IS NULL OR n.expires_at > datetime('now'))
ORDER BY priority ASC, n.created_at DESC;

-- Vue pour statistiques
CREATE VIEW IF NOT EXISTS v_notification_stats AS
SELECT 
    user_id,
    COUNT(*) as total_count,
    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
    SUM(CASE WHEN is_read = 1 THEN 1 ELSE 0 END) as read_count,
    SUM(CASE WHEN level = 'critical' THEN 1 ELSE 0 END) as critical_count,
    SUM(CASE WHEN level = 'warning' THEN 1 ELSE 0 END) as warning_count,
    MAX(created_at) as last_notification_at
FROM notifications
WHERE is_dismissed = 0
GROUP BY user_id;
