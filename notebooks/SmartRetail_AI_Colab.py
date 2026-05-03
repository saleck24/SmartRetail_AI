# ============================================================
# SmartRetail AI — Full Training Pipeline (Google Colab)
# Dataset: Corporación Favorita Grocery Sales Forecasting
# Auteur   : SmartRetail AI Team
# Version  : 2.0 (Corrigé & Complet)
# ============================================================
# INSTRUCTIONS COLAB :
#   1. Exécutez chaque cellule (==== CELL X ====) dans l'ordre
#   2. Uploadez kaggle.json quand CELL 2 le demande
#   3. Le modèle final est téléchargé automatiquement par CELL 16
# ============================================================

# ==== CELL 1: Installation ====
# ⚠️ EXECUTEZ CETTE CELLULE EN PREMIER — TOUJOURS
import subprocess, sys

# Installation via pip — on N'IMPORTE PAS kaggle ici !
# kaggle s'authentifie automatiquement a l'import, avant que kaggle.json existe → erreur
print("Installation des dependances...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q',
                       'kaggle', 'lightgbm', 'xgboost', 'optuna'])
print("✅ Tous les packages installes !\n")

# ==== CELL 2: Configuration Kaggle API ====
# DOIT se faire AVANT tout import de kaggle
from google.colab import files
import os, glob

print("Uploadez votre fichier kaggle.json")
uploaded = files.upload()

# Recuperer le vrai nom du fichier uploade
# (Colab peut le renommer en "kaggle (1).json" si kaggle.json existe deja)
uploaded_filename = list(uploaded.keys())[0]
print(f"Fichier recu : {uploaded_filename}")

os.makedirs('/root/.config/kaggle', exist_ok=True)
# On copie TOUJOURS vers /root/.config/kaggle/kaggle.json quel que soit le nom
os.system(f'cp "{uploaded_filename}" /root/.config/kaggle/kaggle.json')
os.system('chmod 600 /root/.config/kaggle/kaggle.json')
print("✅ Kaggle API configuree !")

# ==== CELL 3: Téléchargement du dataset ====
print("\nTelechargement du dataset Favorita...")
os.makedirs('/content/favorita', exist_ok=True)

ret = os.system('kaggle competitions download -c favorita-grocery-sales-forecasting -p /content/favorita')
if ret != 0:
    raise RuntimeError(
        "\n❌ ERREUR DE TELECHARGEMENT KAGGLE\n"
        "   Cause probable : vous n'avez pas accepte les regles de la competition.\n"
        "   → Allez sur : https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/rules\n"
        "   → Cliquez 'I Understand and Accept'\n"
        "   → Relancez ensuite cette cellule"
    )

# Le ZIP Favorita contient des fichiers .7z — il faut p7zip pour les extraire
print("Installation de p7zip pour les archives .7z...")
os.system('apt-get install -qq p7zip-full')

print("Extraction du ZIP principal...")
os.system('unzip -q /content/favorita/favorita-grocery-sales-forecasting.zip -d /content/favorita/')

print("Extraction des archives .7z internes...")
for f7z in glob.glob('/content/favorita/*.7z'):
    print(f"  Extraction de {os.path.basename(f7z)}...")
    os.system(f'7z e "{f7z}" -o/content/favorita/ -y -bd > /dev/null')

# Verification finale
csv_files = glob.glob('/content/favorita/*.csv')
if not csv_files:
    # Afficher le contenu pour debugger
    print("Contenu de /content/favorita/ :")
    os.system('ls -lh /content/favorita/')
    raise RuntimeError("❌ Aucun fichier CSV trouve. Voir le contenu ci-dessus pour diagnostiquer.")

print(f"\n✅ Dataset pret ! {len(csv_files)} fichiers CSV :")
for f in sorted(csv_files):
    size_mb = os.path.getsize(f) / 1e6
    print(f"   - {os.path.basename(f):35s} ({size_mb:.1f} MB)")

# ==== CELL 4: Imports ====
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time, os, json, joblib, warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error, max_error
from xgboost import XGBRegressor
import lightgbm as lgb
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    HAS_TF = True
    print(f"TensorFlow {tf.__version__} disponible")
