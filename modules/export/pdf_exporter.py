"""Export PDF des rapports - Phase 8.

Génération de rapports PDF pour les analyses financières.
"""

import base64
import io
from dataclasses import dataclass
from datetime import datetime

import streamlit as st

from modules.logger import logger


@dataclass
class PDFReportConfig:
    """Configuration d'un rapport PDF."""
    title: str
    subtitle: str = ""
    period: str = ""
    include_summary: bool = True
    include_charts: bool = True
    include_transactions: bool = True
    logo_url: str = ""


class PDFExporter:
    """Exporteur de rapports PDF."""
    
    def __init__(self):
        self.has_reportlab = self._check_reportlab()
    
    def _check_reportlab(self) -> bool:
        """Vérifie si reportlab est disponible."""
        try:
            from reportlab.lib import colors  # noqa: F401
            from reportlab.lib.pagesizes import A4  # noqa: F401
            from reportlab.platypus import SimpleDocTemplate  # noqa: F401
            return True
        except ImportError:
            logger.warning("reportlab non installé - Export PDF basique uniquement")
            return False
    
    def generate_report(
        self,
        config: PDFReportConfig,
        data: dict,
        output_path: str | None = None
    ) -> bytes:
        """Génère un rapport PDF."""
        if self.has_reportlab:
            return self._generate_with_reportlab(config, data, output_path)
        else:
            return self._generate_html_fallback(config, data)
    
    def _generate_with_reportlab(
        self,
        config: PDFReportConfig,
        data: dict,
        output_path: str | None = None
    ) -> bytes:
        """Génère un PDF avec ReportLab."""
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#10B981'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        elements = []
        
        # Titre
        elements.append(Paragraph(config.title, title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        if config.subtitle:
            elements.append(Paragraph(config.subtitle, styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
        
        if config.period:
            elements.append(Paragraph(f"Période: {config.period}", styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))
        
        # Résumé
        if config.include_summary and 'summary' in data:
            elements.append(Paragraph("Résumé", styles['Heading3']))
            summary_data = [
                ['Métrique', 'Valeur'],
                ['Total revenus', f"{data['summary'].get('income', 0):.2f} €"],
                ['Total dépenses', f"{data['summary'].get('expenses', 0):.2f} €"],
                ['Balance', f"{data['summary'].get('balance', 0):.2f} €"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Transactions
        if config.include_transactions and 'transactions' in data:
            elements.append(PageBreak())
            elements.append(Paragraph("Transactions", styles['Heading3']))
            elements.append(Spacer(1, 0.2 * inch))
            
            trans_data = [['Date', 'Libellé', 'Montant', 'Catégorie']]
            for tx in data['transactions'][:100]:
                trans_data.append([
                    tx.get('date', ''),
                    tx.get('label', '')[:40],
                    f"{tx.get('amount', 0):.2f} €",
                    tx.get('category', '')
                ])
            
            trans_table = Table(trans_data, colWidths=[1.2 * inch, 2.5 * inch, 1 * inch, 1.3 * inch])
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(trans_table)
        
        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - FinancePerso",
            footer_style
        ))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer = buffer.getvalue()
        buffer.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer)
        
        return pdf_buffer
    
    def _generate_html_fallback(self, config: PDFReportConfig, data: dict) -> bytes:
        """Génère un HTML pour impression en PDF (fallback)."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{config.title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 20px;
                    color: #1F2937;
                }}
                h1 {{
                    color: #10B981;
                    text-align: center;
                    border-bottom: 3px solid #10B981;
                    padding-bottom: 10px;
                }}
                h2 {{ color: #374151; }}
                .summary {{
                    background: #F3F4F6;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background: #374151;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #E5E7EB;
                }}
                tr:nth-child(even) {{ background: #F9FAFB; }}
                .footer {{
                    text-align: center;
                    color: #9CA3AF;
                    font-size: 0.8rem;
                    margin-top: 40px;
                }}
                @media print {{
                    body {{ margin: 0; }}
                }}
            </style>
        </head>
        <body>
            <h1>💰 {config.title}</h1>
            {f'<h2>{config.subtitle}</h2>' if config.subtitle else ''}
            {f'<p><strong>Période:</strong> {config.period}</p>' if config.period else ''}
        """
        
        if config.include_summary and 'summary' in data:
            html += f"""
            <div class="summary">
                <h2>Résumé</h2>
                <p><strong>Total revenus:</strong> {data['summary'].get('income', 0):.2f} €</p>
                <p><strong>Total dépenses:</strong> {data['summary'].get('expenses', 0):.2f} €</p>
                <p><strong>Balance:</strong> {data['summary'].get('balance', 0):.2f} €</p>
            </div>
            """
        
        if config.include_transactions and 'transactions' in data:
            html += """
            <h2>Transactions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Libellé</th>
                        <th>Montant</th>
                        <th>Catégorie</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for tx in data['transactions'][:100]:
                html += f"""
                    <tr>
                        <td>{tx.get('date', '')}</td>
                        <td>{tx.get('label', '')}</td>
                        <td>{tx.get('amount', 0):.2f} €</td>
                        <td>{tx.get('category', '')}</td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
        
        html += f"""
            <div class="footer">
                Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - FinancePerso
            </div>
        </body>
        </html>
        """
        
        return html.encode('utf-8')
    
    def render_export_button(
        self,
        config: PDFReportConfig,
        data: dict,
        button_text: str = "📄 Exporter PDF"
    ):
        """Rend un bouton d'export PDF."""
        if st.button(button_text, type="secondary"):
            with st.spinner("Génération du PDF..."):
                try:
                    pdf_bytes = self.generate_report(config, data)
                    
                    # Créer le lien de téléchargement
                    b64 = base64.b64encode(pdf_bytes).decode()
                    filename = f"financeperso_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    href = f'''
                        <a href="data:application/pdf;base64,{b64}" 
                           download="{filename}"
                           style="
                               display: inline-block;
                               padding: 0.5rem 1rem;
                               background: #10B981;
                               color: white;
                               text-decoration: none;
                               border-radius: 8px;
                               font-weight: 500;
                           ">
                            ⬇️ Télécharger le PDF
                        </a>
                    '''
                    
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("PDF généré avec succès!")
                    
                except Exception as e:
                    logger.error(f"Erreur génération PDF: {e}")
                    st.error(f"Erreur lors de la génération du PDF: {e}")


class PDFReportUI:
    """Interface UI pour les rapports PDF."""
    
    def __init__(self):
        self.exporter = PDFExporter()
    
    def render_report_generator(
        self,
        transactions: list[dict],
        period: str = ""
    ):
        """Rend l'interface de génération de rapport."""
        st.subheader("📄 Rapport PDF")
        
        with st.form("pdf_report_form"):
            cols = st.columns(2)
            
            with cols[0]:
                title = st.text_input("Titre du rapport", value="Rapport Financier")
                include_summary = st.checkbox("Inclure le résumé", value=True)
            
            with cols[1]:
                subtitle = st.text_input("Sous-titre", value="")
                include_transactions = st.checkbox("Inclure les transactions", value=True)
            
            submitted = st.form_submit_button("Générer le PDF", type="primary")
            
            if submitted:
                # Préparer les données
                income = sum(t['amount'] for t in transactions if t.get('amount', 0) > 0)
                expenses = sum(t['amount'] for t in transactions if t.get('amount', 0) < 0)
                
                config = PDFReportConfig(
                    title=title,
                    subtitle=subtitle,
                    period=period,
                    include_summary=include_summary,
                    include_transactions=include_transactions
                )
                
                data = {
                    'summary': {
                        'income': income,
                        'expenses': abs(expenses),
                        'balance': income + expenses
                    },
                    'transactions': transactions[:100]
                }
                
                self.exporter.render_export_button(config, data)


# Instance globale
pdf_exporter = PDFExporter()
