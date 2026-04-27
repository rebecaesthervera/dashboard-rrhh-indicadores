import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión RRHH Exincor", layout="wide")

# 2. COLORES CORPORATIVOS
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']

@st.cache_data(ttl=60) # Actualización cada 60 segundos
def cargar_datos(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid={gid}"
        df = pd.read_csv(url)
        # Limpieza profunda de columnas: sin espacios y en mayúsculas
        df.columns = df.columns.str.strip().str.upper()
        # Limpieza de datos: quitar espacios en blanco extra dentro de las celdas
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"Error crítico cargando hoja {gid}: {e}")
        return pd.DataFrame()

try:
    # CARGA DE DATOS
    df_main = cargar_datos("1543772338") # Base principal
    df_cump = cargar_datos("540729566")  # Hoja cumpleaños (3ra pestaña)
    
    if not df_main.empty and 'LEGAJO' in df_main.columns:
        df_main = df_main.dropna(subset=['LEGAJO'])

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f]
        if archivos:
            st.image(archivos[0], width=150)

    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")

    tab1, tab2 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños y Trayectoria"])

    with tab1:
        # (Esta sección del panel de dotación se mantiene igual, ya que funciona bien)
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
            cols_anillo = ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS']
            tits_anillo = ['Género', 'Categoría', 'Contratación', 'C. Costos']
            for ui, db_col, tit in zip([c1, c2, c3, c4], cols_anillo, tits_anillo):
                with ui:
                    if db_col in df_fil.columns and not df_fil[db_col].empty:
                        d_p = df_fil[db_col].value_counts().reset_index()
                        fig = px.pie(d_p, names=db_col, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': tit, 'x': 0.5})
                        st.plotly_chart(fig, use_container_width=True)
            if 'PUESTO' in df_fil.columns:
                df_p = df_fil['PUESTO'].value_counts().reset_index()
                fig_p = px.bar(df_p, x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Dotación por Puesto")
                fig_p.update_layout(height=280, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_p, use_container_width=True)
            cl1, cl2 = st.columns([2, 1])
            with cl1:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    d_r = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    fig_r = px.bar(d_r, x='RESPONSABLE DIRECTO', y='count', text='count', color_discrete_sequence=['#1E3A8A'], title="Responsables")
                    st.plotly_chart(fig_r, use_container_width=True)
            with cl2:
                if 'ÁREA' in df_fil.columns:
                    d_a = df_fil['ÁREA'].value_counts().reset_index()
                    fig_a = px.bar(d_a, x='ÁREA', y='count', text='count', color_discrete_sequence=['#64748B'], title="Áreas")
                    st.plotly_chart(fig_a, use_container_width=True)

    # --- PESTAÑA 2: CUMPLEAÑOS (SECCIÓN CORREGIDA Y ROBUSTA) ---
    with tab2:
        st.subheader(f"🎂 Cumpleaños y Trayectoria de {datetime.now().strftime('%B')}")
        
        # 1. Nombres de columnas (limpios por la función cargar_datos)
        col_f_nac = 'FECHA NACIMIENTO'
        col_name = 'APELLIDO Y NOMBRE'
        # Buscador flexible para la fecha de ingreso en la hoja principal
        col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), None)

        if not df_cump.empty and col_f_nac in df_cump.columns and col_name in df_cump.columns:
            
            # 2. CONVERSIÓN ROBUSTA DE FECHAS
            # Primero, aseguramos que la columna sea texto y limpiamos espacios
            df_cump[col_f_nac] = df_cump[col_f_nac].astype(str).str.strip()
            
            # Intentamos la conversión con el formato día/mes/año, ignorando errores
            df_cump['FECHA_NAC_DT'] = pd.to_datetime(df_cump[col_f_nac], format='%d/%m/%Y', errors='coerce')
            
            # Si quedan fechas sin convertir (NaT), intentamos una conversión genérica
            df_cump['FECHA_NAC_DT'] = df_cump['FECHA_NAC_DT'].fillna(pd.to_datetime(df_cump[col_f_nac], errors='coerce'))
            
            hoy = datetime.now()
            
            # 3. Filtrar por mes actual (Abril)
            # Solo tomamos las filas donde la conversión de fecha fue exitosa
            df_validos = df_cump.dropna(subset=['FECHA_NAC_DT'])
            df_mes = df_validos[df_validos['FECHA_NAC_DT'].dt.month == hoy.month].copy()
            
            # (Opcional) Tabla de diagnóstico: Solo se ve si hay errores de conversión
            errores = df_cump[df_cump['FECHA_NAC_DT'].isna()]
            if not errores.empty and st.checkbox("Ver errores de formato de fecha en Excel"):
                st.warning(f"Hay {len(errores)} filas donde la fecha no se pudo leer. Revisa el formato en Excel (debe ser DD/MM/AAAA).")
                st.dataframe(errores[[col_name, col_f_nac]])

            if not df_mes.empty:
                # Ordenar por día
                df_mes['DIA'] = df_mes['FECHA_NAC_DT'].dt.day
                df_mes = df_mes.sort_values('DIA')
                
                # 4. Diseño de Tarjetas
                cols_c = st.columns(3) # 3 tarjetas por fila
                
                for idx, row in df_mes.reset_index().iterrows():
                    with cols_c[idx % 3]:
                        with st.container(border=True):
                            # Encabezado con el día
                            st.markdown(f"<h3 style='color:#1E3A8A; margin:0;'>📅 Día {int(row['DIA'])}</h3>", unsafe_allow_html=True)
                            
                            # Nombre completo
                            nombre_empleado = row[col_name]
                            st.markdown(f"**{nombre_empleado}**")
                            
                            # 5. Cálculo de Trayectoria (Cruce de datos)
                            if col_f_ing and not df_main.empty:
                                # Buscamos al empleado en la base principal por nombre exacto
                                match = df_main[df_main['APELLIDO Y NOMBRE'] == nombre_empleado]
                                
                                if not match.empty:
                                    # Leemos la fecha de ingreso
                                    fecha_ingreso_raw = match[col_f_ing].values[0]
                                    # Intentamos convertir la fecha de ingreso
                                    f_i = pd.to_datetime(fecha_ingreso_raw, errors='coerce', dayfirst=True)
                                    
                                    if not pd.isnull(f_i):
                                        # Calculamos años (sin contar días/meses restantes)
                                        anos = hoy.year - f_i.year - ((hoy.month, hoy.day) < (f_i.month, f_i.day))
                                        
                                        # Mostramos la trayectoria con una estrella
                                        st.markdown(f"<p style='color:#64748B; margin:5px 0;'>⭐ Trayectoria: <b>{max(0, anos)} años</b></p>", unsafe_allow_html=True)
                                        
                                        # Etiquetas especiales
                                        if anos >= 10: st.success("🏆 Personal Histórico")
                                        elif anos == 0: st.caption("🌱 ¡Su primer año!")
                                    else:
                                        st.caption("⚠️ Fecha ingreso inválida en base principal")
                                else:
                                    st.caption("ℹ️ No encontrado en base principal")
                            
                            st.divider()
                            # Botón de acción (opcional)
                            st.button("Felicitar ✨", key=f"btn_cump_v3_{idx}", use_container_width=True)
            else:
                st.info(f"No se encontraron cumpleaños registrados para el mes de {hoy.strftime('%B')}. Revisa que las fechas en la pestaña de cumpleaños estén en formato DD/MM/AAAA.")
        else:
            st.error("Error de configuración: No se encontraron las columnas 'FECHA NACIMIENTO' o 'APELLIDO Y NOMBRE' en la pestaña de cumpleaños.")

except Exception as e:
    st.error(f"Ocurrió un error general en la aplicación: {e}")
