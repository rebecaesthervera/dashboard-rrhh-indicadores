import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Exincor", layout="wide")

# 2. COLORES CORPORATIVOS
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=600)
def cargar_datos(gid):
    sheet_url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    # Carga de datos
    df_main = cargar_datos("1543772338")
    if 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])
        
    df_cump = cargar_datos("540729566")
    
    # --- PROCESAMIENTO DE CUMPLEAÑOS ---
    col_fecha = next((c for c in df_cump.columns if 'FECHA' in c or 'NACIMIENTO' in c), None)
    cumples_hoy_lista = []
    if col_fecha:
        df_cump['FECHA_LIMPIA'] = pd.to_datetime(df_cump[col_fecha], errors='coerce', dayfirst=True)
        hoy = datetime.now()
        mask_hoy = (df_cump['FECHA_LIMPIA'].dt.month == hoy.month) & (df_cump['FECHA_LIMPIA'].dt.day == hoy.day)
        cumples_hoy_lista = df_cump[mask_hoy]['APELLIDO Y NOMBRE'].tolist()

    if cumples_hoy_lista:
        for persona in cumples_hoy_lista:
            st.toast(f"🎂 ¡Hoy es el cumpleaños de {persona}!", icon="🎉")

    # --- ENCABEZADO ---
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Dotación Exincor</h2>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños del Mes"])

    with tab1:
        # --- FILTROS ---
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            conv_opts = ["Todos"] + sorted(df_main['CONVENIO'].dropna().unique().tolist()) if 'CONVENIO' in df_main.columns else ["Todos"]
            sel_conv = st.selectbox("Convenio", conv_opts)
            
        with col_f2:
            resp_opts = ["Todos"] + sorted(df_main['RESPONSABLE DIRECTO'].dropna().unique().tolist()) if 'RESPONSABLE DIRECTO' in df_main.columns else ["Todos"]
            sel_resp = st.selectbox("Responsable Directo", resp_opts)
            
        with col_f3:
            area_opts = ["Todas"] + sorted(df_main['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df_main.columns else ["Todas"]
            sel_area = st.selectbox("Área", area_opts)
            
        with col_f4:
            nombres_opts = ["Todos"] + sorted(df_main['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df_main.columns else ["Todos"]
            sel_nombre = st.selectbox("Personal", nombres_opts)

        # Aplicar Filtros
        df_fil = df_main.copy()
        if sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        # --- DISEÑO ---
        col_izq, col_centro, col_der = st.columns([1.5, 3, 2.5])

        with col_izq:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; font-size:18px;'>Total Activos</p>", unsafe_allow_html=True)
                # LÍNEA CORREGIDA AQUÍ:
                st.markdown(f"<h1 style='text-align:center; color:#1E3A8A;'>{len(df_fil)}</h1>", unsafe_allow_html=True)
            with st.container(border=True):
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=540, use_container_width=True)

        with col_centro:
            # Gráfico de Barras Verticales (Puestos hacia arriba)
            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Dotación por Puesto</b></p>", unsafe_allow_html=True)
                if 'PUESTO' in df_fil.columns:
                    df_p = df_fil['PUESTO'].value_counts().reset_index()
                    fig_p = px.bar(df_p, x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'])
                    fig_p.update_layout(height=300, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_p, use_container_width=True)

            # Gráfico por Responsable Directo
            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Distribución por Responsable Directo</b></p>", unsafe_allow_html=True)
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    df_res = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    fig_res = px.pie(df_res, names='RESPONSABLE DIRECTO', values='count', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig_res.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
                    st.plotly_chart(fig_res, use_container_width=True)

        with col_der:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Centro de Costos</b></p>", unsafe_allow_html=True)
                if 'CENTRO DE COSTOS' in df_fil.columns:
                    df_cc = df_fil['CENTRO DE COSTOS'].value_counts().reset_index()
                    fig_cc = px.pie(df_cc, names='CENTRO DE COSTOS', values='count', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS[2:])
                    # Se quitó el espacio en blanco (ahora es un anillo completo)
                    fig_cc.update_layout(height=280, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
                    st.plotly_chart(fig_cc, use_container_width=True)

            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Dotación por Área</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns:
                    df_a = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_a, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'])
                    fig_a.update_layout(height=250, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_a, use_container_width=True)

    with tab2:
        st.subheader("🎂 Próximos Cumpleaños")
        if col_fecha:
            mes_actual = datetime.now().month
            cumples_mes = df_cump[df_cump['FECHA_LIMPIA'].dt.month == mes_actual].copy()
            if not cumples_mes.empty:
                cumples_mes['DIA'] = cumples_mes['FECHA_LIMPIA'].dt.day
                cumples_mes = cumples_mes.sort_values('DIA')
                cols = st.columns(5)
                for i, row in cumples_mes.iterrows():
                    with cols[i % 5]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='color:#1E3A8A; text-align:center;'>{int(row['DIA'])}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:14px;'>{row['APELLIDO Y NOMBRE']}</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
