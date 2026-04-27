import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión RRHH Exincor", layout="wide")

# 2. COLORES CORPORATIVOS
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=60)
def cargar_datos(gid):
    try:
        # Forzamos la URL de exportación limpia
        url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Error en hoja {gid}: {e}")
        return pd.DataFrame()

try:
    # CARGA DE DATOS (IDs exactos de tus hojas)
    df_main = cargar_datos("1543772338") # Base principal
    df_cump = cargar_datos("540729566")  # Hoja de Cumpleaños
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if archivos:
            st.image(archivos[0], width=150)

    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños y Trayectoria"])

    with tab1:
        # --- FILTROS ---
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        with col_f1:
            conv_opts = ["Todos"] + sorted(df_main['CONVENIO'].dropna().unique().tolist()) if 'CONVENIO' in df_main.columns else ["Todos"]
            sel_conv = st.selectbox("Convenio", conv_opts)
        with col_f2:
            resp_opts = ["Todos"] + sorted(df_main['RESPONSABLE DIRECTO'].dropna().unique().tolist()) if 'RESPONSABLE DIRECTO' in df_main.columns else ["Todos"]
            sel_resp = st.selectbox("Responsable Directo", resp_opts)
        with col_f3:
            tipo_col = next((c for c in df_main.columns if 'CONTRATACIÓN' in c or 'CONTRATACION' in c), 'TIPO DE CONTRATACIÓN')
            tipo_opts = ["Todos"] + sorted(df_main[tipo_col].dropna().unique().tolist()) if tipo_col in df_main.columns else ["Todos"]
            sel_tipo = st.selectbox("Tipo Contratación", tipo_opts)
        with col_f4:
            area_opts = ["Todas"] + sorted(df_main['ÁREA'].dropna().unique().tolist()) if 'ÁREA' in df_main.columns else ["Todas"]
            sel_area = st.selectbox("Área", area_opts)
        with col_f5:
            nombres_opts = ["Todos"] + sorted(df_main['APELLIDO Y NOMBRE'].dropna().unique().tolist()) if 'APELLIDO Y NOMBRE' in df_main.columns else ["Todos"]
            sel_nombre = st.selectbox("Personal", nombres_opts)

        # Aplicar Filtros
        df_fil = df_main.copy()
        if 'CONVENIO' in df_fil.columns and sel_conv != "Todos": df_fil = df_fil[df_fil['CONVENIO'] == sel_conv]
        if 'RESPONSABLE DIRECTO' in df_fil.columns and sel_resp != "Todos": df_fil = df_fil[df_fil['RESPONSABLE DIRECTO'] == sel_resp]
        if tipo_col in df_fil.columns and sel_tipo != "Todos": df_fil = df_fil[df_fil[tipo_col] == sel_tipo]
        if 'ÁREA' in df_fil.columns and sel_area != "Todas": df_fil = df_fil[df_fil['ÁREA'] == sel_area]
        if 'APELLIDO Y NOMBRE' in df_fil.columns and sel_nombre != "Todos": df_fil = df_fil[df_fil['APELLIDO Y NOMBRE'] == sel_nombre]

        # --- CUERPO (7 INDICADORES) ---
        c_met, c_graf = st.columns([1.2, 3.8])
        with c_met:
            st.metric("Total Activos", len(df_fil))
            st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=650)

        with c_graf:
            # 1, 2, 3 y 4: Anillos
            c1, c2, c3, c4 = st.columns(4)
            cols_anillo = ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS']
            tits_anillo = ['Género', 'Categoría', 'Contratación', 'C. Costos']
            for ui, db_col, tit in zip([c1, c2, c3, c4], cols_anillo, tits_anillo):
                with ui:
                    if db_col in df_fil.columns:
                        d_p = df_fil[db_col].value_counts().reset_index()
                        fig = px.pie(d_p, names=db_col, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': tit, 'x': 0.5})
                        st.plotly_chart(fig, use_container_width=True)

            # 5: Puestos
            if 'PUESTO' in df_fil.columns:
                df_p = df_fil['PUESTO'].value_counts().reset_index()
                fig_p = px.bar(df_p, x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Dotación por Puesto")
                fig_p.update_layout(height=280, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)

            # 6 y 7: Responsables y Áreas
            cl1, cl2 = st.columns([2, 1])
            with cl1:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    d_r = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    fig_r = px.bar(d_r, x='RESPONSABLE DIRECTO', y='count', text='count', color_discrete_sequence=['#1E3A8A'], title="Responsables")
                    fig_r.update_layout(height=250)
                    st.plotly_chart(fig_r, use_container_width=True)
            with cl2:
                if 'ÁREA' in df_fil.columns:
                    d_a = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(df_a, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'], title="Áreas")
                    fig_a.update_layout(height=250)
                    st.plotly_chart(fig_a, use_container_width=True)

    with tab2:
        st.subheader("🎂 Cumpleaños y Trayectoria del Mes")
        
        # Identificar columnas
        col_f_nac = next((c for c in df_cump.columns if 'FECHA' in c or 'NACIMIENTO' in c), None)
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), None)

        if col_f_nac and not df_cump.empty:
            df_cump['FECHA_NAC'] = pd.to_datetime(df_cump[col_f_nac], errors='coerce', dayfirst=True)
            hoy = datetime.now()
            df_mes = df_cump[df_cump['FECHA_NAC'].dt.month == hoy.month].copy()
            
            if not df_mes.empty:
                df_mes['DIA'] = df_mes['FECHA_NAC'].dt.day
                df_mes = df_mes.sort_values('DIA')
                
                cols_c = st.columns(3)
                for idx, row in df_mes.reset_index().iterrows():
                    with cols_c[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"### 📅 Día {int(row['DIA'])}")
                            st.markdown(f"**{row['APELLIDO Y NOMBRE']}**")
                            
                            if col_f_ing:
                                m = df_main[df_main['APELLIDO Y NOMBRE'] == row['APELLIDO Y NOMBRE']]
                                if not m.empty:
                                    f_i = pd.to_datetime(m[col_f_ing].values[0], errors='coerce')
                                    if not pd.isnull(f_i):
                                        ant = hoy.year - f_i.year - ((hoy.month, hoy.day) < (f_i.month, f_i.day))
                                        st.markdown(f"⭐ **Trayectoria:** {max(0, ant)} años")
                            
                            st.divider()
                            st.button("Felicitar ✨", key=f"btn_cump_{idx}", use_container_width=True)
            else:
                st.info(f"No hay cumpleaños en {hoy.strftime('%B')}.")
        else:
            st.warning("Verifica los nombres de las columnas en el Excel.")

except Exception as e:
    st.error(f"Error crítico: {e}")