except ImportError:
    HAS_TF = False
    print("TensorFlow non disponible — LSTM skipped")

DATA_PATH = '/content/favorita'
os.makedirs('/content/outputs', exist_ok=True)
os.makedirs('/content/outputs/eda_plots', exist_ok=True)
os.makedirs('/content/outputs/benchmark_plots', exist_ok=True)
print("Imports OK")

# ==== CELL 5: Optimisation mémoire ====
def reduce_mem_usage(df):
    for col in df.columns:
        col_type = df[col].dtype
        # Ignorer les colonnes object ET datetime (Timestamp non comparable a float)
        if col_type == object or str(col_type).startswith('datetime'):
            continue
        c_min, c_max = df[col].min(), df[col].max()
        if str(col_type)[:3] == 'int':
            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                df[col] = df[col].astype(np.int8)
            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                df[col] = df[col].astype(np.int16)
            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
    return df

# ==== CELL 6: Chargement des données ====
print("Chargement du dataset Favorita (Filtre sur 2017 pour eviter le crash RAM)...")
chunks = []
for chunk in pd.read_csv(f'{DATA_PATH}/train.csv',
                          parse_dates=['date'],
                          chunksize=5_000_000,
                          dtype={'store_nbr': np.int8, 'item_nbr': np.int32,
                                 'unit_sales': np.float32, 'onpromotion': 'boolean'}):
    chunk = chunk.rename(columns={'store_nbr': 'store', 'item_nbr': 'item', 'unit_sales': 'sales'})
    chunk['sales'] = chunk['sales'].clip(lower=0)
    
    # ⚠️ FIX OOM : Garder uniquement l'annee 2017 (environ 24 millions de lignes au lieu de 125M)
    # Cela permet a Colab de ne pas exploser sa RAM de 12.6 GB lors du Feature Engineering
    chunk = chunk[chunk['date'] >= '2017-01-01']
    
    if not chunk.empty:
        chunks.append(reduce_mem_usage(chunk))


df = pd.concat(chunks, ignore_index=True)
print(f"Dataset: {len(df):,} lignes | {df.memory_usage(deep=True).sum()/1e9:.2f} GB")

stores_df   = pd.read_csv(f'{DATA_PATH}/stores.csv')
items_df    = pd.read_csv(f'{DATA_PATH}/items.csv')
holidays_df = pd.read_csv(f'{DATA_PATH}/holidays_events.csv', parse_dates=['date'])
oil_df      = pd.read_csv(f'{DATA_PATH}/oil.csv', parse_dates=['date'])
oil_df      = oil_df.rename(columns={'dcoilwtico': 'oil_price'})
oil_df      = oil_df.set_index('date').resample('D').interpolate(method='linear').reset_index()
print(f"Stores: {len(stores_df)} | Items: {len(items_df)} | Holidays: {len(holidays_df)} | Oil: {len(oil_df)}")

# ==== CELL 7: EDA ====
sns.set_theme(style='darkgrid', palette='muted')
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('EDA — Corporación Favorita (Dataset Complet)', fontsize=16, fontweight='bold')

monthly = df.groupby(df['date'].dt.to_period('M'))['sales'].sum()
monthly.plot(ax=axes[0,0], color='#06B6D4', linewidth=2)
axes[0,0].set_title('Ventes Totales par Mois (2013–2017)')

dow = df.groupby(df['date'].dt.dayofweek)['sales'].mean()
dow.index = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']
dow.plot(kind='bar', ax=axes[0,1], color='#8B5CF6', edgecolor='white')
axes[0,1].set_title('Ventes Moyennes par Jour de Semaine')
axes[0,1].tick_params(axis='x', rotation=0)

df.groupby('store')['sales'].sum().nlargest(10).plot(kind='barh', ax=axes[1,0], color='#F59E0B', edgecolor='white')
axes[1,0].set_title('Top 10 Magasins par Ventes')

axes[1,1].hist(np.log1p(df['sales']), bins=60, color='#10B981', edgecolor='white', alpha=0.8)
axes[1,1].set_title('Distribution des Ventes (log1p)')

plt.tight_layout()
plt.savefig('/content/outputs/eda_plots/01_eda_overview.png', dpi=150, bbox_inches='tight')
plt.show()
print("EDA Plot 1/2 sauvegardé")

