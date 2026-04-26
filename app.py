import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestión de RRHH - Indicadores",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Panel de Control de Recursos Humanos")
st.markdown("---")

# ==========================================
# 2. FUNCIÓN DE CARGA Y LIMPIEZA DE DATOS
# ==========================================
@st.cache_data(ttl=600)
def cargar_datos():
    # URL de exportación de tu Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1ElY2OaVFq3GzNiWoe69HCtnmQZe8rEK7/export?format=csv&gid=1543772338"
    
    # Lectura del archivo
    df = pd.read_csv(sheet_url)
    
    # NORMALIZACIÓN: Quitamos espacios y pasamos a MAYÚSCULAS los nombres de las columnas
    df.columns = df.columns.str.strip().str.upper()
    
    return df

# ==========================================
# 3. CUERPO PRINCIPAL DE LA APLICACIÓN
# ==========================================
try:
    df = cargar_datos()

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("📌 Indicadores Generales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Personal", len(df))
    
    with col2:
        if 'EDAD' in df.columns:
            promedio_edad = pd.to_numeric(df['EDAD'], errors='coerce').mean()
            st.metric("Promedio de Edad", f"{promedio_edad:.1f} años")
    
    with col3:
        if 'ANTIGÜEDAD' in df.columns:
            promedio_ant = pd.to_numeric(df['ANTIGÜEDAD'], errors='coerce').mean()
            st.metric("Antigüedad Promedio", f"{promedio_ant:.1f} años")

    with col4:
        # Ejemplo de indicador de género o rotación si tuvieras la columna
        st.metric("Empresas Gestionadas", "2")

    st.markdown("---")

    # --- FILTROS Y TABLA DE PERSONAL ---
    st.subheader("📂 Seguimiento por Áreas")
    
    # Definimos las áreas según tu estructura administrativa
    # (Administración y Finanzas se separan como pediste)
    areas_base = ["TODAS", "ADMINISTRACIÓN CONTABLE", "FINANZAS", "PRODUCCIÓN", "LOGÍSTICA", "VENTAS"]
    
    # Si la columna 'ÁREA' existe, tomamos las que haya en el sheet, si no usamos las base
    if 'ÁREA' in df.columns:
        areas_sheet = df['ÁREA'].dropna().unique().tolist()
        opciones_area = sorted(list(set(["TODAS"] + [str(a).upper().strip() for a in areas_sheet])))
    else:
        opciones_area = areas_base

    area_sel = st.selectbox("Filtrar por Departamento:", opciones_area)

    if area_sel != "TODAS" and 'ÁREA' in df.columns:
        df_filtrado = df[df['ÁREA'].str.upper().str.strip() == area_sel]
    else:
        df_filtrado = df

    # Mostrar tabla con columnas clave
    cols_a_mostrar = [c for c in ['LEGAJO', 'APELLIDO Y NOMBRE', 'PUESTO', 'ÁREA'] if c in df.columns]
    st.dataframe(df_filtrado[cols_a_mostrar], use_container_width=True)

    st.markdown("---")

    # --- MÓDULO DE DESEMPEÑO ---
    st.subheader("📈 Evaluación de Desempeño y KPI")
    
    col_eval1, col_eval2 = st.columns(2)
    
    with col_eval1:
        st.write("**Sistema de Calificación**")
        st.info("Métricas estandarizadas en escala del 1 al 5.")
        
        nombre_empleado = st.selectbox("Seleccionar empleado para revisar:", df['APELLIDO Y NOMBRE'].unique())
        nota_tecnica = st.slider("Competencias Técnicas / BIM / Diseño:", 1, 5, 3)
        nota_soft = st.slider("Competencias Blandas / Gestión:", 1, 5, 3)
        
    with col_eval2:
        st.write("**Propuestas de Mejora Implementadas**")
        propuestas = st.number_input("Cantidad de propuestas del colaborador:", min_value=0, step=1)
        
        # Lógica de puntuación según cantidad de propuestas
        if propuestas >= 3:
            puntos_mejora = 5
        elif propuestas == 2:
            puntos_mejora = 4
        elif propuestas == 1:
            puntos_mejora = 3
        else:
            puntos_mejora = 1
            
        st.metric("Puntaje por Innovación", f"{puntos_mejora} / 5")
        
    if st.button("Simular Resultado Final"):
        promedio_final = (nota_tecnica + nota_soft + puntos_mejora) / 3
        st.success(f"El promedio de desempeño proyectado para {nombre_empleado} es: {promedio_final:.2f}")

except Exception as e:
    st.error("⚠️ Error de Conexión o Estructura")
    st.write(f"No pudimos procesar los datos. Detalle: {e}")
    st.warning("Asegúrate de que la primera fila de tu Excel tenga los nombres: LEGAJO, APELLIDO Y NOMBRE, PUESTO, ÁREA, EDAD.")
