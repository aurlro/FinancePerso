# -*- coding: utf-8 -*-
"""
Barre de recherche globale pour FinancePerso.
Permet de rechercher des transactions, catégories, membres rapidement.
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories_with_emojis
from modules.logger import logger
from modules.transaction_types import get_color_for_transaction


class GlobalSearch:
    """Barre de recherche globale avec résultats en temps réel."""

    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """Initialise les variables de session."""
        if "search_query" not in st.session_state:
            st.session_state["search_query"] = ""
        if "search_results" not in st.session_state:
            st.session_state["search_results"] = []
        if "last_search_time" not in st.session_state:
            st.session_state["last_search_time"] = None

    def search_transactions(self, query: str, limit: int = 10) -> pd.DataFrame:
        """Recherche dans les transactions."""
        if not query or len(query) < 2:
            return pd.DataFrame()

        try:
            df = get_all_transactions()
            if df.empty:
                return pd.DataFrame()

            query_lower = query.lower()

            # Recherche dans les colonnes principales (toujours présentes)
            mask = df["label"].str.lower().str.contains(query_lower, na=False) | df[
                "category_validated"
            ].str.lower().str.contains(query_lower, na=False)

            # Recherche dans les colonnes optionnelles (si présentes)
            if "category_predicted" in df.columns:
                mask |= df["category_predicted"].str.lower().str.contains(query_lower, na=False)
            if "member" in df.columns:
                mask |= df["member"].str.lower().str.contains(query_lower, na=False)

            # Recherche dans le montant (si la requête est un nombre)
            try:
                amount_query = float(query.replace(",", ".").replace(" ", ""))
                mask |= df["amount"].abs() == abs(amount_query)
            except ValueError:
                pass

            results = df[mask].head(limit)
            return results

        except Exception as e:
            logger.error(f"Erreur recherche transactions: {e}")
            return pd.DataFrame()

    def search_categories(self, query: str) -> List[Dict[str, Any]]:
        """Recherche dans les catégories."""
        if not query or len(query) < 2:
            return []

        try:
            categories = get_categories_with_emojis()
            query_lower = query.lower()

            results = [
                {"name": name, "emoji": emoji}
                for name, emoji in categories.items()
                if query_lower in name.lower()
            ]
            return results[:5]

        except Exception as e:
            logger.error(f"Erreur recherche categories: {e}")
            return []

    def format_transaction_result(self, row: pd.Series) -> str:
        """Formate un résultat de transaction pour l'affichage."""
        date_str = pd.to_datetime(row["date"]).strftime("%d/%m/%Y")
        amount = row["amount"]
        # Format français: espace pour milliers, virgule pour décimales
        amount_str = f"{abs(amount):,.2f} €".replace(",", " ").replace(".", ",")
        label = row["label"][:40] + "..." if len(row["label"]) > 40 else row["label"]
        category = row.get("category_validated", "Non catégorisé")

        color = get_color_for_transaction(category)
        sign = "+" if amount > 0 else ""
        return f"📅 {date_str} | **{label}** | :{color}[{sign}{amount_str}] | *{category}*"

    def render_compact(self):
        """Version compacte de la barre de recherche pour la sidebar."""
        with st.container():
            st.markdown("---")
            st.caption("🔍 Recherche rapide")

            # Input de recherche
            query = st.text_input(
                "Rechercher",
                placeholder="Transactions, catégories...",
                label_visibility="collapsed",
                key="global_search_input",
            )

            if query and len(query) >= 2:
                # Résultats
                tx_results = self.search_transactions(query, limit=5)
                cat_results = self.search_categories(query)

                if not tx_results.empty:
                    st.caption(f"📊 {len(tx_results)} transaction(s)")
                    for _, row in tx_results.head(3).iterrows():
                        result_text = self.format_transaction_result(row)
                        if st.button(
                            result_text, key=f"search_tx_{row['id']}", use_container_width=True
                        ):
                            st.session_state["selected_transaction_id"] = row["id"]
                            st.session_state["active_op_tab"] = "✅ Validation"
                            st.switch_page("pages/1_Opérations.py")

                if cat_results:
                    st.caption(f"🏷️ {len(cat_results)} catégorie(s)")
                    for cat in cat_results[:3]:
                        emoji = cat.get("emoji", "🏷️")
                        name = cat.get("name", "Inconnu")
                        if st.button(
                            f"{emoji} {name}", key=f"search_cat_{name}", use_container_width=True
                        ):
                            st.session_state["filter_category"] = name
                            st.session_state["active_op_tab"] = "✅ Validation"
                            st.switch_page("pages/1_Opérations.py")

                if tx_results.empty and not cat_results:
                    st.caption("Aucun résultat")

    def render_full(self):
        """Version complète avec page de résultats."""
        st.title("🔍 Recherche globale")

        # Barre de recherche principale
        query = st.text_input(
            "Rechercher dans vos finances",
            placeholder="Ex: 'courses', '-50', 'amazon', 'restaurant'...",
            key="full_search_input",
        )

        if not query or len(query) < 2:
            st.info("💡 Tapez au moins 2 caractères pour rechercher")
            return

        # Onglets pour différents types de résultats
        tab_tx, tab_cat = st.tabs(["📊 Transactions", "🏷️ Catégories"])

        with tab_tx:
            results = self.search_transactions(query, limit=50)

            if results.empty:
                st.warning("Aucune transaction trouvée")
            else:
                st.success(f"{len(results)} transaction(s) trouvée(s)")

                # Filtres
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox("Trier par", ["date", "montant", "label"])
                with col2:
                    order = st.selectbox("Ordre", ["Décroissant", "Croissant"])

                # Tri
                ascending = order == "Croissant"
                if sort_by == "date":
                    results = results.sort_values("date", ascending=ascending)
                elif sort_by == "montant":
                    results = results.sort_values("amount", ascending=ascending)
                elif sort_by == "label":
                    results = results.sort_values("label", ascending=ascending)

                # Affichage
                st.dataframe(
                    results[["date", "label", "amount", "category_validated", "member"]],
                    use_container_width=True,
                    hide_index=True,
                )

        with tab_cat:
            cat_results = self.search_categories(query)

            if not cat_results:
                st.warning("Aucune catégorie trouvée")
            else:
                st.success(f"{len(cat_results)} catégorie(s) trouvée(s)")

                for cat in cat_results:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.2, 0.8])
                        with col1:
                            st.write(f"### {cat.get('emoji', '🏷️')}")
                        with col2:
                            st.write(f"**{cat.get('name', 'Inconnu')}**")
                            if cat.get("description"):
                                st.caption(cat["description"])

                            if st.button("Voir les transactions", key=f"cat_btn_{cat['name']}"):
                                st.session_state["filter_category"] = cat["name"]
                                st.session_state["active_op_tab"] = "✅ Validation"
                                st.switch_page("pages/1_Opérations.py")


def render_global_search_compact():
    """Fonction utilitaire pour afficher la recherche compacte."""
    search = GlobalSearch()
    search.render_compact()


def render_global_search_full():
    """Fonction utilitaire pour afficher la recherche complète."""
    search = GlobalSearch()
    search.render_full()


# Export
__all__ = ["GlobalSearch", "render_global_search_compact", "render_global_search_full"]
