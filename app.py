
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Sistema de Alertas Tempranas – Ingeniería Electrónica")

df = pd.read_csv("datos_alertas.csv")

anio = st.selectbox("Año", sorted(df["Año"].unique()))
mes = st.selectbox("Mes", sorted(df["Mes"].unique()))

asignaturas = st.multiselect(
    "Asignaturas",
    sorted(df["Asignatura"].unique())
)

df_f = df[(df["Año"] == anio) & (df["Mes"] == mes)]
if asignaturas:
    df_f = df_f[df_f["Asignatura"].isin(asignaturas)]

conteo = df_f["Asignatura"].value_counts().reset_index()
conteo.columns = ["Asignatura", "Frecuencia"]

fig = px.bar(
    conteo,
    x="Asignatura",
    y="Frecuencia",
    text="Frecuencia"
)

st.plotly_chart(fig, use_container_width=True)
