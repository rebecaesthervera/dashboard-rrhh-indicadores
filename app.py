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
    
    # --- PROCESAMIENTO DE FECHAS PARA ALERTAS ---
    col_fecha = next((c for c in df_cump.columns if 'FECHA' in c or 'NACIMIENTO' in c), None)
    cumples_hoy_lista = []
    
    if col_fecha:
        df_cump['FECHA_LIMPIA'] = pd.to_datetime(df_cump[col_fecha], errors='coerce', dayfirst=True)
        hoy = datetime.now()
        # Filtramos exactamente por DIA y MES actual
        mask_hoy = (df_cump['FECHA_LIMPIA'].dt.month == hoy.month) & (df_cump['FECHA_LIMPIA'].dt.day == hoy.day)
        cumples_hoy_df = df_cump[mask_hoy]
        cumples_hoy_lista = cumples_hoy_df['APELLIDO Y NOMBRE'].tolist()

    # --- MÓDULO DE ALERTAS (Se muestra antes que todo) ---
    if cumples_hoy_lista:
        for persona in cumples_hoy_lista:
            st.balloons() # Efecto visual de globos
            st.toast(f"🎂 ¡Hoy es el cumpleaños de {persona}!", icon="🎉")
            st.warning(f"🔔 **RECORDATORIO:** Hoy es el cumpleaños de **{persona}**. ¡No olvides saludarle!")

    # --- ENCABEZADO ---
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Dotación Exincor</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # PESTAÑAS
    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños del Mes"])

    with tab1:
        # Filtros
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            area_opts = ["Todas"] + sorted(df_main['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df_main.columns else ["Todas"]
            sel_area = st.selectbox("Área", area_opts)
        with col_f2:
            cat_opts = ["Todas"] + sorted(df_main['CATEGORÍA'].dropna().unique().tolist()) if 'CATEGORÍA' in df_main.columns else ["Todas"]
            sel_cat = st.selectbox("Categoría", cat_opts)
        with col_f3:
            cc_opts = ["Todos"] + sorted(df_main['CENTRO DE COSTOS'].dropna().unique().tolist()) if 'CENTRO DE COSTOS' in df_main.columns else ["Todos"]
            sel_cc = st.selectbox("Centro de Costos", cc_opts)
        with col_f4:
            nombres_opts = ["Todos"] + sorted(df_main['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df_main.columns else ["Todos"]
            sel_nombre = st.selectbox("Apellido y Nombre", nombres_opts)

        df_fil = df_main.copy()
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_cat != "Todas": df_fil = df_fil[df_fil['CATEGORÍA'] == sel_cat]
        if sel_cc != "Todos": df_fil = df_fil[df_fil['CENTRO DE COSTOS'] == sel_cc]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        # Grilla Original
        col_izq, col_centro, col_der = st.columns([1.5, 3, 2.5])

        with col_izq:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; font-size:18px;'>Total Activos</p>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align:center; color:#1E3A8A;'>{len(df_fil)}</h1>", unsafe_allow_html=True)
            with st.container(border=True):
                if 'APELLIDO Y NOMBRE' in df_fil.columns:
                    st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=580, use_container_width=True)

        with col_centro:
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Género</b></p>", unsafe_allow_html=True)
                    if 'GÉNERO' in df_fil.columns:
                        fig_g = px.pie(df_fil, names='GÉNERO', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig_g.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
                        st.plotly_chart(fig_g, use_container_width=True)
            with c2:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Categoría</b></p>", unsafe_allow_html=True)
                    if 'CATEGORÍA' in df_fil.columns:
                        fig_c = px.pie(df_fil, names='CATEGORÍA', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS[::-1])
                        fig_c.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
                        st.plotly_chart(fig_c, use_container_width=True)

            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Dotación por Puesto</b></p>", unsafe_allow_html=True)
                if 'PUESTO' in df_fil.columns:
                    df_p = df_fil['PUESTO'].value_counts().reset_index()
                    fig_p = px.bar(df_p, y='PUESTO', x='count', orientation='h', text='count', color_discrete_sequence=['#3B82F6'])
                    fig_p.update_layout(height=240, margin=dict(t=0, b=0, l=0, r=10), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_p, use_container_width=True)

            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Centro de Costos</b></p>", unsafe_allow_html=True)
                if 'CENTRO DE COSTOS' in df_fil.columns:
                    df_cc = df_fil['CENTRO DE COSTOS'].value_counts().reset_index()
                    fig_cc = px.pie(df_cc, names='CENTRO DE COSTOS', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS[2:])
                    fig_cc.update_layout(height=160, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
                    st.plotly_chart(fig_cc, use_container_width=True)

        with col_der:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Dotación por Área</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns:
                    df_a = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_a, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'])
                    fig_a.update_layout(height=220, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_a, use_container_width=True)

            with st.container(border=True):
                st.markdown("<p style='text-align:center; background-color:#F1F5F9; padding:5px;'><b>Mapa Estructural</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns and 'PUESTO' in df_fil.columns:
                    fig_tree = px.treemap(df_fil, path=[px.Constant("Exincor"), 'ÁREA', 'PUESTO'], color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig_tree.update_layout(height=415, margin=dict(t=10, b=0, l=0, r=0))
                    st.plotly_chart(fig_tree, use_container_width=True)

    with tab2:
        st.subheader("🎂 Próximos Cumpleaños")
        if col_fecha:
            mes_actual = datetime.now().month
            cumples_mes = df_cump[df_cump['FECHA_LIMPIA'].dt.month == mes_actual].copy()
            if not cumples_mes.empty:
                cumples_mes['DIA'] = cumples_mes['FECHA_LIMPIA'].dt.day
                cumples_mes = cumples_mes.sort_values('DIA')
                st.success(f"Hay {len(cumples_mes)} cumpleaños en el mes actual.")
                cols = st.columns(5)
                for i, row in cumples_mes.iterrows():
                    with cols[i % 5]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='color:#1E3A8A; text-align:center;'>{int(row['DIA'])}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:14px;'>{row['APELLIDO Y NOMBRE']}</p>", unsafe_allow_html=True)
            else:
                st.info("No hay cumpleaños este mes.")

except Exception as e:
    st.error(f"Error: {e}")
