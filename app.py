import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión RRHH Exincor", layout="wide")

# 2. COLORES CORPORATIVOS
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=30)
def cargar_datos(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
        # Cargamos el CSV directamente
        df = pd.read_csv(url)
        
        # Paso 1: Limpiar nombres de columnas (quitar espacios y pasar a MAYÚSCULAS)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Paso 2: Resolver nombres duplicados (como 'TIPO DE BAJA') automáticamente
        if df.columns.duplicated().any():
            # Esto agrega un sufijo .1, .2 a las columnas repetidas para que no den error
            df.columns = pd.io.common.dedup_names(df.columns, is_duplicated=df.columns.duplicated())
            
        # Paso 3: Limpiar el contenido de las celdas
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"Error al cargar GID {gid}: {e}")
        return pd.DataFrame()

def limpiar_fecha(df, col):
    if col in df.columns:
        s = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
    return pd.Series([pd.NaT] * len(df))

try:
    # --- CARGA AUTOMÁTICA DE DATOS ---
    df_main = cargar_datos("1543772338")  # Dotación
    df_cump = cargar_datos("540729566")   # Cumpleaños
    df_rot = cargar_datos("209126075")    # Rotación
    df_baj = cargar_datos("728077629")    # BAJA EN ARCA
    
    hoy = datetime.now()

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f]
        if archivos: st.image(archivos[0], width=150)
    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Panel de Dotación", 
        "🎂 Cumpleaños Mensuales", 
        "📉 Rotación Mensual", 
        "❌ Detalle de Bajas"
    ])

    # --- TAB 3: ROTACIÓN ---
    with tab3:
        st.header("📉 Análisis de Rotación Mensual")
        if not df_rot.empty:
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.plotly_chart(px.line(df_rot, x='MES', y='ROTACIÓN', title="Evolución % Turnover", markers=True), use_container_width=True)
            with c_r2:
                st.plotly_chart(px.bar(df_rot, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Movimientos Mensuales"), use_container_width=True)

    # --- TAB 4: BAJA EN ARCA ---
    with tab4:
        st.header("❌ Detalle de Bajas (ARCA)")
        if not df_baj.empty:
            # Filtramos para que solo aparezcan los que ya se fueron (no "Activos")
            df_egresos = df_baj[df_baj['ANTIGUEDAD'].astype(str).str.contains('años|meses|días', case=False, na=False)].copy()
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                st.plotly_chart(px.pie(df_egresos, names='MOTIVO', title="Principales Motivos de Salida", hole=0.4), use_container_width=True)
            with c_b2:
                # Buscamos la columna de tipo de baja (usamos la última por si se renombró por duplicado)
                col_tipo = [c for c in df_egresos.columns if 'TIPO DE BAJA' in c][-1]
                st.plotly_chart(px.pie(df_egresos, names=col_tipo, title="Tipo de Egreso (Voluntaria/Involuntaria)", hole=0.4), use_container_width=True)
            
            st.plotly_chart(px.histogram(df_egresos, x='ÁREA', color='MOTIVO', title="Distribución de Bajas por Departamento", barmode='group'), use_container_width=True)

    # (Aquí siguen tus códigos de Tab 1 y Tab 2 que ya funcionan)

except Exception as e:
    st.error(f"Error general en la aplicación: {e}")
