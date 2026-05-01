import gradio as gr
import pandas as pd
import joblib
import os
import requests

# ---------------------------
# CONFIGURATION & LOADER
# ---------------------------
API_URL = os.environ.get("API_URL", None)
API_KEY = os.environ.get("API_KEY", "secret-token-123")

model_path = 'models/lightgbm_stock_predictor.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None

# Chargement des métadonnées pour une interface réaliste
try:
    items_df = pd.read_csv("data/items.csv")
    stores_df = pd.read_csv("data/stores.csv")
    holidays_df = pd.read_csv("data/holidays_events.csv")
    holidays_df['date'] = pd.to_datetime(holidays_df['date'])

    item_choices = (items_df['item_nbr'].astype(str) + " - " + items_df['family']).head(200).tolist()
    store_choices = (stores_df['store_nbr'].astype(str) + " - " + stores_df['city']).tolist()
    store_cities = dict(zip(stores_df['store_nbr'], stores_df['city']))
except Exception:
    item_choices = ["1 - GROCERY", "2 - BEVERAGES"]
    store_choices = ["1 - Quito", "2 - Guayaquil"]
    store_cities = {1: "Quito", 2: "Guayaquil"}
    holidays_df = pd.DataFrame(columns=["date"])

def predict_stock(date, store_selection, product_selection, sales_lag_7, sales_rolling_mean_7, current_stock):
    """
    Fonction appelée par l'interface web pour générer une prédiction et une recommandation.
    """
    if sales_lag_7 <= 0 or sales_rolling_mean_7 <= 0 or current_stock <= 0:
        return "<h3 style='color:orange;'>Avertissement: Les valeurs doivent être supérieures à 0.</h3>"

    try:
        store_id = int(float(store_selection.split(" - ")[0]))
        item = int(float(product_selection.split(" - ")[0]))
        dt = pd.to_datetime(date)
    except:
        return "<h3>Erreur dans la saisie des données.</h3>"
    
    city = store_cities.get(store_id, "Inconnue")

    if API_URL:
        # Consommation de l'API FastAPI (Architecture Microservices)
        payload = {
            "date": dt.strftime('%Y-%m-%d'),
            "store_id": store_id,
            "item_id": item,
            "sales_lag_7": sales_lag_7,
            "sales_rolling_mean_7": sales_rolling_mean_7
        }
        try:
            headers = {"X-API-Key": API_KEY}
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                expected_demand = response.json().get("expected_demand", 0)
            else:
                return f"<h3 style='color:red;'>Erreur API ({response.status_code}): {response.text}</h3>"
        except Exception as e:
            return f"<h3 style='color:red;'>Erreur de connexion à l'API: {str(e)}</h3>"
    else:
        # Fallback local (Architecture Monolithique originale)
        if model is None:
            return "<h3 style='color:red;'>Erreur: Le modèle n'a pas été trouvé et l'API n'est pas configurée. Lancez d'abord dashboard/train_model.py</h3>"
        
        month = dt.month
        dayofweek = dt.dayofweek
        is_weekend = 1 if dayofweek in [5, 6] else 0
        is_holiday = 1 if dt in holidays_df['date'].values else 0
        
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
        
        pred = model.predict(input_data)[0]
        expected_demand = max(0, int(round(pred)))
    
    
    # Génération du HTML enrichi pour le rapport
    if current_stock < expected_demand:
        status_color = "#ff4d4d"
        status_icon = "🚨"
        status_text = "RUPTURE IMMINENTE"
        a_commander = expected_demand - current_stock
        reco = f"Commander en urgence <b>{a_commander}</b> unités."
    elif current_stock == expected_demand:
        status_color = "#ffa64d"
        status_icon = "⚠️"
        status_text = "FLUX TENDU"
        reco = f"Le stock couvrira exactement la demande. Surveillez de près."
    else:
        status_color = "#2eb82e"
        status_icon = "✅"
        status_text = "STOCK SUFFISANT"
        reco = f"Aucune action requise."

    formatted_date = dt.strftime('%d %b %Y')
    
    html_report = f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: #f9f9f9; text-align: center;">
        <h2 style="margin-top: 0; color: #333;">💡 Recommandation ERP</h2>
        <p style="font-size: 16px; color: #555;">Prévision de l'IA pour le <b style="color: #333;">{formatted_date}</b> :</p>
        <h1 style="color: #007bff; font-size: 40px; margin: 10px 0;">{expected_demand} unités</h1>
        
        <div style="display: flex; justify-content: space-around; margin: 20px 0;">
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); width: 45%;">
                <p style="margin: 0; font-size: 14px; color: #888;">📦 Stock Actuel</p>
                <h3 style="margin: 5px 0; color: #333;">{int(current_stock)}</h3>
            </div>
            <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); width: 45%;">
                <p style="margin: 0; font-size: 14px; color: #888;">📍 Localisation</p>
                <h3 style="margin: 5px 0; color: #333;">{city} <span style="font-size: 12px; font-weight: normal; color: #666;">(Magasin {store_id})</span></h3>
            </div>
        </div>

        <div style="background-color: {status_color}; color: white; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <h3 style="margin: 0;">{status_icon} STATUT : {status_text}</h3>
            <p style="margin: 5px 0 0 0; font-size: 16px;">{reco}</p>
        </div>
    </div>
    """
    return html_report

# ---------------------------
# INTERFACE WEBU GRADIO PRO
# ---------------------------
# Thème personnalisé Soft avec quelques tweaks
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
)

with gr.Blocks(title="Pro ERP AI Predictor") as demo:
    
    # En-tête
    gr.HTML(
        """
        <div style="text-align: center; padding: 20px; background-color: #0b1f38; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0;">🤖 ERP AI Predictor Pro</h1>
            <p style="color: #a0aec0; margin-top: 5px; font-size: 16px;">Analyse LightGBM des stocks corporatifs (Favorita Dataset)</p>
        </div>
        """
    )
    
    with gr.Tabs():
        # TAB 1 : Simulateur
        with gr.TabItem("🎯 Simulateur Analytique"):
            with gr.Row():
                # Colonne 1 : Entrées Utilisateur
                with gr.Column(scale=4):
                    gr.Markdown("### ⚙️ Paramètres Opérationnels")
                    
                    with gr.Group():
                        date_input = gr.DateTime(label="📅 Date de prévision cible", value="2017-08-16", type="string")
                        with gr.Row():
                            store_input = gr.Dropdown(label="🏪 Magasin", choices=store_choices, value=store_choices[0])
                            item_input = gr.Dropdown(label="📦 Catégorie Produit", choices=item_choices, value=item_choices[0])
                    
                    gr.Markdown("### 📊 Variables Métiers Récents")
                    with gr.Group():
                        with gr.Row():
                            lag_input = gr.Number(label="⏮️ Ventes J-7 (u)", value=15)
                            roll_input = gr.Number(label="📉 Moyenne 7j (u)", value=12.5)
                        stock_input = gr.Number(label="📦 Stock Physique Disponible (u)", value=10)
                    
                    predict_btn = gr.Button("🚀 Lancer l'Analyse Prédictive", variant="primary", size="lg")
                
                # Colonne 2 : Résultat de l'IA
                with gr.Column(scale=5):
                    gr.Markdown("### 📋 Rapport d'Intelligence Artificielle")
                    output_html = gr.HTML(
                        """
                        <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 40px; text-align: center; color: #888;">
                            <h3>En attente de simulation...</h3>
                            <p>Veuillez entrer les paramètres à gauche et lancer la prédiction.</p>
                        </div>
                        """
                    )
        
        # TAB 2 : Info / Doc
        with gr.TabItem("📖 Informations du Modèle"):
            gr.Markdown(
                """
                ### 🏗️ Architecture du Modèle Prédictif
                Ce Predictor utilise un modèle **LightGBM (Gradient Boosting Machine)** performant pour la régression.
                
                - **Données d'entraînement** : Échantillon représentatif de **1 million de lignes** de transactions réelles (Corporación Favorita, année 2017) pour garantir un apprentissage rapide et performant.
                - **Features principales** : Saisonnalité (Mois, Jour J/F), Jours Fériés nationaux, Ventes Lag et Moyennes Mobiles (7 jours).
                - **Objectif** : Anticiper la demande exacte afin de réduire les coûts de stockage inutiles et de prévenir les ruptures dommageables au chiffre d'affaires.
                """
            )

    # Actions
    predict_btn.click(
        fn=predict_stock,
        inputs=[date_input, store_input, item_input, lag_input, roll_input, stock_input],
        outputs=output_html
    )

if __name__ == "__main__":
    # En local (venv), on utilise 127.0.0.1 pour que le lien généré soit cliquable (localhost).
    # Dans Docker, l'IP doit être 0.0.0.0 pour exposer le port.
    host = os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1")
    demo.launch(
        share=False,
        server_name=host,
        server_port=7860,
        theme=custom_theme
    )
