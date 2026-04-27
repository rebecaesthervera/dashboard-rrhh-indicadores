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
    except:
        return pd.DataFrame()

def limpiar_fecha(df, col):
    if col in df.columns:
        s = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
    return pd.Series([pd.NaT] * len(df))

try:
    # CARGA DE DATOS
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

    # --- LÓGICA DE GLOBOS (CUMPLEAÑOS DE HOY) ---
    col_f_nac = 'FECHA NACIMIENTO'
    df_cump['DT_NAC'] = limpiar_fecha(df_cump, col_f_nac)
    hoy = datetime.now()
    cumpleañeros_hoy = df_cump[(df_cump['DT_NAC'].dt.month == hoy.month) & (df_cump['DT_NAC'].dt.day == hoy.day)]
    
    if not cumpleañeros_hoy.empty:
        st.balloons()
        for _, persona in cumpleañeros_hoy.iterrows():
            st.toast(f"🎂 ¡Hoy es el cumpleaños de {persona['APELLIDO Y NOMBRE']}!", icon="🎉")

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f]
        if archivos: st.image(archivos[0], width=150)
    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "📅 Efemérides y Aniversarios"])

    with tab1:
        # --- FILTROS (7 INDICADORES) ---
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
            st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600)
        
        with c_graf:
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
        # --- SELECTOR DE MES Y TARJETAS ---
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        sel_mes = st.selectbox("Seleccionar mes de consulta", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)

        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), 'FECHA INGRESO')
        df_main['DT_ING'] = limpiar_fecha(df_main, col_f_ing)

        st.subheader(f"Efemérides de {meses[sel_mes-1]}")
        t_vida, t_lab = st.tabs(["🎂 Cumpleaños de Vida", "🎖️ Aniversarios Laborales"])

        with t_vida:
            df_v = df_cump[df_cump['DT_NAC'].dt.month == sel_mes].copy()
            if not df_v.empty:
                df_v['DIA'] = df_v['DT_NAC'].dt.day
                df_v = df_v.sort_values('DIA')
                c_idx = 0
                for _, r in df_v.iterrows():
                    if c_idx % 3 == 0: cols_v = st.columns(3)
                    with cols_v[c_idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"### 📅 Día {int(r['DIA'])}")
                            st.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                            # Trayectoria cruzada
                            m = df_main[df_main['APELLIDO Y NOMBRE'] == r['APELLIDO Y NOMBRE']]
                            if not m.empty and not pd.isnull(m['DT_ING'].values[0]):
                                ant = hoy.year - m['DT_ING'].dt.year.values[0]
                                st.caption(f"⭐ Trayectoria: {int(ant)} años")
                            st.divider()
                            st.button("Felicitar ✨", key=f"v_{idx}_{c_idx}")
                    c_idx += 1
            else:
                st.info("No hay cumpleaños registrados.")

        with t_lab:
            df_l = df_main[df_main['DT_ING'].dt.month == sel_mes].copy()
            if not df_l.empty:
                df_l['ANTIGUEDAD'] = hoy.year - df_l['DT_ING'].dt.year
                df_l = df_l.sort_values('ANTIGUEDAD', ascending=False) # Antiguos primero
                c_idx_l = 0
                for _, r in df_l.iterrows():
                    if c_idx_l % 3 == 0: cols_l = st.columns(3)
                    with cols_l[c_idx_l % 3]:
                        with st.container(border=True):
                            st.markdown(f"### 📅 Día {int(r['DT_ING'].day)}")
                            st.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                            if r['ANTIGUEDAD'] > 0:
                                st.success(f"🎊 ¡Cumple {int(r['ANTIGUEDAD'])} años!")
                            else:
                                st.info("🌱 ¡Ingresó este año!")
                            st.caption(f"Desde: {r['DT_ING'].strftime('%d/%m/%Y')}")
                    c_idx_l += 1
            else:
                st.info("No hay aniversarios laborales.")

except Exception as e:
    st.error(f"Error: {e}")
