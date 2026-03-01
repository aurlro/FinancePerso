-- Migration 010: Analytics tables
-- Crée les tables pour le suivi interne des métriques

-- Table des sessions analytics (si pas déjà créée par le module)
CREATE TABLE IF NOT EXISTS analytics_sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_seconds INTEGER,
    pages_viewed TEXT,  -- JSON
    user_id TEXT
);

-- Table des événements analytics (si pas déjà créée par le module)
CREATE TABLE IF NOT EXISTS analytics_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT,
    page TEXT,
    properties TEXT,  -- JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session ON analytics_events(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_sessions_started ON analytics_sessions(started_at);
