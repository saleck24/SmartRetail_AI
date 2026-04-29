import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ---------------------------
# CONFIG PAGE
# ---------------------------
st.set_page_config(page_title="App ERP Stock - Favorita", layout="wide", page_icon="📊")

st.title("📊 ERP Dashboard Intelligent (Favorita)")
st.markdown("Analyse des tendances de ventes réelles d'une chaîne de supermarchés (Équateur).")

# ---------------------------
# DATA LOADER
# ---------------------------
@st.cache_data
def load_data():
    # Logique de chargement hybride (Local vs Docker)
    if os.path.exists("data/train.csv"):
        file_path = "data/train.csv"
    elif os.path.exists("data/train_sample.csv"):
        file_path = "data/train_sample.csv"
    else:
        return pd.DataFrame()

    # Chargement de l'échantillon (100k lignes pour la fluidité)
    df = pd.read_csv(file_path, nrows=100000)
    df['date'] = pd.to_datetime(df['date'])
    
    # Chargement des métadonnées
    stores_df = pd.read_csv("data/stores.csv")
    items_df = pd.read_csv("data/items.csv")
    
    # Jointures pour avoir les noms des villes et les catégories de produits
    df = df.merge(stores_df[['store_nbr', 'city']], on='store_nbr', how='left')
    df = df.merge(items_df[['item_nbr', 'family']], on='item_nbr', how='left')
    
    # Renommage pour compatibilité
    df = df.rename(columns={
        'store_nbr': 'store_id',
        'item_nbr': 'item_id',
        'unit_sales': 'sales'
    })
    return df

with st.spinner('Chargement des données Favorita...'):
    df = load_data()

if df.empty:
    st.error("Les données 'data/train.csv' sont introuvables. Lancez d'abord la préparation des données.")
    st.stop()

# ---------------------------
# SIDEBAR (FILTRES)
# ---------------------------
st.sidebar.header("🔎 Filtres Métiers")

# Choix de la ville
cities = sorted(df['city'].unique())
selected_city = st.sidebar.selectbox("🏙️ Ville", cities)

# Filtrer les magasins de cette ville
stores_in_city = sorted(df[df['city'] == selected_city]['store_id'].unique())
selected_store = st.sidebar.selectbox("🏪 Numéro du Magasin", stores_in_city)

# Choix de la famille de produits
families = sorted(df['family'].unique())
selected_family = st.sidebar.selectbox("🛒 Catégorie de Produits", families)

# Filtrer les produits de cette famille
items_in_family = sorted(df[df['family'] == selected_family]['item_id'].unique())
selected_item = st.sidebar.selectbox("📦 Code Article", items_in_family)

# Choix de la période (Date - Logique Métier pour le Jury)
import datetime
# Limites réelles de l'entièreté du dataset Corporación Favorita (pas juste de l'échantillon)
real_min_date = datetime.date(2013, 1, 1)
real_max_date = datetime.date(2017, 8, 16)

# Valeur par défaut : ce qu'on a réellement en mémoire pour afficher des graphiques au démarrage
loaded_min = df['date'].min().date()
loaded_max = df['date'].max().date()

try:
    date_range = st.sidebar.date_input(
        "📅 Période Globale", 
        value=(loaded_min, loaded_max),
        min_value=real_min_date,
        max_value=real_max_date
    )
except Exception:
    date_range = (loaded_min, loaded_max)

# ---------------------------
# BONUS – SIMULATION IA
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.header("🤖 Simulation")
simulate = st.sidebar.slider("Impact Événementiel (Ventes %)", -50, 100, 0)

