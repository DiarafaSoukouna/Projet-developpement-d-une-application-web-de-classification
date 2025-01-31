import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter
import pandas as pd
FLASK_API_URL = "http://127.0.0.1:5000/data"

# 🔄 Récupérer les données
response = requests.get(FLASK_API_URL)
if response.status_code == 200:
    data = response.json()
    volume= data["volume"]
    taux = data["taux"] 
    temps = data["temps"]
    categories = data["categories"]
    annees = data["date_evolution"]


else:
    st.error("⚠️ Erreur lors de la récupération des données !")
    st.stop()

# 🎨 Styles Streamlit
st.set_page_config(page_title="📊 Tableau de Bord KPI", layout="wide")

# 🏆 Titre
st.title("📊 Tableau de Bord KPI DanayaFile")

# 📌 **1. Indicateurs Clés sous forme de Cartes**
st.subheader("📌 Indicateurs Clés de Performance")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="color: #333; margin: 0;">📦 Volume Total</h3>
            <h1 style="color: #1f77b4; margin: 0;">{volume:,.0f} Mo</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="color: #333; margin: 0;">📈 Taux Moyen</h3>
            <h1 style="color: #ff7f0e; margin: 0;">{taux:.2f} %</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="color: #333; margin: 0;">⏳ Temps Moyen</h3>
            <h1 style="color: #2ca02c; margin: 0;">{temps:.2f} min</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

category_counts = dict(Counter(categories))
df_categories = pd.DataFrame(category_counts.items(), columns=["Catégorie", "Nombre"])

# 🎨 **4. Graphique en barres**
fig_bar = px.bar(
    df_categories,
    x="Catégorie",
    y="Nombre",
    text="Nombre",
    title="📊 Répartition des Catégories de fichiers",
    color="Catégorie",
    color_discrete_sequence=px.colors.qualitative.Set2,  # Meilleure palette pour lecture
    labels={"Nombre": "Nombre d'occurrences", "Catégorie": "Catégories"},
)

fig_bar.update_traces(textposition="outside", textfont_size=14)
fig_bar.update_layout(
    xaxis_title="Catégories",
    yaxis_title="Nombre d'occurrences",
    showlegend=False,
    template="plotly_white",
    height=500,
)



fig_pie = px.pie(
    df_categories,
    names="Catégorie",
    values="Nombre",
    title="📊 Répartition des Catégories (Camembert)",
    color="Catégorie",
    color_discrete_sequence=px.colors.qualitative.Pastel, 
    hole=0.3, 
    labels={"Nombre": "Nombre d'occurrences", "Catégorie": "Catégories"},
)


fig_pie.update_traces(
    textposition="inside",
    textinfo="percent+label",
    pull=[0.1] * len(df_categories), 
    marker=dict(line=dict(color="#FFFFFF", width=2)), 
)
fig_pie.update_layout(
    showlegend=True,
    template="plotly_white",
    height=500,
    margin=dict(t=50, b=50),
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.plotly_chart(fig_pie, use_container_width=True)


  
date_evolution = data["date_evolution"]

df_dates = pd.DataFrame(date_evolution)

df_annee = df_dates.groupby("annee")["total"].sum().reset_index()
fig_annee = px.line(
    df_annee,
    x="annee",
    y="total",
    title="📈 Tendance des entrées par année",
    markers=True,
    text="total"
)
fig_annee.update_traces(textposition="top center")
fig_annee.update_layout(xaxis_title="Année", yaxis_title="Nombre d'entrées", template="plotly_white")


annees_disponibles = sorted(df_dates["annee"].unique(), reverse=True)
annee_selectionnee = st.selectbox("📅 Sélectionnez une année pour voir les détails par mois :", ["Toutes les années"] + annees_disponibles)


if annee_selectionnee != "Toutes les années":
    df_mois = df_dates[df_dates["annee"] == annee_selectionnee]
    

    mois_order = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    df_mois["mois"] = pd.Categorical(df_mois["mois"], categories=mois_order, ordered=True)
    df_mois = df_mois.groupby("mois")["total"].sum().reset_index()

    fig_mois = px.line(
        df_mois,
        x="mois",
        y="total",
        title=f"📈 Évolution mensuelle pour {annee_selectionnee}",
        markers=True,
        text="total"
    )
    fig_mois.update_traces(textposition="top center")
    fig_mois.update_layout(
        xaxis=dict(title="Mois", tickmode="array", tickvals=mois_order),
        yaxis_title="Nombre d'entrées",
        template="plotly_white"
    )
    st.plotly_chart(fig_mois, use_container_width=True)
else:
    st.plotly_chart(fig_annee, use_container_width=True)