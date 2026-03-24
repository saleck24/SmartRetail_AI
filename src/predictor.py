import gradio as gr
import pandas as pd
import joblib
import os

# Chargement du modèle XGBoost Serialisé (.pkl)
model_path = 'models/xgboost_stock_predictor.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None

# Chargement des métadonnées pour une interface réaliste
items_df = pd.read_csv("data/items.csv")
stores_df = pd.read_csv("data/stores.csv")
holidays_df = pd.read_csv("data/holidays_events.csv")
holidays_df['date'] = pd.to_datetime(holidays_df['date'])

# On crée une liste de produits (ID - Famille) pour le dropdown
# On prend les 100 premiers produits pour garder l'interface fluide
item_choices = (items_df['item_nbr'].astype(str) + " - " + items_df['family']).head(100).tolist()

# On crée une liste de magasins (ID - Ville) pour le dropdown
store_choices = (stores_df['store_nbr'].astype(str) + " - " + stores_df['city']).tolist()

# On crée un dictionnaire des villes pour l'affichage dans le rapport
store_cities = dict(zip(stores_df['store_nbr'], stores_df['city']))

def predict_stock(date, store_selection, product_selection, sales_lag_7, sales_rolling_mean_7, current_stock):
    """
    Fonction appelée par l'interface web pour générer une prédiction et une recommandation.
    """
    if model is None:
        return "Erreur: Le modèle XGBoost n'a pas été trouvé. Lancez d'abord src/train_model.py"
    
    # Validation des entrées numériques (doivent être strictement positives)
    if sales_lag_7 <= 0 or sales_rolling_mean_7 <= 0 or current_stock <= 0:
        return "Erreur: Les valeurs de ventes et de stock doivent être strictement supérieures à 0 pour cette simulation."

    # 1. Extraction des IDs depuis les sélections "ID - Nom"
    try:
        store_id = int(store_selection.split(" - ")[0])
    except:
        return "Erreur dans la sélection du magasin."
        
    try:
        item = int(product_selection.split(" - ")[0])
    except:
        return "Erreur dans la sélection du produit."

    # 2. Parsing de la date saisie
    try:
        dt = pd.to_datetime(date)
    except:
        return "Erreur: Format de date invalide."
    
    month = dt.month
    dayofweek = dt.dayofweek
    is_weekend = 1 if dayofweek in [5, 6] else 0
    
    # Vérification si c'est un jour férié
    is_holiday = 1 if dt in holidays_df['date'].values else 0
    
    # 3. Re-création de la ligne de "Features" exactement comme lors de l'entraînement
    input_data = pd.DataFrame({
        'store': [store_id],
        'item': [item],
        'month': [month],
        'dayofweek': [dayofweek],
        'is_weekend': [is_weekend],
        'is_holiday': [is_holiday],
        'sales_lag_7': [sales_lag_7],
        'sales_rolling_mean_7': [sales_rolling_mean_7]
    })
    
    # 4. Appel du modèle IA
    pred = model.predict(input_data)[0]
    expected_demand = max(0, int(round(pred)))
    
    # 5. Récupération de la ville
    city = store_cities.get(store_id, "Inconnue")
    
    # 6. Formatage de la date (dd/mm/yyyy hh:mm:ss) et Bolding des métriques
    formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
    bold_units = f"**{expected_demand}**"
    bold_date = f"**{formatted_date}**"
    
    # 7. Règle Métier ERP : Recommandation & Couleurs (HTML compatible Markdown)
    if current_stock < expected_demand:
        color = "red"
        alerte = f"<span style='color: {color}; font-weight: bold;'>ALERTE RUPTURE IMMINENTE</span>"
        a_commander = expected_demand - current_stock
        reco = f"**ACTION REQUISE :** <span style='color: {color};'>Commander en urgence **{a_commander}** unités aujourd'hui.</span>"
    else:
        color = "green"
        alerte = f"<span style='color: {color}; font-weight: bold;'>STOCK SUFFISANT</span>"
        reco = f"**AUCUNE ACTION :** <span style='color: {color};'>Le stock couvre la demande prévue.</span>"
    
    # 8. Formatage du résultat affiché
    result = f"PRÉVISION DE L'IA XGBOOST (Favorita) : {bold_units} unités seront vendues le {bold_date}.\n\n"
    result += f"**Localisation :** Magasin {store_id} ({city})\n\n"
    result += f"**Produit :** {product_selection}\n\n"
    result += f"**ANALYSE DU STOCK** :\n\n"
    result += f"**- Stock Actuel** : {int(current_stock)}\n\n"
    result += f"**- Statut** : {alerte}\n\n"
    result += f"**RECOMMANDATION ERP** :\n\n{reco}"
    
    return result

# Configuration de l'interface Web (Gradio Blocks - Compatible v6.0+)
with gr.Blocks() as demo:
    
    with gr.Column():
        # Header
        gr.Markdown(
            """
            # ERP Intelligent : Analyse de Stock Real-World
            ### Simulation sur le Dataset Corporación Favorita (Équateur)
            ---
            """
        )
        
        with gr.Row():
            # Colonne de Gauche : Saisie des données
            with gr.Column(scale=1):
                gr.Markdown("### Paramètres de Simulation")
                with gr.Group():
                    # Utilisation d'un type "date" pour afficher le calendrier
                    date_input = gr.DateTime(label="Date de prévision", value="2017-08-16", type="string")
                    with gr.Row():
                        store_input = gr.Dropdown(label="Sélection du Magasin", choices=store_choices, value=store_choices[0])
                        # Dropdown avec Noms réels des produits
                        item_input = gr.Dropdown(label="Sélection du Produit (ID - Famille)", choices=item_choices, value=item_choices[0])
                
                gr.Markdown("### Historique Récent")
                with gr.Group():
                    with gr.Row():
                        lag_input = gr.Number(label="Ventes à J-7 (kg/u)", value=10, minimum=0.1)
                        roll_input = gr.Number(label="Moyenne 7j (kg/u)", value=12, minimum=0.1)
                    stock_input = gr.Number(label="Stock Physique Actuel", value=5, minimum=0.1)
                
                predict_btn = gr.Button("Générer l'Analyse prédictive", variant="primary")

            # Colonne de Droite : Résultat et Recommandation
            with gr.Column(scale=1):
                gr.Markdown("### Rapport de Réapprovisionnement")
                output_report = gr.Markdown(
                    "Saisissez les données et cliquez sur le bouton pour obtenir une recommandation."
                )
                
                gr.Markdown(
                    """
                    > **Note technique :** Ce module est désormais configuré pour le dataset **Favorita**. 
                    > Il utilise l'historique réel de consommation pour prédire les besoins de stock par magasin et par catégorie.
                    """
                )

    # Logique de clic
    predict_btn.click(
        fn=predict_stock,
        inputs=[date_input, store_input, item_input, lag_input, roll_input, stock_input],
        outputs=output_report
    )

if __name__ == "__main__":
    demo.launch(
        share=False, 
        theme=gr.themes.Soft(), 
        css=".container { max-width: 900px; margin: auto; padding: 20px; }"
    )
