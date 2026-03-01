"""
Import Preview Module - Aperçu avant import

Permet aux utilisateurs de voir et valider les transactions avant import définitif.
Particulièrement utile pour Sophie (débutante) qui a besoin de vérification.
"""

import streamlit as st
import pandas as pd
from typing import Optional

from modules.ui.feedback import toast_warning, toast_info


def render_import_preview(
    df: pd.DataFrame,
    detected_bank: str,
    duplicates: Optional[pd.DataFrame] = None,
    on_confirm=None,
    on_cancel=None,
    key: str = "import_preview"
):
    """
    Render an import preview screen.
    
    Args:
        df: DataFrame des transactions à importer
        detected_bank: Nom de la banque détectée
        duplicates: DataFrame des doublons potentiels (optionnel)
        on_confirm: Callback quand l'utilisateur confirme
        on_cancel: Callback quand l'utilisateur annule
        key: Clé unique pour les widgets
    """
    total_tx = len(df)
    duplicate_count = len(duplicates) if duplicates is not None else 0
    new_tx = total_tx - duplicate_count
    
    # Header
    st.markdown("### 📊 Prévisualisation de l'import")
    st.markdown(f"**Banque détectée:** {detected_bank}")
    
    # Résumé
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", f"{total_tx} transactions")
    with col2:
        st.metric("Nouvelles", f"{new_tx} transactions", delta_color="normal")
    with col3:
        if duplicate_count > 0:
            st.metric("Doublons", f"{duplicate_count}", delta_color="inverse")
        else:
            st.metric("Doublons", "0")
    
    st.divider()
    
    # Alertes
    if duplicate_count > 0:
        toast_warning(f"⚠️ {duplicate_count} transaction(s) semblent être des doublons")
        
        with st.expander("🔍 Voir les doublons détectés"):
            st.dataframe(duplicates, use_container_width=True)
            
            ignore_duplicates = st.checkbox(
                "Ignorer les doublons lors de l'import",
                value=True,
                key=f"{key}_ignore_dup"
            )
    else:
        ignore_duplicates = False
    
    # Aperçu des transactions
    st.markdown("#### 📋 Aperçu des transactions (5 premières lignes)")
    
    preview_df = df.head(5).copy()
    
    # Format pour affichage
    display_cols = ['date', 'label', 'amount', 'category_validated'] if 'category_validated' in preview_df.columns else ['date', 'label', 'amount']
    st.dataframe(preview_df[display_cols], use_container_width=True)
    
    # Statistiques rapides
    if 'amount' in df.columns:
        st.markdown("#### 💰 Résumé financier")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_in = df[df['amount'] > 0]['amount'].sum() if len(df[df['amount'] > 0]) > 0 else 0
            st.metric("Total Entrées", f"+{total_in:,.2f} €")
        
        with col2:
            total_out = abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0
            st.metric("Total Dépenses", f"-{total_out:,.2f} €")
        
        with col3:
            balance = total_in - total_out
            color = "normal" if balance >= 0 else "inverse"
            st.metric("Balance", f"{balance:,.2f} €", delta_color=color)
    
    # Options avancées
    with st.expander("⚙️ Options d'import"):
        col1, col2 = st.columns(2)
        
        with col1:
            auto_categorize = st.checkbox(
                "Catégoriser automatiquement",
                value=True,
                key=f"{key}_auto_cat",
                help="Applique les règles de catégorisation automatique"
            )
        
        with col2:
            skip_validation = st.checkbox(
                "Marquer comme validées",
                value=False,
                key=f"{key}_skip_val",
                help="Les transactions seront marquées comme validées sans revue"
            )
    
    st.divider()
    
    # Actions
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("❌ Annuler", key=f"{key}_cancel", use_container_width=True):
            if on_cancel:
                on_cancel()
            st.session_state[f"{key}_cancelled"] = True
            st.rerun()
    
    with col2:
        if st.button("🔧 Corriger", key=f"{key}_fix", use_container_width=True):
            toast_info("Retour à l'étape de sélection du fichier")
            if on_cancel:
                on_cancel()
            st.rerun()
    
    with col3:
        confirm_label = f"✅ Confirmer l'import ({new_tx} transactions)"
        if st.button(confirm_label, key=f"{key}_confirm", type="primary", use_container_width=True):
            options = {
                'ignore_duplicates': ignore_duplicates,
                'auto_categorize': auto_categorize,
                'skip_validation': skip_validation
            }
            if on_confirm:
                on_confirm(df, options)
            st.session_state[f"{key}_confirmed"] = True
            st.rerun()


