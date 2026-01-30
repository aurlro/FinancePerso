"""
Recurrence Analysis Page - Enhanced V2
Features:
- Improved drill-down with transaction IDs
- Grouping by category and tags
- Filters for better exploration
- Better income detection (salaries, benefits)
"""
import streamlit as st
import pandas as pd
from modules.data_manager import get_all_transactions, get_categories_with_emojis
from modules.analytics_v2 import (
    detect_recurring_payments_v2, 
    group_by_category, 
    get_recurring_by_tags,
    analyze_recurrence_summary
)
from modules.ui import load_css
from modules.ui.components.transaction_drill_down import render_transaction_drill_down

st.set_page_config(page_title="Récurrence", page_icon="🔁", layout="wide")
load_css()

st.title("🔁 Analyse des Récurrences")
st.markdown("Détection automatique des abonnements, factures et revenus réguliers.")

# Load data
df = get_all_transactions()

if df.empty:
    st.info("Aucune donnée disponible pour l'analyse.")
else:
    # Sidebar filters
    st.sidebar.header("🔍 Filtres")
    
    # We only analyze validated transactions for better accuracy
    validated_df = df[df['status'] == 'validated']
    
    if validated_df.empty:
        st.warning("Veuillez valider quelques transactions pour permettre l'analyse des récurrences.")
    else:
        # Run analysis
        with st.spinner("Analyse des tendances en cours..."):
            recurring_df = detect_recurring_payments_v2(validated_df)
        
        if recurring_df.empty:
            st.info("""
            Aucune récurrence claire détectée pour le moment. 
            
            **Conseils :**
            - L'analyse nécessite au moins 2 occurrences d'une même opération
            - Les opérations doivent avoir un montant régulier et une périodicité mensuelle/trimestrielle
            - Pour les salaires : vérifiez qu'ils sont bien catégorisés comme 'Revenus'
            """)
        else:
            # Summary metrics
            summary = analyze_recurrence_summary(validated_df, recurring_df)
            
            st.success(f"**{summary.get('total_detected', 0)}** récurrences détectées "
                      f"({summary.get('expense_count', 0)} dépenses, "
                      f"{summary.get('income_count', 0)} revenus)")
            
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
                options=["Par opération", "Par catégorie", "Par tag"],
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
                
                # Apply filters
                filtered_df = recurring_df.copy()
                
                if show_type == "Dépenses uniquement":
                    filtered_df = filtered_df[filtered_df['avg_amount'] < 0]
                elif show_type == "Revenus uniquement":
                    filtered_df = filtered_df[filtered_df['avg_amount'] > 0]
                
                if freq_filter != "Toutes":
                    filtered_df = filtered_df[filtered_df['frequency_label'] == freq_filter]
                
                if var_filter != "Tous":
                    filtered_df = filtered_df[filtered_df['variability'] == var_filter]
                
                if filtered_df.empty:
                    st.info("Aucune opération ne correspond aux filtres sélectionnés.")
                else:
                    # Group by type
                    expenses = filtered_df[filtered_df['avg_amount'] < 0].copy()
                    incomes = filtered_df[filtered_df['avg_amount'] > 0].copy()
                    
                    # Display Incomes First
                    if not incomes.empty:
                        st.subheader(f"💰 Revenus Réguliers ({len(incomes)})")
                        
                        for _, row in incomes.iterrows():
                            with st.container(border=True):
                                c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 0.5])
                                
                                cat_name = row['category']
                                emoji = cat_emoji_map.get(cat_name, "💰")
                                
                                # Show sample labels if different from grouped label
                                display_label = row['label']
                                if len(row.get('sample_labels', [])) > 1:
                                    display_label = f"{display_label} *(+{len(row['sample_labels'])-1} variantes)*"
                                
                                c1.markdown(f"**{emoji} {display_label}**")
                                c1.caption(f"{row['count']} occurrences")
                                
                                c2.markdown(f"**{row['avg_amount']:,.2f} €**")
                                c2.caption("Montant moyen")
                                
                                c3.markdown(f"**{row['frequency_label']}**")
                                c3.caption(f"~{row['frequency_days']:.0f} jours")
                                
                                c4.markdown(f":grey[{row['last_date']}]")
                                c4.caption("Dernière")
                                
                                # Variability indicator
                                var_color = "🟢" if row['variability'] == 'Fixe' else "🟡"
                                c5.markdown(f"{var_color}")
                                c5.caption(row['variability'])
                                
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
                                c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 0.5])
                                
                                cat_name = row['category']
                                emoji = cat_emoji_map.get(cat_name, "🏷️")
                                
                                display_label = row['label']
                                if len(row.get('sample_labels', [])) > 1:
                                    display_label = f"{display_label} *(+{len(row['sample_labels'])-1} variantes)*"
                                
                                c1.markdown(f"**{emoji} {display_label}**")
                                c1.caption(f"{row['count']} occurrences")
                                
                                c2.markdown(f"**{abs(row['avg_amount']):,.2f} €**")
                                c2.caption("Montant moyen")
                                
                                c3.markdown(f"**{row['frequency_label']}**")
                                c3.caption(f"~{row['frequency_days']:.0f} jours")
                                
                                c4.markdown(f":grey[{row['last_date']}]")
                                c4.caption("Dernière")
                                
                                var_color = "🟢" if row['variability'] == 'Fixe' else "🟡"
                                c5.markdown(f"{var_color}")
                                c5.caption(row['variability'])
                                
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
                
                cat_grouped = group_by_category(recurring_df)
                
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
                
                tag_data = get_recurring_by_tags(validated_df, recurring_df)
                
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
            
            # Tips and help
            st.divider()
            with st.expander("💡 Comprendre l'analyse des récurrences"):
                st.markdown("""
                **Comment ça marche ?**
                
                1. **Détection** : L'algorithme regroupe les transactions par libellé similaire
                2. **Analyse** : Il vérifie la régularité des dates et la cohérence des montants
                3. **Classification** : Les opérations sont classées par fréquence (mensuelle, trimestrielle...)
                
                **Pour les revenus (salaires, chômage) :**
                - Les libellés varient souvent (dates, références)
                - L'algorithme essaie de détecter les patterns : "FRANCE TRAVAIL", "SALAIRE", "PENSION"
                - Assurez-vous que vos revenus sont bien catégorisés comme "Revenus"
                
                **Conseils pour améliorer la détection :**
                - Validez vos transactions régulièrement
                - Utilisez des tags pour marquer les opérations récurrentes
                - Vérifiez que les montants sont cohérents (même opération = montant similaire)
                """)

from modules.ui.layout import render_app_info
render_app_info()
