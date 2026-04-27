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
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    
    # --- BUSCADOR INTELIGENTE DE LOGO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        # Buscamos cualquier archivo que sea imagen en tu carpeta
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
            columnas_anillo = ['GÉNERO', 'CATEGORÍA', 'TIPO DE CONTRATACIÓN', 'CENTRO DE COSTOS']
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
        st.subheader("🎂 Próximos Cumpleaños")
        st.write("Consulta la pestaña de cumpleaños en tu Google Sheets.")

except Exception as e:
    st.error(f"Error: {e}")
