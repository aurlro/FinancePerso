"""
Configuration Dashboard - Overview of all settings.
Provides a quick glance at configuration status and quick actions.
"""
import streamlit as st
from modules.db.members import get_members
from modules.db.categories import get_categories
from modules.db.transactions import get_all_transactions
from modules.db.budgets import get_budgets
from modules.notifications import get_notification_settings
from modules.ai_manager import is_ai_available
import os


def render_config_dashboard():
    """Render the configuration overview dashboard."""
    
    st.markdown("""
    <style>
    .config-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
    }
    .config-card.success { border-left-color: #22c55e; }
    .config-card.warning { border-left-color: #f59e0b; }
    .config-card.error { border-left-color: #ef4444; }
    .config-status {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.85em;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 500;
    }
    .status-ok { background: #dcfce7; color: #166534; }
    .status-warn { background: #fef3c7; color: #92400e; }
    .status-error { background: #fee2e2; color: #991b1b; }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("🏠 Vue d'ensemble")
    st.markdown("État de votre configuration en un coup d'œil.")
    
    # Get data
    members = get_members()
    categories = get_categories()
    transactions = get_all_transactions()
    budgets = get_budgets()
    notif_settings = get_notification_settings()
    ai_available = is_ai_available()
    
    # --- STATUS CARDS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        member_count = len(members) if not members.empty else 0
        status_class = "success" if member_count >= 1 else "error"
        status_text = f"✅ {member_count} membre(s)" if member_count > 0 else "❌ Aucun membre"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>👥 Membres</h4>
            <span class="config-status {'status-ok' if member_count > 0 else 'status-error'}">{status_text}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Tout va bien !' if member_count > 0 else 'Ajoutez au moins un membre'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cat_count = len(categories) if categories else 0
        status_class = "success" if cat_count >= 3 else "warning" if cat_count > 0 else "error"
        status_text = f"✅ {cat_count} catégorie(s)" if cat_count > 0 else "❌ Aucune catégorie"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>🏷️ Catégories</h4>
            <span class="config-status {'status-ok' if cat_count >= 3 else 'status-warn' if cat_count > 0 else 'status-error'}">{status_text}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Bonne couverture' if cat_count >= 5 else 'Ajoutez des catégories'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        tx_count = len(transactions) if not transactions.empty else 0
        status_class = "success" if tx_count > 0 else "warning"
        status_text = f"✅ {tx_count} transaction(s)" if tx_count > 0 else "⏳ En attente d'import"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>📊 Données</h4>
            <span class="config-status {'status-ok' if tx_count > 0 else 'status-warn'}">{status_text}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Données disponibles' if tx_count > 0 else 'Importez votre premier relevé'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- SECOND ROW ---
    col4, col5, col6 = st.columns(3)
    
    with col4:
        ai_status = "✅ Configurée" if ai_available else "⚠️ Mode hors ligne"
        status_class = "success" if ai_available else "warning"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>🤖 Intelligence Artificielle</h4>
            <span class="config-status {'status-ok' if ai_available else 'status-warn'}">{ai_status}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Catégorisation automatique active' if ai_available else 'Configurez une clé API pour activer l\'IA'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        notif_enabled = notif_settings.get('notif_enabled', 'false').lower() == 'true'
        notif_status = "✅ Activées" if notif_enabled else "🔕 Désactivées"
        status_class = "success" if notif_enabled else "warning"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>🔔 Notifications</h4>
            <span class="config-status {'status-ok' if notif_enabled else 'status-warn'}">{notif_status}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Alertes budget activées' if notif_enabled else 'Activez les alertes'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        budget_count = len(budgets) if not budgets.empty else 0
        budget_status = f"✅ {budget_count} budget(s)" if budget_count > 0 else "⚠️ Aucun budget"
        status_class = "success" if budget_count > 0 else "warning"
        
        st.markdown(f"""
        <div class="config-card {status_class}">
            <h4>💰 Budgets</h4>
            <span class="config-status {'status-ok' if budget_count > 0 else 'status-warn'}">{budget_status}</span>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                {'Suivi actif' if budget_count > 0 else 'Définissez vos limites'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- QUICK ACTIONS ---
    st.subheader("⚡ Actions rapides")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("👥 Ajouter un membre", use_container_width=True):
            st.session_state['config_jump_to'] = 'Profil'
            st.rerun()
    
    with col_q2:
        if st.button("🏷️ Nouvelle catégorie", use_container_width=True):
            st.session_state['config_jump_to'] = 'Profil'
            st.rerun()
    
    with col_q3:
        if st.button("💰 Définir un budget", use_container_width=True):
            st.session_state['config_jump_to'] = 'Budgets'
            st.rerun()
    
    with col_q4:
        if st.button("🔔 Tester notifications", use_container_width=True):
            st.session_state['config_jump_to'] = 'Notifications'
            st.rerun()
    
    st.divider()
    
    # --- RECENT ACTIVITY ---
    st.subheader("📈 Activité récente")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        if not transactions.empty:
            last_import = transactions['date'].max()
            st.metric("Dernière transaction", last_import)
        else:
            st.info("Aucune transaction importée")
    
    with col_a2:
        if not budgets.empty:
            st.write("**Budgets définis :**")
            for _, row in budgets.head(5).iterrows():
                st.write(f"• {row['category']}: {row['amount']:.0f}€")
        else:
            st.info("Aucun budget défini")
