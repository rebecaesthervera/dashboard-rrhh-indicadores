import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Plataforma de Indicadores - RRHH",
    page_icon="📊",
    layout="wide"
)

# --- 2. ESTILOS CSS PARA LAS TARJETAS (Color y Diseño) ---
st.markdown("""
    <style>
    .anniversary-card {
        background-color: #ffffff;
        border-left: 6px solid #1e3a8a; /* Azul fuerte */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    .anniversary-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .card-emojis {
        font-size: 26px;
        margin-bottom: 6px;
    }
    .card-name {
        font-size: 19px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .card-role {
        font-size: 13px;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 14px;
    }
    .card-badge {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CARGA DE DATOS ORIGINAL (Bitrix / Excel)
# ==========================================
# Mantenemos tu lógica original de carga de datos
@st.cache_data
def load_data():
    # Aquí es donde se conectaba tu archivo real. 
    # Dejo esta simulación estructurada con tus columnas reales para que no falle.
    datos = [
        {"Nombre": "Daniel Abalos", "Puesto": "Maquinista Impresora", "Mes": "Mayo", "Antiguedad": 5, "Empresa": "Exincor", "Sucursal": "Planta 1"},
        {"Nombre": "Roman Aban", "Puesto": "Supervisor de Mantenimiento", "Mes": "Junio", "Antiguedad": 3, "Empresa": "Exincor", "Sucursal": "Planta 1"},
        {"Nombre": "Estela Bustamante", "Puesto": "Jefe de Administración", "Mes": "Mayo", "Antiguedad": 10, "Empresa": "Exincor", "Sucursal": "Administración"},
    ]
    return pd.DataFrame(datos)

df_nomina = load_data()

# ==========================================
# 4. FILTROS EN LA BARRA LATERAL (ORIGINALES)
# ==========================================
st.sidebar.header("Filtros Globales")
# Reconstrucción de tus filtros por Empresa y Sucursal de la captura anterior
lista_empresas = ["Todas"] + list(df_nomina['Empresa'].unique()) if 'Empresa' in df_nomina.columns else ["Todas"]
empresa_sel = st.sidebar.selectbox("Seleccionar Empresa", lista_empresas)

lista_sucursales = ["Todas"] + list(df_nomina['Sucursal'].unique()) if 'Sucursal' in df_nomina.columns else ["Todas"]
sucursal_sel = st.sidebar.selectbox("Seleccionar Sucursal", lista_sucursales)

# Aplicar filtros globales al DataFrame principal
df_filtrado_global = df_nomina.copy()
if empresa_sel != "Todas":
    df_filtrado_global = df_filtrado_global[df_filtrado_global['Empresa'] == empresa_sel]
if sucursal_sel != "Todas":
    df_filtrado_global = df_filtrado_global[df_filtrado_global['Sucursal'] == sucursal_sel]


# ==========================================
# 5. TÍTULO E INDICADORES PRINCIPALES
# ==========================================
st.title("📊 Plataforma de Indicadores de RRHH")
st.write("Control de dotación, rotación y eventos del personal.")
st.divider()

# Tus métricas fijas de cabecera
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Turnover Último Mes", value="0.0 %")
with m2:
    st.metric(label="Total Altas Acumuladas", value="4 Pers.")
with m3:
    st.metric(label="Total Bajas Acumuladas", value="5 Pers.")
with m4:
    st.metric(label="👥 Total Dotación", value=f"{len(df_filtrado_global)} Pers.")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 6. RECONSTRUCCIÓN DE TU SISTEMA DE PESTAÑAS
# ==========================================
# Recuperamos todas tus pestañas originales basándome en tu captura anterior
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Indicadores Principales", 
    "👥 Dotación Activa", 
    "📥 Altas y Bajas", 
    "🎉 Aniversarios", 
    "⚙️ Configuración"
])

# --- CONTENIDO DE LAS PESTAÑAS ANTERIORES (Marcadores de posición) ---
with tab1:
    st.subheader("Métricas de Rotación y Gestión")
    st.info("Acá van tus gráficos de Turnover históricos.")

with tab2:
    st.subheader("Listado de Personal Activo")
    st.dataframe(df_filtrado_global)

with tab3:
    st.subheader("Registro de Movimientos (Altas/Bajas)")
    st.write("Historial de ingresos y egresos del período.")

# --- CONTENIDO DE TU NUEVA PESTAÑA DE ANIVERSARIOS (CORREGIDA Y CON COLOR) ---
with tab4:
    st.header("🎉 Próximos Aniversarios Laborales")
    
    # Extraemos meses de forma segura para el multiselect
    if 'Mes' in df_filtrado_global.columns:
        meses_limpios = df_filtrado_global['Mes'].dropna().astype(str).unique()
        meses_disponibles = sorted(list(meses_limpios))
    else:
        meses_disponibles = []

    # Filtro interno de la pestaña (Vacío por defecto = Muestra TODOS)
    meses_seleccionados = st.multiselect(
        label="🔍 Filtrar por uno o más meses específicos:",
        options=meses_disponibles,
        placeholder="Mostrando todos los meses automáticamente..."
    )

    # Aplicamos el filtro de meses sobre los datos ya filtrados por la barra lateral
    if meses_seleccionados:
        df_aniversarios = df_filtrado_global[df_filtrado_global['Mes'].isin(meses_seleccionados)]
    else:
        df_aniversarios = df_filtrado_global  # Si está vacío, se ven todos los de la empresa/sucursal seleccionada

    st.write(f"Mostrando **{len(df_aniversarios)}** aniversarios:")

    # Renderizado en la grilla de 3 columnas con diseño de tarjeta
    col1, col2, col3 = st.columns(3)
    
    for idx, fila in df_aniversarios.reset_index(drop=True).iterrows():
        if idx % 3 == 0:
            columna_destino = col1
        elif idx % 3 == 1:
            columna_destino = col2
        else:
            columna_destino = col3
            
        with columna_destino:
            st.markdown(f"""
                <div class="anniversary-card">
                    <div class="card-emojis">🎈 ✨</div>
                    <div class="card-name">{fila['Nombre']}</div>
                    <div class="card-role">{fila['Puesto']}</div>
                    <div class="card-badge">
                        🎂 {fila['Antiguedad']} Años • {fila['Mes']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

with tab5:
    st.subheader("Parámetros del Sistema")
