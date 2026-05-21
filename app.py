import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión RRHH Exincor", layout="wide")

# --- TUNEO DE COLOR DE FONDO Y DISEÑO DE TARJETAS ---
st.markdown("""
    <style>
    /* Fondo general de la plataforma con un sutil contraste azul-gris */
    .stApp {
        background-color: #f1f5f9;
    }
    /* Estilo premium para las tarjetas visuales de cumpleaños y aniversarios */
    .custom-card {
        background-color: #ffffff;
        border-left: 6px solid #0f2c59; /* Azul corporativo oscuro */
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .card-title { font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .card-subtitle { font-size: 13px; color: #475569; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }
    .card-badge { display: inline-block; background-color: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; margin-right: 4px; margin-bottom: 4px;}
    .card-badge-secondary { display: inline-block; background-color: #f1f5f9; color: #475569; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 11px; }
    
    /* Diseño estilizado para los contenedores de las métricas superiores */
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. COLORES Y TRADUCCIONES (Inspirados en la paleta premium, sin amarillo)
PALETA_PREMIUM = ['#0f2c59', '#1d4ed8', '#b1b1b1', '#64748b', '#38bdf8', '#5a8cb3']
COLOR_BAJAS_SUAVE = '#64748B'  
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
    # --- CARGA DE DATOS REALES ---
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
        st.markdown("<h1 style='color: #0f2c59; margin-top: 10px;'>Gestión de RRHH Exincor</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Panel de Dotación", "📉 Rotación Mensual", "📋 Detalle de Egresos", "🎂 Cumpleaños y Aniversarios"])

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

            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Personal Activo Filtrado", f"{len(df_fil):,}".replace(",", "."))
            st.markdown('</div>', unsafe_allow_html=True)
            
            promedio_edad = 0
            cant_adultos = 0
            porc_adultos = 0
            area_senior = "N/A"
            df_edad_valida = pd.DataFrame()

            if 'EDAD' in df_fil.columns:
                df_fil['EDAD'] = pd.to_numeric(df_fil['EDAD'], errors='coerce')
                df_edad_valida = df_fil.dropna(subset=['EDAD'])
                if not df_edad_valida.empty:
                    promedio_edad = df_edad_valida['EDAD'].mean()
                    adultos_mayores = df_edad_valida[df_edad_valida['EDAD'] >= 46]
                    cant_adultos = len(adultos_mayores)
                    porc_adultos = (cant_adultos / len(df_edad_valida)) * 100
                    if 'ÁREA' in adultos_mayores.columns and not adultos_mayores.empty:
                        area_senior = adultos_mayores['ÁREA'].value_counts().index[0]
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 📈 Indicadores Demográficos y Estructura Organizacional")
            c_dem1, c_dem2 = st.columns(2)
            
            with c_dem1:
                if not df_edad_valida.empty:
                    bins = [0, 25, 35, 45, 55, 100]
                    labels = ['Hasta 25 años', '26 a 35 años', '36 a 45 años', '46 a 55 años', 'Más de 55 años']
                    df_edad_valida['RANGO_EDAD'] = pd.cut(df_edad_valida['EDAD'], bins=bins, labels=labels, right=False)
                    
                    fig_edad = px.histogram(df_edad_valida, x='RANGO_EDAD', color='ÁREA' if 'ÁREA' in df_edad_valida.columns else None,
                                            title="Distribución de Rangos de Edad Abiertos por Área",
                                            category_orders={'RANGO_EDAD': labels},
                                            color_discrete_sequence=PALETA_PREMIUM)
                    fig_edad.update_layout(xaxis_title="Rango de Edad", yaxis_title="Cantidad de Colaboradores", height=300, legend_title_text="Áreas")
                    st.plotly_chart(fig_edad, use_container_width=True)
                    
                    st.info(
                        f"**Resumen Ejecutivo (Edad):** La dotación activa presenta una edad promedio de **{promedio_edad:.1f} años**. "
                        f"El **{porc_adultos:.1f}%** de la nómina (**{cant_adultos} colaboradores**) se concentra en las franjas de **46 años o más**, "
                        f"detectándose que el área de **{area_senior}** es la que presenta mayor densidad de este perfil experto."
                    )
                    
                    # --- ALERTA DETALLADA DE PRÓXIMOS A JUBILARSE ---
                    st.markdown("---")
                    st.markdown("#### ⏳ Control de Seguimiento Pre-Jubilatorio")
                    col_sexo = next((c for c in df_edad_valida.columns if 'SEXO' in c or 'GÉNERO' in c or 'GENERO' in c), None)
                    
                    if col_sexo:
                        df_edad_valida.loc[:, col_sexo] = df_edad_valida[col_sexo].astype(str).str.strip().str.upper()
                        jubilables = df_edad_valida[
                            ((df_edad_valida[col_sexo].str.contains('F', na=False)) & (df_edad_valida['EDAD'] >= 59)) |
                            ((df_edad_valida[col_sexo].str.contains('M', na=False)) & (df_edad_valida['EDAD'] >= 64))
                        ]
                    else:
                        jubilables = df_edad_valida[df_edad_valida['EDAD'] >= 59]
                    
                    if not jubilables.empty:
                        st.warning(f"⚠️ **Atención:** Se identificaron **{len(jubilables)}** colaboradores alcanzando la edad límite o próximos a iniciar gestiones jubilatorias:")
                        cols_mostrar_jub = [c for c in ['APELLIDO Y NOMBRE', 'ÁREA', 'EDAD', col_sexo] if c and c in jubilables.columns]
                        st.dataframe(jubilables[cols_mostrar_jub].sort_values('EDAD', ascending=False), hide_index=True, use_container_width=True)
                    else:
                        st.success("✅ No se registran colaboradores en rangos de edad críticos para trámite jubilatorio inmediato.")
            
            with c_dem2:
                if 'RESPONSABLE DIRECTO' in df_fil.columns:
                    df_dep = df_fil['RESPONSABLE DIRECTO'].value_counts().reset_index()
                    df_dep.columns = ['Responsable Directo', 'Colaboradores a Cargo']
                    df_dep = df_dep[df_dep['Responsable Directo'] != '-']
                    if not df_dep.empty:
                        fig_dep = px.bar(df_dep, x='Colaboradores a Cargo', y='Responsable Directo', 
                                         orientation='h', title="Estructura de Dependencia Jerárquica (Líneas de Reporte)",
                                         color_discrete_sequence=[PALETA_PREMIUM[0]])
                        fig_dep.update_layout(height=300, yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig_dep, use_container_width=True)
                        
                        lider_max = df_dep.iloc[0]['Responsable Directo']
                        cant_max = df_dep.iloc[0]['Colaboradores a Cargo']
                        st.info(f"**Resumen Ejecutivo (Estructura):** Análisis del alcance de control directo por responsable. Actualmente, **{lider_max}** consolida el volumen de reporte más alto con **{cant_max}** colaboradores directos bajo su supervisión jerárquica.")

            st.markdown("---")
            st.markdown("### 📋 Distribución Detallada de Personal")

            c_izq, c_der = st.columns([1.5, 3.5])
            with c_izq:
                st.markdown("<p style='font-weight: bold; margin-bottom: 5px; color: #0f2c59;'>Cantidad de Personas por Área</p>", unsafe_allow_html=True)
                if 'ÁREA' in df_fil.columns:
                    df_areas_cant = df_fil['ÁREA'].value_counts().reset_index()
                    df_areas_cant.columns = ['ÁREA', 'CANTIDAD']
                    st.dataframe(df_areas_cant, hide_index=True, height=350, use_container_width=True)
            with c_der:
                i1, i2, i3, i4 = st.columns(4)
                for ui, c, t in zip([i1, i2, i3, i4], ['GÉNERO', 'CATEGORÍA', tipo_col, 'CENTRO DE COSTOS'], ['Género', 'Categoría', 'Contratación', 'C. Costos']):
                    if c in df_fil.columns:
                        counts = df_fil[c].value_counts()
                        # Usamos la paleta premium sin amarillo
                        fig = px.pie(counts.reset_index(), names=c, values='count', hole=0.6, color_discrete_sequence=PALETA_PREMIUM)
                        fig.update_layout(height=220, margin=dict(t=30, b=0, l=0, r=0), showlegend=False, title={'text': t, 'x': 0.5})
                        ui.plotly_chart(fig, use_container_width=True)
                        
                if not df_fil.empty:
                    gen_pred = df_fil['GÉNERO'].value_counts().index[0] if 'GÉNERO' in df_fil.columns and not df_fil['GÉNERO'].empty else "N/A"
                    cat_pred = df_fil['CATEGORÍA'].value_counts().index[0] if 'CATEGORÍA' in df_fil.columns and not df_fil['CATEGORÍA'].empty else "N/A"
                    st.info(f"**Análisis de Distribución Interna:** Los indicadores de estructura muestran que el género predominante es **{gen_pred}** y la categoría con mayor densidad de colaboradores es **{cat_pred}**.")

    # --- TAB 2: ROTACIÓN MENSUAL ---
    with tab2:
        st.header("📉 Análisis de Rotación y Movimientos")
        if not df_rot.empty:
            df_rot['ROT_VAL'] = pd.to_numeric(df_rot['ROTACIÓN'].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
            df_rot['ALTAS'] = pd.to_numeric(df_rot['ALTAS'], errors='coerce').fillna(0)
            df_rot['BAJAS'] = pd.to_numeric(df_rot['BAJAS'], errors='coerce').fillna(0)
            
            df_rot_valida = df_rot.dropna(subset=['ROT_VAL'])
            if not df_rot_valida.empty:
                ult_fila = df_rot_valida.iloc[-1]
                ult_mes = ult_fila['MES']
                ult_rot = ult_fila['ROT_VAL']
                texto_rotacion = f"registra su última medición disponible en **{ult_mes}** reflejando un **{ult_rot:.1f}%**."
                idx_ultimo = df_rot_valida.index[-1]
                df_rot_activa = df_rot.loc[:idx_ultimo].copy()
            else:
                texto_rotacion = "no registra porcentajes numéricos procesables."
                ult_rot = 0
                ult_mes = "N/A"
                df_rot_activa = df_rot.copy()

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(label=f"Turnover Último Mes ({ult_mes})", value=f"{ult_rot:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(label="Total Altas Acumuladas", value=f"{int(df_rot_activa['ALTAS'].sum())} Pers.")
                st.markdown('</div>', unsafe_allow_html=True)
            with m3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric(label="Total Bajas Acumuladas", value=f"{int(df_rot_activa['BAJAS'].sum())} Pers.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")

            c1, c2 = st.columns(2)
            with c1:
                fig_turn = px.line(df_rot_activa, x='MES', y='ROT_VAL', title="Evolución Mensual del % Turnover", markers=True, color_discrete_sequence=[PALETA_PREMIUM[0]])
                fig_turn.update_yaxes(ticksuffix="%")
                fig_turn.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10))
                st.plotly_chart(fig_turn, use_container_width=True)
                
            with c2:
                # Usamos colores premium sin amarillo
                fig_mov = px.bar(df_rot_activa, x='MES', y=['ALTAS', 'BAJAS'], barmode='group', title="Balance de Movimientos de Personal", color_discrete_sequence=[PALETA_PREMIUM[0], PALETA_PREMIUM[2]])
                fig_mov.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10), legend_title_text="Movimiento")
                st.plotly_chart(fig_mov, use_container_width=True)
            
            st.info(f"**Interpretación de Rotación:** El índice de rotación de personal (*Turnover*) {texto_rotacion} Al ocultar las proyecciones vacías del año, se evidencia con claridad el comportamiento real del período.")

    # --- TAB 3: DETALLE DE EGRESOS ---
    with tab3:
        st.header("📋 Detalle y Registro de Egresos")
        if not df_baj.empty:
            df_e = df_baj[df_baj['ANTIGUEDAD'].astype(str).str.contains('años|meses|días', case=False, na=False)].copy()
            df_e['FECHA_BAJA_DT'] = limpiar_fecha(df_e, 'FECHA DE BAJA')
            df_e['MES_NOMBRE'] = df_e['FECHA_BAJA_DT'].dt.strftime('%B').map(MESES_ES)
            df_e['MES_NUM'] = df_e['FECHA_BAJA_DT'].dt.month
            
            if 'sel_area' in locals() and sel_area != "Todas" and 'ÁREA' in df_e.columns:
                df_e = df_e[df_e['ÁREA'] == sel_area]

            b_mes = df_e.groupby(['MES_NUM', 'MES_NOMBRE']).size().reset_index(name='CANTIDAD').sort_values('MES_NUM')
            col_t = [c for c in df_e.columns if 'TIPO DE BAJA' in c][0]

            g1, g2, g3 = st.columns([1.5, 1.25, 1.25])
            with g1:
                fig_bar_bajas = px.bar(b_mes, x='MES_NOMBRE', y='CANTIDAD', title="Bajas por Mes", text='CANTIDAD', color_discrete_sequence=[COLOR_BAJAS_SUAVE])
                fig_bar_bajas.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), yaxis_visible=False)
                st.plotly_chart(fig_bar_bajas, use_container_width=True)
                
            with g2:
                # Usamos colores premium sin amarillo
                fig_motivo = px.pie(df_e, names='MOTIVO', title="Causas de Salida", hole=0.5, color_discrete_sequence=PALETA_PREMIUM)
                fig_motivo.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), showlegend=False)
                st.plotly_chart(fig_motivo, use_container_width=True)
                
            with g3:
                # Usamos colores premium sin amarillo
                fig_tipo_b = px.pie(df_e, names=col_t, title="Tipo de Egreso", hole=0.5, color_discrete_sequence=PALETA_AZUL_GRIS)
                fig_tipo_b.update_layout(height=180, margin=dict(t=30, b=10, l=10, r=10), showlegend=False)
                st.plotly_chart(fig_tipo_b, use_container_width=True)

            st.markdown("---")
            st.markdown("<p style='font-weight: bold; font-size: 16px; color: #0f2c59;'>📋 Registro Nominal de Personal Desvinculado</p>", unsafe_allow_html=True)
            
            columnas_mostrar = ['APELLIDO Y NOMBRE', 'ÁREA', 'FECHA DE BAJA', 'MOTIVO', col_t]
            cols_reales = [c for c in columnas_mostrar if c in df_e.columns]
            
            if not df_e.empty:
                df_tabla_bajas = df_e[cols_reales].sort_values(by=cols_reales[2] if len(cols_reales)>2 else cols_reales[0], ascending=False)
                st.dataframe(df_tabla_bajas, hide_index=True, use_container_width=True, height=250)
            else:
                st.info("No se registran bajas para los criterios seleccionados.")
            
            motivo_pred = df_e['MOTIVO'].value_counts().index[0] if 'MOTIVO' in df_e.columns and not df_e['MOTIVO'].empty else "N/A"
            tipo_pred = df_e[col_t].value_counts().index[0] if not df_e[col_t].empty else "N/A"
            st.info(f"**Análisis Crítico de Egresos:** La principal causa registrada de salida corresponde a **{motivo_pred}**, clasificada mayoritariamente como **{tipo_pred}**.")

    # --- TAB 4: CUMPLEAÑOS Y ANIVERSARIOS ---
    with tab4:
        st.header("🎉 Agenda de Celebraciones de la Nómina")
        
        meses_lista = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # --- MEJORA: CONSOLA DE FILTRO COMPACTO ---
        st.markdown('<div class="custom-card" style="border-left:none; border-top: 4px solid #0f2c59; padding: 15px; background-color: #f8fafc; margin-bottom: 25px;">', unsafe_allow_html=True)
        c_filtro_izq, c_filtro_der = st.columns([1.5, 3.5])
        with c_filtro_izq:
            sel_mes_dropdown = st.selectbox(
                label="📅 Seleccionar Período de Consulta:",
                options=["Todo el Año"] + meses_lista,
                index=0
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        sel_meses = [] if sel_mes_dropdown == "Todo el Año" else [sel_mes_dropdown]
        st.markdown("<br>", unsafe_allow_html=True)
        
        t_cump, t_ani = st.tabs(["🎂 Cumpleaños", "🎖️ Aniversarios Laborales"])
        
        with t_cump:
            if not df_cump.empty:
                df_cump['DT_NAC'] = limpiar_fecha(df_cump, 'FECHA NACIMIENTO')
                df_cump['MES_NOMBRE'] = df_cump['DT_NAC'].dt.month.apply(lambda x: meses_lista[int(x)-1] if pd.notnull(x) else None)
                df_cump['DIA'] = df_cump['DT_NAC'].dt.day
                
                if sel_meses:
                    df_v = df_cump[df_cump['MES_NOMBRE'].isin(sel_meses)].copy()
                    if not df_v.empty:
                        df_v['MES_NUM'] = df_v['DT_NAC'].dt.month
                        df_v = df_v.sort_values(['MES_NUM', 'DIA'])
                else:
                    df_v = df_cump.dropna(subset=['DT_NAC']).copy()
                    if not df_v.empty:
                        df_v['MES_NUM'] = df_v['DT_NAC'].dt.month
                        df_v = df_v.sort_values(['MES_NUM', 'DIA'])
                
                if not df_v.empty:
                    st.write(f"Mostrando **{len(df_v)}** cumpleaños registrados:")
                    
                    col1, col2, col3 = st.columns(3)
                    for idx, (_, r) in enumerate(df_v.reset_index().iterrows()):
                        if idx % 3 == 0: target_col = col1
                        elif idx % 3 == 1: target_col = col2
                        else: target_col = col3
                        
                        with target_col:
                            edad_txt = ""
                            if pd.notnull(r['DT_NAC']):
                                edad_que_cumple = hoy.year - r['DT_NAC'].year
                                edad_txt = f"• Cumple {int(edad_que_cumple)} años"

                            st.markdown(f"""
                                <div class="custom-card" style="border-left-color: #ef4444; height: 100%;">
                                    <div style="font-size: 22px; margin-bottom: 5px;">🎂 ✨</div>
                                    <div class="card-title">{r['APELLIDO Y NOMBRE']}</div>
                                    <div class="card-subtitle">Área: {r['ÁREA'] if 'ÁREA' in r else 'Exincor'}</div>
                                    <div class="card-badge" style="background-color: #fee2e2; color: #991b1b;">📅 Día {int(r['DIA'])} de {r['MES_NOMBRE']}</div>
                                    <div class="card-badge-secondary">{edad_txt}</div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No se registran cumpleaños para los meses seleccionados.")
            else:
                st.info("La base de datos de cumpleaños se encuentra vacía.")

        with t_ani:
            if not df_main.empty:
                col_f_ing = next((c for c in df_main.columns if 'INGRESO' in c or 'ALTA' in c), 'FECHA INGRESO')
                df_main['DT_ING'] = limpiar_fecha(df_main, col_f_ing)
                df_main['MES_NOMBRE'] = df_main['DT_ING'].dt.month.apply(lambda x: meses_lista[int(x)-1] if pd.notnull(x) else None)
                df_main['DIA'] = df_main['DT_ING'].dt.day
                
                if sel_meses:
                    df_ani_fil = df_main[df_main['MES_NOMBRE'].isin(sel_meses)].copy()
                    if not df_ani_fil.empty:
                        df_ani_fil['MES_NUM'] = df_ani_fil['DT_ING'].dt.month
                        df_ani_fil = df_ani_fil.sort_values(['MES_NUM', 'DIA'])
                else:
                    df_ani_fil = df_main.dropna(subset=['DT_ING']).copy()
                    if not df_ani_fil.empty:
                        df_ani_fil['MES_NUM'] = df_ani_fil['DT_ING'].dt.month
                        df_ani_fil = df_ani_fil.sort_values(['MES_NUM', 'DIA'])
                
                if not df_ani_fil.empty:
                    st.write(f"Mostrando **{len(df_ani_fil)}** aniversarios laborales:")
                    
                    col1, col2, col3 = st.columns(3)
                    for idx, (_, r) in enumerate(df_ani_fil.reset_index().iterrows()):
                        if idx % 3 == 0: target_col = col1
                        elif idx % 3 == 1: target_col = col2
                        else: target_col = col3
                        
                        with target_col:
                            ant = hoy.year - r['DT_ING'].year
                            puesto_txt = r['PUESTO'] if 'PUESTO' in r else (r['ÁREA'] if 'ÁREA' in r else 'Exincor')
                            
                            # ETIQUETAS CORPORATIVAS
                            if ant >= 5:
                                tag_reconocimiento = "🎖️ Talento Senior"
                            elif ant >= 2:
                                tag_reconocimiento = "⚡ Trayectoria Consolidada"
                            else:
                                tag_reconocimiento = "🌱 Nuevo Talento"
                                
                            fecha_exacta_txt = r[col_f_ing] if col_f_ing in r else ""

                            st.markdown(f"""
                                <div class="custom-card" style="border-left-color: #0f2c59; height: 100%;">
                                    <div style="font-size: 22px; margin-bottom: 5px;">🎖️ 🏆</div>
                                    <div class="card-title">{r['APELLIDO Y NOMBRE']}</div>
                                    <div class="card-subtitle">Puesto: {puesto_txt}</div>
                                    <div style="margin-bottom: 8px;">
                                        <span class="card-badge" style="background-color: #e0f2fe; color: #0369a1;">🎉 {int(ant)} Años • {int(r['DIA'])} de {r['MES_NOMBRE']}</span>
                                    </div>
                                    <div class="card-badge-secondary" style="background-color: #f0fdf4; color: #166534; font-weight:700;">{tag_reconocimiento}</div>
                                    <div style="font-size: 11px; color: #64748B; margin-top: 6px; font-weight: 500;">Ingreso: {fecha_exacta_txt}</div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No se registran aniversarios laborales para los meses seleccionados.")
            else:
                st.info("La base de datos general se encuentra vacía.")

except Exception as e:
    st.error(f"Error crítico en la plataforma: {e}")
