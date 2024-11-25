import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

class ExportManager:
    def __init__(self, export_dir='exports'):
        self.export_dir = export_dir
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def export_to_excel(self, clients_df, factures_df):
        """Exporte les données vers un fichier Excel"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'export_recouvrement_{timestamp}.xlsx'
        filepath = os.path.join(self.export_dir, filename)

        # Création du fichier Excel avec plusieurs feuilles
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Export des clients
            clients_df.to_excel(writer, sheet_name='Clients', index=False)
            
            # Export des factures
            factures_df.to_excel(writer, sheet_name='Factures', index=False)
            
            # Création d'une feuille de synthèse
            summary_data = {
                'Métrique': [
                    'Nombre total de clients',
                    'Nombre total de factures',
                    'Montant total facturé',
                    'Montant total payé',
                    'Montant total en attente',
                    'Montant total en retard',
                    'Taux de recouvrement'
                ],
                'Valeur': [
                    len(clients_df),
                    len(factures_df),
                    factures_df['montant'].sum(),
                    factures_df[factures_df['statut'] == 'Payée']['montant'].sum(),
                    factures_df[factures_df['statut'] == 'En attente']['montant'].sum(),
                    factures_df[factures_df['statut'] == 'En retard']['montant'].sum(),
                    f"{(factures_df[factures_df['statut'] == 'Payée']['montant'].sum() / factures_df['montant'].sum() * 100):.2f}%"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Synthèse', index=False)

        return filepath

    def export_to_pdf(self, clients_df, factures_df):
        """Exporte les données vers un fichier PDF"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'export_recouvrement_{timestamp}.pdf'
        filepath = os.path.join(self.export_dir, filename)

        pdf = FPDF()
        pdf.add_page()

        # Configuration de la police
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)

        # Titre
        pdf.set_font('DejaVu', '', 16)
        pdf.cell(0, 10, 'Rapport de Recouvrement', 0, 1, 'C')
        pdf.ln(10)

        # Synthèse
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Synthèse', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 12)
        
        summary_data = [
            ['Nombre total de clients', str(len(clients_df))],
            ['Nombre total de factures', str(len(factures_df))],
            ['Montant total facturé', f"{factures_df['montant'].sum():.2f} €"],
            ['Montant total payé', f"{factures_df[factures_df['statut'] == 'Payée']['montant'].sum():.2f} €"],
            ['Montant en attente', f"{factures_df[factures_df['statut'] == 'En attente']['montant'].sum():.2f} €"],
            ['Montant en retard', f"{factures_df[factures_df['statut'] == 'En retard']['montant'].sum():.2f} €"],
            ['Taux de recouvrement', f"{(factures_df[factures_df['statut'] == 'Payée']['montant'].sum() / factures_df['montant'].sum() * 100):.2f}%"]
        ]

        for item in summary_data:
            pdf.cell(100, 10, item[0], 0, 0)
            pdf.cell(0, 10, item[1], 0, 1)

        pdf.ln(10)

        # Top 5 des clients avec le plus de factures en retard
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Top 5 des clients en retard de paiement', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 12)

        retard_par_client = factures_df[factures_df['statut'] == 'En retard'].groupby('client_id').agg({
            'montant': 'sum'
        }).sort_values('montant', ascending=False).head()

        if not retard_par_client.empty:
            for idx, row in retard_par_client.iterrows():
                client_nom = clients_df[clients_df['id'] == idx]['nom'].iloc[0]
                pdf.cell(100, 10, client_nom, 0, 0)
                pdf.cell(0, 10, f"{row['montant']:.2f} €", 0, 1)

        pdf.output(filepath)
        return filepath
