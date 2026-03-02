"""
Database schema initialization and migrations.
Handles database schema creation, updates, and versioning.
"""

from modules.backup_manager import auto_backup_daily
from modules.db.connection import get_db_connection
from modules.logger import logger


def init_db() -> None:
    """
    Initialize database schema and run all migrations.

    Creates all tables, adds default data, and ensures schema is up-to-date.
    Automatically creates a backup before modifying the database.
    """
    auto_backup_daily()  # Automatic daily versioning

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                label TEXT,
                amount REAL,
                original_category TEXT,
                account_id TEXT,
                category_validated TEXT,
                ai_confidence REAL,
                status TEXT,
                comment TEXT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrations for transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [info[1] for info in cursor.fetchall()]

        migrations = [
            ("ai_confidence", "ALTER TABLE transactions ADD COLUMN ai_confidence REAL"),
            (
                "account_label",
                "ALTER TABLE transactions ADD COLUMN account_label TEXT DEFAULT 'Compte Principal'",
            ),
            ("member", "ALTER TABLE transactions ADD COLUMN member TEXT DEFAULT 'Anonyme'"),
            ("tags", "ALTER TABLE transactions ADD COLUMN tags TEXT"),
            ("beneficiary", "ALTER TABLE transactions ADD COLUMN beneficiary TEXT"),
            ("tx_hash", "ALTER TABLE transactions ADD COLUMN tx_hash TEXT"),
            ("card_suffix", "ALTER TABLE transactions ADD COLUMN card_suffix TEXT"),
            (
                "is_manually_ungrouped",
                "ALTER TABLE transactions ADD COLUMN is_manually_ungrouped INTEGER DEFAULT 0",
            ),
            ("notes", "ALTER TABLE transactions ADD COLUMN notes TEXT"),
            ("updated_at", "ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP"),
        ]

        for col, migration_sql in migrations:
            if col not in columns:
                cursor.execute(migration_sql)
                logger.info(f"Added column: {col}")

        # Create unique index on tx_hash
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tx_hash ON transactions(tx_hash)")

        # Transaction History Table (for undo functionality)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_group_id TEXT,
                tx_ids TEXT,
                prev_status TEXT,
                prev_category TEXT,
                prev_member TEXT,
                prev_tags TEXT,
                prev_beneficiary TEXT,
                prev_notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration for transaction_history table
        cursor.execute("PRAGMA table_info(transaction_history)")
        columns_hist = [info[1] for info in cursor.fetchall()]
        if "prev_notes" not in columns_hist:
            cursor.execute("ALTER TABLE transaction_history ADD COLUMN prev_notes TEXT")
            logger.info("Added column: prev_notes to transaction_history")

        # Performance Indexes - Single column
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions(date)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON transactions(category_validated)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_member ON transactions(member)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_label ON transactions(label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_amount ON transactions(amount)")

        # Composite Indexes for common query patterns
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_date_category ON transactions(date, category_validated)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_date ON transactions(status, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date_member ON transactions(date, member)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category_amount ON transactions(category_validated, amount)"
        )

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                emoji TEXT DEFAULT '🏷️',
                is_fixed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Add columns to categories
        cursor.execute("PRAGMA table_info(categories)")
        columns_cat = [info[1] for info in cursor.fetchall()]

        if "emoji" not in columns_cat:
            cursor.execute("ALTER TABLE categories ADD COLUMN emoji TEXT DEFAULT '🏷️'")
        if "is_fixed" not in columns_cat:
            cursor.execute("ALTER TABLE categories ADD COLUMN is_fixed INTEGER DEFAULT 0")
        if "suggested_tags" not in columns_cat:
            cursor.execute("ALTER TABLE categories ADD COLUMN suggested_tags TEXT")

        # Initialize default categories
        # (name, emoji, is_fixed, suggested_tags)
        default_cats = [
            ("Alimentation", "🛒", 0, "Courses, Supermarché, Bio"),
            ("Transport", "🚗", 0, "Essence, Péage, Parking, SNCF"),
            ("Loisirs", "🎮", 0, "Cinéma, Sortie, Sport"),
            ("Santé", "🏥", 0, "Docteur, Pharmacie, Dentiste, Mutuelle, Remboursement"),
            ("Logement", "🏠", 1, "Loyer, Travaux, Meuble, Déco"),
            ("Revenus", "💰", 0, "Salaire, Virement, Remboursement"),
            ("Autre", "📦", 0, ""),
            ("Restaurants", "🍴", 0, "Restau, Bar, Café, Deliveroo"),
            ("Abonnements", "📱", 1, "Netflix, Spotify, Internet, Mobile"),
            ("Services", "🛠️", 0, "Assurance, Banque, Impôts"),
            ("Cadeaux", "🎁", 0, "Anniversaire, Noël"),
            ("Virement Interne", "🔄", 0, ""),
            ("Inconnu", "❓", 0, ""),
            ("Hors Budget", "🚫", 0, ""),
            ("Impôts", "🧾", 1, ""),
            ("Assurances", "🛡️", 1, ""),
        ]

        for name, emoji, is_fixed, s_tags in default_cats:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, emoji, is_fixed, suggested_tags) VALUES (?, ?, ?, ?)",
                (name, emoji, is_fixed, s_tags),
            )
            # Also update existing categories if suggested_tags is empty
            cursor.execute(
                "UPDATE categories SET suggested_tags = ? WHERE name = ? AND (suggested_tags IS NULL OR suggested_tags = '')",
                (s_tags, name),
            )

        # Member Mappings table (Cards)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_suffix TEXT UNIQUE,
                member_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Account Member Mappings table (Defaults per account)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_member_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_label TEXT UNIQUE,
                member_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Beneficiary Aliases table (Magic Fix 5.1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS beneficiary_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias TEXT UNIQUE,
                normalized_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Learning Rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                category TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("PRAGMA table_info(learning_rules)")
        columns_rules = [info[1] for info in cursor.fetchall()]
        if "priority" not in columns_rules:
            cursor.execute("ALTER TABLE learning_rules ADD COLUMN priority INTEGER DEFAULT 1")

        # Budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                amount REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Add member_type column
        cursor.execute("PRAGMA table_info(members)")
        columns_mem = [info[1] for info in cursor.fetchall()]
        if "member_type" not in columns_mem:
            cursor.execute("ALTER TABLE members ADD COLUMN member_type TEXT DEFAULT 'HOUSEHOLD'")

        # Initialize default members (generic names)
        default_members = [
            ("Moi", "HOUSEHOLD"),
            ("Conjoint", "HOUSEHOLD"),
            ("Famille", "HOUSEHOLD"),
            ("Maison", "HOUSEHOLD"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO members (name, member_type) VALUES (?, ?)", default_members
        )

        # Initialize default rules for internal transfers (generic patterns)
        default_rules = [
            ("VIR INST", "Virement Interne", 5),
            ("VIR VRT", "Virement Interne", 5),
            ("VIR SEPA", "Virement Interne", 5),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO learning_rules (pattern, category, priority) VALUES (?, ?, ?)",
            default_rules,
        )

        # Initialize default card mappings (generic)
        default_mappings = [("0000", "Moi"), ("0001", "Conjoint")]
        cursor.executemany(
            "INSERT OR IGNORE INTO member_mappings (card_suffix, member_name) VALUES (?, ?)",
            default_mappings,
        )

        # Settings table for user configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Initialize default settings with internal transfer targets
        # Store as comma-separated list for simplicity
        default_settings = [
            (
                "internal_transfer_targets",
                "AURELIEN,DUO,JOINT,EPARGNE,LDDS,LIVRET,ELISE",
                "Mots-clés pour détecter les virements internes (séparés par des virgules)",
            ),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
            default_settings,
        )

        # Dashboard Layouts table for customizable dashboard
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashboard_layouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                layout_json TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on name for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_layout_name ON dashboard_layouts(name)")

        # Initialize default layout if not exists
        cursor.execute("SELECT COUNT(*) FROM dashboard_layouts WHERE name = 'default'")
        if cursor.fetchone()[0] == 0:
            default_layout_json = """[{"id": "kpi_1", "type": "kpi_depenses", "title": "💸 Dépenses", "position": 1, "size": "small", "visible": true, "config": {}}, {"id": "kpi_2", "type": "kpi_revenus", "title": "💰 Revenus", "position": 2, "size": "small", "visible": true, "config": {}}, {"id": "kpi_3", "type": "kpi_solde", "title": "📊 Solde", "position": 3, "size": "small", "visible": true, "config": {}}, {"id": "kpi_4", "type": "kpi_epargne", "title": "🎯 Taux d'épargne", "position": 4, "size": "small", "visible": true, "config": {}}, {"id": "evol_1", "type": "evolution_chart", "title": "📈 Évolution", "position": 5, "size": "large", "visible": true, "config": {}}, {"id": "sav_1", "type": "savings_trend", "title": "💹 Tendance épargne", "position": 6, "size": "medium", "visible": true, "config": {}}, {"id": "cat_1", "type": "categories_chart", "title": "📊 Répartition", "position": 7, "size": "medium", "visible": true, "config": {}}, {"id": "top_1", "type": "top_expenses", "title": "🔥 Top dépenses", "position": 8, "size": "medium", "visible": true, "config": {}}]"""
            cursor.execute(
                "INSERT INTO dashboard_layouts (name, layout_json, is_active) VALUES (?, ?, ?)",
                ("default", default_layout_json, 1),
            )
            logger.info("Created default dashboard layout")

        # Recycle Bin table for soft delete functionality
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recycle_bin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER NOT NULL,
                table_name TEXT NOT NULL DEFAULT 'transactions',
                data JSON NOT NULL,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_by TEXT,
                expires_at TIMESTAMP,
                restored_at TIMESTAMP,
                restored BOOLEAN DEFAULT 0
            )
        """)

        # Indexes for recycle bin
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recycle_bin_original ON recycle_bin(original_id, restored)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recycle_bin_expires ON recycle_bin(expires_at, restored)"
        )

        # Recurrence Feedback table for subscription management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurrence_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label_pattern TEXT NOT NULL,
                category TEXT,
                user_feedback INTEGER,  -- 1 for confirm, 0 for reject
                feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                UNIQUE(label_pattern, category)
            )
        """)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recurrence_feedback_lookup ON recurrence_feedback(label_pattern, category)"
        )

        conn.commit()
        logger.info("Database initialized successfully")


def add_performance_indexes() -> None:
    """
    Add performance indexes to the database.

    Safe to run multiple times (uses IF NOT EXISTS).
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_validated)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_member ON transactions(member)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_hash ON transactions(tx_hash)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_label)",
        ]

        for idx_sql in indexes:
            cursor.execute(idx_sql)
            logger.info(f"Created index: {idx_sql.split('idx_')[1].split(' ')[0]}")

        conn.commit()
        logger.info("Performance indexes added successfully")
