"""
Migrations V2 - Notifications, Households, Invitations
Ajoute les tables pour les PRs #6, #7, #8
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.db.connection import get_db_connection
from modules.logger import logger


def run_migrations():
    """Run all V2 migrations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # ============================================
        # PR #7: Households table
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                owner_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES api_users(id) ON DELETE CASCADE
            )
        """)
        
        # Household members junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS household_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',
                is_active INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES api_users(id) ON DELETE CASCADE,
                UNIQUE(household_id, user_id)
            )
        """)
        
        # Invitations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS household_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER NOT NULL,
                invited_by INTEGER NOT NULL,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                role TEXT DEFAULT 'member',
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                FOREIGN KEY (household_id) REFERENCES households(id) ON DELETE CASCADE,
                FOREIGN KEY (invited_by) REFERENCES api_users(id) ON DELETE CASCADE
            )
        """)
        
        # ============================================
        # PR #6: Notifications table
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT,
                is_read INTEGER DEFAULT 0,
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES api_users(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_unread 
            ON notifications(user_id, is_read, created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invitations_token 
            ON household_invitations(token)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invitations_email 
            ON household_invitations(email, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_household_members_user 
            ON household_members(user_id, is_active)
        """)
        
        conn.commit()
        logger.info("V2 migrations completed successfully")


if __name__ == "__main__":
    run_migrations()
    print("✅ Migrations V2 completed")
