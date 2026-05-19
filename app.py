import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión RRHH Exincor", layout="wide")

# 2. COLORES Y TRADUCCIONES
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']
COLOR_BAJAS_SUAVE = '#64748B'  # Color sofisticado y menos agresivo que el rojo para las desvinculaciones
MESES_ES = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

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
    
    # NUEVO ORDEN DE PESTAÑAS: Cumpleaños pasa al final
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Panel de Dotación", "📉 Rotación Mensual", "❌ Detalle de Bajas", "🎂 Cumpleaños y Aniversarios"])

    # --- TAB 1: PANEL DE DOTACIÓN ---
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
            
            st.markdown("### 📈 Indicadores Demográficos y Estructura Organizacional")
            c_dem1, c_dem2 = st.columns(2)
            
            with c_dem1:
                if 'EDAD' in df_fil.columns:
                    df_fil['EDAD'] = pd.to_numeric(df_fil['EDAD'], errors='coerce')
                    df_edad_valida = df_fil.dropna(subset=['EDAD'])
                    if not df_edad_valida.empty:
                        bins = [0, 25, 35, 45, 55, 100]
                        labels = ['Hasta 25 años', '26 a 35 años', '36 a 45 años', '46 a 55 años', 'Más de 55 años']
                        df_edad_valida['RANGO_EDAD'] = pd.cut(df_edad_valida['EDAD'], bins=bins, labels=labels, right=False)
                        promedio_edad = df_edad_valida['EDAD'].mean()
                        
                        adultos_mayores = df_edad_valida[df_edad_valida['EDAD'] >= 46]
                        cant_adultos = len(adultos_mayores)
                        porc_adultos = (cant_adultos / len(df_edad_valida)) * 100
                        
                        area_senior = "N/A"
                        if 'ÁREA' in adultos_mayores.columns and not adultos_mayores.empty:
                            area_senior = adultos_mayores['ÁREA'].value_counts().index[0]
                        
                        fig_edad = px.histogram(df_edad_valida, x='RANGO_EDAD', color='ÁREA' if 'ÁREA' in df_edad_valida.columns else None,
                                                title=f"Distribución de Rangos de Edad Abiertos por Área (Promedio: {promedio_edad:.1f} años)",
                                                category_orders={'RANGO_EDAD': labels},
                                                color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig_edad.update_layout(xaxis_title="Rango de Edad", yaxis_title="Cantidad de Colaboradores", height=300, legend_title_text="Áreas")
                        st.plotly_chart(fig_edad, use_container_width=True)
                        
                        st.info(
                            f"**Resumen Ejecutivo (Edad):** La dotación activa presenta una edad promedio de **{promedio_edad:.1f} años**. "
                            f"El **{porc_adultos:.1f}%** de la nómina (**{cant_adultos} colaboradores**) se concentra en las franjas de **46 años o más**, "
                            f"detectándose que el área de **{area_senior}** es la que presenta mayor densidad de este perfil experto."
                        )
            
            with c_dem2:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    df_dep = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    df_dep.columns = ['Responsable Directo', 'Colaboradores a Cargo']
                    df_dep = df_dep[df_dep['Responsable Directo'] != '-']
                    if not df_dep.empty:
                        fig_dep = px.bar(df_dep, x='Colaboradores a Cargo', y='Responsable Directo', 
                                         orientation='h', title="Estructura de Dependencia Jerárquica (Líneas de Reporte)",
                                         color_discrete_sequence=['#64748B'])
                        fig_dep.update_layout(height=300, yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig_dep, use_container_width=True)
                        
                        lider_max = df_dep.iloc[0]['Responsable Directo']
                        cant_max = df_dep.iloc[0]['Colaboradores a Cargo']
                        st.info(f"**Resumen Ejecutivo (Estructura):** Análisis del alcance de control directo por responsable. Actualmente, **{lider_max}** consolida el volumen de reporte más alto con **{cant_max}** colaboradores directos bajo su supervisión jerárquica.")

            st.markdown("---")
            st.markdown("### 📋 Distribución Detallada de Personal")

            c_izq, c_der = st.columns([1.5, 3.5])
            with c_izq:
                st.markdown("<p style='font-weight: bold; margin-bottom: 5px; color: #1E3A8A;'>Cantidad de Personas por Área</p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns:
                    df_areas_cant = df_fil['ÁREA'].value_counts().reset_index()
                    df_areas_cant.columns = ['ÁREA', 'CANTIDAD']
                    st.dataframe(df_areas_cant, hide_index=True, height=350, use_container_width=True)
            with c_der:
                i1, i2, i3, i4 = st.columns(4)
                for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                    if c in df_fil.columns:
                        counts = df_fil[c].value_counts()
                        fig = px.pie(counts.reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_AZUL_GRIS)
                        fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                        ui.plotly_chart(fig, use_container_width=True)
                        
                if not df_fil.empty:
                    gen_pred = df_fil['GÉNERO'].value_counts().index[0] if 'GÉNERO' in df_fil.columns and not df_fil['GÉNERO'].empty else "N/A"
                    cat_pred = df_fil['CATEGORÍA'].value_counts().index[0] if 'CATEGORÍA' in df_fil.columns and not df_fil['CATEGORÍA'].empty else "N/A"
                    st.info(f"**Análisis de Distribución Interna:** Los indicadores de estructura muestran que el género predominante es **{gen_pred}** y la categoría con mayor densidad de colaboradores es **{cat_pred}**.")

    # --- TAB 2: ROTACIÓN MENSUAL ---
    with tab2:
        st.header("📉 Rotación Mensual")
        if not df_rot.empty:
            df_rot['ROT_VAL'] = pd.to_numeric(df_rot['ROTACIÓN'].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
            
            c1, c2 = st.columns(2)
            with c1:
                fig_turn = px.line(df_rot, x='MES', y='ROT_VAL', title="% Turnover", markers=True)
                fig_turn.update_yaxes(ticksuffix="%")
                st.plotly_chart(fig_turn, use_container_width=True)
            with c2:
                st.plotly_chart(px.bar(df_rot, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Movimientos"), use_container_width=True)
            
            df_rot_valida = df_rot.dropna(subset=['ROT_VAL'])
            if not df_rot_valida.empty:
                ult_fila = df_rot_valida.iloc[-1]
                ult_mes = ult_fila['MES']
                ult_rot = ult_fila['ROT_VAL']
                texto_rotacion = f"registra su última medición disponible en **{ult_mes}** reflejando un **{ult_rot:.1f}%**."
            else:
                texto_rotacion = "no registra porcentajes numéricos procesables."
                
            st.info(f"**Interpretación de Rotación:** El índice de rotación de personal (*Turnover*) {texto_rotacion}")

    # --- TAB 3: DETALLE DE BAJAS (REDISEÑADA COMPLETAMENTE) ---
    with tab3:
        st.header("❌ Detalle y Registro de Egresos")
        if not df_baj.empty:
            df_e = df_baj[df_baj['ANTIGUEDAD'].astype(str).str.contains('años|meses|días', case=False, na=False)].copy()
            df_e['FECHA_BAJA_DT'] = limpiar_fecha(df_e, 'FECHA DE BAJA')
            df_e['MES_NOMBRE'] = df_e['FECHA_BAJA_DT'].dt.strftime('%B').map(MESES_ES)
            df_e['MES_NUM'] = df_e['FECHA_BAJA_DT'].dt.month
            
            # Filtro dinámico cruzado por área si se seleccionó en el panel principal
            if 'sel_area' in locals() and sel_area != "Todas":
                if 'ÁREA' in df_e.columns:
                    df_e = df_e[df_e['ÁREA'] == sel_area]

            b_mes = df_e.groupby(['MES_NUM', 'MES_NOMBRE']).size().reset_index(name='CANTIDAD').sort_values('MES_NUM')
            col_t = [c for c in df_e.columns if 'TIPO DE BAJA' in c][0]

            # Fila Superior: Gráficos estilizados, más chicos y con colores corporativos suaves
            g1, g2, g3 = st.columns([1.5, 1.25, 1.25])
            
            with g1:
                # Barras mensuales más bajas y en color sobrio grisáceo
                fig_bar_bajas = px.bar(b_mes, x='MES_NOMBRE', y='CANTIDAD', title="Bajas por Mes", text='CANTIDAD', color_discrete_sequence=[COLOR_BAJAS_SUAVE])
                fig_bar_bajas.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), yaxes_visible=False)
                st.plotly_chart(fig_bar_bajas, use_container_width=True)
                
            with g2:
                fig_motivo = px.pie(df_e, names='MOTIVO', title="Causas de Salida", hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                fig_motivo.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), showlegend=False)
                st.plotly_chart(fig_motivo, use_container_width=True)
                
            with g3:
                fig_tipo_b = px.pie(df_e, names=col_t, title="Tipo de Egreso", hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                fig_tipo_b.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), showlegend=False)
                st.plotly_chart(fig_tipo_b, use_container_width=True)

            st.markdown("---")
            
            # Fila Inferior: Incorporación de la Nómina Detallada de Bajas solicitada
            st.markdown("<p style='font-weight: bold; font-size: 16px; color: #1E3A8A;'>📋 Registro Nominal de Personal Desvinculado</p>", unsafe_allow_html=True)
            
            columnas_mostrar = ['APELLIDO Y NOMBRE', 'ÁREA', 'FECHA DE BAJA', 'MOTIVO', col_t]
            # Nos aseguramos de mostrar solo columnas existentes para evitar errores
            cols_reales = [c for c in columnas_mostrar if c in df_e.columns]
            
            if not df_e.empty:
                df_tabla_bajas = df_e[cols_reales].sort_values(by=cols_reales[2] if len(cols_reales)>2 else cols_reales[0], ascending=False)
                st.dataframe(df_tabla_bajas, hide_index=True, use_container_width=True, height=250)
            else:
                st.info("No se registran bajas para los criterios seleccionados.")
            
            # Resumen interpretativo
            motivo_pred = df_e['MOTIVO'].value_counts().index[0] if 'MOTIVO' in df_e.columns and not df_e['MOTIVO'].empty else "N/A"
            tipo_pred = df_e[col_t].value_counts().index[0] if not df_e[col_t].empty else "N/A"
            st.info(f"**Análisis Crítico de Egresos:** La principal causa registrada de salida corresponde a **{motivo_pred}**, clasificada mayoritariamente como **{tipo_pred}**.")

    # --- TAB 4: CUMPLEAMOS Y ANIVERSARIOS (MOVIDA AL FINAL) ---
    with tab4:
        meses_lista = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        sel_mes = st.selectbox("Mes de consulta", meses_lista, index=hoy.month-1)
        num_mes = meses_lista.index(sel_mes) + 1
        
        t_cump, t_ani = st.tabs(["🎂 Cumpleaños", "🎖️ Aniversarios Laborales"])
        
        with t_cump:
            df_cump['DT_NAC'] = limpiar_fecha(df_cump, 'FECHA NACIMIENTO')
            df_v = df_cump[df_cump['DT_NAC'].dt.month == num_mes].copy()
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
            else: st.info(f"No hay cumpleaños en {sel_mes}")

        with t_ani:
            col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), 'FECHA INGRESO')
            df_main['DT_ING'] = limpiar_fecha(df_main, col_f_ing)
            df_ani = df_main[df_main['DT_ING'].dt.month == num_mes].copy()
            if not df_ani.empty:
                for i in range(0, len(df_ani), 3):
                    cols = st.columns(3)
                    for j, (_, r) in enumerate(df_ani.iloc[i:i+3].iterrows()):
                        with cols[j]:
                            with st.container(border=True):
                                ant = hoy.year - r['DT_ING'].year
                                st.markdown(f"### 🎖️ {int(ant)} Años")
                                st.markdown(f"**{r['APELLIDO Y NOMBRE']}**")
                                st.caption(f"Ingreso: {r['DT_ING'].strftime('%d/%m/%Y')}")
            else: st.info(f"No hay aniversarios en {sel_mes}")

except Exception as e:
    st.error(f"Error crítico: {e}")
