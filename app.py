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
        # Eliminar horas y limpiar espacios
        s = df[col].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
        return pd.to_datetime(s, format='%d/%m/%Y', errors='coerce')
    return pd.Series([pd.NaT] * len(df))

try:
    df_main = cargar_datos("1543772338")
    df_cump = cargar_datos("540729566")
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

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
        # (Se mantiene el panel de 7 indicadores que funciona bien)
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
            for ui, col_p, tit_p in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                if col_p in df_fil.columns:
                    fig = px.pie(df_fil[col_p].value_counts().reset_index(), names=col_p, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                    fig.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': tit_p, 'x': 0.5})
                    ui.plotly_chart(fig, use_container_width=True)
            
            if 'PUESTO' in df_fil.columns:
                st.plotly_chart(px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', color_discrete_sequence=['#3B82F6'], title="Puestos").update_layout(height=250), use_container_width=True)
            
            r_c1, r_c2 = st.columns([2, 1])
            if 'RESPONSABLE DIRECTO' in df_fil.columns: r_c1.plotly_chart(px.bar(df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index(), x='RESPONSABLE DIRECTO', y='count', color_discrete_sequence=['#1E3A8A'], title="Responsables").update_layout(height=230), use_container_width=True)
            if 'ÁREA' in df_fil.columns: r_c2.plotly_chart(px.bar(df_fil['ÁREA'].value_counts().reset_index(), x='ÁREA', y='count', color_discrete_sequence=['#64748B'], title="Áreas").update_layout(height=230), use_container_width=True)

    with tab2:
        # --- LÓGICA DE MESES Y ANIVERSARIOS CORREGIDA ---
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        hoy = datetime.now()
        sel_mes = st.selectbox("Seleccionar mes de consulta", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)

        col_f_nac = 'FECHA NACIMIENTO'
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), 'FECHA INGRESO')
        
        df_cump['DT_NAC'] = limpiar_fecha(df_cump, col_f_nac)
        df_main['DT_ING'] = limpiar_fecha(df_main, col_f_ing)

        st.subheader(f"Efemérides de {meses[sel_mes-1]}")
        sub1, sub2 = st.tabs(["🎂 Cumpleaños de Vida", "🎖️ Aniversarios Laborales (Orden Antigüedad)"])

        with sub1:
            df_v = df_cump[df_cump['DT_NAC'].dt.month == sel_mes].copy()
            if not df_v.empty:
                df_v['DIA'] = df_v['DT_NAC'].dt.day
                for _, r in df_v.sort_values('DIA').iterrows():
                    with st.container(border=True):
                        c_dia, c_txt = st.columns([1, 5])
                        c_dia.markdown(f"<h2 style='text-align:center;'>{int(r['DIA'])}</h2>", unsafe_allow_html=True)
                        c_txt.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                        # Mostrar trayectoria si existe el cruce
                        m = df_main[df_main['APELLIDO Y NOMBRE'] == r['APELLIDO Y NOMBRE']]
                        if not m.empty and not pd.isnull(m['DT_ING'].values[0]):
                            anos = hoy.year - m['DT_ING'].dt.year.values[0]
                            c_txt.caption(f"⭐ Antigüedad en la empresa: {int(anos)} años")
            else:
                st.info(f"No hay cumpleaños registrados en {meses[sel_mes-1]}")

        with sub2:
            # FILTRO: Personas que ingresaron en el mes seleccionado
            df_l = df_main[df_main['DT_ING'].dt.month == sel_mes].copy()
            if not df_l.empty:
                # CÁLCULO DE ANTIGÜEDAD
                df_l['ANTIGUEDAD'] = hoy.year - df_l['DT_ING'].dt.year
                # ORDENAR: De más antiguo (mayor número de años) a más reciente
                df_l = df_l.sort_values('ANTIGUEDAD', ascending=False)
                
                for _, r in df_l.iterrows():
                    with st.container(border=True):
                        c_dia, c_txt = st.columns([1, 5])
                        # Día del mes que ingresó
                        dia_ing = int(r['DT_ING'].day)
                        c_dia.markdown(f"<h2 style='text-align:center;'>{dia_ing}</h2>", unsafe_allow_html=True)
                        c_txt.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                        
                        if r['ANTIGUEDAD'] > 0:
                            c_txt.success(f"🎊 ¡Cumple {int(r['ANTIGUEDAD'])} años en la empresa!")
                        else:
                            c_txt.info("🌱 ¡Ingresó este año!")
                        
                        c_txt.caption(f"Fecha de ingreso original: {r['DT_ING'].strftime('%d/%m/%Y')}")
            else:
                st.info(f"No hay aniversarios laborales en {meses[sel_mes-1]}")

except Exception as e:
    st.error(f"Error: {e}")
