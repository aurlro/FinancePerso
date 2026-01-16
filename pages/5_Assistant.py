import streamlit as st
import pandas as pd
import json
from modules.data_manager import get_all_transactions, update_transaction_category, add_learning_rule, get_learning_rules, init_db, get_categories
from modules.categorization import clean_label, predict_category_ai
from modules.ui import load_css, card_kpi
from modules.ai_manager import get_ai_provider, get_active_model_name
from modules.analytics import detect_recurring_payments, detect_financial_profile

st.set_page_config(page_title="Assistant Audit", page_icon="🕵️", layout="wide")
load_css()
init_db()
st.title("🕵️ Assistant d'Audit")
st.markdown("Je scanne vos transactions pour détecter des incohérences ou des erreurs de catégorisation.")

# AUDIT FUNCTIONS
def detect_inconsistencies(df):
    """
    Find labels that have been categorized differently across transactions.
    """
    # Create a clean label column for grouping
    df['clean'] = df['label'].apply(clean_label)
    
    # Filter only validated or relevant categories
    df_valid = df[(df['status'] != 'pending') & 
                  (~df['category_validated'].isin(['Virement Interne', 'Hors Budget']))].copy()
    if df_valid.empty: return []

    # Group by clean label
    grouped = df_valid.groupby('clean')['category_validated'].unique()
    
    inconsistencies = []
    
    for label, categories in grouped.items():
        # Filter out 'Inconnu' if we have other valid categories
        cats = [c for c in categories if c != 'Inconnu']
        if len(set(cats)) > 1:
            # Found same label with different categories
            # Get examples
            examples = df_valid[df_valid['clean'] == label][['id', 'date', 'label', 'amount', 'category_validated']]
            inconsistencies.append({
                "type": "Incohérence",
                "label": label,
                "details": f"Classé comme : {', '.join(cats)}",
                "rows": examples
            })
            
    return inconsistencies

def ai_audit_batch(df):
    """
    Send unique label/category pairs to AI to check for logical errors.
    """
    # Get unique pairs of (clean_label, category)
    df['clean'] = df['label'].apply(clean_label)
    unique_pairs = df[['clean', 'category_validated']].drop_duplicates()
    
    # Limit to 50 for MVP to save tokens/time
    unique_pairs = unique_pairs.head(50)
    
    prompt_data = unique_pairs.to_dict(orient='records')
    
    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()
        prompt = f"""
        Analyse ces paires (Libellé, Catégorie) et identifie celles qui semblent ERRONÉES.
        Ignore les cas ambigus, concentre-toi sur les erreurs flagrantes (ex: 'McDonalds' en 'Santé', 'Impôts' en 'Loisirs').
        
        Données : {json.dumps(prompt_data, ensure_ascii=False)}
        
        Réponds uniquement en JSON (liste d'objets) :
        [
            {{ "clean": "Libellé", "current": "Catégorie actuelle", "suggested": "Correction suggérée", "reason": "Pourquoi" }}
        ]
        Si aucune erreur, renvoie [].
        """
        
        suggestions = provider.generate_json(prompt, model_name=model_name)
        
        # Link back to transactions
        results = []
        for sugg in suggestions:
            # Find matching rows
            matches = df[(df['clean'] == sugg['clean']) & (df['category_validated'] == sugg['current'])]
            if not matches.empty:
                results.append({
                    "type": "Suspicion IA",
                    "label": sugg['clean'],
                    "details": f"{sugg['current']} ➔ {sugg['suggested']} ({sugg['reason']})",
                    "suggested_category": sugg['suggested'],
                    "rows": matches
                })
        return results

    except Exception as e:
        st.error(f"Erreur audit IA: {e}")
        return []


tab_audit, tab_sub, tab_setup = st.tabs(["🔎 Audit & Qualité", "💸 Abonnements & Récurrents", "🏗️ Configuration Assistée"])

with tab_audit:
    # --- EXISTING AUDIT LOGIC ---
    if st.button("Lancer l'analyse 🔎", type="primary"):
        with st.spinner("Analyse des incohérences et vérification IA..."):
            df = get_all_transactions()
            
            if df.empty:
                st.warning("Pas de transactions à analyser.")
            else:
                inconsistencies = detect_inconsistencies(df)
                ai_suggestions = ai_audit_batch(df)
                
                st.session_state['audit_results'] = inconsistencies + ai_suggestions
                st.rerun()

    if 'audit_results' in st.session_state:
        results = st.session_state['audit_results']
        
        if not results:
            st.success("Aucune anomalie détectée ! Tout semble propre. ✨")
        else:
            st.info(f"{len(results)} anomalies potentielles trouvées.")
            
            for i, item in enumerate(results):
                with st.expander(f"{item['type']} : {item['label']}"):
                    st.write(f"**Détails :** {item['details']}")
                    st.dataframe(
                        item['rows'][['date', 'label', 'amount', 'category_validated']],
                        column_config={
                            "date": "Date",
                            "label": "Libellé",
                            "amount": "Montant",
                            "category_validated": "Catégorie"
                        },
                        use_container_width=True
                    )
                    
                    col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
                    
                    with col_act1:
                        if item.get('suggested_category'):
                            if st.button("✅ Accepter", key=f"fix_{i}", help=f"Appliquer : {item['suggested_category']}"):
                                for tx_id in item['rows']['id']:
                                    update_transaction_category(tx_id, item['suggested_category'])
                                st.success("Correction appliquée !")
                                st.session_state['audit_results'].pop(i)
                                st.rerun()

                    with col_act2:
                        if st.button("❌ Ignorer", key=f"ignore_{i}", help="Ne pas corriger"):
                            st.session_state['audit_results'].pop(i)
                            st.rerun()
                            
                    with col_act3:
                        # Manual correction
                        options = get_categories()
                        # Pre-select current if in list, else first
                        current_cat = item['rows'].iloc[0]['category_validated']
                        idx = options.index(current_cat) if current_cat in options else 0
                        
                        manual_cat = st.selectbox("Autre correction", options, key=f"manual_{i}", index=idx, label_visibility="collapsed")
                        
                        if st.button("Appliquer", key=f"apply_manual_{i}"):
                             for tx_id in item['rows']['id']:
                                    update_transaction_category(tx_id, manual_cat)
                             st.success("Correction manuelle appliquée !")
                             st.session_state['audit_results'].pop(i)
                             st.rerun()

