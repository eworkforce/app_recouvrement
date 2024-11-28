# EDNA Recouvrement - v0.1

Application de gestion des recouvrements et suivi des factures clients.

## Fonctionnalités

- Tableau de bord interactif avec statistiques en temps réel
- Gestion des clients
- Gestion des factures
- Suivi des paiements
- Visualisation des données avec graphiques
- Export des données

## Prérequis

- Python 3.8+
- Les dépendances listées dans `requirements.txt`

## Installation

1. Cloner le repository
```bash
git clone https://github.com/votre-repo/edna-recouvrement.git
```

2. Installer les dépendances
```bash
pip install -r requirements.txt
```

3. Lancer l'application
```bash
python app.py
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

## Technologies utilisées

- Flask
- Bootstrap 5
- Plotly
- Pandas
- SQLite (à venir)

## Développement

Version actuelle : 0.1
Voir `VERSION.md` pour l'historique des versions.

## Contribution

Pour contribuer au projet :
1. Forker le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT.
