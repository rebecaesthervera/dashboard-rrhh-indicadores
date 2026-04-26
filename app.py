import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard RRHH Completo", layout="wide")
st.title("📊 Panel Avanzado de Capital Humano")

# 2. FUNCIÓN DE CARGA Y LIMPIEZA DE DATOS
@st.cache_data(ttl=600)
def cargar_datos():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    df = pd.read_csv(sheet_url)
    
    # NORMALIZACIÓN ROBUSTA
    df.columns = df.columns.str.strip().str.upper()
    
    if 'LEGAJO' in df.columns:
        df = df.dropna(subset=['LEGAJO'])
        
    return df

try:
    df = cargar_datos()

    # --- FILTROS LATERALES ---
    st.sidebar.header("Filtros")
    area_list = ["TODAS"] + sorted(df['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df.columns else ["TODAS"]
    sel_area = st.sidebar.selectbox("Área:", area_list)

    df_plot = df.copy()
    if sel_area != "TODAS":
        df_plot = df[df['ÁREA'] == sel_area]

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("📌 KPIs Generales")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Personal Total", len(df_plot))
    
    if 'EDAD' in df.columns:
        m2.metric("Edad Promedio", f"{pd.to_numeric(df_plot['EDAD'], errors='coerce').mean():.1f} años")
        
    if 'ANTIGÜEDAD' in df.columns:
         m3.metric("Antigüedad Promedio", f"{pd.to_numeric(df_plot['ANTIGÜEDAD'], errors='coerce').mean():.1f} años")
         
    m4.metric("Empresas Gestionadas", "2")

    st.markdown("---")

    # --- INDICADORES DE GÉNERO ---
    st.subheader("⚖️ Distribución de Género")
    if 'GÉNERO' in df_plot.columns:
        # Normalizamos la columna de género a mayúsculas para poder contar bien
        df_plot['GÉNERO_NORM'] = df_plot['GÉNERO'].fillna('OTROS').astype(str).str.strip().str.upper()
        
        # Contamos según las palabras clave más comunes
        hombres = len(df_plot[df_plot['GÉNERO_NORM'].isin(['HOMBRE', 'MASCULINO', 'M'])])
        mujeres = len(df_plot[df_plot['GÉNERO_NORM'].isin(['MUJER', 'FEMENINO', 'F'])])
        total_gender = len(df_plot)
        otros = total_gender - hombres - mujeres
        
        col_g1, col_g2, col_g3 = st.columns(3)
        
        with col_g1:
            st.metric("Hombres", hombres)
            if total_gender > 0:
                st.write(f"{(hombres/total_gender)*100:.1f}% del total")
        
        with col_g2:
            st.metric("Mujeres", mujeres)
            if total_gender > 0:
                st.write(f"{(mujeres/total_gender)*100:.1f}% del total")
                
        with col_g3:
            if otros > 0:
                st.metric("Otros / No especificado", otros)
        
        # Gráfico de torta de género usando la columna original para no perder tu formato
        fig_genero = px.pie(df_plot, names='GÉNERO', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_genero, use_container_width=True)
    else:
        st.info("💡 Columna 'GÉNERO' no encontrada. Pendiente de carga.")

    st.markdown("---")

    # --- SECCIÓN DE GRÁFICOS ---
    st.subheader("📈 Análisis por Categoría y Área")
    col_bar, col_pie = st.columns(2)

    with col_bar:
        st.write("Categoría Profesional")
        if 'CATEGORÍA' in df_plot.columns and not df_plot['CATEGORÍA'].isnull().all():
            fig_cat = px.bar(df_plot['CATEGORÍA'].value_counts().reset_index(),
                             x='CATEGORÍA', y='count', labels={'CATEGORÍA':'Categoría', 'count':'Cantidad'})
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("💡 Columna 'CATEGORÍA' no encontrada o vacía.")

    with col_pie:
        st.write("Distribución por Área")
        if 'ÁREA' in df_plot.columns and not df_plot['ÁREA'].isnull().all():
            fig_area = px.pie(df_plot, names='ÁREA', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.warning("Falta columna 'ÁREA' para mostrar este gráfico.")

    st.markdown("---")
    
    # --- LISTA DE PERSONAL ---
    st.subheader("📋 Lista Detallada de Personal")
    # Busca dinámicamente estas columnas
    cols_common = ['LEGAJO', 'APELLIDO Y NOMBRE', 'NOMBRE COMPLETO', 'CATEGORÍA', 'PUESTO', 'ÁREA', 'EDAD', 'ANTIGÜEDAD', 'GÉNERO', 'TÍTULO']
    cols_present = [c for c in cols_common if c in df.columns]
    
    st.dataframe(df_plot[cols_present], use_container_width=True)

except Exception as e:
    st.error(f"Error en el panel: {e}")
