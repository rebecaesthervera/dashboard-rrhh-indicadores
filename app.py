import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RRHH Exincor", layout="wide")
st.title("📊 Gestión Integrada de Capital Humano - Exincor")

@st.cache_data(ttl=600)
def cargar_datos():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.upper()
    if 'LEGAJO' in df.columns:
        df = df.dropna(subset=['LEGAJO'])
    return df

try:
    df = cargar_datos()

    # --- CREACIÓN DE PESTAÑAS ---
    tab_resumen, tab_distribucion, tab_antiguedad, tab_evaluacion = st.tabs([
        "🏠 Resumen General", 
        "📂 Áreas y Perfiles", 
        "⏳ Permanencia", 
        "📈 Desempeño 1-5"
    ])

    with tab_resumen:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Dotación Actual", len(df))
        if 'EDAD' in df.columns:
            col2.metric("Edad Promedio", f"{pd.to_numeric(df['EDAD'], errors='coerce').mean():.1f} años")
        if 'ANTIGÜEDAD' in df.columns:
            col3.metric("Antigüedad Promedio", f"{pd.to_numeric(df['ANTIGÜEDAD'], errors='coerce').mean():.1f} años")
        col4.metric("Empresa", "Exincor")
        
        st.markdown("---")
        st.subheader("⚖️ Indicador de Género")
        if 'GÉNERO' in df.columns:
            fig_gen = px.pie(df, names='GÉNERO', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_gen, use_container_width=True)

    with tab_distribucion:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Distribución por Áreas**")
            if 'ÁREA' in df.columns:
                fig_area = px.pie(df, names='ÁREA', color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_area, use_container_width=True)
        with c2:
            st.write("**Categorías Profesionales**")
            if 'CATEGORÍA' in df.columns:
                fig_cat = px.bar(df['CATEGORÍA'].value_counts().reset_index(), x='CATEGORÍA', y='count')
                st.plotly_chart(fig_cat, use_container_width=True)

    with tab_antiguedad:
        st.subheader("⏱️ Análisis de Permanencia")
        if 'ANTIGÜEDAD' in df.columns:
            df['ANTIGÜEDAD'] = pd.to_numeric(df['ANTIGÜEDAD'], errors='coerce')
            # NUEVO INDICADOR: Rangos de antigüedad
            bins = [0, 2, 5, 10, 20, 50]
            labels = ['Novatos (0-2)', 'Junior (2-5)', 'Seniors (5-10)', 'Expertos (10-20)', 'Históricos (20+)']
            df['RANGO_ANT'] = pd.cut(df['ANTIGÜEDAD'], bins=bins, labels=labels)
            
            fig_ant = px.bar(df['RANGO_ANT'].value_counts().reset_index(), x='RANGO_ANT', y='count', 
                             title="Distribución por Años en la Empresa", color='RANGO_ANT')
            st.plotly_chart(fig_ant, use_container_width=True)

    with tab_evaluacion:
        st.subheader("🎯 Monitoreo de Desempeño (Escala 1-5)")
        st.info("Este módulo utiliza tu escala estandarizada para medir el cumplimiento de objetivos.")
        
        # Simulador de métrica de desempeño si aún no tienes los datos finales
        eval_cols = [c for c in ['EVALUACIÓN', 'KPI', 'DESEMPEÑO'] if c in df.columns]
        if eval_cols:
            avg_eval = pd.to_numeric(df[eval_cols[0]], errors='coerce').mean()
            st.metric("Promedio General de Desempeño", f"{avg_eval:.2f} / 5.0")
        else:
            st.warning("Para activar este panel, agrega columnas de 'EVALUACIÓN' con valores del 1 al 5 en tu Sheet.")

    st.markdown("---")
    st.subheader("📋 Nómina Completa")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar pestañas: {e}")
