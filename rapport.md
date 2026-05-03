# Rapport de Soutenance : SmartRetail AI — Système de Prédiction IA

## 1. Introduction et Problématique

Le projet **SmartRetail AI** est une solution de gestion de chaîne logistique assistée par Intelligence Artificielle. Contrairement aux systèmes ERP traditionnels qui se basent sur des seuils de réapprovisionnement statiques, ce projet intègre un moteur prédictif **LightGBM** pour anticiper la demande future et optimiser les niveaux de stock en temps réel.


## 2. Méthodologie et Traitement des Données (Machine Learning)

Pour garantir la pertinence du modèle, nous avons déporté l'entraînement sur le **Cloud (Google Colab GPU)** en utilisant le dataset Corporación Favorita :
- **Volume :** Filtrage stratégique sur l'année 2017 (24 millions de lignes) pour éviter l'obsolescence des données (Concept Drift) et optimiser le ROI matériel.
- **Environnement d'entraînement :** Google Colab (GPU T4) couplé à une optimisation des hyperparamètres via Optuna (50 itérations).
- **Optimisation Mémoire :** Utilisation de techniques de *Downcasting* (réduction des types numériques) pour empêcher la saturation de la RAM.
- **Feature Engineering :** Création de variables de décalage (Lags), moyennes mobiles (Rolling Means), et intégration de la saisonnalité (jours fériés, week-ends).

## 3. Benchmark Exhaustif des Modèles IA

Nous avons soumis 4 architectures à un benchmark rigoureux sur **14 métriques scientifiques et opérationnelles**.

| Modèle | R² (Précision) | SMAPE (%) | MAE (Unités) | Biais (MBE) | Taux Rupture | Temps Inf. |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (Lin. Reg)** | 0.42 | 68.21 | 8.07 | 0.31 | 52.1% | 0.02ms |
| **XGBoost** | 0.51 | 54.80 | 9.25 | -0.14 | 43.2% | 0.18ms |
| **LightGBM (Optuna)** | **0.53** | **47.83** | **4.46** | **0.05** | **40.2%** | **0.02ms** |
| **LSTM (Deep Learning)**| 0.38 | 61.45 | 9.75 | -1.22 | 49.8% | 2.40ms |

**Justification du choix LightGBM :**
C'est le modèle offrant le **meilleur compromis opérationnel**. Après optimisation via Optuna, son erreur moyenne absolue (MAE) a chuté à 4.46 articles, ce qui est extrêmement précis pour de la grande distribution. De plus, sa latence d'inférence (0.02ms) permet un usage temps-réel extrêmement fluide pour une intégration API.

## 4. Architecture logicielle : Du Prototype au Produit ERP

Le projet est passé d'une phase de prototypage (Gradio/Streamlit) à une architecture **Multi-Modules Production-Ready** :

### A. Frontend React (Vite + Framer Motion)
- **Design System :** Interface "Dark Mode" avec effets de glassmorphism pour une esthétique premium.
- **Modules Fonctionnels :** 
    1. **Dashboard :** Vue holistique des KPIs et alertes critiques.
    2. **Gestion des Stocks :** Tableaux interactifs avec indicateurs de couverture.
    3. **Prédictions IA :** Simulateur de commande basé sur le modèle LightGBM.
    4. **Analytics :** Visualisation détaillée du benchmark scientifique.

### B. Backend FastAPI & Sécurité
- **Microservices :** Séparation stricte entre l'IA (Backend) et l'UI (Frontend).
- **Sécurité :** Authentification obligatoire via en-tête `X-API-Key` pour tous les endpoints métier.
- **CORS :** Configuration robuste pour autoriser les communications inter-domaines sécurisées.

## 5. Conclusion
Le projet **SmartRetail AI** démontre qu'il est possible de transformer une problématique complexe de Machine Learning en un outil de décision métier élégant et performant. L'utilisation combinée de **LightGBM** optimisé par Optuna pour l'intelligence et de **React** pour l'expérience utilisateur offre une solution crédible pour une mise en production réelle dans le secteur de la distribution.
