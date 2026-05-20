import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Plataforma de Indicadores - RRHH",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (Color y Tarjetas) ---
st.markdown("""
    <style>
    /* Estilos generales de la app */
    .main {
        background-color: #f8fafc;
    }
    
    /* Tarjetas de Aniversario */
    .anniversary-card {
        background-color: #ffffff;
        border-left: 6px solid #1e3a8a; /* Azul fuerte corporativo */
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
        font-family: 'Source Sans Pro', sans-serif;
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
        background-color: #e0f2fe; /* Celeste/Azul suave muy estético */
        color: #0369a1; /* Texto azul oscuro */
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARGA DE DATOS (Simulada o Real)
# ==========================================
# REEMPLAZÁ ESTE BLOQUE por tu lectura real del Excel si lo tenés en otra variable, por ejemplo:
# df_nomina = pd.read_excel("tu_archivo.xlsx")

@st.cache_data
def cargar_datos_ejemplo():
    # Datos de prueba basados en tu captura para que veas el diseño de inmediato
    datos = [
        {"Nombre": "Daniel Abalos", "Puesto": "Maquinista Impresora", "Mes": "Mayo", "Antiguedad": 5},
        {"Nombre": "Roman Aban", "Puesto": "Supervisor de Mantenimiento", "Mes": "Junio", "Antiguedad": 3},
        {"Nombre": "Estela Bustamante", "Puesto": "Jefe de Administración", "Mes": "Mayo", "Antiguedad": 10},
        {"Nombre": "Carlos Gómez", "Puesto": "Operario de Producción", "Mes": "Julio", "Antiguedad": 2},
        {"Nombre": "Laura Martínez", "Puesto": "Analista de COMEX", "Mes": "Mayo", "Antiguedad": 4},
        {"Nombre": "Jorge Rodriguez", "Puesto": "Encargado de Logística", "Mes": "Agosto", "Antiguedad": 8}
    ]
    return pd.DataFrame(datos)

df_nomina = cargar_datos_ejemplo()


# ==========================================
# 2. SECCIÓN DE INDICADORES (Métricas de cabecera)
# ==========================================
st.title("📊 Plataforma de Indicadores de RRHH")
st.write("Control de dotación, rotación y eventos del personal.")
st.hr()

# Métricas rápidas arriba (manteniendo la prolijidad de tu primera pantalla)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="📈 Turnover", value="2.4 %", delta="-0.5 %")
with m2:
    st.metric(label="✨ Altas Mes", value="4", delta="2")
with m3:
    st.metric(label="📉 Bajas Mes", value="1", delta="-1")
with m4:
    st.metric(label="👥 Total Dotación", value=str(len(df_nomina)))

st.br()


# ==========================================
# 3. PESTAÑA / SECCIÓN DE ANIVERSARIOS
# ==========================================
st.header("🎉 Próximos Aniversarios Laborales")

# --- TRATAMIENTO SEGURO CONTRA ERRORES ---
# Limpiamos nulos de la columna 'Mes', pasamos a texto y ordenamos para que no rompa el multiselect
if 'Mes' in df_nomina.columns:
    meses_limpios = df_nomina['Mes'].dropna().astype(str).unique()
    meses_disponibles = sorted(list(meses_limpios))
else:
    meses_disponibles = []

# --- FILTRO MULTISELECT (Si está vacío, muestra TODOS) ---
meses_seleccionados = st.multiselect(
    label="🔍 Filtrar por uno o más meses:",
    options=meses_disponibles,
    placeholder="Mostrando todos los meses de forma automática..."
)

# Lógica del filtro abierto
if meses_seleccionados:
    df_filtrado = df_nomina[df_nomina['Mes'].isin(meses_seleccionados)]
else:
    df_filtrado = df_nomina  # Si no hay selección, recuperamos la vista completa

st.write(f"Mostrando **{len(df_filtrado)}** colaboradores en la lista:")


# ==========================================
# 4. RENDERIZADO EN FORMATO TARJETAS (GRID)
# ==========================================
# Distribución limpia en 3 columnas
col1, col2, col3 = st.columns(3)

# Resetear el índice para que el reparto sea correlativo y prolijo
for idx, fila in df_filtrado.reset_index(drop=True).iterrows():
    
    # Repartimos de forma equitativa entre las 3 columnas
    if idx % 3 == 0:
        columna_destino = col1
    elif idx % 3 == 1:
        columna_destino = col2
    else:
        columna_destino = col3
        
    with columna_destino:
        # Armamos la tarjeta con HTML inyectado de forma segura
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