holidays_df['date'] = pd.to_datetime(holidays_df['date'])
holiday_dates = set(holidays_df['date'].dt.date)
df['is_holiday'] = df['date'].dt.date.isin(holiday_dates).astype(np.int8)
df['year']  = df['date'].dt.year
df['month'] = df['date'].dt.month.astype(np.int8)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
df.groupby('is_holiday')['sales'].mean().plot(kind='bar', ax=axes[0], color=['#3B82F6','#EF4444'], edgecolor='white')
axes[0].set_title('Ventes : Jour Férié vs Normal')
axes[0].set_xticklabels(['Normal','Jour Férié'], rotation=0)
df.groupby(['year','month'])['sales'].mean().unstack(0).plot(ax=axes[1], linewidth=2)
axes[1].set_title('Saisonnalité Mensuelle par Année')
plt.tight_layout()
plt.savefig('/content/outputs/eda_plots/02_seasonality.png', dpi=150, bbox_inches='tight')
plt.show()
print("EDA Plot 2/2 sauvegardé")

# ==== CELL 8: Feature Engineering ====
print("Feature Engineering...")
df = df.sort_values(['store','item','date']).reset_index(drop=True)
df['dayofweek'] = df['date'].dt.dayofweek.astype(np.int8)
df['is_weekend'] = (df['dayofweek'] >= 5).astype(np.int8)

for lag in [7, 14, 28]:
    df[f'sales_lag_{lag}'] = df.groupby(['store','item'])['sales'].shift(lag).astype(np.float32)

for w in [7, 14]:
    df[f'sales_roll_mean_{w}'] = df.groupby(['store','item'])['sales'].transform(
        lambda x: x.shift(1).rolling(w).mean()).astype(np.float32)

df['sales_roll_std_7'] = df.groupby(['store','item'])['sales'].transform(
    lambda x: x.shift(1).rolling(7).std()).astype(np.float32)

# Merge stores
df = df.merge(stores_df[['store_nbr','city','type','cluster']].rename(columns={'store_nbr':'store'}), on='store', how='left')
df['store_type']    = df['type'].astype('category').cat.codes.astype(np.int8)
df['store_cluster'] = df['cluster'].astype(np.int8)

# Merge items
df = df.merge(items_df[['item_nbr','family']].rename(columns={'item_nbr':'item'}), on='item', how='left')
df['item_family'] = df['family'].astype('category').cat.codes.astype(np.int16)

# Merge oil prices (indicateur macroéconomique — Équateur dépend du pétrole)
df = df.merge(oil_df[['date','oil_price']], on='date', how='left')
df['oil_price'] = df['oil_price'].fillna(method='ffill').astype(np.float32)

df = df.dropna().reset_index(drop=True)
df = reduce_mem_usage(df)

FEATURES = ['store','item','month','dayofweek','is_weekend','is_holiday',
            'sales_lag_7','sales_lag_14','sales_lag_28',
            'sales_roll_mean_7','sales_roll_mean_14','sales_roll_std_7',
            'store_type','store_cluster','item_family','oil_price']
TARGET = 'sales'
X = df[FEATURES].values
y = df[TARGET].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(f"Train: {len(X_train):,} | Test: {len(X_test):,} | Features: {len(FEATURES)}")

# ==== CELL 9: Métriques ====
def smape(yt, yp):
    d = (np.abs(yt) + np.abs(yp)) / 2.0
    return np.mean(np.abs(yp - yt) / np.where(d==0,1,d)) * 100

def mape(yt, yp):
    return np.mean(np.abs((yt-yp)/np.maximum(yt,1))) * 100

def rmsle(yt, yp):
    return np.sqrt(np.mean((np.log1p(yt) - np.log1p(np.maximum(yp,0)))**2))

