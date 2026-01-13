import streamlit as st
from modules.data_manager import get_all_transactions, update_transaction_category
from modules.categorization import clean_label, predict_category_ai
from modules.ui import load_css
import pandas as pd
import json
import google.generativeai as genai
import os

st.set_page_config(page_title="Assistant Audit", page_icon="🕵️", layout="wide")
load_css()
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
    df_valid = df[df['status'] != 'pending'].copy()
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
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return []

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
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
        
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        suggestions = json.loads(text)
        
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

from modules.analytics import detect_recurring_payments
from modules.ui import card_kpi

tab_audit, tab_sub = st.tabs(["🔎 Audit & Qualité", "💸 Abonnements & Récurrents"])

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
                    st.dataframe(item['rows'][['date', 'label', 'amount', 'category_validated']])
                    
                    if item.get('suggested_category'):
                        if st.button(f"Accepter la correction ({item['suggested_category']})", key=f"fix_{i}"):
                            for tx_id in item['rows']['id']:
                                update_transaction_category(tx_id, item['suggested_category'])
                            st.success("Correction appliquée !")
                            st.session_state['audit_results'].pop(i)
                            st.rerun()

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
