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


tab_audit, tab_anomalies, tab_trends, tab_chat, tab_sub, tab_setup = st.tabs([
    "🔎 Audit & Qualité", 
    "🎯 Anomalies", 
    "📊 Tendances",
    "💬 Chat IA",
    "💸 Abonnements & Récurrents", 
    "🏗️ Configuration Assistée"
])

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
                                ids_to_update = [int(uid) for uid in item['rows']['id'].tolist()]
                                for tx_id in ids_to_update:
                                    update_transaction_category(tx_id, item['suggested_category'])
                                st.cache_data.clear()
                                st.success(f"Correction appliquée sur {len(ids_to_update)} transactions !")
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
                             ids_to_update = [int(uid) for uid in item['rows']['id'].tolist()]
                             for tx_id in ids_to_update:
                                    update_transaction_category(tx_id, manual_cat)
                             st.cache_data.clear()
                             st.success(f"Correction manuelle appliquée sur {len(ids_to_update)} transactions !")
                             st.session_state['audit_results'].pop(i)
                             st.rerun()

# --- NEW: ANOMALIES TAB ---
with tab_anomalies:
    st.header("🎯 Détection d'Anomalies de Montant")
    st.markdown("Identifie les transactions avec des montants inhabituels par rapport à l'historique.")
    
    if st.button("Analyser les anomalies 🔍", type="primary"):
        from modules.ai import detect_amount_anomalies
        
        with st.spinner("Analyse statistique des montants..."):
            df = get_all_transactions()
            anomalies = detect_amount_anomalies(df)
            st.session_state['anomaly_results'] = anomalies
            st.rerun()
    
    if 'anomaly_results' in st.session_state:
        anomalies = st.session_state['anomaly_results']
        
        if not anomalies:
            st.success("✅ Aucune anomalie de montant détectée !")
        else:
            st.warning(f"⚠️ {len(anomalies)} anomalies détectées")
            
            for i, anom in enumerate(anomalies):
                severity_color = "🔴" if anom.get('severity') == 'high' else "🟠"
                with st.expander(f"{severity_color} {anom['label']} - {anom['details']}"):
                    st.dataframe(
                        anom['rows'][['date', 'label', 'amount', 'category_validated']],
                        use_container_width=True
                    )
                    
                    if st.button("Marquer comme normal", key=f"dismiss_anom_{i}"):
                        st.session_state['anomaly_results'].pop(i)
                        st.rerun()

# --- NEW: TRENDS TAB ---
with tab_trends:
    st.header("📊 Analyse de Tendances")
    st.markdown("Identifie les changements significatifs dans vos habitudes de dépenses.")
    
    if st.button("Analyser les tendances 📈", type="primary"):
        from modules.ai import analyze_spending_trends
        import datetime
        
        with st.spinner("Comparaison des périodes..."):
            df = get_all_transactions()
            df['date_dt'] = pd.to_datetime(df['date'])
            
            # Current month
            today = datetime.date.today()
            current_month = today.strftime('%Y-%m')
            df_current = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]
            
            # Previous month
            prev_month_date = today.replace(day=1) - datetime.timedelta(days=1)
            prev_month = prev_month_date.strftime('%Y-%m')
            df_prev = df[df['date_dt'].dt.strftime('%Y-%m') == prev_month]
            
            trends = analyze_spending_trends(df_current, df_prev)
            st.session_state['trend_insights'] = trends
            st.rerun()
    
    if 'trend_insights' in st.session_state:
        insights = st.session_state['trend_insights']
        
        st.subheader("Insights Détectés")
        for insight in insights:
            st.markdown(f"- {insight}")

# --- NEW: CHAT IA TAB ---
with tab_chat:
    st.header("💬 Assistant Conversationnel")
    st.markdown("Posez vos questions sur vos finances en langage naturel.")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Display chat history
    for msg in st.session_state['chat_history']:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
    
    # Chat input
    if user_input := st.chat_input("Posez votre question..."):
        # Add user message
        st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
        
        # Get AI response
        from modules.ai import chat_with_assistant
        with st.spinner("L'assistant réfléchit..."):
            response = chat_with_assistant(user_input, st.session_state['chat_history'])
        
        # Add assistant response
        st.session_state['chat_history'].append({'role': 'assistant', 'content': response})
        st.rerun()
    
    # Clear chat button
    if st.button("Effacer la conversation"):
        st.session_state['chat_history'] = []
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
                        
                        # Add details button
                        with st.popover("👁️ Voir détails", use_container_width=False):
                            st.markdown("### 📊 Informations complètes")
                            details_data = cand.get('sample_transactions', pd.DataFrame())
                            if not details_data.empty:
                                # Show first transaction as example
                                sample = details_data.iloc[0]
                                st.markdown(f"**Libellé complet** : `{sample.get('label', 'N/A')}`")
                                st.markdown(f"**Date** : {sample.get('date', 'N/A')}")
                                st.markdown(f"**Montant** : {sample.get('amount', 0):.2f} €")
                                st.markdown(f"**Compte** : {sample.get('account_label', 'N/A')}")
                                st.markdown(f"**Catégorie actuelle** : {sample.get('category_validated', 'Inconnu')}")
                                
                                if len(details_data) > 1:
                                    st.markdown(f"*({len(details_data)} transactions similaires trouvées)*")
                            else:
                                st.info("Aucun détail disponible")
                                
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
    
    st.divider()
    # --- NEW: MANUAL PROFILE SETUP FORM ---
    from modules.ui.components.profile_form import render_profile_setup_form
    render_profile_setup_form(key_prefix="assistant")

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
            display_rec = recurring[['label', 'avg_amount', 'frequency_label', 'variability', 'category', 'last_date']].copy()
            display_rec['avg_amount'] = display_rec['avg_amount'].apply(lambda x: f"{x:.2f} €")
            
            st.dataframe(
                display_rec,
                column_config={
                    "label": "Libellé",
                    "avg_amount": "Montant Moyen",
                    "frequency_label": "Fréquence",
                    "variability": "Type",
                    "category": "Catégorie",
                    "last_date": "Dernière transaction"
                },
                use_container_width=True
            )
            
            st.markdown("*> Note : Cette liste est basée sur la régularité des paiements (intervalle ~30 jours) et la constance du montant.*")

from modules.ui.layout import render_app_info
render_app_info()
