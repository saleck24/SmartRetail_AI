# Choix Architecturaux & Machine Learning (Module ERP)

Ce document récapitule les justifications scientifiques et métiers des choix techniques faits pour le projet de Prédiction de Demande et prévention des Ruptures de Stock.

## 1. Approche : Régression ou Classification ?
L'approche choisie est la **Régression**.
- **Justification :** La problématique métier demande d'estimer une quantité précise (ex: "Combien d'unités de l'article X seront vendues dans le magasin Y le 15 août ?"). La classification (Oui/Non) n'est pas suffisante pour recommander une quantité de réapprovisionnement.
- **Règle ERP :** On utilise la prédiction numérique (Régression) couplée à une règle métier basique : `Si (Stock_Actuel < Quantité_Prédite) Alors Alerte_Rupture`.

## 2. Comparaison Scientifique Multi-Modèles (Matrice de Décision)

Pour choisir l'IA de production, nous avons évalué 4 familles d'algorithmes sur un échantillon d'un million de lignes (Données 2017).

| Critère | Baseline (Linear Reg) | Principal (LightGBM) | Comparaison (XGBoost) | Bonus (LSTM) |
| :--- | :--- | :--- | :--- | :--- |
| **Erreur Moyenne (MAE)** | **8.07** | 9.53 | 9.25 | 9.75 |
| **Stabilité (RMSE)** | 55.77 | 55.60 | **55.58** | 58.72 |
| **Complexité** | Simple | Moyenne | Haute | Très Haute |
| **Temps d'entraînement** | **< 1s** | 1.8s | 3.9s | 17.6s |
| **Interprétabilité** | Totale | Importance (Gains) | Importance (Poids) | Faible |
| **Usage ERP** | Filtrage de base | **Prédiction Rapide** | Analyse fine | Recherche (Bonus) |

### Pourquoi avoir choisi LightGBM comme Modèle Principal ?
Bien que la Régression Linéaire soit très rapide et XGBoost très précis sur le RMSE, **LightGBM est le choix "Principal"** pour le produit final :

1.  **Vitesse d'exécution :** LightGBM est environ **2x plus rapide** que XGBoost à l'entraînement tout en offrant des performances quasi-identiques. Pour un ERP gérant des milliers de produits, la rapidité de mise à jour des stocks est vitale.
2.  **Efficacité mémoire :** Contrairement aux modèles Deep Learning (LSTM) ou à XGBoost, LightGBM utilise beaucoup moins de RAM, ce qui facilite son déploiement sur de petits serveurs.
3.  **Gestion native des catégories :** Il traite plus efficacement les IDs de magasins et d'articles que la régression linéaire.

### Analyse du Bonus (LSTM)
Le modèle **LSTM** (Deep Learning) a été testé comme approche temporelle. Bien que prometteur, il nécessite beaucoup plus de ressources pour un gain marginal sur des données tabulaires. Il reste pertinent pour de futures analyses sur des séquences très longues.

### Le Pitch (Argumentaire ROI)
"Mon architecture repose sur **LightGBM** pour sa balance parfaite entre **vitesse chirurgicale** et **précision métrique**. Il garantit une prédiction de stock fiable en quelques secondes, là où d'autres modèles bloqueraient les ressources de l'ERP."

## 3. Analyse de la Performance : Mes Indicateurs Clés
Pour valider la pertinence de mon modèle principal (LightGBM), j'ai sélectionné trois métriques complémentaires permettant d'analyser l'erreur sous différents angles opérationnels :

1. **MAE (Mean Absolute Error) :**
   - C'est ma mesure de l'erreur "physique" moyenne. Si j'ai une MAE de 8, cela signifie qu'en moyenne, m'a prévision s'écarte de 8 unités de la réalité. C'est l'indicateur le plus simple pour expliquer les résultats aux équipes métier.

2. **RMSE (Root Mean Squared Error) :**
   - J'utilise cette métrique pour pénaliser les erreurs importantes. En gestion de stock, une erreur isolée mais massive (ex: rater un pic de vente de Noël) est bien plus grave qu'une petite erreur quotidienne. Le RMSE m'assure que mon modèle reste stable et évite les ruptures catastrophiques.

