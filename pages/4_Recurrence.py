"""
🔁 Analyse des Récurrences - Enhanced V3
Features:
- User feedback on detected recurrences (confirm/reject)
- Manual addition of recurring patterns
- Separate views for confirmed, rejected, and pending recurrences
- Improved drill-down with transaction IDs
"""
import streamlit as st
import pandas as pd
from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories_with_emojis
from modules.db.recurrence_feedback import (
    init_recurrence_feedback_table,
    set_recurrence_feedback,
    get_all_feedback,
    delete_feedback,
    get_feedback_stats
)
from modules.analytics_v2 import (
    detect_recurring_payments_v2, 
    group_by_category, 
    get_recurring_by_tags,
    analyze_recurrence_summary
)
from modules.ui import load_css, render_scroll_to_top
from modules.ui.components.transaction_drill_down import render_transaction_drill_down
from modules.ui.recurrence_manager import (
    render_recurrence_card,
    render_feedback_summary,
    render_confirmed_recurring_section,
    render_rejected_recurring_section,
    render_manual_add_section,
    filter_by_user_feedback
)

st.set_page_config(page_title="Récurrence", page_icon="🔁", layout="wide")
load_css()
init_recurrence_feedback_table()

# Helper functions (defined before use)
def confirm_recurrence(label: str, category: str):
    """Mark a recurrence as confirmed by user."""
    success = set_recurrence_feedback(
        label_pattern=label,
        is_recurring=True,
        category=category,
        notes="Confirmée par l'utilisateur"
    )
    if success:
        st.toast(f"✅ '{label}' confirmé comme récurrence", icon="✅")
        st.rerun()
    else:
        st.error("Erreur lors de la sauvegarde")

def reject_recurrence(label: str, category: str):
    """Mark a recurrence as rejected (false positive)."""
    # Get reason from session state if available
    note_key = f'pending_note_{label}'
    note = st.session_state.get(note_key, "Rejetée par l'utilisateur")
    
    success = set_recurrence_feedback(
        label_pattern=label,
        is_recurring=False,
        category=category,
        notes=note
    )
    if success:
        st.toast(f"❌ '{label}' marqué comme non-récurrent", icon="❌")
        st.rerun()
    else:
        st.error("Erreur lors de la sauvegarde")

st.title("🔁 Analyse des Récurrences")
st.markdown("Détection et validation des abonnements, factures et revenus réguliers.")

# Feedback summary at top
render_feedback_summary()

# Load data
df = get_all_transactions()

if df.empty:
    st.info("Aucune donnée disponible pour l'analyse.")