def show_import_progress(current_step: int, total_steps: int, step_label: str):
    """
    Show a detailed progress bar for import operations.
    
    Args:
        current_step: Étape actuelle (1-based)
        total_steps: Nombre total d'étapes
        step_label: Label de l'étape courante
    """
    progress = current_step / total_steps
    
    st.progress(progress, text=f"Étape {current_step}/{total_steps}: {step_label}")
    
    # Détail des étapes
    steps = [
        "📁 Lecture du fichier",
        "🔍 Détection du format", 
        "📊 Parsing des transactions",
        "🔄 Détection des doublons",
        "🏷️ Catégorisation automatique",
        "💾 Enregistrement en base"
    ]
    
    with st.expander("Voir le détail des étapes", expanded=False):
        for i, step in enumerate(steps, 1):
            if i < current_step:
                st.markdown(f"✅ ~~{step}~~")
            elif i == current_step:
                st.markdown(f"🔄 **{step}** ← En cours")
            else:
                st.markdown(f"⏳ {step}")


def calculate_import_stats(df: pd.DataFrame) -> dict:
    """
    Calculate statistics for an import preview.
    
    Args:
        df: DataFrame with transactions to import
    
    Returns:
        Dictionary with stats (total_in, total_out, balance, count)
    """
    if df.empty or 'amount' not in df.columns:
        return {
            'total_in': 0.0,
            'total_out': 0.0,
            'balance': 0.0,
            'count': len(df) if not df.empty else 0
        }
    
    total_in = df[df['amount'] > 0]['amount'].sum() if len(df[df['amount'] > 0]) > 0 else 0
    total_out = abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0
    balance = total_in - total_out
    
    return {
        'total_in': float(total_in),
        'total_out': float(total_out),
        'balance': float(balance),
        'count': len(df)
    }


def format_preview_dataframe(df: pd.DataFrame, max_rows: int = 5) -> pd.DataFrame:
    """
    Format a DataFrame for preview display.
    
    Args:
        df: DataFrame to format
        max_rows: Maximum number of rows to show
    
    Returns:
        Formatted DataFrame subset
    """
    if df.empty:
        return df
    
    preview_df = df.head(max_rows).copy()
    
    # Select display columns if they exist
    display_cols = ['date', 'label', 'amount']
    if 'category_validated' in preview_df.columns:
        display_cols.append('category_validated')
    
    available_cols = [col for col in display_cols if col in preview_df.columns]
    return preview_df[available_cols]


def show_import_summary(imported: int, categorized: int, duplicates_skipped: int, errors: list):
    """
    Show a summary after import completion.
    """
    st.success(f"✅ Import terminé avec succès!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Transactions importées", imported)
    
    with col2:
        st.metric("Catégorisées automatiquement", categorized)
    
    with col3:
        if duplicates_skipped > 0:
            st.metric("Doublons ignorés", duplicates_skipped)
    
    if errors:
        with st.expander(f"⚠️ {len(errors)} erreur(s) lors de l'import"):
            for error in errors:
                st.error(error)
    
    st.info("👉 Rendez-vous dans la page **Opérations** pour valider les transactions importées.")
    
    if st.button("🔄 Importer un autre fichier", type="primary"):
        # Reset uniquement les clés liées à l'import (pas tout l'état utilisateur)
        import_keys = [k for k in st.session_state.keys() if k.startswith(("import_", "df_to_import", "selected_bank"))]
        for key in import_keys:
            del st.session_state[key]
        st.session_state.import_step = 0
        st.rerun()
