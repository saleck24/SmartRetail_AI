# 🛒 ERP Intelligent : Prédiction de Demande et Optimisation des Stocks
**Systèmes d'Information (IA et Business Intelligence)**

Ce projet implémente un module ERP Intelligent conçu pour automatiser les décisions de réapprovisionnement. En s'appuyant sur des données de ventes réelles, l'IA prédit la demande future, estime les risques de rupture et recommande les quantités optimales de commande.

---

## 📊 Dataset : Corporación Favorita (Kaggle)
Le projet utilise un jeu de données réel provenant de la chaîne équatorienne **Corporación Favorita** (données de 2013 à 2017).
- **Volume :** Plus de 125 millions d'enregistrements (échantillonnés pour ce prototype).
- **Richesse :** 54 magasins, des dizaines de villes et des milliers d'articles enrichis de métadonnées (`stores.csv`, `items.csv`, `holidays_events.csv`).
- **Lien :** [Favorita Grocery Sales Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting)

---

## 🚀 Fonctionnalités Clés
- **Modélisation Avancée (LightGBM) :** Notre modèle principal, choisi pour son excellence en rapidité et précision sur les données massives.
- **Étude Comparative :** Inclus une comparaison scientifique entre Linear Regression, XGBoost, LightGBM et LSTM.
- **Analyse de Saisonnalité :** Détection automatique des cycles hebdomadaires et mensuels.
- **Facteur Événementiel :** Intégration des **jours fériés** pour prévenir les ruptures lors des pics de consommation.
- **Interfaces Interactives :**
  - **Dashboard (Streamlit) :** Analyse historique et exploration des tendances.
  - **Predictor (Gradio) :** Outil opérationnel de prédiction en temps réel avec calendrier intégré.

---

## 🛠️ Installation et Utilisation

### Option A : Lancement Local (Développement & Démo Rapide)
*Utilisez cette méthode pour exécuter les interfaces en mode "monolithique", où les modèles sont chargés directement en mémoire.*

**1. Prérequis et Dépendances :**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**2. Lancement des modules :**
- **Analyse Exploratoire (EDA) :** Consulter `notebooks/01_EDA.ipynb`.
- **Entraînement :** `python dashboard/train_model.py` (pour comparer les 4 modèles).
- **Dashboard :** `streamlit run dashboard/dashboard.py` (Accessible sur `http://localhost:8501`)
- **Predictor :** `python dashboard/predictor.py` (Accessible sur `http://localhost:7860`)

### Option B : Lancement Microservices (Production & API)
*Utilisez cette méthode pour déployer l'architecture finale séparant l'API (FastAPI) des Front-ends (Gradio/Streamlit) via Docker.*

**1. Prérequis :** Docker et Docker Compose installés.
**2. Démarrage :**
```bash
docker-compose up --build
```
**3. Accès :**
- **API (Swagger) :** `http://localhost:8000/docs`
- **Dashboard :** `http://localhost:8501`
- **Predictor (Branché sur l'API) :** `http://localhost:7860`

---

## 🏢 Architecture du Projet
```text
erp_ai_stock_prediction/
├── api/                    # Backend FastAPI (Microservice IA)
├── data/                   # Fichiers sources (train.csv, metadata)
├── models/                 # Modèles IA sauvegardés (.pkl)
├── notebooks/              # Analyse exploratoire (EDA - Complétée)
├── dashboard/              # Code source (Dashboard Streamlit, Predictor Gradio, Train)
├── IA_Justifications.md    # Documentation scientifique et matrice de comparaison
├── docker-compose.yml      # Orchestration des microservices
├── Dockerfile.api          # Image Docker pour le backend FastAPI
├── Dockerfile.dashboard    # Image Docker pour les frontends (Streamlit/Gradio)
├── requirements.txt        # Liste des dépendances (incluant LightGBM, FastAPI, TF)
└── README.md               # Ce fichier
```

### 📄 Fichiers Clés
- **`dashboard/train_model.py`** : Moteur d'entraînement multi-modèles.
- **`dashboard/dashboard.py`** : Visualisation analytique pour les décideurs.
- **`dashboard/predictor.py`** : Outil terrain (Génère l'alerte rupture via LightGBM).
- **`IA_Justifications.md`** : Justification académique (Linear Reg vs XGBoost vs LightGBM vs LSTM).

---

## 👨‍🎓 Contexte Académique
Ce travail a été réalisé dans le cadre d'un Master 1 SI. Il démontre la capacité d'une Intelligence Artificielle à s'intégrer dans un processus métier classique (ERP) pour apporter une valeur ajoutée quantifiable (réduction des invendus et des ruptures).
