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
scheduler = BackgroundScheduler()
export_manager = ExportManager()

# Création des fichiers CSV s'ils n'existent pas
if not os.path.exists('data'):
    os.makedirs('data')

def init_csv():
    if not os.path.exists('data/clients.csv'):
        pd.DataFrame(columns=['id', 'nom', 'email', 'telephone']).to_csv('data/clients.csv', index=False)
    if not os.path.exists('data/factures.csv'):
        pd.DataFrame(columns=['id', 'numero', 'client_id', 'montant', 'date_emission', 'date_echeance', 'statut']).to_csv('data/factures.csv', index=False)

init_csv()

def calculate_statistics(factures_df):
    stats = {
        'total_factures': len(factures_df),
        'montant_total': factures_df['montant'].sum(),
        'montant_impaye': factures_df[factures_df['statut'].isin(['En attente', 'En retard'])]['montant'].sum(),
        'nb_retard': len(factures_df[factures_df['statut'] == 'En retard']),
        'montant_retard': factures_df[factures_df['statut'] == 'En retard']['montant'].sum(),
        'taux_recouvrement': (factures_df[factures_df['statut'] == 'Payée']['montant'].sum() / 
                            factures_df['montant'].sum() * 100) if len(factures_df) > 0 else 0
    }
    return stats

