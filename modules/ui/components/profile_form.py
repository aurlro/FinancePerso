
import streamlit as st
from modules.db.rules import add_learning_rule
from modules.db.budgets import set_budget
from modules.db.categories import get_categories

def render_profile_setup_form(key_prefix="profile"):
    """
    Render a form to manually setup financial profile (Income, Housing, Subscriptions).
    
    Args:
        key_prefix: Unique key prefix for Streamlit widgets to allow multiple instances.
    """
    with st.form(f"{key_prefix}_form"):
        st.subheader("📝 Configuration Manuelle")
        st.markdown("Définissez vos postes principaux pour automatiser le classement.")
        
        # --- REVENUS ---
        st.markdown("### 💰 Revenus Principaux")
        col1, col2 = st.columns(2)
        with col1:
            salary_employer = st.text_input("Employeur / Source (Mot-clé)", placeholder="Ex: CAPGEMINI, CAF...", key=f"{key_prefix}_salary_kw")
        with col2:
            salary_amount = st.number_input("Montant Net Mensuel (€)", min_value=0.0, step=50.0, key=f"{key_prefix}_salary_amt")
            
        # --- LOGEMENT ---
        st.markdown("### 🏠 Logement")
        col3, col4 = st.columns(2)
        with col3:
            housing_keyword = st.text_input("Bailleur / Banque (Mot-clé)", placeholder="Ex: FONCIA, CREDIT AGRICOLE...", key=f"{key_prefix}_housing_kw")
        with col4:
            housing_amount = st.number_input("Loyer / Mensualité (€)", min_value=0.0, step=50.0, key=f"{key_prefix}_housing_amt")
            
        # --- ABONNEMENTS ---
        st.markdown("### 📱 Abonnements & Charges")
        st.caption("Ajoutez des mots-clés pour vos charges récurrentes (électricité, internet, téléphone...)")
        
        # Dynamic list of pairs (Keyword, Category)
        # For MVP, we stick to 3 fixed slots to act as "common providers"
        c_sub1, c_cat1 = st.columns([2, 1])
        c_sub2, c_cat2 = st.columns([2, 1])
        c_sub3, c_cat3 = st.columns([2, 1])
        
        cats = get_categories()
        
        with c_sub1:
            sub1_kw = st.text_input("Abonnement 1 (Mot-clé)", placeholder="Ex: EDF, ENGIE...", key=f"{key_prefix}_sub1")
        with c_cat1:
            sub1_cat = st.selectbox("Catégorie", cats, index=cats.index("Logement") if "Logement" in cats else 0, key=f"{key_prefix}_cat1")
            
        with c_sub2:
            sub2_kw = st.text_input("Abonnement 2 (Mot-clé)", placeholder="Ex: ORANGE, NETFLIX...", key=f"{key_prefix}_sub2")
        with c_cat2:
            sub2_cat = st.selectbox("Catégorie", cats, index=cats.index("Abonnements") if "Abonnements" in cats else 0, key=f"{key_prefix}_cat2")
            
        with c_sub3:
            sub3_kw = st.text_input("Abonnement 3 (Mot-clé)", placeholder="Ex: MAIF, ALIANZ...", key=f"{key_prefix}_sub3")
        with c_cat3:
            sub3_cat = st.selectbox("Catégorie", cats, index=cats.index("Assurances") if "Assurances" in cats else 0, key=f"{key_prefix}_cat3")

        st.divider()
        submitted = st.form_submit_button("Sauvegarder mon profil ✅", type="primary")
        
        if submitted:
            count_rules = 0
            
            # 1. Revenus
            if salary_employer:
                if add_learning_rule(salary_employer, "Revenus", priority=5):
                    count_rules += 1
            if salary_amount > 0:
                set_budget("Revenus", salary_amount)
                
            # 2. Logement
            if housing_keyword:
                if add_learning_rule(housing_keyword, "Logement", priority=5):
                    count_rules += 1
            if housing_amount > 0:
                set_budget("Logement", housing_amount)
                
            # 3. Abonnements
            subs = [(sub1_kw, sub1_cat), (sub2_kw, sub2_cat), (sub3_kw, sub3_cat)]
            for kw, cat in subs:
                if kw:
                    if add_learning_rule(kw, cat, priority=3):
                        count_rules += 1
            
            st.success(f"Profil sauvegardé ! {count_rules} règles de catégorisation créées.")
            return True
            
    return False
