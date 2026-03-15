# -*- coding: utf-8 -*-
"""
Page d'import unifiée avec Design System V5.5.

Remplace: pages/01_Import.py (legacy)
"""

import io
from typing import Any

import pandas as pd
import streamlit as st

from modules.db.transactions import save_transactions
from modules.ingestion import process_csv_file
from modules.logger import logger
from modules.ui.molecules.loader import loader
from modules.ui.molecules.toast import toast_error, toast_info, toast_success
from modules.ui.tokens.colors import Colors
from modules.ui.tokens.spacing import Spacing


def render_import_page() -> None:
    """
    Render the unified import page with Design System V5.5.
    """
    # Header
    st.markdown(f"""
    <h1 style="color: {Colors.GRAY_900}; margin-bottom: {Spacing.SMALL}px;">
        📥 Import de transactions
    </h1>
    <p style="color: {Colors.GRAY_600};">
        Importez vos relevés bancaires au format CSV
    </p>
    """, unsafe_allow_html=True)
    
    # Upload section
    st.markdown("#### 📁 Fichier CSV")
    
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre fichier CSV ou cliquez pour parcourir",
        type=["csv"],
        help="Formats supportés: CSV (UTF-8)",
        key="import_file_uploader",
    )
    
    if uploaded_file is not None:
        render_uploaded_file_section(uploaded_file)


def render_uploaded_file_section(uploaded_file: Any) -> None:
    """Render section after file upload."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.success(f"✅ Fichier chargé: **{uploaded_file.name}**")
        st.caption(f"Taille: {len(uploaded_file.getvalue()) / 1024:.1f} KB")
    
    with col2:
        if st.button("🗑️ Supprimer", use_container_width=True):
            st.session_state.import_file_uploader = None
            st.rerun()
    
    st.divider()
    
    # Options
    st.markdown("#### ⚙️ Options d'import")
    
    col1, col2 = st.columns(2)
    with col1:
        account_label = st.text_input(
            "Nom du compte",
            value="Compte Principal",
            help="Identifie le compte source",
        )
    with col2:
        encoding = st.selectbox(
            "Encodage",
            options=["utf-8", "latin-1", "cp1252"],
            index=0,
        )
    
    # Preview before import
    st.markdown("#### 👁️ Aperçu")
    
    try:
        df_preview = load_preview(uploaded_file, encoding)
        if not df_preview.empty:
            st.dataframe(df_preview.head(10), use_container_width=True, hide_index=True)
            st.caption(f"{len(df_preview)} transactions détectées")
        else:
            st.warning("⚠️ Aucune transaction détectée")
    except Exception as e:
        toast_error("Erreur de lecture", str(e))
        return
    
    # Import button
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("📥 Importer les transactions", type="primary", use_container_width=True):
            process_import(uploaded_file, account_label, encoding)


def load_preview(uploaded_file: Any, encoding: str) -> pd.DataFrame:
    """Load a preview of the CSV file."""
    try:
        df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode(encoding)))
        return df
    except Exception as e:
        logger.error(f"Error loading preview: {e}")
        return pd.DataFrame()


def process_import(uploaded_file: Any, account_label: str, encoding: str) -> None:
    """Process the import of transactions."""
    with loader("Import en cours...", show_progress=True):
        try:
            # Process CSV
            df = process_csv_file(
                uploaded_file.getvalue().decode(encoding),
                account_label=account_label,
            )
            
            if df.empty:
                toast_error("Import vide", "Aucune transaction valide trouvée")
                return
            
            # Save to database
            save_transactions(df)
            
            # Success message
            toast_success(
                "Import réussi !",
                f"{len(df)} transactions importées avec succès",
            )
            
            # Redirect to validation page
            st.info("🔄 Redirection vers la page de validation...")
            st.switch_page("pages/05_Audit.py")
            
        except Exception as e:
            logger.exception("Import failed")
            toast_error("Erreur d'import", str(e))


def render_import_history() -> None:
    """Render import history section."""
    st.divider()
    st.markdown("#### 📜 Historique des imports")
    
    # Mock history - replace with actual data
    history = [
        {"date": "2024-03-14", "file": "releve_mars.csv", "count": 45},
        {"date": "2024-02-15", "file": "releve_fevrier.csv", "count": 38},
    ]
    
    if history:
        for item in history:
            with st.container():
                cols = st.columns([2, 3, 2, 1])
                with cols[0]:
                    st.write(f"📅 {item['date']}")
                with cols[1]:
                    st.write(f"📄 {item['file']}")
                with cols[2]:
                    st.write(f"✅ {item['count']} transactions")
                with cols[3]:
                    if st.button("🗑️", key=f"delete_{item['date']}"):
                        toast_info("Fonction à implémenter")
            st.divider()
    else:
        st.info("Aucun historique d'import")


def render() -> None:
    """Alias for render_import_page."""
    render_import_page()
