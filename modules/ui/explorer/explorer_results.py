"""
Explorer Results - Affichage des résultats de l'explorateur.
"""
import streamlit as st
import pandas as pd
from typing import Optional


def render_summary_cards(df: pd.DataFrame):
    """Render summary statistic cards."""
    if df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Transactions", len(df))
    
    with col2:
        total = df['amount'].sum() if 'amount' in df.columns else 0
        st.metric("Total", f"{total:,.2f} €")
    
    with col3:
        avg = df['amount'].mean() if 'amount' in df.columns else 0
        st.metric("Moyenne", f"{avg:,.2f} €")
    
    with col4:
        if 'date' in df.columns and not df.empty:
            date_range = f"{df['date'].min()} → {df['date'].max()}"
            st.metric("Période", date_range)


def render_transactions_table(df: pd.DataFrame, key_prefix: str = "explorer"):
    """Render transactions as an interactive table."""
    if df.empty:
        st.info("Aucune transaction ne correspond aux filtres.")
        return
    
    # Prepare display columns
    display_df = df.copy()
    
    # Format amount
    if 'amount' in display_df.columns:
        display_df['amount_formatted'] = display_df['amount'].apply(
            lambda x: f"{x:,.2f} €" if pd.notna(x) else ""
        )
    
    # Format date
    if 'date' in display_df.columns:
        display_df['date_formatted'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
    
    # Select and rename columns for display
    column_config = {}
    display_cols = []
    
    if 'date_formatted' in display_df.columns:
        display_cols.append('date_formatted')
        column_config['date_formatted'] = st.column_config.TextColumn("Date", width="small")
    
    if 'label' in display_df.columns:
        display_cols.append('label')
        column_config['label'] = st.column_config.TextColumn("Libellé", width="large")
    
    if 'amount_formatted' in display_df.columns:
        display_cols.append('amount_formatted')
        column_config['amount_formatted'] = st.column_config.TextColumn("Montant", width="small")
    
    if 'category_validated' in display_df.columns:
        display_cols.append('category_validated')
        column_config['category_validated'] = st.column_config.TextColumn("Catégorie", width="medium")
    
    if 'account_label' in display_df.columns:
        display_cols.append('account_label')
        column_config['account_label'] = st.column_config.TextColumn("Compte", width="medium")
    
    if 'member' in display_df.columns:
        display_cols.append('member')
        column_config['member'] = st.column_config.TextColumn("Membre", width="small")
    
    if 'tags' in display_df.columns:
        display_cols.append('tags')
        column_config['tags'] = st.column_config.TextColumn("Tags", width="medium")
    
    # Show table
    st.dataframe(
        display_df[display_cols],
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        key=f"{key_prefix}_table"
    )


def render_charts(df: pd.DataFrame, explorer_type: str, explorer_value: str):
    """Render charts for the filtered data."""
    if df.empty or len(df) < 2:
        return
    
    st.subheader("📈 Analyse visuelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Evolution over time
        if 'date' in df.columns and 'amount' in df.columns:
            df_chart = df.copy()
            df_chart['date'] = pd.to_datetime(df_chart['date'])
            df_chart = df_chart.sort_values('date')
            
            # Group by month
            df_chart['month'] = df_chart['date'].dt.to_period('M')
            monthly = df_chart.groupby('month')['amount'].sum().reset_index()
            monthly['month_str'] = monthly['month'].astype(str)
            
            if not monthly.empty:
                st.line_chart(
                    monthly.set_index('month_str')['amount'],
                    use_container_width=True
                )
                st.caption("Évolution mensuelle")
    
    with col2:
        # Distribution by amount
        if 'amount' in df.columns:
            amounts = df['amount'].abs()
            hist_data = pd.DataFrame({'Montant': amounts})
            st.bar_chart(
                hist_data['Montant'].value_counts().head(10),
                use_container_width=True
            )
            st.caption("Distribution des montants")


def render_export_section(df: pd.DataFrame):
    """Render export options."""
    st.divider()
    st.subheader("💾 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Télécharger CSV",
            data=csv,
            file_name=f"exploration_{len(df)}_transactions.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("📋 Copier dans le presse-papier", use_container_width=True):
            df.to_clipboard(index=False)
            st.toast("📋 Copié !", icon="✅")
    
    with col3:
        if st.button("📧 Partager par email", use_container_width=True, disabled=True):
            st.info("Fonctionnalité à venir")


def render_no_results():
    """Render message when no results found."""
    st.markdown("""
    <div style='
        text-align: center;
        padding: 3rem;
        background: #f8fafc;
        border-radius: 12px;
        border: 2px dashed #cbd5e1;
        margin: 2rem 0;
    '>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
        <h3 style='color: #64748b; margin-bottom: 0.5rem;'>Aucun résultat</h3>
        <p style='color: #94a3b8;'>Essayez d'ajuster vos filtres pour voir plus de transactions.</p>
    </div>
    """, unsafe_allow_html=True)


def render_explorer_results(
    df: pd.DataFrame,
    explorer_type: str,
    explorer_value: str,
    key_prefix: str = "explorer"
):
    """
    Render complete results section.
    
    Args:
        df: Filtered DataFrame
        explorer_type: 'category' or 'tag'
        explorer_value: Selected category/tag value
        key_prefix: Key prefix for Streamlit widgets
    """
    if df.empty:
        render_no_results()
        return
    
    # Summary
    st.subheader(f"📊 Résultats : {len(df)} transaction(s)")
    render_summary_cards(df)
    
    st.divider()
    
    # Transactions table
    render_transactions_table(df, key_prefix)
    
    st.divider()
    
    # Charts
    render_charts(df, explorer_type, explorer_value)
    
    st.divider()
    
    # Export
    render_export_section(df)
