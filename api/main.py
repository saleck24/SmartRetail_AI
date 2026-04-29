from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from datetime import datetime

app = FastAPI(
    title="ERP AI Stock Predictor API",
    description="API FastAPI pour la prédiction de la demande de stock en utilisant LightGBM",
    version="1.0.0"
)

# ---------------------------
# GLOBAL VARIABLES & LOADER
# ---------------------------
MODEL_PATH = 'models/lightgbm_stock_predictor.pkl'
model = None
holidays_df = pd.DataFrame(columns=["date"])

@app.on_event("startup")
def load_assets():
    global model, holidays_df
    # Chargement du modèle
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("SUCCESS: Modele LightGBM charge avec succes.")
    else:
        print("WARNING: Modele introuvable. Lancez dashboard/train_model.py en premier.")

    # Chargement des jours fériés
    try:
        holidays_df = pd.read_csv("data/holidays_events.csv")
        holidays_df['date'] = pd.to_datetime(holidays_df['date']).dt.date
        print("SUCCESS: Donnees des jours feries chargees.")
    except Exception as e:
        print(f"ERROR: Impossible de charger les jours feries: {e}")

# ---------------------------
# SCHEMAS
# ---------------------------
class PredictionRequest(BaseModel):
    date: str  # Format 'YYYY-MM-DD'
    store_id: int
    item_id: int
    sales_lag_7: float
    sales_rolling_mean_7: float

class PredictionResponse(BaseModel):
    expected_demand: int
    status: str
    message: str

# ---------------------------
# ENDPOINTS
# ---------------------------
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API ERP AI Stock Predictor"}

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
def predict_stock(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible. Veuillez entraîner le modèle d'abord.")

    try:
        dt = datetime.strptime(request.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD.")

    # Extraction des features temporelles
    month = dt.month
    dayofweek = dt.weekday()
    is_weekend = 1 if dayofweek in [5, 6] else 0
    is_holiday = 1 if dt in holidays_df['date'].values else 0

    # Création du DataFrame d'entrée pour le modèle
    input_data = pd.DataFrame({
        'store': [request.store_id],
        'item': [request.item_id],
        'month': [month],
        'dayofweek': [dayofweek],
        'is_weekend': [is_weekend],
        'is_holiday': [is_holiday],
        'sales_lag_7': [request.sales_lag_7],
        'sales_rolling_mean_7': [request.sales_rolling_mean_7]
    })

    try:
        # Prédiction
        pred = model.predict(input_data)[0]
        expected_demand = max(0, int(round(pred)))
        
        return PredictionResponse(
            expected_demand=expected_demand,
            status="success",
            message=f"Prédiction effectuée avec succès."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
