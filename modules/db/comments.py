"""Système de commentaires sur transactions.

Implémente la Phase 7 du plan FinCouple - Commentaires chat-like.
"""

from dataclasses import dataclass
from datetime import datetime

from modules.db.connection import get_db_connection
from modules.logger import logger


@dataclass
class Comment:
    """Un commentaire sur une transaction."""
    id: int
    transaction_id: int
    user_id: str
    user_name: str
    content: str
    created_at: datetime
    updated_at: datetime | None = None
    is_edited: bool = False
    reply_to: int | None = None


class CommentManager:
    """Gestionnaire de commentaires."""
    
    def __init__(self):
        self._ensure_table()
    
    def _ensure_table(self):
        """Crée la table des commentaires si elle n'existe pas."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    user_name TEXT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_edited INTEGER DEFAULT 0,
                    reply_to INTEGER,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
    
    def add_comment(
        self,
        transaction_id: int,
        user_id: str,
        content: str,
        user_name: str = None,
        reply_to: int = None
    ) -> Comment:
        """Ajoute un commentaire."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transaction_comments 
                (transaction_id, user_id, user_name, content, reply_to)
                VALUES (?, ?, ?, ?, ?)
                """,
                (transaction_id, user_id, user_name, content, reply_to)
            )
            conn.commit()
            comment_id = cursor.lastrowid
            
            logger.info(f"Commentaire ajouté tx={transaction_id} user={user_id}")
            
            return Comment(
                id=comment_id,
                transaction_id=transaction_id,
                user_id=user_id,
                user_name=user_name,
                content=content,
                created_at=datetime.now(),
                reply_to=reply_to
            )
    
    def get_comments(self, transaction_id: int) -> list[Comment]:
        """Récupère tous les commentaires d'une transaction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, transaction_id, user_id, user_name, content,
                       created_at, updated_at, is_edited, reply_to
                FROM transaction_comments
                WHERE transaction_id = ?
                ORDER BY created_at ASC
                """,
                (transaction_id,)
            )
            
            comments = []
            for row in cursor.fetchall():
                comments.append(Comment(
                    id=row[0],
                    transaction_id=row[1],
                    user_id=row[2],
                    user_name=row[3],
                    content=row[4],
                    created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                    updated_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    is_edited=bool(row[7]),
                    reply_to=row[8]
                ))
            
            return comments
    
    def get_comment_count(self, transaction_id: int) -> int:
        """Compte les commentaires d'une transaction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM transaction_comments WHERE transaction_id = ?",
                (transaction_id,)
            )
            return cursor.fetchone()[0]
    
    def edit_comment(self, comment_id: int, new_content: str) -> bool:
        """Modifie un commentaire."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE transaction_comments
                SET content = ?, updated_at = ?, is_edited = 1
                WHERE id = ?
                """,
                (new_content, datetime.now().isoformat(), comment_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_comment(self, comment_id: int) -> bool:
        """Supprime un commentaire."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM transaction_comments WHERE id = ?",
                (comment_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_unread_comments(
        self,
        user_id: str,
        since: datetime = None
    ) -> list[dict]:
        """Récupère les commentaires non lus par un utilisateur."""
        # Note: Pour une implémentation complète, il faudrait une table
        # de lecture des commentaires. Ici, on retourne les commentaires
        # récents des transactions de l'utilisateur.
        
        if since is None:
            since = datetime.now() - timedelta(days=7)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT tc.*, t.label as transaction_label
                FROM transaction_comments tc
                JOIN transactions t ON tc.transaction_id = t.id
                WHERE tc.user_id != ?
                AND tc.created_at > ?
                ORDER BY tc.created_at DESC
                """,
                (user_id, since.isoformat())
            )
            
            return [dict(row) for row in cursor.fetchall()]


class CommentUI:
    """Interface UI pour les commentaires."""
    
    def __init__(self):
        self.manager = CommentManager()
    
    def render_chat_panel(self, transaction_id: int, current_user: str, current_user_name: str = None):
        """Rend le panneau de chat pour une transaction."""
        import streamlit as st
        
        st.subheader("💬 Commentaires")
        
        # Afficher les commentaires existants
        comments = self.manager.get_comments(transaction_id)
        
        if not comments:
            st.info("Aucun commentaire. Soyez le premier à commenter !")
        else:
            # Container scrollable pour les commentaires
            with st.container():
                for comment in comments:
                    self._render_comment_bubble(comment, current_user)
        
        # Zone de saisie
        st.divider()
        with st.form(key=f"comment_form_{transaction_id}", clear_on_submit=True):
            new_comment = st.text_area(
                "Votre message",
                placeholder="Ajouter un commentaire...",
                key=f"comment_input_{transaction_id}",
                height=80
            )
            
            cols = st.columns([3, 1])
            with cols[1]:
                submitted = st.form_submit_button(
                    "Envoyer 💬",
                    use_container_width=True,
                    type="primary"
                )
            
            if submitted and new_comment.strip():
                self.manager.add_comment(
                    transaction_id=transaction_id,
                    user_id=current_user,
                    content=new_comment.strip(),
                    user_name=current_user_name
                )
                st.rerun()
    
    def _render_comment_bubble(self, comment: Comment, current_user: str):
        """Rend une bulle de commentaire."""
        import streamlit as st
        
        is_me = comment.user_id == current_user
        
        # Style différent selon l'émetteur
        if is_me:
            # Mon message (aligné à droite, fond primary)
            cols = st.columns([1, 4])
            with cols[1]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 16px 16px 4px 16px;
                    margin: 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 0.85rem; margin-bottom: 4px;">{comment.content}</div>
                    <div style="font-size: 0.7rem; opacity: 0.9; text-align: right;">
                        {comment.created_at.strftime('%H:%M')} {'✏️' if comment.is_edited else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Message de l'autre (aligné à gauche, fond gris)
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"""
                <div style="
                    background: #F3F4F6;
                    color: #1F2937;
                    padding: 12px 16px;
                    border-radius: 16px 16px 16px 4px;
                    margin: 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 4px;">
                        {comment.user_name or comment.user_id}
                    </div>
                    <div style="font-size: 0.85rem;">{comment.content}</div>
                    <div style="font-size: 0.7rem; color: #9CA3AF; margin-top: 4px;">
                        {comment.created_at.strftime('%H:%M')} {'✏️' if comment.is_edited else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_comment_badge(self, transaction_id: int):
        """Rend un badge avec le nombre de commentaires."""
        import streamlit as st
        
        count = self.manager.get_comment_count(transaction_id)
        
        if count > 0:
            st.markdown(f"""
            <span style="
                background: #10B981;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
            ">💬 {count}</span>
            """, unsafe_allow_html=True)


# Instance globale
comment_manager = CommentManager()
