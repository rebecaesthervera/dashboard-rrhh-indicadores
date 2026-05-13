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
        # URL base de tu Google Sheet actual
        url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.upper()
        # Limpieza de espacios en blanco
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        return pd.DataFrame()

def limpiar_fecha(df, col):
    if col in df.columns:
        s = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
    return pd.Series([pd.NaT] * len(df))

try:
    # --- CARGA AUTOMÁTICA CON TUS GIDs NUEVOS ---
    df_main = cargar_datos("1543772338")  # Panel Dotación
    df_cump = cargar_datos("540729566")   # Cumpleaños
    df_rot = cargar_datos("209126075")    # Rotación (GID proporcionado)
    df_baj = cargar_datos("728077629")    # Bajas (GID proporcionado)
    
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
    
    # Definición de las 4 pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Panel de Dotación", 
        "🎂 Cumpleaños Mensuales", 
        "📉 Rotación Mensual", 
        "❌ Detalle de Bajas"
    ])

    # --- TAB 1: PANEL DE DOTACIÓN (Tu código original) ---
    with tab1:
        if not df_main.empty:
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
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=500)
            with c_der:
                i1, i2, i3, i4 = st.columns(4)
                for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                    if c in df_fil.columns:
                        fig = px.pie(df_fil[c].value_counts().reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=200, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                        ui.plotly_chart(fig, use_container_width=True)
                
                if 'PUESTO' in df_fil.columns:
                    st.plotly_chart(px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', color_discrete_sequence=['#3B82F6'], title="Puestos").update_layout(height=300), use_container_width=True)

    # --- TAB 2: CUMPLEAÑOS (Tu código original) ---
    with tab2:
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        sel_mes = st.selectbox("Mes de consulta", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)
        st.subheader(f"Cumpleaños de {meses[sel_mes-1]}")
        # Aquí continúa tu lógica de tarjetas de cumpleaños...

    # --- TAB 3: ROTACIÓN MENSUAL (AUTOMÁTICA) ---
    with tab3:
        st.header("📉 Indicadores de Rotación (Turnover)")
        if not df_rot.empty:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                # Línea de tiempo del Turnover
                fig_rot_line = px.line(df_rot, x='MES', y='ROTACIÓN', title="Evolución % de Rotación", markers=True, color_discrete_sequence=['#1E3A8A'])
                st.plotly_chart(fig_rot_line, use_container_width=True)
            with col_r2:
                # Barras de Altas y Bajas
                fig_mov = px.bar(df_rot, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Movimientos de Personal", color_discrete_map={"ALTAS": "#3B82F6", "BAJAS": "#EF4444"})
                st.plotly_chart(fig_mov, use_container_width=True)
        else:
            st.info("Cargando datos de rotación desde Google Sheets...")

    # --- TAB 4: DETALLE DE BAJAS (AUTOMÁTICA) ---
    with tab4:
        st.header("❌ Análisis de Bajas")
        if not df_baj.empty:
            # Filtrar solo bajas reales (excluyendo "Activo")
            # Buscamos la columna de antigüedad o fecha de baja para filtrar
            df_egresos = df_baj[df_baj['ANTIGUEDAD'].astype(str).str.contains('años|meses|días', case=False, na=False)].copy()
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                st.plotly_chart(px.pie(df_egresos, names='MOTIVO', title="Causas de Salida", hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe))
            with c_b2:
                # El tipo de baja suele ser la última columna (Voluntaria/Involuntaria)
                col_tipo = df_egresos.columns[-1]
                st.plotly_chart(px.pie(df_egresos, names=col_tipo, title="Tipo de Egreso", hole=0.4, color_discrete_sequence=['#64748B', '#1E3A8A']))
            
            st.plotly_chart(px.histogram(df_egresos, x='ÁREA', color='MOTIVO', title="Bajas por Área y Motivo", barmode='group'))
        else:
            st.info("Cargando detalle de bajas desde Google Sheets...")

except Exception as e:
    st.error(f"Error general en la aplicación: {e}")
