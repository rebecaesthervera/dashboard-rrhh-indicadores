import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Layout ancho para que entre todo como en la foto)
st.set_page_config(page_title="Dotación - Exincor", layout="wide")

# 2. DEFINICIÓN DE COLORES CORPORATIVOS (Azul y Gris)
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

# 3. CARGA DE DATOS (Modificada para leer múltiples pestañas)
@st.cache_data(ttl=600)
def cargar_datos(gid):
    sheet_url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.upper()
    return df

try:
    # Cargamos la pestaña principal (1543772338) y la de cumples (540729566)
    df_main = cargar_datos("1543772338")
    if 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])
        
    df_cump = cargar_datos("540729566")

    # --- ENCABEZADO PRINCIPAL ---
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Dotación Exincor</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # CREACIÓN DE PESTAÑAS
    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños del Mes"])

    with tab1:
        # --- FILTROS (Ahora con 4 columnas para incluir Centro de Costos) ---
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

        # Aplicar filtros
        df_fil = df_main.copy()
        if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if sel_cat != "Todas": df_fil = df_fil[df_fil['CATEGORÍA'] == sel_cat]
        if sel_cc != "Todos": df_fil = df_fil[df_fil['CENTRO DE COSTOS'] == sel_cc]
        if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        st.write("") # Espacio

        # --- ESTRUCTURA DE TARJETAS (GRILLA ORIGINAL INTACTA) ---
        col_izq, col_centro, col_der = st.columns([1.5, 3, 2.5])

        # -- COLUMNA IZQUIERDA --
        with col_izq:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; font-size:18px; margin-bottom:-10px;'>Total Activos</p>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align:center; color:#1E3A8A; font-size:60px;'>{len(df_fil)}</h1>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("<p style='color:#64748B; margin-bottom:5px;'><b>Apellido y Nombre</b></p>", unsafe_allow_html=True)
                if 'APELLIDO Y NOMBRE' in df_fil.columns:
                    # Aumenté un poquito el alto para que cuadre con el nuevo gráfico de la columna central
                    st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=580, use_container_width=True)

        # -- COLUMNA CENTRAL --
        with col_centro:
            c_sup1, c_sup2 = st.columns(2)
            
            with c_sup1:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Género</b></p>", unsafe_allow_html=True)
                    if 'GÉNERO' in df_fil.columns and not df_fil['GÉNERO'].isnull().all():
                        fig_g = px.pie(df_fil, names='GÉNERO', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig_g.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                        fig_g.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200)
                        st.plotly_chart(fig_g, use_container_width=True)
                    else:
                        st.info("Sin datos")

            with c_sup2:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Categoría</b></p>", unsafe_allow_html=True)
                    if 'CATEGORÍA' in df_fil.columns and not df_fil['CATEGORÍA'].isnull().all():
                        fig_c = px.pie(df_fil, names='CATEGORÍA', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS[::-1])
                        fig_c.update_traces(textposition='inside', textinfo='percent', showlegend=False)
                        fig_c.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200)
                        st.plotly_chart(fig_c, use_container_width=True)
                    else:
                        st.info("Sin datos")

            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Dotación por Puesto</b></p>", unsafe_allow_html=True)
                if 'PUESTO' in df_fil.columns and not df_fil['PUESTO'].isnull().all():
                    df_puesto = df_fil['PUESTO'].value_counts().reset_index()
                    fig_p = px.bar(df_puesto, y='PUESTO', x='count', orientation='h', text='count', color_discrete_sequence=['#3B82F6'])
                    fig_p.update_traces(textposition='outside')
                    fig_p.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=10, r=10), height=240, xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_p, use_container_width=True)
                else:
                    st.info("Sin datos")
                    
            # NUEVO GRÁFICO: Centro de Costos agregado al final de la columna central para no romper tu diseño
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Centro de Costos</b></p>", unsafe_allow_html=True)
                if 'CENTRO DE COSTOS' in df_fil.columns and not df_fil['CENTRO DE COSTOS'].isnull().all():
                    df_cc = df_fil['CENTRO DE COSTOS'].value_counts().reset_index()
                    fig_cc = px.pie(df_cc, names='CENTRO DE COSTOS', values='count', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS[2:])
                    fig_cc.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
                    fig_cc.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=160)
                    st.plotly_chart(fig_cc, use_container_width=True)
                else:
                    st.info("Sin datos de Centro de Costos")

        # -- COLUMNA DERECHA --
        with col_der:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Dotación por Área</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns and not df_fil['ÁREA'].isnull().all():
                    df_area = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_area, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'])
                    fig_a.update_traces(textposition='outside')
                    fig_a.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220, xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig_a, use_container_width=True)
                else:
                    st.info("Sin datos")

            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Distribución Estructural (Área -> Puesto)</b></p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns and 'PUESTO' in df_fil.columns:
                    fig_tree = px.treemap(df_fil, path=[px.Constant("Exincor"), 'ÁREA', 'PUESTO'], color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig_tree.update_traces(textinfo="label+value")
                    # Aumenté un poco el alto del treemap para emparejar con el centro de costos
                    fig_tree.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=415)
                    st.plotly_chart(fig_tree, use_container_width=True)
                else:
                    st.info("Faltan datos")

    # --- PESTAÑA DE CUMPLEAÑOS ---
    with tab2:
        st.subheader("🎂 Próximos Cumpleaños")
        
        # Busca dinámicamente la columna de fecha
        col_fecha = next((c for c in df_cump.columns if 'FECHA' in c or 'NACIMIENTO' in c), None)

        if col_fecha:
            # MAGIA PARA ARGENTINA: dayfirst=True soluciona el problema de los meses invertidos
            df_cump['FECHA_LIMPIA'] = pd.to_datetime(df_cump[col_fecha], errors='coerce', dayfirst=True)
            
            mes_actual = datetime.now().month
            cumples_mes = df_cump[df_cump['FECHA_LIMPIA'].dt.month == mes_actual].copy()

            if not cumples_mes.empty:
                cumples_mes['DIA'] = cumples_mes['FECHA_LIMPIA'].dt.day
                cumples_mes = cumples_mes.sort_values('DIA')

                st.success(f"¡Tenemos {len(cumples_mes)} cumpleaños registrados para este mes!")

                # Tarjetas visuales de cumpleaños
                cols = st.columns(5)
                for i, row in cumples_mes.iterrows():
                    with cols[i % 5]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='color:#1E3A8A; text-align:center; margin-bottom:0px;'>{int(row['DIA'])}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; color:#64748B; font-size:14px;'>{row['APELLIDO Y NOMBRE']}</p>", unsafe_allow_html=True)
            else:
                st.info("No hay cumpleaños registrados para el mes en curso.")
        else:
            st.warning("No se encontró la columna de fecha. Por favor nombra la columna como 'FECHA DE NACIMIENTO'.")

except Exception as e:
    st.error(f"Error en el panel: {e}")
