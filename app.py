import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dashboard RRHH Avanzado", layout="wide")
st.title("📊 Indicadores Visuales de Capital Humano")

# 2. CARGA DE DATOS
@st.cache_data(ttl=600)
def cargar_datos():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.upper()
    
    # Limpieza de filas vacías basada en Legajo
    if 'LEGAJO' in df.columns:
        df = df.dropna(subset=['LEGAJO'])
    return df

try:
    df = cargar_datos()
    
    # --- FILTROS LATERALES ---
    st.sidebar.header("Filtros de Visualización")
    area_list = ["TODAS"] + sorted(df['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df.columns else ["TODAS"]
    sel_area = st.sidebar.selectbox("Filtrar por Área:", area_list)
    
    df_plot = df.copy()
    if sel_area != "TODAS":
        df_plot = df[df['ÁREA'] == sel_area]

    # --- MÉTRICAS RÁPIDAS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Personal en Vista", len(df_plot))
    if 'EDAD' in df.columns:
        m2.metric("Edad Promedio", f"{pd.to_numeric(df_plot['EDAD'], errors='coerce').mean():.1f} años")
    m3.metric("Empresas", "Construcción / Cartón")

    st.markdown("---")

    # --- SECCIÓN DE GRÁFICOS ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("🏢 Distribución por Áreas")
        if 'ÁREA' in df.columns:
            fig_area = px.pie(df_plot, names='ÁREA', hole=0.4, 
                             color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.warning("Falta columna 'ÁREA' para mostrar este gráfico.")

    with col_der:
        st.subheader("👥 Personal por Categoría")
        if 'CATEGORÍA' in df.columns:
            fig_cat = px.bar(df_plot['CATEGORÍA'].value_counts().reset_index(), 
                            x='index', y='CATEGORÍA', labels={'index':'Categoría', 'CATEGORÍA':'Cantidad'})
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("💡 Columna 'CATEGORÍA' no encontrada. Pendiente de carga.")

    st.markdown("---")

    col_bot1, col_bot2 = st.columns(2)

    with col_bot1:
        st.subheader("🎂 Rangos Etarios (Edades)")
        if 'EDAD' in df.columns:
            # Convertimos a numérico por seguridad
            df_plot['EDAD'] = pd.to_numeric(df_plot['EDAD'], errors='coerce')
            fig_edad = px.histogram(df_plot, x="EDAD", nbins=10, 
                                   labels={'EDAD':'Edad'}, 
                                   color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig_edad, use_container_width=True)
        else:
            st.warning("Falta columna 'EDAD' para el histograma.")

    with col_bot2:
        st.subheader("🎓 Nivel Académico / Título")
        if 'TÍTULO' in df.columns:
            fig_tit = px.pie(df_plot, names='TÍTULO', 
                            color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_tit, use_container_width=True)
        else:
            st.info("💡 Columna 'TÍTULO' no encontrada. Pendiente de carga.")

except Exception as e:
    st.error(f"Error en la visualización: {e}")
