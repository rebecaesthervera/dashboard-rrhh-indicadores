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
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.upper()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except:
        return pd.DataFrame()

def limpiar_fecha(df, col):
    if col in df.columns:
        s = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
    return pd.Series([pd.NaT] * len(df))

try:
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    hoy = datetime.now()

    # --- LÓGICA DE GLOBOS ---
    col_f_nac = 'FECHA NACIMIENTO'
    df_cump['DT_NAC'] = limpiar_fecha(df_cump, col_f_nac)
    cumple_hoy = df_cump[(df_cump['DT_NAC'].dt.month == hoy.month) & (df_cump['DT_NAC'].dt.day == hoy.day)]
    if not cumple_hoy.empty:
        st.balloons()

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f]
        if archivos: st.image(archivos[0], width=150)
    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # NUEVAS PESTAÑAS AGREGADAS AQUÍ
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Panel de Dotación", 
        "🎂 Cumpleaños Mensuales", 
        "📉 Rotación Mensual", 
        "❌ Detalle de Bajas"
    ])

    with tab1:
        # --- TU CÓDIGO ACTUAL DE DOTACIÓN ---
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        def get_opts(df, col, d="Todos"):
            return [d] + sorted(df[col].dropna().unique().tolist()) if col in df.columns else [d]
        with col_f1: sel_conv = st.selectbox("Convenio", get_opts(df_main, 'CONVENIO'))
        with col_f2: sel_resp = st.selectbox("Responsable Directo", get_opts(df_main, 'RESPONSABLE DIRECTO'))
        tipo_col = next((c for c in df_main.columns if 'CONTRATACIÓN' in c or 'CONTRATACION' in c), 'TIPO DE CONTRATACIÓN')
        with col_f3: sel_tipo = st.selectbox("Tipo Contratación", get_opts(df_main, tipo_col))
        with col_f4: sel_area = st.selectbox("Área", get_opts(df_main, 'ÁREA', "Todas"))
        with col_f5: sel_nombre = st.selectbox("Personal", get_opts(df_main, 'APELLIDO Y NOMBRE'))

        df_fil = df_main.copy()
        if sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if sel_tipo != "Todos": df_fil = df_fil[df_fil[tipo_col] == sel_tipo]
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        c_izq, c_der = st.columns([1, 4])
        with c_izq:
            st.metric("Total Activos", len(df_fil))
            st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600, use_container_width=True)
        with c_der:
            i1, i2, i3, i4 = st.columns(4)
            for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                if c in df_fil.columns:
                    fig = px.pie(df_fil[c].value_counts().reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                    ui.plotly_chart(fig, use_container_width=True)
            
            if 'PUESTO' in df_fil.columns:
                fig_p = px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Puestos")
                st.plotly_chart(fig_p.update_layout(height=300), use_container_width=True)

    with tab2:
        # --- TU CÓDIGO ACTUAL DE CUMPLEAÑOS ---
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        sel_mes = st.selectbox("Mes de consulta", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)
        st.subheader(f"Cumpleaños en {meses[sel_mes-1]}")
        # ... (aquí sigue el resto de tu lógica de tab2)

    # --- NUEVA PESTAÑA 3: ROTACIÓN ---
    with tab3:
        st.header("📉 Análisis de Rotación Mensual")
        archivo_rot = st.file_uploader("Subí tu planilla de Rotación", type=["xlsx"], key="u_rot")
        if archivo_rot:
            df_r = pd.read_excel(archivo_rot)
            col_rot1, col_rot2 = st.columns(2)
            with col_rot1:
                st.plotly_chart(px.line(df_r, x='MES', y='ROTACIÓN', title="Evolución % Turnover", markers=True))
            with col_rot2:
                st.plotly_chart(px.bar(df_r, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Movimientos"))

    # --- NUEVA PESTAÑA 4: DETALLE DE BAJAS ---
    with tab4:
        st.header("❌ Detalle de Bajas Enero - Abril")
        archivo_baj = st.file_uploader("Subí tu planilla de Bajas", type=["xlsx"], key="u_baj")
        if archivo_baj:
            df_b = pd.read_excel(archivo_baj)
            # Solo procesamos los que NO dicen "Activo"
            df_real_bajas = df_b[df_b['ANTIGUEDAD'] != 'Activo'].copy()
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                st.plotly_chart(px.pie(df_real_bajas, names='MOTIVO', title="Causas de Salida", hole=0.4))
            with c_b2:
                st.plotly_chart(px.pie(df_real_bajas, names=df_real_bajas.columns[-1], title="Tipo de Baja", hole=0.4))
            
            st.plotly_chart(px.histogram(df_real_bajas, x='ÁREA', color='MOTIVO', title="Bajas por Área"))

except Exception as e:
    st.error(f"Error: {e}")