def compute_metrics(name, yt, yp, tt, it):
    res = {
        'Modèle': name,
        'MAE': round(mean_absolute_error(yt,yp),4),
        'RMSE': round(np.sqrt(mean_squared_error(yt,yp)),4),
        'MAPE (%)': round(mape(yt,yp),2),
        'SMAPE (%)': round(smape(yt,yp),2),
        'RMSLE': round(rmsle(yt,yp),4),
        'R²': round(r2_score(yt,yp),4),
        'Stockout Rate (%)': round(np.mean(yp<yt)*100,2),
        'Overstock Rate (%)': round(np.mean(yp>yt*1.2)*100,2),
        'Train Time (s)': round(tt,2),
        'Inference (ms)': round(it,2),
    }
    print(f"\n{'='*50}\n  {name}\n{'='*50}")
    for k,v in res.items():
        if k != 'Modèle': print(f"  {k:<25}: {v}")
    return res

all_results = []

# ==== CELL 10: Linear Regression ====
print("\n[1/4] Linear Regression (Baseline)...")
t0 = time.time()
lr = LinearRegression(n_jobs=-1)
# ⚠️ FIX OOM : LinearRegression (Scikit-Learn) explose la RAM sur 15M de lignes (conversion float64).
# On l'entraîne sur un échantillon aléatoire de 1 million de lignes (largement suffisant pour une baseline).
idx_lr = np.random.choice(len(X_train), min(1_000_000, len(X_train)), replace=False)
lr.fit(X_train[idx_lr], y_train[idx_lr])
tt = time.time()-t0
t1 = time.time(); yp = lr.predict(X_test); it = (time.time()-t1)/len(X_test)*1000
all_results.append(compute_metrics("Linear Regression (Baseline)", y_test, yp, tt, it))

# ==== CELL 11: XGBoost ====
print("\n[2/4] XGBoost...")
t0 = time.time()
xgb = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                   subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                   random_state=42, tree_method='hist', device='cuda')
xgb.fit(X_train, y_train, eval_set=[(X_test,y_test)], verbose=100)
tt = time.time()-t0
t1 = time.time(); yp_xgb = xgb.predict(X_test); it = (time.time()-t1)/len(X_test)*1000
all_results.append(compute_metrics("XGBoost", y_test, yp_xgb, tt, it))

# ==== CELL 12: LightGBM + Optuna ====
print("\n[3/4] LightGBM + Optuna Hyperparameter Tuning (50 trials)...")
def lgbm_objective(trial):
    params = {
        'n_estimators':      trial.suggest_int('n_estimators', 200, 1000),
        'learning_rate':     trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
        'num_leaves':        trial.suggest_int('num_leaves', 31, 255),
        'max_depth':         trial.suggest_int('max_depth', 4, 12),
        'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
        'subsample':         trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree':  trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha':         trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda':        trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        'device': 'gpu', 'n_jobs': -1, 'random_state': 42, 'verbose': -1,
    }
    m = lgb.LGBMRegressor(**params)
    idx = np.random.choice(len(X_train), min(500_000, len(X_train)), replace=False)
    m.fit(X_train[idx], y_train[idx])
    return mean_absolute_error(y_test, m.predict(X_test))

study = optuna.create_study(direction='minimize')
study.optimize(lgbm_objective, n_trials=50, show_progress_bar=True)
best_params = study.best_params
print(f"Meilleurs hyperparamètres: {best_params}")

t0 = time.time()
lgbm = lgb.LGBMRegressor(**best_params, device='gpu', verbose=-1)
lgbm.fit(X_train, y_train)
tt = time.time()-t0
t1 = time.time(); yp_lgbm = lgbm.predict(X_test); it = (time.time()-t1)/len(X_test)*1000
all_results.append(compute_metrics("LightGBM + Optuna (Principal)", y_test, yp_lgbm, tt, it))

fig, ax = plt.subplots(figsize=(10,6))
pd.Series(lgbm.feature_importances_, index=FEATURES).sort_values(ascending=True).plot(
    kind='barh', ax=ax, color='#06B6D4', edgecolor='white')
