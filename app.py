import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
        try:
            st.image("Logotipo_Exincor_Final.png", width=150)
        except:
            st.info("ℹ️ Sube 'Logotipo_Exincor_Final.png' a GitHub")

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
            tipo_col = 'TIPO DE CONTRATACIÓN'
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
        if sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if sel_tipo != "Todos": df_fil = df_fil[df_fil[tipo_col] == sel_tipo]
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        # --- CUERPO DEL DASHBOARD ---
        col_izq, col_der = st.columns([1.2, 3.8])

        with col_izq:
            st.metric("Total Activos", len(df_fil))
            st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600, use_container_width=True)

        with col_der:
            # Fila 1: 4 Anillos
            c1, c2, c3, c4 = st.columns(4)
            for col_ui, col_df, titulo, paleta in zip([c1, c2, c3, c4], 
                                                     ['GÉNERO', 'CATEGORÍA', 'TIPO DE CONTRATACIÓN', 'CENTRO DE COSTOS'],
                                                     ['Género', 'Categoría', 'Contratación', 'Centro Costos'],
                                                     [PALETA_AZUL_GRIS, PALETA_AZUL_GRIS[2:], PALETA_AZUL_GRIS[4:], PALETA_AZUL_GRIS]):
                with col_ui:
                    if col_df in df_fil.columns:
                        data_pie = df_fil[col_df].value_counts().reset_index()
                        fig = px.pie(data_pie, names=col_df, values='count', hole=0.6, color_discrete_sequence=paleta)
                        fig.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': titulo, 'x': 0.5})
                        st.plotly_chart(fig, use_container_width=True)

            # Fila 2: Puestos
            if 'PUESTO' in df_fil.columns:
                df_p = df_fil['PUESTO'].value_counts().reset_index()
                fig_p = px.bar(df_p, x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Dotación por Puesto")
                fig_p.update_layout(height=300, margin=dict(t=50, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)

            # Fila 3: Responsables y Áreas
            cl1, cl2 = st.columns([2, 1])
            with cl1:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    d_resp = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    fig_res = px.bar(d_resp, x='RESPONSABLE DIRECTO', y='count', text='count', color_discrete_sequence=['#1E3A8A'], title="Responsables")
                    st.plotly_chart(fig_res, use_container_width=True)
            with cl2:
                if 'ÁREA' in df_fil.columns:
                    df_a = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_a, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'], title="Áreas")
                    st.plotly_chart(fig_a, use_container_width=True)

    with tab2:
        st.subheader("🎂 Cumpleaños del Mes")
        if not df_cump.empty:
            st.info("Revisa tu hoja de cumpleaños en Google Sheets para ver la lista completa.")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")