else:
    # Sidebar filters
    st.sidebar.header("🔍 Filtres")
    
    # Validation status filter
    st.sidebar.subheader("📊 Statut de validation")
    show_confirmed = st.sidebar.checkbox("✅ Confirmées", value=True)
    show_pending = st.sidebar.checkbox("🤔 À vérifier", value=True)
    show_rejected = st.sidebar.checkbox("❌ Rejetées (faux positifs)", value=False)
    
    # We only analyze validated transactions for better accuracy
    validated_df = df[df['status'] == 'validated']
    
    if validated_df.empty:
        st.warning("Veuillez valider quelques transactions pour permettre l'analyse des récurrences.")
    else:
        # Run analysis
        with st.spinner("Analyse des tendances en cours..."):
            recurring_df = detect_recurring_payments_v2(validated_df)
        
        # Apply user feedback filters
        filtered_df = filter_by_user_feedback(
            recurring_df,
            show_confirmed=show_confirmed,
            show_rejected=show_rejected,
            show_pending=show_pending
        )
        
        if recurring_df.empty:
            st.info("""
            Aucune récurrence claire détectée pour le moment. 
            
            **Conseils :**
            - L'analyse nécessite au moins 2 occurrences d'une même opération
            - Les opérations doivent avoir un montant régulier et une périodicité mensuelle/trimestrielle
            - Pour les salaires : vérifiez qu'ils sont bien catégorisés comme 'Revenus'
            """)
            
            # Show manual add section even when no detections
            render_manual_add_section(on_add=lambda label, cat: st.rerun())
            
        else:
            # Summary metrics
            summary = analyze_recurrence_summary(validated_df, filtered_df)
            
            # Count by validation status
            stats = get_feedback_stats()
            
            st.success(
                f"**{len(filtered_df)}** récurrences affichées "
                f"(✅ {stats['confirmed']} confirmées, "
                f"🤔 {stats['confirmed'] + stats['rejected'] - stats['total']} en attente, "
                f"❌ {stats['rejected']} rejetées)"
            )
            
            # Summary cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💳 Mensuel charges", f"{summary.get('monthly_expense_total', 0):,.0f} €")
            with col2:
                st.metric("💰 Mensuel revenus", f"{summary.get('monthly_income_total', 0):,.0f} €")
            with col3:
                st.metric("📂 Catégories", summary.get('categories_covered', 0))
            with col4:
                balance = summary.get('monthly_income_total', 0) - summary.get('monthly_expense_total', 0)
                st.metric("📊 Balance mensuelle", f"{balance:,.0f} €")
            
            st.divider()
            
            # View mode selection
            view_mode = st.segmented_control(
                "Vue d'analyse",
                options=["Par opération", "Par catégorie", "Par tag", "Vue validation"],
                default="Par opération"
            )
            
            cat_emoji_map = get_categories_with_emojis()
            
            if view_mode == "Par opération":
                # Filter controls
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    show_type = st.selectbox(
                        "Type",
                        ["Tous", "Dépenses uniquement", "Revenus uniquement"]
                    )
                
                with filter_col2:
                    freq_filter = st.selectbox(
                        "Fréquence",
                        ["Toutes", "Mensuel", "Trimestriel", "Annuel"]
                    )
                
                with filter_col3:
                    var_filter = st.selectbox(
                        "Montant",
                        ["Tous", "Fixe", "Variable"]
                    )
                
                # Apply additional filters
                display_df = filtered_df.copy()
                
                if show_type == "Dépenses uniquement":
                    display_df = display_df[display_df['avg_amount'] < 0]
                elif show_type == "Revenus uniquement":
                    display_df = display_df[display_df['avg_amount'] > 0]
                
                if freq_filter != "Toutes":
                    display_df = display_df[display_df['frequency_label'] == freq_filter]
                
                if var_filter != "Tous":
                    display_df = display_df[display_df['variability'] == var_filter]
                
                if display_df.empty:
                    st.info("Aucune opération ne correspond aux filtres sélectionnés.")
                else:
                    # Group by type
                    expenses = display_df[display_df['avg_amount'] < 0].copy()
                    incomes = display_df[display_df['avg_amount'] > 0].copy()
                    
                    # Display Incomes First
                    if not incomes.empty:
                        st.subheader(f"💰 Revenus Réguliers ({len(incomes)})")
                        
                        for _, row in incomes.iterrows():
                            with st.container(border=True):
                                render_recurrence_card(
                                    row=row,
                                    on_confirm=lambda label, cat: confirm_recurrence(label, cat),
                                    on_reject=lambda label, cat: reject_recurrence(label, cat),
                                    cat_emoji_map=cat_emoji_map
                                )
                                
                                # Drill-down with stored transaction IDs
                                with st.expander("👁️ Voir les transactions", expanded=False):
                                    tx_ids = row.get('transaction_ids', [])
                                    if tx_ids:
                                        render_transaction_drill_down(
                                            category=row['category'],
                                            transaction_ids=tx_ids,
                                            key_prefix=f"rec_inc_{row['label'][:20]}"
                                        )
                                    else:
                                        st.warning("Aucune transaction trouvée.")
                    
                    # Display Expenses
                    if not expenses.empty:
                        st.subheader(f"💳 Abonnements & Charges ({len(expenses)})")
                        
                        for _, row in expenses.iterrows():
                            with st.container(border=True):
                                render_recurrence_card(
                                    row=row,
                                    on_confirm=lambda label, cat: confirm_recurrence(label, cat),
                                    on_reject=lambda label, cat: reject_recurrence(label, cat),
                                    cat_emoji_map=cat_emoji_map
                                )
                                
                                # Drill-down with stored transaction IDs
                                with st.expander("👁️ Voir les transactions", expanded=False):
                                    tx_ids = row.get('transaction_ids', [])
                                    if tx_ids:
                                        render_transaction_drill_down(
                                            category=row['category'],
                                            transaction_ids=tx_ids,
                                            key_prefix=f"rec_exp_{row['label'][:20]}"
                                        )
                                    else:
                                        st.warning("Aucune transaction trouvée.")
            
            elif view_mode == "Par catégorie":
                st.subheader("📂 Vue par Catégories")
                
                cat_grouped = group_by_category(filtered_df)
                
                if not cat_grouped.empty:
                    for _, row in cat_grouped.iterrows():
                        emoji = cat_emoji_map.get(row['category'], "📂")
                        
                        with st.container(border=True):
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            
                            col1.markdown(f"**{emoji} {row['category']}**")
                            col1.caption(f"{len(row['labels'])} opérations régulières")
                            
                            total = row['total_amount']
                            col2.markdown(f"**{abs(total):,.2f} €**")
                            col2.caption("Total moyen" if total < 0 else "Total revenus")
                            
                            col3.markdown(f"**{row['total_occurrences']}**")
                            col3.caption("Occurrences/mois")
                            
                            col4.markdown(f"**{row['dominant_frequency']}**")
                            col4.caption("Fréquence")
                            
                            # Show operations in this category
                            with st.expander("Voir les opérations"):
                                for op_label in row['labels'][:5]:
                                    st.caption(f"• {op_label}")
                                if len(row['labels']) > 5:
                                    st.caption(f"*... et {len(row['labels']) - 5} autres*")
                else:
                    st.info("Aucune donnée par catégorie.")
            
            elif view_mode == "Par tag":
                st.subheader("🏷️ Vue par Tags")
                
                tag_data = get_recurring_by_tags(validated_df, filtered_df)
                
                if not tag_data.empty:
                    # Filter by tag if many
                    all_tags = tag_data['tag'].tolist()
                    selected_tags = st.multiselect(
                        "Filtrer par tags",
                        options=all_tags,
                        default=all_tags[:5] if len(all_tags) > 5 else all_tags
                    )
                    
                    if selected_tags:
                        filtered_tags = tag_data[tag_data['tag'].isin(selected_tags)]
                        
                        for _, row in filtered_tags.iterrows():
                            with st.container(border=True):
                                tcol1, tcol2, tcol3 = st.columns([2, 1, 1])
                                
                                tcol1.markdown(f"**🏷️ {row['tag']}**")
                                tcol1.caption(f"{row['count']} transactions")
                                
                                tcol2.markdown(f"**{abs(row['total_amount']):,.2f} €**")
                                tcol2.caption("Total")
                                
                                tcol3.markdown(f"**{abs(row['avg_amount']):,.2f} €**")
                                tcol3.caption("Moyenne")
                else:
                    st.info("Aucune opération récurrente n'a de tags associés.")
            
            elif view_mode == "Vue validation":
                st.subheader("📊 Vue par statut de validation")
                
                # Show confirmed recurrences
                confirmed_feedback = get_all_feedback(status='confirmed')
                if confirmed_feedback:
                    st.markdown(f"**✅ Confirmées ({len(confirmed_feedback)})**")
                    for item in confirmed_feedback:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.markdown(f"**{item['label_pattern']}**")
                                if item['category']:
                                    st.caption(f"Cat: {item['category']}")
                            with col2:
                                if item.get('notes'):
                                    st.caption(f"💬 {item['notes']}")
                            with col3:
                                if st.button("🔄 Annuler", key=f"undo_c_{item['id']}"):
                                    delete_feedback(item['label_pattern'], item['category'])
                                    st.rerun()
                else:
                    st.info("Aucune récurrence confirmée.")
                
                # Show rejected recurrences
                rejected_feedback = get_all_feedback(status='rejected')
                if rejected_feedback:
                    st.markdown(f"**❌ Rejetées ({len(rejected_feedback)})**")
                    for item in rejected_feedback:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([3, 2, 1])
                            with col1:
                                st.markdown(f"**{item['label_pattern']}**")
                                if item['category']:
                                    st.caption(f"Cat: {item['category']}")
                            with col2:
                                if item.get('notes'):
                                    st.caption(f"💬 {item['notes']}")
                            with col3:
                                if st.button("🔄 Restaurer", key=f"undo_r_{item['id']}"):
                                    delete_feedback(item['label_pattern'], item['category'])
                                    st.rerun()
                else:
                    st.info("Aucun faux positif rejeté.")
            
            # Manual add section
            render_manual_add_section(on_add=lambda label, cat: st.rerun())
            
            # Show confirmed and rejected sections (compact)
            render_confirmed_recurring_section(recurring_df, cat_emoji_map)
            render_rejected_recurring_section()
            
            # Tips and help
            st.divider()
            with st.expander("💡 Comprendre l'analyse des récurrences"):
                st.markdown("""
                **Comment ça marche ?**
                
                1. **Détection** : L'algorithme regroupe les transactions par libellé similaire
                2. **Analyse** : Il vérifie la régularité des dates et la cohérence des montants
                3. **Validation** : Vous confirmez ou rejetez chaque détection
                4. **Mémorisation** : Vos préférences sont sauvegardées pour les futures analyses
                
                **Pour les revenus (salaires, chômage) :**
                - Les libellés varient souvent (dates, références)
                - L'algorithme essaie de détecter les patterns : "FRANCE TRAVAIL", "SALAIRE", "PENSION"
                - Assurez-vous que vos revenus sont bien catégorisés comme "Revenus"
                
                **Gestion des faux positifs :**
                - Si une opération est détectée par erreur, cliquez sur "❌ Pas une récurrence"
                - L'opération sera exclue des futures analyses
                - Vous pouvez la restaurer à tout moment depuis la "Vue validation"
                
                **Ajout manuel :**
                - Si une récurrence n'est pas détectée automatiquement, utilisez "➕ Ajouter manuellement"
                - Utile pour les nouveaux abonnements ou patterns complexes
                """)


render_scroll_to_top()

from modules.ui.layout import render_app_info
render_app_info()
