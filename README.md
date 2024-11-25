# Application de Recouvrement - v0.1

Application web de gestion des recouvrements permettant de suivre les factures clients et de générer des exports automatiques.

## Fonctionnalités

- Tableau de bord avec visualisation des données
- Gestion des clients
- Gestion des factures
- Exports automatiques (quotidien, hebdomadaire, mensuel)

## Prérequis

- Python 3.8+
- Les dépendances listées dans `requirements.txt`

## Installation

1. Cloner le dépôt
2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

1. Démarrer l'application :
   ```bash
   python app.py
   ```
2. Ouvrir un navigateur et aller à `http://localhost:5000`

## Structure des données

Les données sont stockées dans des fichiers CSV dans le dossier `data/` :
- `clients.csv` : Liste des clients
- `factures.csv` : Liste des factures
- `export_config.json` : Configuration des exports automatiques

## Développement

Version actuelle : 0.1
Voir `VERSION.md` pour l'historique des versions.