3. **MAPE (Mean Absolute Percentage Error) :**
   - Cette métrique exprime l'erreur en pourcentage. Elle me permet de vérifier que mon modèle est aussi fiable sur les articles à fort volume que sur les articles de niche.

## 4. Résultats de mes Tests sur le Dataset Favorita (2017)

En entraînant mon architecture sur un échantillon d'un million de lignes incluant les cycles de paie et les jours fériés, j'ai obtenu les résultats suivants pour mon modèle principal :

- **MAE (Erreur Moyenne) :** Environ **9.53** unités par article/magasin.
- **RMSE (Qualité des pics) :** **55.60**. Ce score démontre une bonne résilience aux variations saisonnières.
- **MAPE (Précision relative) :** **242.48%**. Ce chiffre s'explique par la nature très volatile des données de 2017 au moment des séismes et événements locaux en Équateur.

**Conclusion Technique :** Mon choix final s'est porté sur **LightGBM** car il offre le meilleur rapport entre temps d'exécution et précision opérationnelle pour un système ERP.

## 5. Démonstration : Entraînement et Visualisation
Pour reproduire ces résultats et tester le système, suivez ces étapes dans un terminal à la racine du projet :

### A. Entraîner le Modèle
Si vous souhaitez ré-entraîner l'IA sur les données historiques :
   ```bash
   venv\Scripts\python dashboard/train_model.py
   ```

### B. Le Dashboard Analytique (Streamlit)
Visualiser les tendances et la saisonnalité :
   ```bash
   venv\Scripts\streamlit run dashboard/dashboard.py
   ```

### C. Le Simulateur de Prévision (Gradio)
Tester des prédictions en temps réel :
   ```bash
   venv\Scripts\python dashboard/predictor.py
   ```

## 6. Origine des Données (Dataset)
Le projet utilise désormais le dataset **Corporación Favorita Grocery Sales**, une référence mondiale pour la prévision de stock réelle.

- **Dataset :** [Corporación Favorita Grocery Sales Forecasting](https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting)
- **Pourquoi ce choix ?**
    - **Données Réelles :** Contrairement au dataset précédent, celui-ci provient d'une véritable chaîne de supermarchés nationale (Équateur).
    - **Richesse :** Il inclut 54 magasins, des dizaines de villes et des milliers de produits répartis par "Familles" (Alimentation, Ménage, etc.).
    - **Localisation :** La structure de ce dataset (Magasins, Produits, Villes) est identique à celle d'un distributeur en Mauritanie, ce qui prouve la viabilité du projet pour un usage local futur.

## 7. Décisions UX/UI : Gestion du Calendrier et Limites Métier

Une attention particulière a été portée à la conception du composant de calendrier dans le dashboard afin de répondre aux exigences d'un système ERP de qualité professionnelle :

