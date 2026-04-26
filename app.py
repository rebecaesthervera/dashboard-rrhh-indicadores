import streamlit as st
import pandas as pd

# 1. Configuración general de la página
st.set_page_config(page_title="Dashboard RRHH", layout="wide")
st.title("📊 Panel de Indicadores y Seguimiento de RRHH")

# 2. Conexión con la base de datos (Google Sheets)
@st.cache_data(ttl=600) # Actualiza los datos cada 10 minutos
def cargar_datos():
    # Transformamos tu enlace para extraer el CSV directamente usando el GID proporcionado
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    df = pd.read_csv(sheet_url)
    return df

try:
    df = cargar_datos()
    
    # 3. Indicadores Generales (Headcount)
    st.header("👥 Visión General de la Nómina")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Personal Activo", len(df))
    with col2:
        # Verificamos si existe la columna EDAD para calcular promedios
        if 'EDAD' in df.columns:
            st.metric("Promedio de Edad", f"{pd.to_numeric(df['EDAD'], errors='coerce').mean():.1f} años")
    with col3:
        if 'ANTIGÜEDAD' in df.columns:
             st.metric("Antigüedad Promedio", f"{pd.to_numeric(df['ANTIGÜEDAD'], errors='coerce').mean():.1f} años")

    st.markdown("---")

    # 4. Filtros por Áreas de Gestión
    st.header("🏢 Distribución por Áreas")
    st.write("Filtro dinámico de personal según la estructura organizativa.")
    
    # Opciones que diferencian claramente las áreas gerenciales y operativas
    areas_disponibles = ["Todas", "Administración Contable", "Finanzas", "Producción", "Comercialización", "Mantenimiento"]
    area_seleccionada = st.selectbox("Seleccione el Área a visualizar:", areas_disponibles)
    
    if area_seleccionada != "Todas":
        df_filtrado = df[df['ÁREA'].str.contains(area_seleccionada, case=False, na=False)]
    else:
        df_filtrado = df
        
    st.dataframe(df_filtrado[['LEGAJO', 'APELLIDO Y NOMBRE', 'PUESTO', 'ÁREA']], use_container_width=True)

    st.markdown("---")

    # 5. Módulo de Evaluaciones de Desempeño y Capacitaciones
    st.header("📈 Desempeño y Plan de Capacitaciones 2026")
    
    tab1, tab2 = st.tabs(["Métricas de Evaluación", "Propuestas de Mejora"])
    
    with tab1:
        st.subheader("Medición de KPIs y Competencias Técnicas")
        st.info("ℹ️ Sistema de puntuación: Todos los factores de evaluación y métricas están estandarizados en una escala del 1 al 5.")
        
        empleado_eval = st.selectbox("Seleccionar colaborador para evaluación:", df['APELLIDO Y NOMBRE'].dropna().unique())
        puntaje = st.slider(f"Calificación general para {empleado_eval}:", min_value=1, max_value=5, value=3)
        st.button("Registrar Evaluación")

    with tab2:
        st.subheader("Gestión de Propuestas de Mejora")
        st.write("Cálculo de puntaje de desempeño según el volumen de mejoras implementadas por el colaborador.")
        
        propuestas_implementadas = st.number_input("Cantidad de propuestas implementadas:", min_value=0, step=1)
        
        # Lógica de puntuación escalonada
        if propuestas_implementadas >= 3:
            score_mejoras = 5
        elif propuestas_implementadas == 2:
            score_mejoras = 4
        elif propuestas_implementadas == 1:
            score_mejoras = 3
        else:
            score_mejoras = 1
            
        st.success(f"Puntaje asignado por propuestas de mejora: **{score_mejoras}** (Escala 1 al 5)")

except Exception as e:
    st.error(f"Error al cargar los datos. Verifica los permisos del enlace. Detalle técnico: {e}")
