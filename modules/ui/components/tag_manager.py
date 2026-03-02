"""
Tag Manager Component.
Gestion des tags avec sélection intelligente et application par lot.
"""

import warnings
from difflib import SequenceMatcher

import streamlit as st

# Couleurs par défaut pour les tags
DEFAULT_TAG_COLORS = {
    "loyer": "#FF6B6B",
    "alimentation": "#4ECDC4",
    "transport": "#45B7D1",
    "loisirs": "#96CEB4",
    "santé": "#FFEAA7",
    "shopping": "#DDA0DD",
    "factures": "#98D8C8",
    "restaurant": "#F7DC6F",
    "essence": "#BB8FCE",
    "supermarché": "#85C1E9",
}

DEFAULT_COLOR = "#95A5A6"


def get_tag_color(tag_name: str, tag_colors: dict | None = None) -> str:
    """
    Retourne la couleur associée à un tag.

    Args:
        tag_name: Nom du tag
        tag_colors: Dictionnaire optionnel de couleurs personnalisées

    Returns:
        Code couleur hexadécimal
    """
    colors = tag_colors or DEFAULT_TAG_COLORS
    return colors.get(tag_name.lower(), DEFAULT_COLOR)


def render_pill_tags(tags: list, tag_colors: dict | None = None):
    """
    Affiche les tags sous forme de pills colorés.

    Args:
        tags: Liste des noms de tags
        tag_colors: Dictionnaire optionnel de couleurs personnalisées
    """
    if not tags:
        return

    colors = tag_colors or DEFAULT_TAG_COLORS
    pills_html = []

    for tag in tags:
        color = colors.get(tag.lower(), DEFAULT_COLOR)
        pills_html.append(
            f'<span style="background-color: {color}; color: white; '
            f"padding: 2px 8px; border-radius: 12px; font-size: 0.8em; "
            f'margin-right: 4px; display: inline-block;">{tag}</span>'
        )

    st.markdown(" ".join(pills_html), unsafe_allow_html=True)


def find_similar_transactions(description: str, transactions_df, threshold: float = 0.6):
    """
    Trouve les transactions similaires basées sur la description.

    Args:
        description: Description à comparer
        transactions_df: DataFrame des transactions
        threshold: Seuil de similarité (0-1)

    Returns:
        Index des transactions similaires
    """
    if transactions_df is None or transactions_df.empty or not description:
        return []

    similar_indices = []
    desc_lower = description.lower()

    for idx, row in transactions_df.iterrows():
        row_desc = str(row.get("description", "")).lower()
        if row_desc:
            similarity = SequenceMatcher(None, desc_lower, row_desc).ratio()
            if similarity >= threshold:
                similar_indices.append(idx)

    return similar_indices


def render_smart_tag_selector(transaction: dict, all_tags: list, tag_colors: dict | None = None):
    """
    Affiche un sélecteur de tags intelligent pour une transaction.

    Args:
        transaction: Dictionnaire contenant les infos de la transaction
        all_tags: Liste de tous les tags disponibles
        tag_colors: Dictionnaire optionnel de couleurs personnalisées

    Returns:
        Liste des tags sélectionnés
    """
    if not all_tags:
        return []

    current_tags = transaction.get("tags", [])
    transaction_id = transaction.get("id", "unknown")

    # Créer une clé unique pour ce sélecteur
    selector_key = f"tag_selector_{transaction_id}"

    # Afficher les tags actuels
    if current_tags:
        st.caption("Tags actuels:")
        render_pill_tags(current_tags, tag_colors)

    # Sélecteur multiselect
    selected_tags = st.multiselect(
        "Ajouter/Modifier les tags", options=all_tags, default=current_tags, key=selector_key
    )

    return selected_tags


def batch_apply_tags_to_similar(selected_indices: list, transactions_df, st_session_state: dict):
    """
    Applique les tags par lot aux transactions similaires.

    Args:
        selected_indices: Index des transactions sélectionnées
        transactions_df: DataFrame des transactions
        st_session_state: Session state de Streamlit

    Returns:
        Nombre de transactions modifiées
    """
    if not selected_indices or transactions_df is None or transactions_df.empty:
        return 0

    # Récupérer les tags à appliquer depuis le session state
    batch_tags_key = "batch_tags_to_apply"
    tags_to_apply = st_session_state.get(batch_tags_key, [])

    if not tags_to_apply:
        return 0

    modified_count = 0

    for idx in selected_indices:
        if idx in transactions_df.index:
            current_tags = transactions_df.loc[idx, "tags"]
            if isinstance(current_tags, str):
                current_tags = [t.strip() for t in current_tags.split(",") if t.strip()]
            elif not isinstance(current_tags, list):
                current_tags = []

            # Ajouter les nouveaux tags sans doublons
            new_tags = list(set(current_tags + tags_to_apply))
            transactions_df.loc[idx, "tags"] = new_tags
            modified_count += 1

    return modified_count


# Pour compatibilité - wrappers avec avertissement de dépréciation


def _warn_deprecation(old_name: str = ""):
    """Affiche un avertissement de dépréciation."""
    msg = "⚠️ Ce composant est déprécié. Utilisez les fonctions directement depuis modules.ui.components.tag_manager"
    st.warning(msg, icon="🔄")
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


__all__ = [
    "get_tag_color",
    "render_pill_tags",
    "find_similar_transactions",
    "render_smart_tag_selector",
    "batch_apply_tags_to_similar",
    "DEFAULT_TAG_COLORS",
    "DEFAULT_COLOR",
]