with tab_setup:
    st.header("🏗️ Configuration Assistée")
    st.markdown("Répondez à quelques questions pour configurer automatiquement vos catégories principales (Salaire, Loyer...)")
    
    if st.button("Lancer l'analyse 🚀", type="primary"):
        df = get_all_transactions()
        if df.empty:
            st.warning("Importez d'abord des données.")
        else:
            candidates = detect_financial_profile(df)
            st.session_state['setup_candidates'] = candidates
            st.rerun()
            
    if 'setup_candidates' in st.session_state:
        cands = st.session_state['setup_candidates']
        if not cands:
            st.success("🎉 Tout semble déjà configuré ! Je n'ai pas trouvé de nouvelles récurrences inconnues.")
            if st.button("Forcer une ré-analyse complète (incluant le déjà connu)"):
                 # TBD: logic to clear cache or ignore existing checks
                 pass
        else:
            st.info(f"J'ai trouvé **{len(cands)}** nouvelles suggestions personnalisées pour vous.")
            
            # Form
            with st.form("onboarding_form"):
                selection_map = {}
                
                for i, cand in enumerate(cands):
                    st.divider()
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**{cand['label']}** (~{cand['amount']:.0f} €)")
                        st.caption(f"Détecté comme : {cand['type']}")
                    with col2:
                        # User choice
                        choice = st.radio(
                            "C'est bien ça ?",
                            ("Oui, confirmer", "Non, ignorer", "Changer catégorie"),
                            key=f"q_{i}",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        
                        if choice == "Changer catégorie":
                            new_cat = st.selectbox("Catégorie correcte", 
                                         get_categories(), 
                                         key=f"cat_{i}")
                            selection_map[i] = {"action": "save", "cat": new_cat}
                        elif choice == "Oui, confirmer":
                             selection_map[i] = {"action": "save", "cat": cand['default_category']}
                        else:
                             selection_map[i] = {"action": "skip"}

                submitted = st.form_submit_button("Sauvegarder ma configuration ✅")
                
                if submitted:
                    count = 0
                    for i, cand in enumerate(cands):
                        decision = selection_map.get(i)
                        if decision and decision['action'] == "save":
                            # Create Learning Rule (+ Validate existing?)
                            # For simplicity, we just add the rule. The user can re-validate or next import acts.
                            # Ideally we also define priority.
                            add_learning_rule(cand['label'], decision['cat'])
                            count += 1
                    
                    st.success(f"{count} règles de configuration créées ! 🚀")
                    del st.session_state['setup_candidates']  
                    # Rerurn to refresh rules in background? 
                    # st.rerun() is inside button logic, might need sleep or direct message.

with tab_sub:
    st.header("Détection des Abonnements")
    st.markdown("Analyse des paiements récurrents sur la base de vos transactions passées.")
    
    df_sub = get_all_transactions()
    if df_sub.empty:
        st.info("Importez des données pour détecter vos abonnements.")
    else:
        recurring = detect_recurring_payments(df_sub)
        
        if recurring.empty:
            st.warning("Aucun paiement récurrent détecté pour l'instant (il faut au moins 2 occurrences).")
        else:
            # Display KPIs
            monthly_total = recurring['avg_amount'].sum()
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                card_kpi("Budget Mensuel Estimé", f"{abs(monthly_total):.2f} €", trend="Fixe", trend_color="neutral")
            with col_s2:
                card_kpi("Abonnements détectés", f"{len(recurring)}", trend="Actifs", trend_color="neutral")
            
            st.divider()
            st.subheader("Détails des récurrences")
            
            # Formating for display
            display_rec = recurring[['label', 'avg_amount', 'frequency_days', 'category', 'last_date']].copy()
            display_rec['avg_amount'] = display_rec['avg_amount'].apply(lambda x: f"{x:.2f} €")
            display_rec['frequency_days'] = display_rec['frequency_days'].apply(lambda x: f"~{x:.0f} jours")
            
            st.dataframe(
                display_rec,
                column_config={
                    "label": "Libellé",
                    "avg_amount": "Montant Moyen",
                    "frequency_days": "Fréquence",
                    "category": "Catégorie",
                    "last_date": "Dernière transaction"
                },
                use_container_width=True
            )
            
            st.markdown("*> Note : Cette liste est basée sur la régularité des paiements (intervalle ~30 jours) et la constance du montant.*")