def validate_client_data(df):
    """Valide le format des données clients"""
    errors = []
    
    # Vérification des colonnes requises
    required_columns = {'nom', 'email', 'telephone'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        errors.append(f"Colonnes manquantes : {', '.join(missing_columns)}")
        return False, errors

    # Validation des données
    for index, row in df.iterrows():
        row_num = index + 2  # +2 car l'index commence à 0 et on skip l'en-tête
        
        # Validation du nom
        if pd.isna(row['nom']) or str(row['nom']).strip() == '':
            errors.append(f"Ligne {row_num}: Le nom est requis")
        
        # Validation de l'email
        if pd.isna(row['email']) or not re.match(r"[^@]+@[^@]+\.[^@]+", str(row['email'])):
            errors.append(f"Ligne {row_num}: Email invalide")
        
        # Validation du téléphone (optionnel mais doit être valide si présent)
        if not pd.isna(row['telephone']):
            if not str(row['telephone']).replace('+', '').replace(' ', '').isdigit():
                errors.append(f"Ligne {row_num}: Numéro de téléphone invalide")
    
    return len(errors) == 0, errors

def validate_facture_data(df):
    """Valide le format des données factures"""
    errors = []
    
    # Vérification des colonnes requises
    required_columns = {'numero', 'client_id', 'montant', 'date_emission', 'date_echeance'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        errors.append(f"Colonnes manquantes : {', '.join(missing_columns)}")
        return False, errors

    # Lecture des clients existants pour la validation des client_id
    clients_df = pd.read_csv('data/clients.csv')
    valid_client_ids = set(clients_df['id'].astype(str))

    # Validation des données
    for index, row in df.iterrows():
        row_num = index + 2
        
        # Validation du numéro de facture
        if pd.isna(row['numero']) or str(row['numero']).strip() == '':
            errors.append(f"Ligne {row_num}: Le numéro de facture est requis")
        
        # Validation du client_id
        if str(row['client_id']) not in valid_client_ids:
            errors.append(f"Ligne {row_num}: Client ID invalide ou inexistant")
        
        # Validation du montant
        try:
            montant = float(row['montant'])
            if montant <= 0:
                errors.append(f"Ligne {row_num}: Le montant doit être positif")
        except (ValueError, TypeError):
            errors.append(f"Ligne {row_num}: Montant invalide")
        
        # Validation des dates
        try:
            date_emission = pd.to_datetime(row['date_emission'])
            date_echeance = pd.to_datetime(row['date_echeance'])
            
            if date_echeance < date_emission:
                errors.append(f"Ligne {row_num}: La date d'échéance ne peut pas être antérieure à la date d'émission")
        except:
            errors.append(f"Ligne {row_num}: Format de date invalide")
    
    return len(errors) == 0, errors

def generate_daily_exports():
    """Génère les exports quotidiens"""
    clients_df = pd.read_csv('data/clients.csv')
    factures_df = pd.read_csv('data/factures.csv')
    
    # Export Excel et PDF
    export_manager.export_to_excel(clients_df, factures_df)
    export_manager.export_to_pdf(clients_df, factures_df)

def generate_weekly_exports():
    """Génère les exports hebdomadaires"""
    generate_daily_exports()

def generate_monthly_exports():
    """Génère les exports mensuels"""
    generate_daily_exports()

def load_export_config():
    """Charge la configuration des exports depuis le fichier JSON"""
    config_file = 'data/export_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def save_export_config(config):
    """Sauvegarde la configuration des exports dans le fichier JSON"""
    with open('data/export_config.json', 'w') as f:
        json.dump(config, f, indent=4)

def reschedule_exports():
    """Replanifie les exports selon la nouvelle configuration"""
    config = load_export_config()
    if not config:
        return

    # Supprimer les jobs existants
    scheduler.remove_all_jobs()

    # Export quotidien
    if config['daily']['enabled']:
        scheduler.add_job(
            func=generate_daily_exports,
            trigger='cron',
            hour=config['daily']['hour'],
            minute=config['daily']['minute'],
            id='daily_export'
        )

    # Export hebdomadaire
    if config['weekly']['enabled']:
        scheduler.add_job(
            func=generate_weekly_exports,
            trigger='cron',
            day_of_week=config['weekly']['day'],
            hour=config['weekly']['hour'],
            minute=config['weekly']['minute'],
            id='weekly_export'
        )

    # Export mensuel
    if config['monthly']['enabled']:
        scheduler.add_job(
            func=generate_monthly_exports,
            trigger='cron',
            day=config['monthly']['day'],
            hour=config['monthly']['hour'],
            minute=config['monthly']['minute'],
            id='monthly_export'
        )

@app.route('/')
def index():
    # Lecture des données
    factures_df = pd.read_csv('data/factures.csv')
    clients_df = pd.read_csv('data/clients.csv')
    
    # Conversion des dates
    factures_df['date_emission'] = pd.to_datetime(factures_df['date_emission'])
    factures_df['date_echeance'] = pd.to_datetime(factures_df['date_echeance'])
    
    # Filtres depuis les paramètres URL
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    client_id = request.args.get('client_id')
    statut = request.args.get('statut')
    
    # Application des filtres
    if start_date:
        factures_df = factures_df[factures_df['date_emission'] >= start_date]
    if end_date:
        factures_df = factures_df[factures_df['date_emission'] <= end_date]
    if client_id:
        factures_df = factures_df[factures_df['client_id'] == int(client_id)]
    if statut:
        factures_df = factures_df[factures_df['statut'] == statut]
    
    # Calcul des statistiques
    stats = calculate_statistics(factures_df)
    
    # Graphiques
    if not factures_df.empty:
        # Graphique des montants par statut
        fig_status = px.pie(factures_df, values='montant', names='statut', 
                          title='Répartition des montants par statut',
                          color_discrete_map={
                              'Payée': '#2E7D32',
                              'En attente': '#FFA000',
                              'En retard': '#D32F2F'
                          })
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        
        # Graphique d'évolution temporelle
        monthly_amounts = factures_df.groupby([
            factures_df['date_emission'].dt.strftime('%Y-%m'),
            'statut'
        ])['montant'].sum().reset_index()
        
        fig_evolution = px.line(monthly_amounts, 
                              x='date_emission', 
                              y='montant',
                              color='statut',
                              title='Évolution des montants facturés',
                              color_discrete_map={
                                  'Payée': '#2E7D32',
                                  'En attente': '#FFA000',
                                  'En retard': '#D32F2F'
                              })
        
        # Conversion des graphiques en JSON pour le frontend
        graphJSON = {
            'status': json.dumps(fig_status, cls=plotly.utils.PlotlyJSONEncoder),
            'evolution': json.dumps(fig_evolution, cls=plotly.utils.PlotlyJSONEncoder)
        }
    else:
        graphJSON = None

    return render_template('index.html', 
                         graphJSON=graphJSON, 
                         stats=stats,
                         clients=clients_df.to_dict('records'))

@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST':
        data = request.json
        clients_df = pd.read_csv('data/clients.csv')
        
        # Génération d'un nouvel ID
        new_id = 1 if clients_df.empty else clients_df['id'].max() + 1
        
        # Ajout du nouveau client
        new_client = pd.DataFrame([{
            'id': new_id,
            'nom': data['nom'],
            'email': data['email'],
            'telephone': data['telephone']
        }])
        
        clients_df = pd.concat([clients_df, new_client], ignore_index=True)
        clients_df.to_csv('data/clients.csv', index=False)
        
        return jsonify({'message': 'Client ajouté avec succès', 'id': int(new_id)})
    
    # GET request
    clients_df = pd.read_csv('data/clients.csv')
    return jsonify(clients_df.to_dict('records'))

@app.route('/factures', methods=['GET', 'POST'])
def factures():
    if request.method == 'POST':
        data = request.json
        factures_df = pd.read_csv('data/factures.csv')
        
        # Génération d'un nouvel ID
        new_id = 1 if factures_df.empty else factures_df['id'].max() + 1
        
        # Ajout de la nouvelle facture
        new_facture = pd.DataFrame([{
            'id': new_id,
            'numero': data['numero'],
            'client_id': data['client_id'],
            'montant': data['montant'],
            'date_emission': data['date_emission'],
            'date_echeance': data['date_echeance'],
            'statut': 'En attente'
        }])
        
        factures_df = pd.concat([factures_df, new_facture], ignore_index=True)
        factures_df.to_csv('data/factures.csv', index=False)
        
        return jsonify({'message': 'Facture ajoutée avec succès', 'id': int(new_id)})
    
    # GET request
    factures_df = pd.read_csv('data/factures.csv')
    clients_df = pd.read_csv('data/clients.csv')
    
    # Joindre les informations du client
    merged_df = factures_df.merge(clients_df[['id', 'nom']], 
                                left_on='client_id', 
                                right_on='id', 
                                suffixes=('', '_client'))
    
    result = merged_df.to_dict('records')
    for r in result:
        r['client_nom'] = r['nom']
        del r['nom']
        
    return jsonify(result)

@app.route('/factures/<int:facture_id>/status', methods=['PUT'])
def update_facture_status(facture_id):
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['En attente', 'Payée', 'En retard']:
        return jsonify({'error': 'Statut invalide'}), 400
    
    factures_df = pd.read_csv('data/factures.csv')
    if facture_id not in factures_df['id'].values:
        return jsonify({'error': 'Facture non trouvée'}), 404
    
    factures_df.loc[factures_df['id'] == facture_id, 'statut'] = new_status
    factures_df.to_csv('data/factures.csv', index=False)
    
    return jsonify({'message': 'Statut mis à jour avec succès'})

@app.route('/import/<type_data>', methods=['POST'])
def import_data(type_data):
    if 'file' not in request.files:
        return jsonify({'success': False, 'errors': ['Aucun fichier fourni']}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'errors': ['Aucun fichier sélectionné']}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'errors': ['Format de fichier non supporté. Utilisez un fichier CSV.']}), 400
    
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(file, dtype=str)
        
        # Nettoyage des noms de colonnes
        df.columns = df.columns.str.lower().str.strip()
        
        # Validation selon le type de données
        if type_data == 'clients':
            is_valid, errors = validate_client_data(df)
        elif type_data == 'factures':
            is_valid, errors = validate_facture_data(df)
        else:
            return jsonify({'success': False, 'errors': ['Type de données non supporté']}), 400
        
        if not is_valid:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Traitement des données valides
        existing_df = pd.read_csv(f'data/{type_data}.csv')
        
        if type_data == 'clients':
            # Génération de nouveaux IDs pour les clients
            start_id = existing_df['id'].max() + 1 if not existing_df.empty else 1
            df['id'] = range(start_id, start_id + len(df))
        else:  # factures
            # Génération de nouveaux IDs pour les factures
            start_id = existing_df['id'].max() + 1 if not existing_df.empty else 1
            df['id'] = range(start_id, start_id + len(df))
            df['statut'] = 'En attente'  # Statut par défaut
        
        # Ajout des nouvelles données
        result_df = pd.concat([existing_df, df], ignore_index=True)
        result_df.to_csv(f'data/{type_data}.csv', index=False)
        
        return jsonify({
            'success': True,
            'message': f'{len(df)} {type_data} importé(s) avec succès',
            'preview': df.head().to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'errors': [f'Erreur lors de l\'importation: {str(e)}']}), 500

