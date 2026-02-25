"""
📅 Abonnements - Redirection vers Automatisation

Cette page a été fusionnée avec la page 🧠 Automatisation.
Les fonctionnalités sont maintenant accessibles dans :
- 📥 Inbox : Validation des nouveaux abonnements
- ⚙️ Règles > 🔁 Abonnements : Gestion des abonnements confirmés
- 📊 Historique > 💳 Calculateur : Calculateur "Reste à vivre"

Ce fichier est conservé pour la compatibilité des favoris/liens.
"""

import streamlit as st
import time

# Redirection automatique après un délai
st.set_page_config(
    page_title="Abonnements - Redirection",
    page_icon="📅",
    layout="wide",
)

st.title("📅 Abonnements")

st.info("""
## 🔄 Cette page a été déplacée

Les fonctionnalités de gestion des abonnements ont été fusionnées avec la page **🧠 Automatisation**
pour une expérience plus cohérente.

### Où trouver vos fonctionnalités :

| Ancien emplacement | Nouvel emplacement |
|-------------------|-------------------|
| Liste des abonnements | 🧠 Automatisation > ⚙️ Règles > 🔁 Abonnements |
| Validation des détections | 🧠 Automatisation > 📥 Inbox |
| Alertes zombies | 🧠 Automatisation > 📥 Inbox > ⚠️ Alertes |
| Calculateur "Reste à vivre" | 🧠 Automatisation > 📊 Historique > 💳 Calculateur |

**Redirection automatique dans 5 secondes...**
""")

# Bouton de redirection immédiate
if st.button("🚀 Aller vers Automatisation", type="primary", use_container_width=True):
    st.switch_page("pages/4_Intelligence.py")

# Redirection auto avec délai
progress_text = "Redirection automatique..."
my_bar = st.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.05)
    my_bar.progress(percent_complete + 1, text=progress_text)

# Redirection JavaScript pour une expérience fluide
st.markdown("""
<script>
    setTimeout(function() {
        window.location.href = '/Intelligence';
    }, 5000);
</script>
""", unsafe_allow_html=True)

# Fallback : lien manuel
st.divider()
st.caption("Si la redirection ne fonctionne pas : [Cliquez ici pour aller vers Automatisation](/Intelligence)")
