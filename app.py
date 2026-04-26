import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dotación - Exincor", layout="wide")

# 2. DEFINICIÓN DE COLORES CORPORATIVOS (Azul y Gris)
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

# 3. CARGA DE DATOS
@st.cache_data(ttl=600)
def cargar_datos():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip().str.upper()
    if 'LEGAJO' in df.columns:
        df = df.dropna(subset=['LEGAJO'])
    return df

try:
    df = cargar_datos()

    # --- ENCABEZADO Y FILTROS ---
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Dotación Exincor</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        area_opts = ["Todas"] + sorted(df['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df.columns else ["Todas"]
        sel_area = st.selectbox("Filtrar por Área", area_opts)
        
    with col_f2:
        cat_opts = ["Todas"] + sorted(df['CATEGORÍA'].dropna().unique().tolist()) if 'CATEGORÍA' in df.columns else ["Todas"]
        sel_cat = st.selectbox("Filtrar por Categoría", cat_opts)
        
    with col_f3:
        nombres_opts = ["Todos"] + sorted(df['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df.columns else ["Todos"]
        sel_nombre = st.selectbox("Buscar Colaborador", nombres_opts)

    # Aplicar filtros
    df_fil = df.copy()
    if sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
    if sel_cat != "Todas": df_fil = df_fil[df_fil['CATEGORÍA'] == sel_cat]
    if sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

    st.write("") # Espacio separador

    # --- ESTRUCTURA DE TARJETAS (GRILLA) ---
    col_izq, col_centro, col_der = st.columns([1.5, 3, 2.5])

    # -- COLUMNA IZQUIERDA --
    with col_izq:
        with st.container(border=True):
            st.markdown("<p style='text-align:center; color:#64748B; font-size:18px; margin-bottom:-10px;'>Total Activos</p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align:center; color:#1E3A8A; font-size:60px;'>{len(df_fil)}</h1>", unsafe_allow_html=True)
            st.caption("👥 *Colaboradores que cumplen los filtros actuales.*")
        
        with st.container(border=True):
            st.markdown("<p style='color:#64748B; margin-bottom:5px;'><b>Nómina Activa</b></p>", unsafe_allow_html=True)
            if 'APELLIDO Y NOMBRE' in df_fil.columns:
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=430, use_container_width=True)

    # -- COLUMNA CENTRAL --
    with col_centro:
        c_sup1, c_sup2 = st.columns(2)
        
        with c_sup1:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Género</b></p>", unsafe_allow_html=True)
                if 'GÉNERO' in df_fil.columns and not df_fil['GÉNERO'].isnull().all():
                    fig_g = px.pie(df_fil, names='GÉNERO', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                    # AQUÍ ESTÁ LA MAGIA: label+percent muestra el nombre y el % adentro del gráfico
                    fig_g.update_traces(textposition='auto', textinfo='label+percent', showlegend=False)
                    fig_g.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200)
                    st.plotly_chart(fig_g, use_container_width=True)
                    st.caption("📊 *Distribución porcentual de la dotación por género.*")
                else:
                    st.info("Sin datos")

        with c_sup2:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Categoría</b></p>", unsafe_allow_html=True)
                if 'CATEGORÍA' in df_fil.columns and not df_fil['CATEGORÍA'].isnull().all():
                    fig_c = px.pie(df_fil, names='CATEGORÍA', hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS[::-1])
                    # Eliminamos la leyenda lateral y ponemos los nombres sobre las porciones
                    fig_c.update_traces(textposition='auto', textinfo='label+percent', showlegend=False)
                    fig_c.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200)
                    st.plotly_chart(fig_c, use_container_width=True)
                    st.caption("📈 *Clasificación según jerarquía o convenio.*")
                else:
                    st.info("Sin datos")

        with st.container(border=True):
            st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Dotación por Puesto</b></p>", unsafe_allow_html=True)
            if 'PUESTO' in df_fil.columns and not df_fil['PUESTO'].isnull().all():
                df_puesto = df_fil['PUESTO'].value_counts().reset_index()
                fig_p = px.bar(df_puesto, y='PUESTO', x='count', orientation='h', text='count', color_discrete_sequence=['#3B82F6'])
                # Formato limpio para que se lea el nombre del puesto y el número exacto
                fig_p.update_traces(textposition='outside')
                fig_p.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=10, r=10), height=240, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)
                st.caption("🎯 *Cantidad exacta de colaboradores asignados a cada rol específico.*")
            else:
                st.info("Sin datos")

    # -- COLUMNA DERECHA --
    with col_der:
        with st.container(border=True):
            st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Dotación por Área</b></p>", unsafe_allow_html=True)
            if 'ÁREA' in df_fil.columns and not df_fil['ÁREA'].isnull().all():
                df_area = df_fil['ÁREA'].value_counts().reset_index()
                fig_a = px.bar(df_area, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'])
                # Nombres de áreas abajo, números exactos arriba de cada barra
                fig_a.update_traces(textposition='outside')
                fig_a.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_a, use_container_width=True)
                st.caption("🏢 *Volumen de personal agrupado por grandes departamentos.*")
            else:
                st.info("Sin datos")

        with st.container(border=True):
            st.markdown("<p style='text-align:center; color:#64748B; background-color:#F1F5F9; padding:5px;'><b>Mapa Estructural (Área -> Puesto)</b></p>", unsafe_allow_html=True)
            if 'ÁREA' in df_fil.columns and 'PUESTO' in df_fil.columns:
                fig_tree = px.treemap(df_fil, path=[px.Constant("Exincor"), 'ÁREA', 'PUESTO'], color_discrete_sequence=PALETA_AZUL_GRIS)
                # Esta línea asegura que se lea el nombre del área/puesto y cuántas personas hay
                fig_tree.update_traces(textinfo="label+value")
                fig_tree.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=230)
                st.plotly_chart(fig_tree, use_container_width=True)
                st.caption("🧩 *Navegación jerárquica: de lo macro (Área) a lo micro (Puesto).*")
            else:
                st.info("Faltan datos")

except Exception as e:
    st.error(f"Error en el panel: {e}")