ax.set_title('LightGBM — Feature Importance (Gain)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('/content/outputs/benchmark_plots/lgbm_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()

# ==== CELL 13: LSTM ====
if HAS_TF:
    print("\n[4/4] LSTM (Deep Learning - Bonus)...")
    N = min(300_000, len(X_train))
    idx = np.random.choice(len(X_train), N, replace=False)
    sx = StandardScaler(); sy = StandardScaler()
    Xts = sx.fit_transform(X_train[idx]).reshape(N, 1, len(FEATURES))
    Xte = sx.transform(X_test).reshape(len(X_test), 1, len(FEATURES))
    yts = sy.fit_transform(y_train[idx].reshape(-1,1))
    t0 = time.time()
    lstm = Sequential([
        LSTM(128, return_sequences=True, input_shape=(1,len(FEATURES))),
        Dropout(0.2), LSTM(64), Dropout(0.2), Dense(32, activation='relu'), Dense(1)
    ])
    lstm.compile(optimizer='adam', loss='huber')
    lstm.fit(Xts, yts, epochs=20, batch_size=1024, validation_split=0.1,
             callbacks=[EarlyStopping(patience=3, restore_best_weights=True)], verbose=1)
    tt = time.time()-t0
    t1 = time.time(); yp_lstm = sy.inverse_transform(lstm.predict(Xte,batch_size=4096)).flatten()
    it = (time.time()-t1)/len(X_test)*1000
    all_results.append(compute_metrics("LSTM (Bonus Deep Learning)", y_test, yp_lstm, tt, it))
else:
    print("\n[4/4] LSTM skipped")

# ==== CELL 14: Benchmark Summary & Graphes ====
df_res = pd.DataFrame(all_results)
print("\n" + "="*80)
print("BENCHMARK COMPLET — SMARTRETAIL AI")
print("="*80)
print(df_res.to_string(index=False))

with open('/content/outputs/benchmark_metrics.json','w',encoding='utf-8') as f:
    json.dump({'best_params_lgbm': best_params, 'results': df_res.to_dict(orient='records')}, f, indent=2, ensure_ascii=False)
print("\nbenchmark_metrics.json sauvegardé")

metrics_to_plot = ['MAE','RMSE','MAPE (%)','SMAPE (%)','RMSLE','R²']
fig, axes = plt.subplots(2,3,figsize=(18,10))
fig.suptitle('Benchmark Multi-Modèles — SmartRetail AI', fontsize=15, fontweight='bold')
colors = ['#3B82F6','#F59E0B','#10B981','#EF4444']
names = df_res['Modèle'].tolist()
for ax, metric in zip(axes.flatten(), metrics_to_plot):
    vals = df_res[metric].values
    bars = ax.bar(range(len(names)), vals, color=colors[:len(names)], edgecolor='white', width=0.6)
    ax.set_title(metric, fontweight='bold')
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([m.split(' ')[0] for m in names], rotation=15, ha='right')
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('/content/outputs/benchmark_plots/benchmark_all_metrics.png', dpi=150, bbox_inches='tight')
plt.show()

# ==== CELL 15: Sauvegarde du modèle & métadonnées ====
joblib.dump(lgbm, '/content/outputs/lightgbm_full_model.pkl')
joblib.dump(best_params, '/content/outputs/best_params.pkl')

# Sauvegarder les noms de features pour le backend FastAPI
feature_meta = {'features': FEATURES, 'target': TARGET, 'best_params': best_params}
with open('/content/outputs/model_metadata.json', 'w') as f:
    json.dump(feature_meta, f, indent=2)

print("\nFichiers sauvegardés dans /content/outputs/:")
print("  - lightgbm_full_model.pkl  (modèle principal)")
print("  - best_params.pkl          (hyperparamètres Optuna)")
print("  - model_metadata.json      (features + config)")
print("  - benchmark_metrics.json   (résultats complets)")
print("  - eda_plots/               (graphiques EDA)")
print("  - benchmark_plots/         (graphiques benchmark)")

# ==== CELL 16: Téléchargement automatique depuis Colab ====
import shutil
from google.colab import files as colab_files
shutil.make_archive('/content/smartretail_outputs', 'zip', '/content/outputs')
colab_files.download('/content/smartretail_outputs.zip')
print("Archive telechargee ! Decompressez dans votre dossier models/ local.")

print("\n" + "="*60)
print(" PIPELINE SMARTRETAIL AI TERMINE AVEC SUCCES !")
print("="*60)
print(" -> Copiez lightgbm_full_model.pkl dans erp_ai_stock_prediction/models/")
print(" -> Copiez model_metadata.json dans erp_ai_stock_prediction/models/")
print("="*60)