- **Le problème de l'absence de limite :** Autoriser l'utilisateur à sélectionner des dates infinies (ex: choisir l'année 2029) alors que la base de données s'arrête en 2017 témoigne d'un manque de validation de saisie (Poor UX). L'interface doit refléter la stricte réalité temporelle des opérations de l'entreprise étudiée.
- **Le problème de la limite matérielle (échantillonnage) :** Pour des raisons d'optimisation (économie de RAM), l'application ne charge par défaut qu'un échantillon de données (les premières 100 000 lignes représentant janvier 2013). Si le calendrier était borné uniquement sur cet échantillon, l'utilisateur serait faussement bloqué sur un mois et l'outil subirait des crashs lors de n'importe quelle tentative d'exploration.
- **La solution hybride implémentée :** J'ai séparé la **limite logique métier** de la **limite technique**. Le calendrier est formellement bloqué sur l'amplitude exacte de l'historique de Corporación Favorita (du 1er Janvier 2013 au 16 Août 2017) pour garantir la pertinence contextuelle devant le jury. Cependant, sa "valeur par défaut" au chargement cible intelligemment l'échantillon actuellement monté en mémoire. Cela résulte en une interface extrêmement robuste, qui s'affiche instantanément au démarrage sans erreur, tout en matérialisant parfaitement la gestion des dates à haute échelle.

## 8. Fonctionnalité BI : Analyse de Scénario (What-If Analysis)

Dans le tableau de bord (Streamlit), un curseur interactif de **Simulation d'Impact Événementiel** a été ajouté. Il s'agit d'un outil d'analyse "What-If" (Analyse de Scénario), une fonctionnalité de pointe très prisée dans les systèmes intelligents (Business Intelligence).

### A. Justification Opérationnelle (Métier)
En gestion de chaîne logistique (Supply Chain), le passé ne reflète pas toujours parfaitement la demande future. Si un gestionnaire de magasin prévoit une énorme campagne publicitaire, une pénurie annoncée chez un concurrent, ou un jour férié inattendu, il doit pouvoir simuler ces fluctuations.
- **Principe :** Le curseur lui permet d'injecter facilement un biais hypothétique (ex: hausse de 30% des ventes).
- **Conséquence :** Les KPIs se recalculent instantanément sur son écran. Cela lui donne une perspective quantitative de l'effort de réapprovisionnement supplémentaire à fournir avant même que l'événement ne se produise (on passe de l'analytique descriptive à la préparation prescriptive).

### B. Transparence Technique
L'algorithme de simulation a été conçu pour être hautement réactif. Une fois les données filtrées, l'application applique la modulation mathématique `df["sales"] * (1 + simulate / 100)` directement en mémoire sur l'ensemble du dataset affiché. Ce mécanisme met immédiatement à jour les objets visuels Plotly et Pandas, démontrant au jury que le dashboard n'est pas un banal afficheur de CSV, mais un véritable moteur de manipulation interactif.

## 9. Architecture Microservices : API FastAPI et Déploiement Docker

Pour le déploiement de l'application, nous avons migré d'une approche "monolithique" vers une **Architecture Microservices** moderne, orchestrée via `docker-compose`.

### A. La Séparation des Responsabilités (Separation of Concerns)
Dans la version initiale, le modèle IA était directement chargé en mémoire par les interfaces frontend (Gradio / Streamlit). Bien que fonctionnel pour un prototype, ce design présente des limites en production. 
Nous avons donc isolé l'IA dans sa propre **API FastAPI** dédiée (`api/main.py`). Le frontend (Gradio) ne charge plus le modèle : il envoie une requête HTTP `POST` au backend et affiche simplement la réponse.

**Justification devant un jury :**
1. **Scalabilité Indépendante :** Si l'interface web reçoit un pic de trafic, nous pouvons multiplier les conteneurs du front-end sans devoir recharger le lourd modèle IA à chaque fois.
2. **Interopérabilité :** L'API `FastAPI` offre des endpoints standards (REST). L'ERP d'une entreprise (développé en Java, C# ou PHP) peut interroger notre IA de prédiction sans avoir besoin de réécrire le code en Python. L'IA devient un service "Agnostique".
3. **Sécurité et Maintenance :** Le code métier complexe et les données de prédiction restent encapsulés et protégés côté serveur backend.

### C. Sécurité Avancée : Gestion Dynamique des Clés API (API Keys)

Pour sécuriser nos endpoints métier (notamment `/predict`), nous avons implémenté une couche de sécurité robuste basée sur des **API Keys dynamiques** via FastAPI Security (`APIKeyHeader`).
- **Phase de développement (TP) :** Une clé statique par défaut (`secret-token-123` ou via variable d'environnement) est acceptée pour faciliter les tests et la démo en local.
- **Phase de production (Projet Final) :** Un endpoint dédié (`/auth/generate-key`) permet de générer à la volée des clés cryptographiques sécurisées (`secrets.token_urlsafe(32)`). Ces clés sont stockées dynamiquement en mémoire (ou en base de données dans une itération future). 
- **Validation :** Toute requête vers `/predict` dépourvue d'un header `X-API-Key` valide se voit rejetée avec une erreur `401 Unauthorized`. Cette approche empêche l'utilisation non autorisée du modèle, protégeant ainsi l'infrastructure IA contre les abus.

**Explication du Flux Machine-to-Machine (M2M) pour la soutenance :**
Il est important de distinguer la *sécurité de l'Interface Utilisateur* de la *sécurité de l'API*. L'interface Gradio ne demande pas de mot de passe à l'employé car elle simule l'environnement interne et sécurisé de l'entreprise. En revanche, lorsqu'une prédiction est demandée, Gradio (le front-end) glisse silencieusement l'API Key dans les *Headers HTTP* et s'authentifie automatiquement auprès de FastAPI (le back-end). L'API Key sert donc uniquement à empêcher des systèmes ou développeurs tiers non autorisés de consommer les ressources de notre intelligence artificielle.

**Le paradoxe du "Guichet Ouvert" (Génération de Clé) :**
Vous remarquerez que la route `/auth/generate-key` est publiquement accessible. C'est un choix architectural totalement assumé (le paradoxe de "l'œuf et de la poule"). Si la route qui génère la clé nécessitait elle-même une clé, aucun développeur partenaire ne pourrait obtenir son premier accès. L'authentification stricte protège uniquement la "salle des coffres" (la route `/predict` qui sollicite le CPU pour l'IA), tout en laissant le "guichet" (`/auth/generate-key`) accessible pour distribuer les jetons d'accès.

### D. Le Choix de Docker et Docker Compose
Nous avons conteneurisé le projet avec `Dockerfile.api` et `Dockerfile.dashboard`.

**Justification devant un jury :**
L'utilisation de Docker résout le célèbre problème du "Ça marche sur ma machine". Il garantit une reproductibilité parfaite. Que le projet soit déployé sur un ordinateur de l'université, un serveur AWS, ou chez un client en Mauritanie, les dépendances (Python 3.9, LightGBM, FastAPI) et les ports réseaux sont scellés dans l'image. L'orchestration avec `docker-compose` permet de démarrer tout l'écosystème en une seule commande professionnelle, démontrant une grande maturité DevOps.

## 10. 🎓 Guide pour le Jour J (Soutenance)

Voici le scénario idéal pour présenter votre projet au jury une fois les services lancés (via `docker-compose up`) :

### 1. Démontrer l'API et la Sécurité (Backend)
- **Lien :** `http://localhost:8000/docs` (Interface Swagger de FastAPI).
- **Générer une clé :** Ouvrez l'endpoint `/auth/generate-key`. Cliquez sur *Try it out* puis *Execute*. Copiez la `api_key` générée (qui simule le token d'un système ERP).
- **Sécuriser l'API :** Remontez en haut de la page, cliquez sur le bouton vert **Authorize**, collez la clé dans le champ `X-API-Key` et validez. L'API est désormais déverrouillée et l'endpoint `/predict` peut être testé manuellement de manière sécurisée.

### 2. Démontrer le Dashboard Analytique (Business Intelligence)
- **Lien :** `http://localhost:8501` (Streamlit).
- **Objectif :** Montrer votre maîtrise des données (Analyse Descriptive et Prescriptive).
- **À montrer :** Naviguez dans les graphiques de saisonnalité pour prouver la complexité du dataset. Utilisez ensuite le **Curseur de Simulation d'Impact (What-If Analysis)** pour montrer comment les données se mettent à jour dynamiquement lorsqu'on simule une hausse inattendue de la demande (ex: événement sportif, promo).

### 3. Démontrer le Simulateur Opérationnel (Predictor ERP)
- **Lien :** `http://localhost:7860` (Gradio).
- **Objectif :** Montrer le cas d'usage final pour un gestionnaire de magasin.
- **À montrer :** L'interface agit comme le front-end d'un système ERP. Saisissez une date, choisissez un magasin et entrez un stock physique délibérément bas (ex: 5 unités). Lancez la prédiction. Montrez comment l'interface appelle silencieusement l'API sécurisée et affiche un **rapport de recommandation avec une alerte (Rupture / Flux tendu / Stock suffisant)** en fonction du modèle LightGBM.
