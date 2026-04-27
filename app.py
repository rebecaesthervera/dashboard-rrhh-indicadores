import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Exincor", layout="wide")

# 2. COLORES CORPORATIVOS
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=60)
def cargar_datos(gid):
    try:
        sheet_url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip().str.upper()
        return df
    except:
        return pd.DataFrame()

try:
    # Carga de datos
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

    # --- ENCABEZADO CON LOGO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = os.listdir('.')
        imagen_logo = next((f for f in archivos if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f), None)
        if imagen_logo:
            st.image(imagen_logo, width=150)
        else:
            st.info("ℹ️ Sube el logo a GitHub")

    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Dotación Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños del Mes"])

    with tab1:
        # --- FILTROS ---
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        with col_f1:
            conv_opts = ["Todos"] + sorted(df_main['CONVENIO'].dropna().unique().tolist()) if 'CONVENIO' in df_main.columns else ["Todos"]
            sel_conv = st.selectbox("Convenio", conv_opts)
        with col_f2:
            resp_opts = ["Todos"] + sorted(df_main['RESPONSABLE DIRECTO'].dropna().unique().tolist()) if 'RESPONSABLE DIRECTO' in df_main.columns else ["Todos"]
            sel_resp = st.selectbox("Responsable Directo", resp_opts)
        with col_f3:
            tipo_col = next((c for c in df_main.columns if 'CONTRATACIÓN' in c or 'CONTRATACION' in c), 'TIPO DE CONTRATACIÓN')
            tipo_opts = ["Todos"] + sorted(df_main[tipo_col].dropna().unique().tolist()) if tipo_col in df_main.columns else ["Todos"]
            sel_tipo = st.selectbox("Tipo Contratación", tipo_opts)
        with col_f4:
            area_opts = ["Todas"] + sorted(df_main['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df_main.columns else ["Todas"]
            sel_area = st.selectbox("Área", area_opts)
        with col_f5:
            nombres_opts = ["Todos"] + sorted(df_main['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df_main.columns else ["Todos"]
            sel_nombre = st.selectbox("Personal", nombres_opts)

        # Aplicar Filtros
        df_fil = df_main.copy()
        if 'CONVENIO' in df_fil.columns and sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if 'RESPONSABLE DIRECTO' in df_fil.columns and sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if tipo_col in df_fil.columns and sel_tipo != "Todos": df_fil = df_fil[df_fil[tipo_col] == sel_tipo]
        if 'ÁREA' in df_fil.columns and sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if 'APELLIDO Y NOMBRE' in df_fil.columns and sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        # --- CUERPO ---
        col_izq, col_der = st.columns([1.2, 3.8])
        with col_izq:
            st.metric("Total Activos", len(df_fil))
            if 'APELLIDO Y NOMBRE' in df_fil.columns:
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600, use_container_width=True)

        with col_der:
            c1, c2, c3, c4 = st.columns(4)
            columnas_anillo = ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS']
            titulos_anillo = ['Género', 'Categoría', 'Contratación', 'Centro Costos']
            
            for col_ui, col_df, tit in zip([c1, c2, c3, c4], columnas_anillo, titulos_anillo):
                with col_ui:
                    if col_df in df_fil.columns:
                        d_pie = df_fil[col_df].value_counts().reset_index()
                        fig = px.pie(d_pie, names=col_df, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=200, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': tit, 'x': 0.5})
                        st.plotly_chart(fig, use_container_width=True)

            if 'PUESTO' in df_fil.columns:
                df_p = df_fil['PUESTO'].value_counts().reset_index()
                fig_p = px.bar(df_p, x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Dotación por Puesto")
                fig_p.update_layout(height=300, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)

    with tab2:
        st.subheader("🎂 Celebraciones del Mes")
        
        # BUSCADOR FLEXIBLE DE FECHAS
        col_fecha_nac = next((c for c in df_cump.columns if 'FECHA' in c or 'NACIMIENTO' in c), None)
        col_fecha_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), None)

        if col_fecha_nac and not df_cump.empty:
            df_cump['FECHA_NAC'] = pd.to_datetime(df_cump[col_fecha_nac], errors='coerce', dayfirst=True)
            mes_actual = datetime.now().month
            hoy = datetime.now()
            
            cumples_mes = df_cump[df_cump['FECHA_NAC'].dt.month == mes_actual].copy()
            
            if not cumples_mes.empty:
                cumples_mes['DIA'] = cumples_mes['FECHA_NAC'].dt.day
                cumples_mes = cumples_mes.sort_values('DIA')
                
                cols_c = st.columns(3)
                for i, row in cumples_mes.reset_index().iterrows():
                    with cols_c[i % 3]:
                        with st.container(border=True):
                            st.markdown(f"### 📅 Día {int(row['DIA'])}")
                            st.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                            
                            # Cálculo de Antigüedad
                            if col_fecha_ing:
                                match = df_main[df_main['APELLIDO Y NOMBRE'] == row['APELLIDO Y NOMBRE']]
                                if not match.empty:
                                    f_ing = pd.to_datetime(match[col_fecha_ing].values[0], errors='coerce')
                                    if not pd.isnull(f_ing):
                                        anos = hoy.year - f_ing.year - ((hoy.month, hoy.day) < (f_ing.month, f_ing.day))
                                        st.markdown(f"⭐ **Trayectoria:** {max(0, anos)} años")
                            
                            st.divider()
                            st.button("Felicitar ✨", key=f"hb_{i}", use_container_width=True)
            else:
                st.info("No hay cumpleaños registrados para este mes.")

except Exception as e:
    st.error(f"Error detectado: {e}")
