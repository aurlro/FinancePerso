"""
Widget du jour - Affiché sur la page d'accueil pour créer l'habitude quotidienne.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import streamlit as st
import pandas as pd

from modules.logger import logger
from modules.db.stats import get_global_stats
from modules.db.budgets import get_budgets
from modules.db.transactions import get_all_transactions
import pandas as pd


def get_spending_insight() -> Dict[str, Any]:
    """Génère un insight pertinent sur les dépenses."""
    today = datetime.now()
    
    # Récupérer les stats globales
    stats = get_global_stats()
    
    if not stats or stats.get('total_transactions', 0) == 0:
        return {
            "type": "welcome",
            "title": "👋 Bienvenue !",
            "message": "Commencez par importer vos premières transactions.",
            "action": "pages/1_Import.py",
            "action_label": "Importer des transactions"
        }
    
    # Calculer les dépenses du jour
    try:
        all_tx = get_all_transactions()
        today_str = today.strftime('%Y-%m-%d')
        today_spending = 0
        
        if not all_tx.empty and 'date' in all_tx.columns:
            all_tx['date'] = pd.to_datetime(all_tx['date'])
            today_tx = all_tx[all_tx['date'].dt.strftime('%Y-%m-%d') == today_str]
            today_spending = today_tx['amount'].sum() if not today_tx.empty else 0
    except Exception:
        today_spending = 0
    
    # Vérifier les budgets
    try:
        budgets_df = get_budgets()
        if not budgets_df.empty:
            # Calculer les dépenses par catégorie pour le mois
            first_day = today.replace(day=1)
            month_tx = all_tx[all_tx['date'] >= first_day] if not all_tx.empty else pd.DataFrame()
            spending_by_category = month_tx.groupby('category')['amount'].sum().to_dict() if not month_tx.empty else {}
            
            # Trouver les budgets critiques (>80%)
            for _, budget in budgets_df.iterrows():
                category = budget['category']
                limit = budget['amount']
                spent = spending_by_category.get(category, 0)
                percentage = (spent / limit * 100) if limit > 0 else 0
                
                if percentage >= 90:
                    return {
                        "type": "alert",
                        "title": f"🚨 Budget {category}",
                        "message": f"{percentage:.0f}% utilisé ({spent:.2f}€ / {limit:.2f}€)",
                        "metric": f"{percentage:.0f}%",
                        "metric_label": "utilisé",
                        "progress": min(percentage / 100, 1.0),
                        "action": "pages/3_Synthese.py",
                        "action_label": "Ajuster le budget"
                    }
                elif percentage >= 80:
                    return {
                        "type": "warning",
                        "title": f"⚠️ Budget {category}",
                        "message": f"{percentage:.0f}% utilisé - attention!",
                        "metric": f"{percentage:.0f}%",
                        "metric_label": "utilisé",
                        "progress": percentage / 100,
                        "action": "pages/3_Synthese.py",
                        "action_label": "Voir le budget"
                    }
    except Exception as e:
        logger.error(f"Error checking budgets: {e}")
    
    # Journée chargée?
    if today_spending > 100:
        return {
            "type": "warning",
            "title": "💸 Journée chargée",
            "message": f"Vous avez dépensé {today_spending:.2f}€ aujourd'hui",
            "metric": f"{today_spending:.2f}€",
            "metric_label": "aujourd'hui",
            "action": "pages/3_Synthese.py",
            "action_label": "Voir les détails"
        }
    
    # Top catégorie du mois
    try:
        if not all_tx.empty:
            first_day = today.replace(day=1)
            month_tx = all_tx[all_tx['date'] >= first_day]
            if not month_tx.empty:
                top_category = month_tx.groupby('category')['amount'].sum().sort_values(ascending=False).head(1)
                if not top_category.empty:
                    cat_name = top_category.index[0]
                    cat_amount = top_category.values[0]
                    return {
                        "type": "info",
                        "title": f"📊 Top dépense: {cat_name}",
                        "message": f"{cat_amount:.2f}€ ce mois",
                        "metric": f"{cat_amount:.2f}€",
                        "metric_label": cat_name,
                        "action": "pages/3_Synthese.py",
                        "action_label": "Explorer"
                    }
    except Exception:
        pass
    
    # Défaut
    total = stats.get('total_transactions', 0)
    savings = stats.get('current_month_savings', 0)
    
    return {
        "type": "info",
        "title": "💰 Récap du jour",
        "message": f"{total} transactions • {savings:+.2f}€ ce mois",
        "action": "pages/3_Synthese.py",
        "action_label": "Voir la synthèse"
    }


def render_daily_widget():
    """Affiche le widget du jour dans Streamlit."""
    insight = get_spending_insight()
    
    # Couleurs selon le type
    colors = {
        "welcome": ("blue", "🌟"),
        "success": ("green", "✅"),
        "info": ("gray", "ℹ️"),
        "warning": ("orange", "⚠️"),
        "alert": ("red", "🚨")
    }
    
    color, default_emoji = colors.get(insight["type"], ("gray", "ℹ️"))
    
    # Style CSS pour le widget
    st.markdown(f"""
    <style>
    .daily-widget {{
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid var(--{color}-500);
        background: linear-gradient(135deg, var(--{color}-50) 0%, rgba(255,255,255,0) 100%);
        margin: 1rem 0;
    }}
    .daily-widget h3 {{
        margin: 0 0 0.5rem 0;
        color: var(--{color}-700);
    }}
    .daily-widget .metric {{
        font-size: 2rem;
        font-weight: bold;
        color: var(--{color}-600);
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Container
    with st.container():
        col1, col2 = st.columns([0.7, 0.3])
        
        with col1:
            st.subheader(f"{insight['title']}")
            st.write(insight['message'])
            
            if 'action' in insight and 'action_label' in insight:
                st.page_link(insight['action'], label=f"→ {insight['action_label']}")
        
        with col2:
            if 'metric' in insight:
                st.metric(
                    label=insight.get('metric_label', ''),
                    value=insight['metric']
                )
            
            if 'progress' in insight:
                st.progress(
                    value=min(insight['progress'], 1.0),
                    text=f"{insight['progress']:.0%}"
                )
    
    st.divider()


def render_quick_stats_row():
    """Affiche une ligne de stats rapides sous le widget."""
    today = datetime.now()
    stats = get_global_stats()
    
    if not stats:
        return
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            label="📊 Total transactions",
            value=f"{stats.get('total_transactions', 0)}",
            delta="enregistrées"
        )
    
    with cols[1]:
        savings = stats.get('current_month_savings', 0)
        st.metric(
            label="💰 Épargne du mois",
            value=f"{savings:+.0f}€",
            delta=f"{stats.get('current_month_rate', 0):.1f}%"
        )
    
    with cols[2]:
        last_import = stats.get('last_import', 'Jamais')
        st.metric(
            label="📥 Dernier import",
            value=last_import if last_import else "Aujourd'hui"
        )
    
    with cols[3]:
        days_remaining = 30 - today.day
        st.metric(
            label="📅 Fin du mois",
            value=f"{days_remaining}j",
            help="Jours restants avant la fin du mois"
        )
