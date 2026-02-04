# -*- coding: utf-8 -*-
"""
Dashboard de Alertas Tempranas - Ingeniería Electrónica
Versión Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import textwrap
from collections import Counter
import string

# Importación opcional de wordcloud
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    st.warning("⚠️ La librería wordcloud no está disponible. La pestaña de Nube de Palabras estará deshabilitada.")

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Alertas Tempranas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de estilo para matplotlib
sns.set(style="whitegrid")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

# Colores personalizados
color_barras = "#a00017"
color_titulo = "#420009"
color_ejes = "#36050c"

# ============================================================
#                   CARGAR DATOS
# ============================================================

@st.cache_data
def cargar_datos():
    """Carga los datos desde Google Sheets"""
    sheet_id = "1uYVrZU-DhCiEwqkpToGDlVBuTB5LVFNBQV2-18N_YBU"
    sheet_name = "Respuestas de formulario 1"
    sheet_name_url = sheet_name.replace(" ", "%20")
    
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_url}"
    
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    # Definir columnas clave
    col_asignatura = "Por favor seleccione el curso"
    col_fecha = "Marca temporal"
    col_preg1 = "¿Cuál cree que es la principal razón por su bajo desempeño en el primer previo de este curso?"
    col_preg2 = "¿Alguna otra razón por la cual tuvo bajo desempeño en el primer previo de este curso?"
    
    # Filtrar columnas
    df_filtered = df[[col_asignatura, col_fecha, col_preg1, col_preg2]].copy()
    
    # Convertir fecha y extraer año/mes
    df_filtered[col_fecha] = pd.to_datetime(df_filtered[col_fecha], errors="coerce")
    df_filtered["Año"] = df_filtered[col_fecha].dt.year
    df_filtered["Mes"] = df_filtered[col_fecha].dt.month
    
    return df_filtered, col_asignatura, col_preg1, col_preg2

# Cargar datos
try:
    df_filtered, col_asignatura, col_preg1, col_preg2 = cargar_datos()
    st.success("✅ Datos cargados correctamente")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
    st.stop()

# ============================================================
#                   TÍTULO Y DESCRIPCIÓN
# ============================================================

st.title("🎓 Sistema de Alertas Tempranas – Ingeniería Electrónica")
st.markdown("---")

# ============================================================
#                   SIDEBAR - FILTROS
# ============================================================

st.sidebar.header("🔍 Filtros")

# Filtro de año
años_disponibles = sorted(df_filtered["Año"].dropna().unique())
año_seleccionado = st.sidebar.selectbox(
    "Selecciona el año:",
    options=años_disponibles,
    index=0 if años_disponibles else None
)

# Filtro de mes
meses_disponibles = sorted(df_filtered["Mes"].dropna().unique())
mes_seleccionado = st.sidebar.selectbox(
    "Selecciona el mes:",
    options=meses_disponibles,
    index=0 if meses_disponibles else None
)

# Filtro de asignaturas
asignaturas_disponibles = sorted(df_filtered[col_asignatura].dropna().unique())
asignaturas_seleccionadas = st.sidebar.multiselect(
    "Selecciona asignaturas:",
    options=asignaturas_disponibles,
    default=asignaturas_disponibles[:1] if asignaturas_disponibles else []
)

# ============================================================
#                   FILTRAR DATOS
# ============================================================

# Filtrar por año y mes
df_filtrado = df_filtered[
    (df_filtered["Año"] == año_seleccionado) & 
    (df_filtered["Mes"] == mes_seleccionado)
]

# Filtrar por asignaturas si hay selección
if asignaturas_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado[col_asignatura].isin(asignaturas_seleccionadas)]

# ============================================================
#                   MÉTRICAS GENERALES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Total de Reportes", len(df_filtrado))

with col2:
    st.metric("📚 Asignaturas", df_filtrado[col_asignatura].nunique())

with col3:
    st.metric("📅 Período", f"{año_seleccionado}-{mes_seleccionado:02d}")

st.markdown("---")

# ============================================================
#                   TABS PARA DIFERENTES VISUALIZACIONES
# ============================================================

if WORDCLOUD_AVAILABLE:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Reportes por Asignatura", 
        "📈 Razones del Bajo Desempeño",
        "🔥 Asignatura vs Razón",
        "☁️ Nube de Palabras"
    ])
else:
    tab1, tab2, tab3 = st.tabs([
        "📊 Reportes por Asignatura", 
        "📈 Razones del Bajo Desempeño",
        "🔥 Asignatura vs Razón"
    ])
    tab4 = None

# ============================================================
#                   TAB 1: REPORTES POR ASIGNATURA
# ============================================================

with tab1:
    st.header("Cantidad de Reportes por Asignatura")
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos para los filtros seleccionados")
    else:
        # Gráfico con Plotly (interactivo)
        conteo_asignaturas = df_filtrado[col_asignatura].value_counts().reset_index()
        conteo_asignaturas.columns = ["Asignatura", "Frecuencia"]
        
        fig_asignaturas = px.bar(
            conteo_asignaturas,
            x="Asignatura",
            y="Frecuencia",
            text="Frecuencia",
            color_discrete_sequence=[color_barras]
        )
        
        fig_asignaturas.update_layout(
            xaxis_title="Asignatura",
            yaxis_title="Frecuencia",
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig_asignaturas, use_container_width=True)
        
        # Opción para descargar gráfico estático
        if st.button("📥 Descargar gráfico (PNG)", key="btn_asignatura"):
            fig_static, ax = plt.subplots(figsize=(10, 6))
            df_filtrado[col_asignatura].value_counts().plot(
                kind="bar",
                color=color_barras,
                edgecolor="black",
                ax=ax
            )
            plt.title(f"Reportes por Asignatura ({año_seleccionado}-{mes_seleccionado})", 
                     color=color_titulo, fontweight="bold")
            plt.ylabel("Frecuencia", color=color_ejes)
            plt.xlabel("Asignatura", color=color_ejes)
            plt.xticks(rotation=45, ha="right")
            plt.grid(axis="y", linestyle="--", alpha=0.4)
            plt.tight_layout()
            
            fig_static.savefig("/tmp/grafica_asignatura.png", format="png", bbox_inches="tight", dpi=300)
            
            with open("/tmp/grafica_asignatura.png", "rb") as file:
                st.download_button(
                    label="💾 Descargar PNG",
                    data=file,
                    file_name=f"grafica_asignatura_{año_seleccionado}_{mes_seleccionado}.png",
                    mime="image/png"
                )
            plt.close()

# ============================================================
#                   TAB 2: RAZONES DEL BAJO DESEMPEÑO
# ============================================================

with tab2:
    st.header("Razones del Bajo Desempeño")
    
    if df_filtrado.empty:
        st.warning("⚠️ No hay datos para los filtros seleccionados")
    else:
        # Contar razones
        conteo_razones = df_filtrado[col_preg1].value_counts().reset_index()
        conteo_razones.columns = ["Razón", "Frecuencia"]
        
        # Gráfico interactivo
        fig_razones = px.bar(
            conteo_razones,
            x="Razón",
            y="Frecuencia",
            text="Frecuencia",
            color_discrete_sequence=[color_barras]
        )
        
        fig_razones.update_layout(
            xaxis_title="Razón",
            yaxis_title="Frecuencia",
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig_razones, use_container_width=True)
        
        # Mostrar tabla de datos
        st.subheader("📋 Detalle de Frecuencias")
        st.dataframe(conteo_razones, use_container_width=True)

# ============================================================
#                   TAB 3: HEATMAP ASIGNATURA VS RAZÓN
# ============================================================

with tab3:
    st.header("Relación: Asignatura vs Razón del Bajo Desempeño")
    
    # Filtrado solo por año para el heatmap
    df_heatmap = df_filtered[df_filtered["Año"] == año_seleccionado]
    
    if asignaturas_seleccionadas:
        df_heatmap = df_heatmap[df_heatmap[col_asignatura].isin(asignaturas_seleccionadas)]
    
    if df_heatmap.empty:
        st.warning("⚠️ No hay datos para los filtros seleccionados")
    else:
        # Crear tabla cruzada
        tabla_cruzada = pd.crosstab(df_heatmap[col_asignatura], df_heatmap[col_preg1])
        
        # Crear heatmap
        fig_heatmap, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(tabla_cruzada, annot=True, fmt="d", cmap="Reds", ax=ax)
        
        plt.title(f"Asignatura vs Razón del Bajo Desempeño (Año: {año_seleccionado})", 
                 fontsize=16, fontweight="bold")
        plt.xlabel("Razón", fontsize=12)
        plt.ylabel("Asignatura", fontsize=12)
        
        # Ajustar etiquetas
        labels = [textwrap.fill(label.get_text(), width=30) for label in ax.get_xticklabels()]
        ax.set_xticklabels(labels, rotation=30, ha="right")
        
        plt.tight_layout()
        
        st.pyplot(fig_heatmap)
        plt.close()
        
        # Mostrar tabla de datos
        st.subheader("📊 Tabla de Frecuencias")
        st.dataframe(tabla_cruzada, use_container_width=True)

# ============================================================
#                   TAB 4: NUBE DE PALABRAS
# ============================================================

if tab4 is not None and WORDCLOUD_AVAILABLE:
    with tab4:
        st.header("Nube de Palabras sobre Causas del Bajo Desempeño")
        
        if df_filtered[col_preg1].dropna().empty:
            st.warning("⚠️ No hay datos suficientes para generar la nube de palabras")
        else:
            # Stopwords personalizadas
            stopwords_extra = {
                "me", "si", "hay", "porque", "suficiente", "ya", "solo", "más", "menos",
                "muy", "puede", "puedo", "fue", "soy", "estoy", "era", "esta", "ese", "eso",
                "lo", "la", "las", "los", "el", "un", "una", "uno", "unos", "unas",
                "al", "del", "de", "por", "con", "para", "sin", "sobre", "entre",
                "que", "se", "yo", "tu", "mi"
            }
            
            # Construir texto
            texto = " ".join(df_filtered[col_preg1].dropna())
            texto = texto.lower()
            texto = texto.translate(str.maketrans("", "", string.punctuation))
            
            tokens = texto.split()
            
            # Filtrar palabras
            palabras_filtradas = [
                t for t in tokens
                if t not in stopwords_extra and len(t) > 2
            ]
            
            # Crear bigramas
            bigramas = []
            for w1, w2 in zip(tokens, tokens[1:]):
                if (w1 not in stopwords_extra or w2 not in stopwords_extra) \
                   and len(w1) > 2 and len(w2) > 2:
                    bigramas.append(f"{w1} {w2}")
            
            # Contar frecuencias
            frecuencias = Counter()
            for palabra in palabras_filtradas:
                frecuencias[palabra] += 1
            for bg in bigramas:
                frecuencias[bg] += 2
            
            if not frecuencias:
                st.warning("⚠️ No hay palabras significativas después de la limpieza")
            else:
                # Generar nube de palabras
                wordcloud = WordCloud(
                    width=1200,
                    height=600,
                    background_color="white",
                    colormap="Reds",
                    max_words=300
                ).generate_from_frequencies(frecuencias)
                
                # Mostrar
                fig_wordcloud, ax = plt.subplots(figsize=(16, 8))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                plt.title("Nube de Palabras: Causas del Bajo Desempeño", 
                         fontsize=18, fontweight="bold")
                
                st.pyplot(fig_wordcloud)
                plt.close()
                
                # Mostrar palabras más frecuentes
                st.subheader("🔤 Palabras/Frases Más Frecuentes")
                palabras_top = pd.DataFrame(
                    frecuencias.most_common(20),
                    columns=["Palabra/Frase", "Frecuencia"]
                )
                st.dataframe(palabras_top, use_container_width=True)

# ============================================================
#                   FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Sistema de Alertas Tempranas - Ingeniería Electrónica</p>
        <p style='font-size: 0.8em; color: gray;'>Desarrollado con Streamlit 🚀</p>
    </div>
    """,
    unsafe_allow_html=True
)
