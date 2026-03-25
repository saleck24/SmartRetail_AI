import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ERP Stock Dashboard - Favorita", layout="wide")

st.title("ERP Intelligent - Analyse Real-World (Favorita)")
st.markdown("Analyse des tendances de ventes réelles d'une chaîne de supermarchés (Équateur).")

@st.cache_data
def load_data():
    # Chargement d'un échantillon pour la fluidité (1 million de lignes)
    df = pd.read_csv("data/train.csv", nrows=1000000)
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

with st.spinner('Chargement des données Favorita (Échantillon)...'):
    df = load_data()

# Filtres Latéraux (Sidebar)
st.sidebar.header("Filtres Métiers")

# Choix de la ville (plus parlant qu'un numéro)
cities = sorted(df['city'].unique())
selected_city = st.sidebar.selectbox("Ville", cities)

# Filtrer les magasins de cette ville
stores_in_city = sorted(df[df['city'] == selected_city]['store_id'].unique())
selected_store = st.sidebar.selectbox("Numéro du Magasin", stores_in_city)

# Choix de la famille de produits
families = sorted(df['family'].unique())
selected_family = st.sidebar.selectbox("Catégorie de Produits", families)

# Filtrer les produits de cette famille
items_in_family = sorted(df[df['family'] == selected_family]['item_id'].unique())
selected_item = st.sidebar.selectbox("Code Article", items_in_family)

# Filtrage final des données
mask = (df['store_id'] == selected_store) & (df['item_id'] == selected_item)
df_filtered = df[mask].copy()

# KPIs Métiers (Headings)
total_sales = df_filtered['sales'].sum()
avg_sales = df_filtered['sales'].mean()
max_sales = df_filtered['sales'].max()

st.markdown(f"### Indicateurs : Magasin {selected_store} ({selected_city}) - Article {selected_item}")
col1, col2, col3 = st.columns(3)
col1.metric("Ventes Totales", f"{total_sales:,.0f} kg/u")
col2.metric("Moyenne Quotidienne", f"{avg_sales:.1f}")
col3.metric("Record de Vente", f"{max_sales:.0f}")

st.markdown("---")

if not df_filtered.empty:
    # Graphique Linéaire
    fig_line = px.line(df_filtered, x='date', y='sales', 
                       title=f"Historique des ventes : {selected_family}",
                       labels={'date': 'Date', 'sales': 'Quantité'})
    st.plotly_chart(fig_line, width='stretch')

    # Saisonnalité
    df_filtered['month'] = df_filtered['date'].dt.month
    monthly_sales = df_filtered.groupby('month')['sales'].mean().reset_index()
    month_names = {1:'Jan', 2:'Fév', 3:'Mar', 4:'Avr', 5:'Mai', 6:'Juin', 
                   7:'Juil', 8:'Août', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Déc'}
    monthly_sales['month_name'] = monthly_sales['month'].map(month_names)
    
    fig_bar = px.bar(monthly_sales, x='month_name', y='sales',
                     title="Consommation moyenne par mois",
                     labels={'month_name': 'Mois', 'sales': 'Moyenne'},
                     color='sales', color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, width='stretch')
else:
    st.warning("Aucune donnée disponible pour cette combinaison Magasin/Produit dans l'échantillon chargé.")

st.success("Analyse Favorita chargée avec succès.")
