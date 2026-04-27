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
        # Limpieza de textos en todas las celdas
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        return pd.DataFrame()

try:
    # CARGA DE DATOS
    df_main = cargar_datos("1543772338") # Hoja principal
    df_cump = cargar_datos("540729566")  # Hoja cumpleaños
    
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

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños y Trayectoria"])

    with tab1:
        # (Panel de dotación optimizado)
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        def get_opts(df, col, default="Todos"):
            if col in df.columns: return [default] + sorted(df[col].dropna().unique().tolist())
            return [default]
        with col_f1: sel_conv = st.selectbox("Convenio", get_opts(df_main, 'CONVENIO'))
        with col_f2: sel_resp = st.selectbox("Responsable Directo", get_opts(df_main, 'RESPONSABLE DIRECTO'))
        tipo_col = next((c for c in df_main.columns if 'CONTRATACIÓN' in c or 'CONTRATACION' in c), 'TIPO DE CONTRATACIÓN')
        with col_f3: sel_tipo = st.selectbox("Tipo Contratación", get_opts(df_main, tipo_col))
        with col_f4: sel_area = st.selectbox("Área", get_opts(df_main, 'ÁREA', "Todas"))
        with col_f5: sel_nombre = st.selectbox("Personal", get_opts(df_main, 'APELLIDO Y NOMBRE'))
        
        df_fil = df_main.copy()
        # Aplicación de filtros...
        if 'CONVENIO' in df_fil.columns and sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if 'RESPONSABLE DIRECTO' in df_fil.columns and sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if tipo_col in df_fil.columns and sel_tipo != "Todos": df_fil = df_fil[df_fil[tipo_col] == sel_tipo]
        if 'ÁREA' in df_fil.columns and sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if 'APELLIDO Y NOMBRE' in df_fil.columns and sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        c_met, c_graf = st.columns([1.2, 3.8])
        with c_met:
            st.metric("Total Activos", len(df_fil))
            if 'APELLIDO Y NOMBRE' in df_fil.columns: st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=650)
        with c_graf:
            c1, c2, c3, c4 = st.columns(4)
            for ui, db_col, tit in zip([c1, c2, c3, c4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                with ui:
                    if db_col in df_fil.columns and not df_fil[db_col].empty:
                        d_p = df_fil[db_col].value_counts().reset_index()
                        fig = px.pie(d_p, names=db_col, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': tit, 'x': 0.5})
                        st.plotly_chart(fig, use_container_width=True)
            if 'PUESTO' in df_fil.columns:
                fig_p = px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Puestos")
                fig_p.update_layout(height=280)
                st.plotly_chart(fig_p, use_container_width=True)
            cl1, cl2 = st.columns([2, 1])
            with cl1:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    st.plotly_chart(px.bar(df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index(), x='RESPONSABLE DIRECTO', y='count', color_discrete_sequence=['#1E3A8A'], title="Responsables").update_layout(height=250), use_container_width=True)
            with cl2:
                if 'ÁREA' in df_fil.columns:
                    st.plotly_chart(px.bar(df_fil['ÁREA'].value_counts().reset_index(), x='ÁREA', y='count', color_discrete_sequence=['#64748B'], title="Áreas").update_layout(height=250), use_container_width=True)

    # --- PESTAÑA 2: CUMPLEAÑOS (CORRECCIÓN SEGÚN TU FOTO) ---
    with tab2:
        mes_actual_nombre = datetime.now().strftime('%B').capitalize()
        st.subheader(f"🎂 Cumpleaños y Trayectoria de {mes_actual_nombre}")
        
        col_f_nac = 'FECHA NACIMIENTO'
        col_name = 'APELLIDO Y NOMBRE'
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), None)

        if not df_cump.empty and col_f_nac in df_cump.columns:
            # LIMPIEZA DE FECHA: Quita el "0:00:00" si existe y espacios
            df_cump[col_f_nac] = df_cump[col_f_nac].astype(str).str.replace(r'\s+.*', '', regex=True).str.strip()
            
            # Conversión forzada
            df_cump['FECHA_DT'] = pd.to_datetime(df_cump[col_f_nac], format='%d/%m/%Y', errors='coerce')
            
            hoy = datetime.now()
            # Filtramos solo los de este mes
            df_mes = df_cump[df_cump['FECHA_DT'].dt.month == hoy.month].copy()
            
            if not df_mes.empty:
                df_mes['DIA'] = df_mes['FECHA_DT'].dt.day
                df_mes = df_mes.sort_values('DIA')
                
                # Dibujar Tarjetas
                c_idx = 0
                for _, row in df_mes.iterrows():
                    if c_idx % 3 == 0: cols = st.columns(3)
                    with cols[c_idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"<h3 style='color:#1E3A8A; margin:0;'>📅 Día {int(row['DIA'])}</h3>", unsafe_allow_html=True)
                            st.markdown(f"**{row[col_name]}**")
                            
                            # Trayectoria
                            if col_f_ing and not df_main.empty:
                                m = df_main[df_main['APELLIDO Y NOMBRE'] == row[col_name]]
                                if not m.empty:
                                    f_i = pd.to_datetime(m[col_f_ing].values[0], errors='coerce', dayfirst=True)
                                    if not pd.isnull(f_i):
                                        ant = hoy.year - f_i.year - ((hoy.month, hoy.day) < (f_i.month, f_i.day))
                                        st.markdown(f"<p style='color:#64748B;'>⭐ Trayectoria: <b>{max(0, ant)} años</b></p>", unsafe_allow_html=True)
                            st.divider()
                            st.button("Felicitar ✨", key=f"btn_{c_idx}", use_container_width=True)
                    c_idx += 1
            else:
                st.info(f"No hay cumpleaños detectados para {mes_actual_nombre}. Revisa que las fechas en la columna '{col_f_nac}' tengan el formato Día/Mes/Año.")
        else:
            st.error("No se pudo leer la columna de fechas. Verifica que se llame 'FECHA NACIMIENTO'.")

except Exception as e:
    st.error(f"Error: {e}")
