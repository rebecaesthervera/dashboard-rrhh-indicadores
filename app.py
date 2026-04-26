import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Gestión RRHH - Exincor", layout="wide")

# 2. COLORES Y ESTILO
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=600)
def cargar_datos(gid):
    url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    # Carga de ambas pestañas
    df_principal = cargar_datos("1543772338")
    if 'LEGAJO' in df_principal.columns:
        df_principal = df_principal.dropna(subset=['LEGAJO'])
        
    df_cumples = cargar_datos("540729566")

    # --- ENCABEZADO ---
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Panel de Control Exincor</h2>", unsafe_allow_html=True)
    
    # --- PESTAÑAS PRINCIPALES ---
    tab_dotacion, tab_cumples = st.tabs(["📊 Dotación e Indicadores", "🎂 Calendario de Cumpleaños"])

    with tab_dotacion:
        # Filtros Superiores
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            area_opts = ["Todas"] + sorted(df_principal['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df_principal.columns else ["Todas"]
            sel_area = st.selectbox("Área", area_opts)
        with col_f2:
            cc_opts = ["Todos"] + sorted(df_principal['CENTRO DE COSTOS'].dropna().unique().tolist()) if 'CENTRO DE COSTOS' in df_principal.columns else ["Todos"]
            sel_cc = st.selectbox("Centro de Costos", cc_opts)
        with col_f3:
            cat_opts = ["Todas"] + sorted(df_principal['CATEGORÍA'].dropna().unique().tolist()) if 'CATEGORÍA' in df_principal.columns else ["Todas"]
            sel_cat = st.selectbox("Categoría", cat_opts)
        with col_f4:
            nombres_opts = ["Todos"] + sorted(df_principal['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df_principal.columns else ["Todos"]
            sel_nombre = st.selectbox("Colaborador", nombres_opts)

        # Aplicar Filtros
        df_fil = df_principal.copy()
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_cc != "Todos": df_fil = df_fil[df_fil['CENTRO DE COSTOS'] == sel_cc]
        if sel_cat != "Todas": df_fil = df_fil[df_fil['CATEGORÍA'] == sel_cat]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        st.markdown("---")
        
        # Dashboard Visual (Estructura de Tarjetas)
        c_izq, c_cen, c_der = st.columns([1.5, 3, 2.5])
        
        with c_izq:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B;'>Activos</p>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align:center; color:#1E3A8A;'>{len(df_fil)}</h1>", unsafe_allow_html=True)
            with st.container(border=True):
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=400, use_container_width=True)

        with c_cen:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Distribución por Género</b></p>", unsafe_allow_html=True)
                if 'GÉNERO' in df_fil.columns:
                    fig_g = px.pie(df_fil, names='GÉNERO', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig_g.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
                    st.plotly_chart(fig_g, use_container_width=True, theme=None)
            
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Centro de Costos</b></p>", unsafe_allow_html=True)
                if 'CENTRO DE COSTOS' in df_fil.columns:
                    df_cc = df_fil['CENTRO DE COSTOS'].value_counts().reset_index()
                    df_cc.columns = ['CC', 'CANT']
                    fig_cc = px.bar(df_cc, x='CANT', y='CC', orientation='h', text='CANT', color_discrete_sequence=['#3B82F6'])
                    fig_cc.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_cc, use_container_width=True, theme=None)

        with c_der:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Dotación por Área</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns:
                    df_area = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_area, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'])
                    fig_a.update_layout(height=450, margin=dict(t=20, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_a, use_container_width=True, theme=None)

    with tab_cumples:
        st.subheader("🎂 Próximos Cumpleaños")
        
        # Procesamiento de fechas
        col_fecha = next((c for c in df_cumples.columns if 'FECHA' in c), None)
        
        if col_fecha:
            df_cumples[col_fecha] = pd.to_datetime(df_cumples[col_fecha], errors='coerce')
            mes_actual = datetime.now().month
            
            # Filtramos los del mes actual
            cumples_mes = df_cumples[df_cumples[col_fecha].dt.month == mes_actual].copy()
            cumples_mes['DIA'] = cumples_mes[col_fecha].dt.day
            cumples_mes = cumples_mes.sort_values('DIA')

            if not cumples_mes.empty:
                st.info(f"Este mes tenemos {len(cumples_mes)} cumpleaños.")
                # Tarjetas de cumpleaños
                cols = st.columns(4)
                for i, row in cumples_mes.iterrows():
                    with cols[i % 4]:
                        with st.container(border=True):
                            st.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                            st.markdown(f"📅 Día: {int(row['DIA'])}")
            else:
                st.write("No hay cumpleaños registrados para este mes.")
        else:
            st.warning("No se encontró la columna de fecha en la pestaña de cumpleaños.")

except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
