"""Data operations UI component - Simplified."""


import streamlit as st

from modules.db.transactions import get_all_transactions


def render_export_section() -> None:
    """Render the export section."""
    df_all = get_all_transactions()
    if df_all.empty:
        st.info("ℹ️ Aucune transaction à exporter.")
        return

    total_tx = len(df_all)
    st.caption(f"📊 {total_tx} transaction(s) disponible(s)")

    col_ex1, col_ex2 = st.columns([3, 1])

    with col_ex1:
        csv = df_all.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            label="📥 Exporter CSV",
            data=csv,
            file_name="financeperso_export.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_data_operations() -> None:
    """Render full data operations section."""
    st.subheader("📤 Export des données")
    render_export_section()
