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
        cols = []
        count = {}
        for col in df.columns:
            c_upper = str(col).strip().upper()
            if c_upper in count:
                count[c_upper] += 1
                cols.append(f"{c_upper}_{count[c_upper]}")
            else:
                count[c_upper] = 0
                cols.append(c_upper)
        df.columns = cols
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
    # --- CARGA DE DATOS ---
    df_main = cargar_datos("1543772338") 
    df_cump = cargar_datos("540729566")  
    df_rot = cargar_datos("209126075")   
    df_baj = cargar_datos("728077629")   
    hoy = datetime.now()

    # --- ENCABEZADO ---
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        archivos = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'app' not in f]
        if archivos: st.image(archivos[0], width=150)
    with col_titulo:
        st.markdown("<h1 style='color: #1E3A8A; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Panel de Dotación", "🎂 Cumpleaños", "📉 Rotación Mensual", "❌ Detalle de Bajas"])

    # --- TAB 1: PANEL DE DOTACIÓN (RECUPERADO) ---
    with tab1:
        if not df_main.empty:
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

            st.metric("Total Activos", len(df_fil))
            c_izq, c_der = st.columns([1, 4])
            with c_izq:
                st.dataframe(df_fil[['APELLIDO Y NOMBRE']], hide_index=True, height=450, use_container_width=True)
            with c_der:
                i1, i2, i3, i4 = st.columns(4)
                for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                    if c in df_fil.columns:
                        fig = px.pie(df_fil[c].value_counts().reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=200, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                        ui.plotly_chart(fig, use_container_width=True)
                if 'PUESTO' in df_fil.columns:
                    st.plotly_chart(px.bar(df_fil['PUESTO'].value_counts().reset_index(), x='PUESTO', y='count', text='count', color_discrete_sequence=['#3B82F6'], title="Puestos").update_layout(height=300), use_container_width=True)

    # --- TAB 2: CUMPLEAÑOS (CORREGIDO) ---
    with tab2:
        if not df_cump.empty:
            df_cump['DT_NAC'] = limpiar_fecha(df_cump, 'FECHA NACIMIENTO')
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            sel_mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: meses[x-1], index=hoy.month-1)
            df_v = df_cump[df_cump['DT_NAC'].dt.month == sel_mes].copy()
            st.subheader(f"Cumpleaños de {meses[sel_mes-1]}: {len(df_v)}")
            if not df_v.empty:
                df_v = df_v.sort_values(by='DT_NAC', key=lambda x: x.dt.day)
                st.dataframe(df_v[['APELLIDO Y NOMBRE', 'FECHA NACIMIENTO']], hide_index=True, use_container_width=True)

    # --- TAB 3: ROTACIÓN (CORREGIDO % Y GRÁFICOS) ---
    with tab3:
        st.header("📉 Rotación Mensual")
        if not df_rot.empty:
            # Corregimos el valor de rotación (si viene como 154, lo pasamos a 1.54)
            df_rot['ROT_CALC'] = pd.to_numeric(df_rot['ROTACIÓN'], errors='coerce') / 100
            
            c1, c2 = st.columns(2)
            with c1:
                fig_turn = px.line(df_rot, x='MES', y='ROT_CALC', title="% Turnover", markers=True)
                fig_turn.update_layout(yaxis_tickformat='.2%')
                st.plotly_chart(fig_turn, use_container_width=True)
            with c2:
                st.plotly_chart(px.bar(df_rot, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Movimientos"), use_container_width=True)
            st.dataframe(df_rot[['MES', 'DOTACIÓN INICIAL', 'ALTAS', 'BAJAS', 'DOTACIÓN FINAL', 'ROTACIÓN']], hide_index=True)

    # --- TAB 4: DETALLE DE BAJAS (CON CANTIDAD POR MES) ---
    with tab4:
        st.header("❌ Detalle Bajas")
        if not df_baj.empty:
            df_e = df_baj[df_baj['ANTIGUEDAD'].astype(str).str.contains('años|meses|días', case=False, na=False)].copy()
            df_e['FECHA_BAJA_DT'] = limpiar_fecha(df_e, 'FECHA DE BAJA')
            
            # Cantidad por mes
            df_e['MES_BAJA'] = df_e['FECHA_BAJA_DT'].dt.strftime('%m - %B')
            bajas_por_mes = df_e.groupby('MES_BAJA').size().reset_index(name='CANTIDAD')
            
            col_inf1, col_inf2 = st.columns([1, 2])
            with col_inf1:
                st.subheader("Bajas por Mes")
                st.table(bajas_por_mes)
            with col_inf2:
                st.plotly_chart(px.bar(bajas_por_mes, x='MES_BAJA', y='CANTIDAD', title="Cantidad de Bajas Mensuales", text='CANTIDAD', color_discrete_sequence=['#EF4444']), use_container_width=True)

            b1, b2 = st.columns(2)
            with b1: st.plotly_chart(px.pie(df_e, names='MOTIVO', title="Causas de Salida", hole=0.4), use_container_width=True)
            with b2:
                col_t = [c for c in df_e.columns if 'TIPO DE BAJA' in c][0]
                st.plotly_chart(px.pie(df_e, names=col_t, title="Tipo de Egreso", hole=0.4), use_container_width=True)
            st.plotly_chart(px.histogram(df_e, x='ÁREA', color='MOTIVO', title="Bajas por Área"), use_container_width=True)

except Exception as e:
    st.error(f"Error crítico: {e}")
