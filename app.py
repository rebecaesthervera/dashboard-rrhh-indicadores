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
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    hoy = datetime.now()

    # --- LÓGICA DE GLOBOS ---
    col_f_nac = 'FECHA NACIMIENTO'
    df_cump['DT_NAC'] = limpiar_fecha(df_cump, col_f_nac)
    cumple_hoy = df_cump[(df_cump['DT_NAC'].dt.month == hoy.month) & (df_cump['DT_NAC'].dt.day == hoy.day)]
    if not cumple_hoy.empty:
        st.balloons()

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
        # --- FILTROS (MANTENEMOS TU PANEL INTACTO) ---
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

        c_izq, c_der = st.columns([1, 4])
        with c_izq:
            st.metric("Total Activos", len(df_fil))
            st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=600, use_container_width=True)
        with c_der:
            i1, i2, i3, i4 = st.columns(4)
            for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                if c in df_fil.columns:
                    fig = px.pie(df_fil[c].value_counts().reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                    ui.plotly_chart(fig, use_container_width=True)
            if 'PUESTO' in df_fil.columns:
                fig_p = px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Puestos")
                st.plotly_chart(fig_p.update_layout(height=300), use_container_width=True)
            r1, r2 = st.columns([2, 1])
            if 'RESPONSABLE DIRECTO' in df_fil.columns: r1.plotly_chart(px.bar(df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index(), x='RESPONSABLE DIRECTO', y='count', color_discrete_sequence=['#1E3A8A'], title="Responsables").update_layout(height=250), use_container_width=True)
            if 'ÁREA' in df_fil.columns: r2.plotly_chart(px.bar(df_fil['ÁREA'].value_counts().reset_index(), x='ÁREA', y='count', color_discrete_sequence=['#64748B'], title="Áreas").update_layout(height=250), use_container_width=True)

    with tab2:
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        sel_mes = st.selectbox("Seleccionar mes de consulta para CUMPLEAÑOS", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)
        
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), 'FECHA INGRESO')
        df_main['DT_ING'] = limpiar_fecha(df_main, col_f_ing)

        t1, t2 = st.tabs(["🎂 Cumpleaños de Vida (Mensual)", "🎖️ Aniversarios Laborales (Todo el Personal)"])

        with t1:
            st.subheader(f"Cumpleaños en {meses[sel_mes-1]}")
            df_v = df_cump[df_cump['DT_NAC'].dt.month == sel_mes].copy()
            if not df_v.empty:
                df_v['DIA'] = df_v['DT_NAC'].dt.day
                df_v = df_v.sort_values('DIA')
                for i in range(0, len(df_v), 3):
                    cols = st.columns(3)
                    for j, (_, r) in enumerate(df_v.iloc[i:i+3].iterrows()):
                        with cols[j]:
                            with st.container(border=True):
                                st.markdown(f"### 📅 Día {int(r['DIA'])}")
                                st.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                                m = df_main[df_main['APELLIDO Y NOMBRE'] == r['APELLIDO Y NOMBRE']]
                                if not m.empty and not pd.isnull(m['DT_ING'].values[0]):
                                    ant = hoy.year - m['DT_ING'].dt.year.values[0]
                                    st.caption(f"⭐ Trayectoria: {int(ant)} años")
            else: st.info(f"No hay cumpleaños en {meses[sel_mes-1]}.")

        with t2:
            st.subheader("Trayectoria y Aniversarios Laborales 2026")
            if not df_main.empty:
                # Calculamos antigüedad de TODOS
                df_all = df_main.dropna(subset=['DT_ING']).copy()
                df_all['ANTIGUEDAD'] = hoy.year - df_all['DT_ING'].dt.year
                df_all = df_all.sort_values('ANTIGUEDAD', ascending=False)
                
                # Buscador opcional para no perderse entre tantas tarjetas
                busqueda = st.text_input("🔍 Buscar empleado por nombre...", "")
                if busqueda:
                    df_all = df_all[df_all['APELLIDO Y NOMBRE'].str.contains(busqueda.upper())]

                for i in range(0, len(df_all), 3):
                    cols = st.columns(3)
                    for j, (_, r) in enumerate(df_all.iloc[i:i+3].iterrows()):
                        with cols[j]:
                            with st.container(border=True):
                                mes_ing = meses[int(r['DT_ING'].month)-1]
                                st.markdown(f"### 🎖️ Ingreso: {mes_ing}")
                                st.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                                if r['ANTIGUEDAD'] > 0:
                                    st.success(f"🎊 Cumple {int(r['ANTIGUEDAD'])} años en 2026")
                                else:
                                    st.info("🌱 Ingresó este año")
                                st.caption(f"Fecha exacta: {r['DT_ING'].strftime('%d/%m/%Y')}")
            else: st.info("No hay datos de ingreso disponibles.")

except Exception as e:
    st.error(f"Error: {e}")
