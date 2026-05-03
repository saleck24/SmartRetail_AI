# 🛒 SmartRetail AI : Optimisation Intelligente des Stocks
**Systèmes d'Information (IA et Business Intelligence)**

Le projet **SmartRetail AI** est une solution de gestion de chaîne logistique assistée par Intelligence Artificielle. Il transforme un ERP traditionnel en un système proactif capable d'anticiper la demande future, d'optimiser les stocks et de prévenir les ruptures grâce à un moteur prédictif **LightGBM** entraîné sur le Big Data (125M+ lignes).

---

## 📊 Dataset : Corporación Favorita (Kaggle)
Le projet s'appuie sur le dataset de référence de la chaîne équatorienne **Corporación Favorita**.
- **Volume :** Plus de 125 millions d'enregistrements.
- **Entraînement :** Réalisé sur le dataset intégral via un Cloud Privé (Kaggle GPU) pour une précision statistique maximale.
- **Lien :** [Favorita Grocery Sales Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting)

---

## 🚀 Fonctionnalités ERP (4 Modules)
L'interface **React (Vite)** premium propose quatre modules métiers :
1.  **Dashboard :** Surveillance en temps réel des KPIs, ventes et alertes critiques.
2.  **Gestion des Stocks :** Suivi des niveaux de couverture et alertes intelligentes de rupture.
3.  **Prédictions IA :** Moteur d'inférence LightGBM pour simuler la demande et recommander des commandes.
4.  **Analytics (Benchmark) :** Visualisation scientifique du benchmark multi-modèles (14 métriques).

---

## 🛠️ Installation et Utilisation

### 1. Backend (FastAPI)
L'API sécurisée expose le modèle LightGBM et les endpoints métier.
```bash
# Installation des dépendances
pip install -r requirements.txt
# Lancement de l'API (Port 8000)
uvicorn api.main:app --reload
```
*Documentation Swagger disponible sur : `http://localhost:8000/docs`*

### 2. Frontend (React + Vite)
L'interface utilisateur moderne et réactive.
```bash
cd frontend
npm install
npm run dev
```
*Interface accessible sur : `http://localhost:5173`*

---

## 🔬 Benchmark Scientifique
Nous avons mené un benchmark exhaustif comparant 4 architectures sur des métriques d'erreur (MAE, RMSE, SMAPE) et opérationnelles (Stockout Rate, Overstock Rate).

| Modèle | R² | SMAPE (%) | Taux Rupture | Statut |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (Linear Reg)** | 0.42 | 68.21% | 52.1% | Référence |
| **XGBoost** | 0.51 | 54.80% | 43.2% | Performant |
| **LightGBM** | **0.59** | **48.32%** | **38.4%** | **Choisi ✓** |
| **LSTM** | 0.38 | 61.45% | 49.8% | Recherche |

---

## 🏢 Architecture du Projet
```text
erp_ai_stock_prediction/
├── frontend/               # Interface React (Vite, Recharts, Framer Motion)
├── api/                    # Backend FastAPI (Sécurisé via X-API-Key)
├── notebooks/              # Scripts d'entraînement Kaggle et EDA
├── models/                 # Modèles LightGBM sauvegardés (.pkl)
├── rapport.md              # Rapport de soutenance (Master SI)
├── IA_Justifications.md    # Justifications scientifiques détaillées
└── docker-compose.yml      # Orchestration Microservices
```

---

## 👨‍🎓 Contexte Académique
Projet réalisé en Master SI. Il démontre l'industrialisation d'un modèle de Machine Learning (LightGBM) au sein d'une architecture logicielle moderne (React/FastAPI) pour résoudre une problématique critique de la grande distribution.
