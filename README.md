# ERP IA : Prédiction de Demande et Stock (Module ML)

Ce projet implémente un module ERP Intelligent capable de prédire la demande future des produits, d’estimer le risque de rupture de stock, et de recommander les quantités optimales de réapprovisionnement.

## Démarrage Rapide

### 1. Livrable Semaine 1 (Exploration des Données - EDA)

Le livrable de la Semaine 1 se trouve dans le fichier `notebooks/01_EDA.ipynb`.

**Que contient ce Notebook ?**
- L'importation du dataset `train.csv`.
- Le nettoyage des données et vérification des valeurs manquantes.
- Une analyse des tendances temporelles et de la saisonnalité.
- Un affichage des volumes de vente moyens par produit (les top-sellers et low-sellers).
- Une interprétation scientifique finale.

### 2. Livrables Phase 2 & 3 (Modélisation & Prototypage)

Le modèle d'Intelligence Artificielle (XGBoost) a été entraîné et sauvegardé. Deux interfaces graphiques ont été développées pour démontrer la précision et l'utilité du modèle ERP.

**Pour lancer le Dashboard Analytique (Streamlit) :**
Ce tableau de bord permet de visualiser les historiques de ventes filtrés par Magasin et par Produit.
```bash
# Dans un terminal à la racine du projet
venv\Scripts\python -m pip install streamlit gradio plotly
venv\Scripts\streamlit run src/dashboard.py
```

**Pour lancer le Simulateur de Prévision (Gradio) :**
Cette interface permet d'interroger le modèle prédictif pour générer des recommandations de réapprovisionnement.
```bash
# Dans un terminal à la racine du projet
venv\Scripts\python src/predictor.py
```
*(Cliquez ensuite sur le lien HTTP Local affiché dans la console)*

## 🏢 Architecture du Projet

Voici l'organisation du dépôt pour comprendre le rôle de chaque dossier et fichier :

```text
erp_ai_stock_prediction/
├── data/                   # Données brutes (train.csv, test.csv)
├── models/                 # Modèles IA entraînés et sauvegardés (.pkl)
├── notebooks/              # Travaux de recherche (EDA, exploration)
├── src/                    # Code source de l'application
│   ├── dashboard.py        # Interface de visualisation (Streamlit)
│   ├── predictor.py        # Interface de prédiction (Gradio)
│   └── train_model.py     # Script d'entraînement de l'IA
├── IA_Justifications.md    # Documentation scientifique et choix techniques
├── requirements.txt        # Liste des dépendances Python
└── README.md               # Documentation générale (ce fichier)
```

### 📂 Rôle des Dossiers
- **`data/`** : Contient les données historiques de ventes. C'est le carburant de l'IA.
- **`models/`** : Stocke le "cerveau" de l'IA (`xgboost_stock_predictor.pkl`). Ce fichier est généré par le script d'entraînement.
- **`notebooks/`** : Contient les analyses préliminaires (Semaine 1) pour valider la qualité des données avant de coder.
- **`src/`** : Regroupe toute la logique métier et les interfaces utilisateurs.

### 📄 Fichiers Clés
- **`train_model.py`** : C'est ici que la magie opère. Il lit les données, entraîne deux modèles (Baseline et XGBoost), compare leurs performances et sauvegarde le meilleur.
- **`dashboard.py`** : Fournit une vision globale et analytique des stocks pour les gestionnaires.
- **`predictor.py`** : L'outil opérationnel qui utilise l'IA pour conseiller le réapprovisionnement au jour le jour.
- **`IA_Justifications.md`** : Explique le **"Pourquoi"** des choix techniques (XGBoost, MAE, RMSE) pour justifier la démarche scientifique.
