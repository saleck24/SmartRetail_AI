import pandas as pd
import numpy as np
import os
import joblib
import time

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import lightgbm as lgb

import warnings
warnings.filterwarnings('ignore')

# Tentative d'import pour le Bonus LSTM
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    HAS_TF = True
except ImportError:
    HAS_TF = False

def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100

def create_features(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
    
    if os.path.exists('data/holidays_events.csv'):
        holidays_df = pd.read_csv('data/holidays_events.csv')
        holidays_df['date'] = pd.to_datetime(holidays_df['date'])
        df = df.merge(holidays_df[['date', 'type']], on='date', how='left')
        df['is_holiday'] = df['type'].notna().astype(int)
        df = df.drop('type', axis=1)
    else:
        df['is_holiday'] = 0

    df = df.sort_values(by=['store', 'item', 'date'])
    df['sales_lag_7'] = df.groupby(['store', 'item'])['sales'].shift(7)
    df['sales_rolling_mean_7'] = df.groupby(['store', 'item'])['sales'].transform(lambda x: x.shift(1).rolling(window=7).mean())
    df['sales_lag_7'] = df['sales_lag_7'].fillna(0)
    df['sales_rolling_mean_7'] = df['sales_rolling_mean_7'].fillna(0)
    
    return df

print("1. Chargement et préparation des données (Favorita Dataset - 2017)...")
try:
    header = pd.read_csv('data/train.csv', nrows=0).columns.tolist()
    # On utilise un échantillon un peu plus petit (1M au lieu de 2M) pour que l'installation et l'entraînement global (incluant LSTM) reste raisonnable
    df = pd.read_csv('data/train.csv', skiprows=120000000, nrows=1000000, names=header)
except Exception as e:
    print(f"Erreur de lecture optimisée : {e}")
    df = pd.read_csv('data/train.csv', nrows=500000)

df = df.rename(columns={'store_nbr': 'store', 'item_nbr': 'item', 'unit_sales': 'sales'})
df['sales'] = df['sales'].clip(lower=0)
df = create_features(df)

features = ['store', 'item', 'month', 'dayofweek', 'is_weekend', 'is_holiday', 'sales_lag_7', 'sales_rolling_mean_7']
target = 'sales'

X = df[features]
y = df[target]

X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# On affiche les résultats dans un dictionnaire pour le rapport final
results = []

def eval_model(name, y_true, y_pred, train_time):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mean_absolute_percentage_error(y_true, y_pred)
    results.append({
        'Modèle': name,
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE (%)': round(mape, 2),
        'Temps (s)': round(train_time, 2)
    })
    print(f"[{name}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | Temps: {train_time:.2f}s")

# --- BASELINE : Linear Regression ---
print("\n3. Entraînement Baseline (Linear Regression)...")
start = time.time()
base_model = LinearRegression()
base_model.fit(X_train_full, y_train_full)
t = time.time() - start
eval_model("Baseline (LinearReg)", y_test, base_model.predict(X_test), t)

# --- COMPARISON : XGBoost ---
print("\n4. Entraînement Comparaison (XGBoost)...")
start = time.time()
xgb_model = XGBRegressor(n_estimators=50, max_depth=6, n_jobs=-1, random_state=42)
xgb_model.fit(X_train_full, y_train_full)
t = time.time() - start
eval_model("XGBoost", y_test, xgb_model.predict(X_test), t)

# --- PRINCIPAL : LightGBM ---
print("\n5. Entraînement Principal (LightGBM)...")
start = time.time()
# Paramètres légers pour rapidité
lgbm_model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1, importance_type='gain', verbose=-1)
lgbm_model.fit(X_train_full, y_train_full)
t = time.time() - start
eval_model("LightGBM (Principal)", y_test, lgbm_model.predict(X_test), t)

# --- BONUS : LSTM (Deep Learning) ---
if HAS_TF:
    print("\n6. Entraînement Bonus (LSTM)...")
    # LSTM nécessite une mise à l'échelle (scaling)
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    
    # échantillonnage pour LSTM (on prend les 100 000 dernières lignes car c'est très lent)
    X_train_lstm = X_train_full.tail(100000)
    y_train_lstm = y_train_full.tail(100000)
    
    X_train_scaled = scaler_x.fit_transform(X_train_lstm)
    X_test_scaled = scaler_x.transform(X_test)
    y_train_scaled = scaler_y.fit_transform(y_train_lstm.values.reshape(-1, 1))
    
    # Reshaping 2D -> 3D [samples, time_steps, features]
    X_train_3d = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
    X_test_3d = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
    
    start = time.time()
    lstm_model = Sequential([
        LSTM(50, activation='relu', input_shape=(1, len(features))),
        Dense(1)
    ])
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit(X_train_3d, y_train_scaled, epochs=5, batch_size=256, verbose=0)
    t = time.time() - start
    
    y_pred_scaled = lstm_model.predict(X_test_3d)
    y_pred_lstm = scaler_y.inverse_transform(y_pred_scaled)
    eval_model("LSTM (Bonus)", y_test, y_pred_lstm.flatten(), t)
else:
    print("\n[SKIP] LSTM non entraîné (TensorFlow non installé).")

# Sauvegarde des résultats pour IA_Justifications.md
print("\n--- RÉSUMÉ COMPARATIF ---")
df_results = pd.DataFrame(results)
print(df_results)

# Sauvegarde du meilleur modèle (LightGBM)
os.makedirs('models', exist_ok=True)
joblib.dump(lgbm_model, 'models/lightgbm_stock_predictor.pkl')
print("\nModèle principal LightGBM sauvegardé dans 'models/lightgbm_stock_predictor.pkl'")
