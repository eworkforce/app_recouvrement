from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import plotly.express as px
import plotly.utils
import json
from datetime import datetime, timedelta
import os
import re
from apscheduler.schedulers.background import BackgroundScheduler
from export_manager import ExportManager

app = Flask(__name__)
app.root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration pour le stockage des données
DATA_DIR = os.path.join(app.root_path, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def init_csv():
    clients_path = os.path.join(DATA_DIR, 'clients.csv')
    factures_path = os.path.join(DATA_DIR, 'factures.csv')
    
    if not os.path.exists(clients_path):
        pd.DataFrame(columns=['id', 'nom', 'email', 'telephone']).to_csv(clients_path, index=False)
    if not os.path.exists(factures_path):
        pd.DataFrame(columns=['id', 'numero', 'client_id', 'montant', 'date_emission', 'date_echeance', 'statut']).to_csv(factures_path, index=False)

init_csv()

# Importer toutes les routes et fonctions de l'application principale
from app import calculate_statistics, validate_client_data, validate_facture_data
from app import index, clients, factures, update_facture_status, import_data
from app import get_latest_exports, download_export, get_export_config, update_export_config

# Point d'entrée pour Vercel
app.add_url_rule('/', 'index', index)
app.add_url_rule('/clients', 'clients', clients, methods=['GET', 'POST'])
app.add_url_rule('/factures', 'factures', factures, methods=['GET', 'POST'])
app.add_url_rule('/factures/<int:facture_id>/status', 'update_facture_status', update_facture_status, methods=['PUT'])
app.add_url_rule('/import/<type_data>', 'import_data', import_data, methods=['POST'])
app.add_url_rule('/exports', 'get_latest_exports', get_latest_exports)
app.add_url_rule('/exports/download/<path:filename>', 'download_export', download_export)
app.add_url_rule('/export-config', 'get_export_config', get_export_config)
app.add_url_rule('/export-config/<export_type>', 'update_export_config', update_export_config, methods=['PUT'])