# Filtrage final des données
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['store_id'] == selected_store) & (df['item_id'] == selected_item) & (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
else:
    mask = (df['store_id'] == selected_store) & (df['item_id'] == selected_item)

df_filtered = df[mask].copy()

if simulate != 0 and not df_filtered.empty:
    df_filtered["sales"] = df_filtered["sales"] * (1 + simulate / 100)

# ---------------------------
# KPI (INDICATEURS)
# ---------------------------
if df_filtered.empty:
    st.warning("⚠️ Aucune donnée disponible pour cette combinaison Magasin/Produit dans l'échantillon chargé.")
else:
    total_sales = df_filtered['sales'].sum()
    avg_sales = df_filtered['sales'].mean()
    max_sales = df_filtered['sales'].max()

    st.markdown(f"### 📍 Focus : Magasin {selected_store} ({selected_city}) - Article {selected_item}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ventes Totales", f"{total_sales:,.0f} u", f"{simulate}% Simulé" if simulate else None)
    col2.metric("📈 Moyenne Quotidienne", f"{avg_sales:.1f} u")
    col3.metric("🏆 Record de Vente", f"{max_sales:.0f} u")

    st.markdown("---")

    # ---------------------------
    # TABS (STRUCTURE PRO)
    # ---------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Analyse", "📈 Avancé", "📂 Données"])

    # ===========================
    # TAB 1 – VISUALISATION
    # ===========================
    with tab1:
        st.subheader(f"Historique des ventes : {selected_family}")

        fig_line = px.line(
            df_filtered, x='date', y='sales', 
            labels={'date': 'Date', 'sales': 'Unités Vendues'},
            template="plotly_white",
            markers=True
        )
        fig_line.update_traces(line_color="#1f77b4", line_width=2, marker=dict(size=8))
        if len(date_range) == 2:
            fig_line.update_xaxes(range=[date_range[0], date_range[1]], tickformat="%Y-%m-%d")
        else:
            fig_line.update_xaxes(tickformat="%Y-%m-%d")
        st.plotly_chart(fig_line, use_container_width=True)

        # Ajout d'une moyenne glissante pour la tendance
        df_filtered_sorted = df_filtered.sort_values(by="date")
        df_filtered_sorted["MA7"] = df_filtered_sorted["sales"].rolling(window=7, min_periods=1).mean()
        
        fig_trend = px.area(
            df_filtered_sorted, x='date', y='MA7',
            title="Tendance Lissée (Moyenne Mobile 7 jours)",
            labels={'date': 'Date', 'MA7': 'Tendance Ventes'},
            color_discrete_sequence=['#ff7f0e'],
            markers=True
        )
        if len(date_range) == 2:
            fig_trend.update_xaxes(range=[date_range[0], date_range[1]], tickformat="%Y-%m-%d")
        else:
            fig_trend.update_xaxes(tickformat="%Y-%m-%d")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ===========================
    # TAB 2 – ANALYSE AVANCÉE
    # ===========================
    with tab2:
        st.subheader("Saisonnalité & Distribution")
        
        df_filtered['month'] = df_filtered['date'].dt.month
        monthly_sales = df_filtered.groupby('month')['sales'].mean().reset_index()
        month_names = {1:'Jan', 2:'Fév', 3:'Mar', 4:'Avr', 5:'Mai', 6:'Juin', 
                       7:'Juil', 8:'Août', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Déc'}
        monthly_sales['month_name'] = monthly_sales['month'].map(month_names)
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_bar = px.bar(
                monthly_sales, x='month_name', y='sales',
                title="Consommation moyenne mensuelle",
                labels={'month_name': 'Mois', 'sales': 'Moyenne u'},
                color='sales', color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_chart2:
            fig_hist = px.histogram(
                df_filtered, x="sales", nbins=30,
                title="Distribution des Ventes",
                labels={'sales': 'Quantités Vendues'},
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    # ===========================
    # TAB 3 – DATA
    # ===========================
    with tab3:
        st.subheader("Dataset filtré")
        st.dataframe(df_filtered.style.format({'sales': "{:.2f}"}), use_container_width=True)

        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Télécharger CSV",
            csv,
            "data_favorita_filtree.csv",
            "text/csv"
        )
