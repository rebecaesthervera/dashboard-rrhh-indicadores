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
    except Exception:
        return pd.DataFrame()

try:
    df_main = cargar_datos("1543772338") # Base principal
    df_cump = cargar_datos("540729566")  # Hoja cumpleaños
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

    st.markdown("<h1 style='color: #1E3A8A;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños y Aniversarios"])

    with tab1:
        # (Se mantiene tu panel de dotación con los 7 indicadores)
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

        c_met, c_graf = st.columns([1.2, 3.8])
        with c_met:
            st.metric("Total Activos", len(df_fil))
            if 'APELLIDO Y NOMBRE' in df_fil.columns: st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600)
        
        with c_graf:
            # Gráficos de anillos y barras (7 indicadores totales)
            i1, i2, i3, i4 = st.columns(4)
            for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                if c in df_fil.columns:
                    ui.plotly_chart(px.pie(df_fil[c].value_counts().reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS).update_layout(height=180, showlegend=False, title=t), use_container_width=True)
            
            if 'PUESTO' in df_fil.columns:
                st.plotly_chart(px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', color_discrete_sequence=['#3B82F6'], title="Puestos").update_layout(height=250), use_container_width=True)
            
            r1, r2 = st.columns([2, 1])
            if 'RESPONSABLE DIRECTO' in df_fil.columns: r1.plotly_chart(px.bar(df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index(), x='RESPONSABLE DIRECTO', y='count', color_discrete_sequence=['#1E3A8A'], title="Responsables").update_layout(height=230), use_container_width=True)
            if 'ÁREA' in df_fil.columns: r2.plotly_chart(px.bar(df_fil['ÁREA'].value_counts().reset_index(), x='ÁREA', y='count', color_discrete_sequence=['#64748B'], title="Áreas").update_layout(height=230), use_container_width=True)

    with tab2:
        # --- NUEVA LÓGICA DINÁMICA DE MESES ---
        meses_dict = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
        mes_actual_idx = datetime.now().month
        
        col_sel_mes, _ = st.columns([2, 3])
        mes_seleccionado = col_sel_mes.selectbox("Seleccionar Mes de Consulta", options=list(meses_dict.keys()), format_func=lambda x: meses_dict[x], index=mes_actual_idx-1)

        st.subheader(f"📅 Eventos de {meses_dict[mes_seleccionado]}")
        
        col_f_nac = 'FECHA NACIMIENTO'
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), None)

        # Procesamiento de Fechas
        def limpiar_y_convertir(df, col):
            if col in df.columns:
                temp_col = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
                return pd.to_datetime(temp_col, format='%d/%m/%Y', errors='coerce')
            return pd.Series([pd.NaT] * len(df))

        df_cump['DT_NAC'] = limpiar_y_convertir(df_cump, col_f_nac)
        df_main['DT_ING'] = limpiar_y_convertir(df_main, col_f_ing)

        # 1. CUMPLEAÑOS DE VIDA
        cumps_vida = df_cump[df_cump['DT_NAC'].dt.month == mes_seleccionado].copy()
        # 2. CUMPLEAÑOS LABORALES (Aniversarios)
        cumps_lab = df_main[df_main['DT_ING'].dt.month == mes_seleccionado].copy()

        t_vida, t_lab = st.tabs(["🎂 Cumpleaños de Vida", "⭐ Aniversarios Laborales"])

        with t_vida:
            if not cumps_vida.empty:
                cumps_vida['DIA'] = cumps_vida['DT_NAC'].dt.day
                for _, row in cumps_vida.sort_values('DIA').iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        c1.markdown(f"## {int(row['DIA'])}")
                        c2.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                        # Buscar trayectoria si existe en la principal
                        m = df_main[df_main['APELLIDO Y NOMBRE'] == row['APELLIDO Y NOMBRE']]
                        if not m.empty and not pd.isnull(m['DT_ING'].values[0]):
                            ing = pd.to_datetime(m['DT_ING'].values[0])
                            ant = datetime.now().year - ing.year
                            st.caption(f"Trayectoria en la empresa: {ant} años")
            else:
                st.info(f"No hay cumpleaños de vida en {meses_dict[mes_seleccionado]}")

        with t_lab:
            if not cumps_lab.empty:
                cumps_lab['DIA'] = cumps_lab['DT_ING'].dt.day
                for _, row in cumps_lab.sort_values('DIA').iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        ant_total = datetime.now().year - row['DT_ING'].year
                        c1.markdown(f"## {int(row['DIA'])}")
                        c2.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                        c2.success(f"🎊 ¡Cumple {ant_total} años en la empresa!")
                        st.caption(f"Fecha de ingreso: {row[col_f_ing]}")
            else:
                st.info(f"No hay aniversarios laborales en {meses_dict[mes_seleccionado]}")

except Exception as e:
    st.error(f"Error: {e}")
