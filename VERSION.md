# EDNA Recouvrement - Historique des versions

## Version 0.1.2 - 2023-11-27

### Nouvelles Fonctionnalités
- Ajout de la suppression des clients et factures
- Ajout du statut "Annulée" pour les factures
- Amélioration de la gestion des statuts des factures

### Améliorations
- Interface utilisateur plus intuitive
- Meilleure gestion des erreurs
- Validation des données améliorée
- Rechargement optimisé des données (sans rechargement complet de la page)

### Corrections
- Correction du bouton "Nouvelle Facture"
- Correction de l'affichage des statuts dans le tableau des factures
- Correction du chargement de la liste des clients dans le formulaire

### Sécurité
- Validation des statuts côté serveur
- Protection contre la suppression des clients ayant des factures

## Version 0.1.1 - 2023-11-27

### Déploiement
- Application déployée avec succès sur Google Cloud Run
- Configuration de production optimisée pour le cloud
- Utilisation de gunicorn comme serveur WSGI

### Fonctionnalités
- Gestion des factures et des clients
- Génération de rapports PDF
- Tableaux de bord avec visualisations
- Export automatique des données
- Interface responsive avec Bootstrap 5

### Technologies
- Backend: Flask (Python)
- Frontend: Bootstrap 5, Plotly
- Serveur: Gunicorn
- Hébergement: Google Cloud Run

## Version 0.1 - 2024-01-25

Première version fonctionnelle de l'application de recouvrement avec les fonctionnalités suivantes :

### Fonctionnalités principales
- Tableau de bord avec graphiques de suivi
- Gestion des clients (ajout, liste)
- Gestion des factures (ajout, liste, mise à jour du statut)
- Système d'exports automatiques (quotidien, hebdomadaire, mensuel)

### Interface utilisateur
- Navigation par sidebar
- Interface responsive
- Graphiques interactifs
- Tableaux de données avec actions
- Modals pour l'ajout de données

### Technique
- Backend en Flask
- Frontend en Bootstrap 5
- Base de données CSV
- Graphiques avec Plotly
- Exports automatisés avec APScheduler
