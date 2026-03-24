import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

import warnings
warnings.filterwarnings('ignore')

def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100

def create_features(df):
    """
    Feature Engineering: Ajout d'informations calendaires et historiques.
    """
    df['date'] = pd.to_datetime(df['date'])
    
    # 1. Variables temporelles
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
    
    # 2. Intégration des Jours Fériés (Holidays)
    if os.path.exists('data/holidays_events.csv'):
        holidays_df = pd.read_csv('data/holidays_events.csv')
        holidays_df['date'] = pd.to_datetime(holidays_df['date'])
        # On ne garde que les colonnes utiles (on marque si c'est un jour férié)
        df = df.merge(holidays_df[['date', 'type']], on='date', how='left')
        df['is_holiday'] = df['type'].notna().astype(int)
        df = df.drop('type', axis=1)
    else:
        df['is_holiday'] = 0

    # 3. Features basées sur l'historique (Lags)
    df = df.sort_values(by=['store', 'item', 'date'])
    
    # Lag 7 : Ventes d'il y a une semaine exactement
    df['sales_lag_7'] = df.groupby(['store', 'item'])['sales'].shift(7)
    
    # Moyenne mobile sur 7 jours (Décalée de 1 pour éviter la fuite de données)
    df['sales_rolling_mean_7'] = df.groupby(['store', 'item'])['sales'].transform(lambda x: x.shift(1).rolling(window=7).mean())
    
    # Pour ne pas perdre trop de données sur un petit échantillon, on remplace les NaNs du début par 0
    df['sales_lag_7'] = df['sales_lag_7'].fillna(0)
    df['sales_rolling_mean_7'] = df['sales_rolling_mean_7'].fillna(0)
    
    return df


print("1. Chargement et préparation des données (Favorita Dataset - 2017)...")
# Le fichier fait 125M de lignes. On saute les 120M premières pour arriver en 2017.
try:
    # Récupération de l'entête
    header = pd.read_csv('data/train.csv', nrows=0).columns.tolist()
    # Chargement des dernières données réelles
    df = pd.read_csv('data/train.csv', skiprows=120000000, nrows=2000000, names=header)
except Exception as e:
    print(f"Erreur de lecture optimisée : {e}")
    df = pd.read_csv('data/train.csv', nrows=1000000)

# Renommage des colonnes pour correspondre à notre logique ERP
df = df.rename(columns={
    'store_nbr': 'store',
    'item_nbr': 'item',
    'unit_sales': 'sales'
})

# Nettoyage : Les ventes négatives (retours) sont ramenées à 0
df['sales'] = df['sales'].clip(lower=0)

df = create_features(df)

# On sépare les features (X) de la cible à prédire (y)
features = ['store', 'item', 'month', 'dayofweek', 'is_weekend', 'is_holiday', 'sales_lag_7', 'sales_rolling_mean_7']
target = 'sales'

X = df[features]
y = df[target]

print(f"Dataset chargé : {len(df)} lignes prêtes pour l'IA.")

print("2. Séparation Entraînement / Test (Split Temporel)")
# Split Temporel : On entraîne sur le passé, on teste sur le futur.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(f"Lignes pour l'entraînement : {len(X_train)} | Lignes pour le test : {len(X_test)}")

# ----------------------------------------------------
# MODÈLE 1 : BASELINE (Régression Linéaire)
# ----------------------------------------------------
print("\n3. Entraînement Modèle Baseline (Régression Linéaire)...")
model_baseline = LinearRegression()
model_baseline.fit(X_train, y_train)

y_pred_base = model_baseline.predict(X_test)
mae_base = mean_absolute_error(y_test, y_pred_base)
rmse_base = np.sqrt(mean_squared_error(y_test, y_pred_base))
mape_base = mean_absolute_percentage_error(y_test, y_pred_base)

print(f"[BASELINE] -> MAE: {mae_base:.2f} | RMSE: {rmse_base:.2f} | MAPE: {mape_base:.2f}%")

# ----------------------------------------------------
# MODÈLE 2 : AVANCÉ (XGBoost)
# ----------------------------------------------------
print("\n4. Entraînement Modèle IA Avancé (XGBoost)...")
# On limite n_estimators à 50 pour que l'entraînement sur Favorita soit très rapide
model_xgb = XGBRegressor(n_estimators=50, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1)
model_xgb.fit(X_train, y_train)

y_pred_xgb = model_xgb.predict(X_test)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
mape_xgb = mean_absolute_percentage_error(y_test, y_pred_xgb)

print(f"[XGBOOST]  -> MAE: {mae_xgb:.2f} | RMSE: {rmse_xgb:.2f} | MAPE: {mape_xgb:.2f}%")

# Sauvegarde des métriques dans un fichier texte pour lecture facile
with open('metrics.txt', 'w') as f:
    f.write(f"MAE: {mae_xgb:.2f}\n")
    f.write(f"RMSE: {rmse_xgb:.2f}\n")
    f.write(f"MAPE: {mape_xgb:.2f}\n")

# ----------------------------------------------------
# COMPARAISON & SAUVEGARDE
# ----------------------------------------------------
improvement = ((mae_base - mae_xgb) / mae_base) * 100
print(f"\n=> Performance Favorita : L'IA XGBoost est {improvement:.1f}% plus performante que le modèle standard !")

# Création du dossier models s'il n'existe pas
os.makedirs('models', exist_ok=True)
joblib.dump(model_xgb, 'models/xgboost_stock_predictor.pkl')
print("\nModèle Favorita sauvegardé avec succès dans 'models/xgboost_stock_predictor.pkl'")
