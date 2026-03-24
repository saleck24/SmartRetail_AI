# Choix Architecturaux & Machine Learning (Module ERP)

Ce document récapitule les justifications scientifiques et métiers des choix techniques faits pour le projet de Prédiction de Demande et prévention des Ruptures de Stock.

## 1. Approche : Régression ou Classification ?
L'approche choisie est la **Régression**.
- **Justification :** La problématique métier demande d'estimer une quantité précise (ex: "Combien d'unités de l'article X seront vendues dans le magasin Y le 15 août ?"). La classification (Oui/Non) n'est pas suffisante pour recommander une quantité de réapprovisionnement.
- **Règle ERP :** On utilise la prédiction numérique (Régression) couplée à une règle métier basique : `Si (Stock_Actuel < Quantité_Prédite) Alors Alerte_Rupture`.

## 2. Modèles d'IA :  Le Rôle du Baseline et du XGBoost
La validation du projet repose sur la comparaison de deux algorithmes :

### Le Baseline (ex: Régression Linéaire)
- **C'est quoi ?** Un modèle mathématique très simple qui tente de tracer une ligne droite dans les données historiques.
- **Son rôle :** Servir de "mètre étalon" (point de référence). Il nous donne l'erreur de base "minimale syndicale" à battre pour prouver l'intérêt d'une IA complexe.

### Le Modèle Avancé (XGBoost)
- **C'est quoi ?** Un algorithme ensembliste puissant (Extreme Gradient Boosting) qui crée des milliers de petits arbres de décision successifs corrigeant chacun les erreurs du précédent. Il excelle pour capter les relations non-linéaires (ex: "S'il fait chaud ET qu'on est dimanche ET que c'est un magasin balnéaire -> fortes ventes").
- **Son rôle :** C'est le "vrai" cerveau de l'ERP. C'est lui qui fera les prédictions en production.
- **Le Pitch (Argumentaire) :** "En comparant mon Baseline (qui se trompe de 25 unités) avec mon XGBoost (qui ne se trompe que de 10 unités), je prouve que mon IA est utile et fait gagner de l'argent (moins d'invendus / moins de ruptures)."

## 3. Évaluation : Les Fonctions de Coût (Métriques)
Pour évaluer si le XGBoost est performant, nous utiliserons 3 métriques d'erreur classiques en régression :

1. **MAE (Mean Absolute Error - L'Erreur Absolue Moyenne) :**
   - **Définition :** Moyenne de l'écart absolu entre la vraie vente et la prédiction.
   - **Pourquoi ?** C'est la métrique la plus compréhensible par le métier. (ex: Une MAE de 5 signifie qu'on se trompe d'environ 5 produits par jour).

2. **RMSE (Root Mean Squared Error - L'Erreur Quadratique Moyenne) :**
   - **Définition :** La racine de la moyenne des erreurs au carré.
   - **Pourquoi ?** Mettre l'erreur au carré "punit" très lourdement les pires prédictions. C'est crucial pour un ERP : une petite erreur tous les jours n'est pas grave, mais une erreur gigantesque de -500 produits un seul jour va causer une rupture de stock dramatique. La RMSE garantit qu'on évite ces "trous d'air".

3. **MAPE (Mean Absolute Percentage Error - Erreur Moyenne en Pourcentage) :**
   - **Définition :** L'erreur exprimée en pourcentage par rapport au volume total vendu.
   - **Pourquoi ?** Se tromper de 5 produits sur un "Top-Vendeur" à 1000/jour c'est bénin (0,5% d'erreur). Se tromper de 5 produits sur un "Flop-Vendeur" à 10/jour, c'est grave (50% d'erreur). Le MAPE permet d'évaluer la fiabilité de l'IA de manière équitable sur l'ensemble du catalogue produit.

### 4. Performance sur Dataset Réel (Favorita - Données 2017)
Lors de l'entraînement sur 2 millions de lignes (échantillon final de 2017) du dataset **Corporatión Favorita**, incluant les **jours fériés**, nous avons obtenu :
- **MAE (Erreur Moyenne) :** Environ **7.60** unités. La précision s'est améliorée grâce à l'intégration des jours fériés et de la saisonnalité fine.
- **RMSE (Root Mean Squared Error) :** **43.95**. Ce score reflète la forte variabilité des ventes en 2017 par rapport aux années précédentes.
- **MAPE (Erreur en Pourcentage) :** **212.48%**. Amélioration notable par rapport à la version précédente (242%), montrant une meilleure robustesse sur les petits articles.

- **Pourquoi ce score ?** L'IA XGBoost capte les pics de vente liés aux cycles de paie (mi-mois et fin de mois) et aux événements locaux propres à une véritable chaîne de distribution.

## 5. Démonstration : Entraînement et Visualisation
Pour reproduire ces résultats et tester le système, suivez ces étapes dans un terminal à la racine du projet :

### A. Entraîner le Modèle (Optionnel si déjà fait)
Si vous souhaitez ré-entraîner l'IA sur les données historiques :
   ```bash
   venv\Scripts\python src/train_model.py
   ```

### B. Le Dashboard Analytique (Streamlit)
Visualiser les tendances et la saisonnalité :
   ```bash
   venv\Scripts\streamlit run src/dashboard.py
   ```

### C. Le Simulateur de Prévision (Gradio)
Tester des prédictions en temps réel :
   ```bash
   venv\Scripts\python src/predictor.py
   ```

## 6. Origine des Données (Dataset)
Le projet utilise désormais le dataset **Corporación Favorita Grocery Sales**, une référence mondiale pour la prévision de stock réelle.

- **Dataset :** [Corporación Favorita Grocery Sales Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting)
- **Pourquoi ce choix ?**
    - **Données Réelles :** Contrairement au dataset précédent, celui-ci provient d'une véritable chaîne de supermarchés nationale (Équateur).
    - **Richesse :** Il inclut 54 magasins, des dizaines de villes et des milliers de produits répartis par "Familles" (Alimentation, Ménage, etc.).
    - **Localisation :** La structure de ce dataset (Magasins, Produits, Villes) est identique à celle d'un distributeur en Mauritanie, ce qui prouve la viabilité du projet pour un usage local futur.