@app.route('/exports/latest', methods=['GET'])
def get_latest_exports():
    """Récupère les derniers fichiers exportés"""
    export_dir = 'exports'
    if not os.path.exists(export_dir):
        return jsonify({'error': 'Aucun export disponible'}), 404
    
    files = []
    for f in os.listdir(export_dir):
        if f.startswith('export_recouvrement_'):
            path = os.path.join(export_dir, f)
            files.append({
                'name': f,
                'date': datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S'),
                'size': os.path.getsize(path)
            })
    
    # Trier par date de modification (plus récent en premier)
    files.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(files)

@app.route('/exports/download/<filename>')
def download_export(filename):
    """Télécharge un fichier d'export"""
    try:
        return send_file(
            os.path.join('exports', filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/export-config', methods=['GET'])
def get_export_config():
    """Récupère la configuration actuelle des exports"""
    config = load_export_config()
    if config:
        return jsonify(config)
    return jsonify({'error': 'Configuration non trouvée'}), 404

@app.route('/export-config/<export_type>', methods=['POST'])
def update_export_config(export_type):
    """Met à jour la configuration d'un type d'export"""
    if export_type not in ['daily', 'weekly', 'monthly']:
        return jsonify({'success': False, 'error': 'Type d\'export invalide'}), 400

    config = load_export_config()
    if not config:
        return jsonify({'success': False, 'error': 'Configuration non trouvée'}), 404

    data = request.json
    config[export_type].update(data)
    save_export_config(config)
    
    # Replanifier les exports
    reschedule_exports()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # Charger la configuration initiale des exports
    config = load_export_config()
    if config:
        reschedule_exports()
    
    # Démarrer le planificateur
    scheduler.start()
    
    app.run(debug=True)
