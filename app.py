import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero) ---
st.set_page_config(
    page_title="Plataforma de Indicadores - RRHH",
    page_icon="📊",
    layout="wide"
)

# --- 2. ESTILOS CSS PARA LAS TARJETAS DE ANIVERSARIO ---
st.markdown("""
    <style>
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
        background-color: #e0f2fe; /* Fondo celeste suave */
        color: #0369a1; /* Texto azul */
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CARGA DE DATOS (Nómina de ejemplo)
# ==========================================
# NOTA: Si ya tenías una variable con tu Excel cargado (ej. df_nomina = pd.read_excel(...)),
# podés usar esa misma y comentar estas líneas de abajo.
@st.cache_data
def cargar_datos_ejemplo():
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
# 4. TÍTULOS E INDICADORES PRINCIPALES (Métricas)
# ==========================================
st.title("📊 Plataforma de Indicadores de RRHH")
st.write("Control de dotación, rotación y eventos del personal.")

st.divider() # Línea divisoria limpia

# Bloque de indicadores de arriba (Volviendo a activarlos)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Turnover Último Mes", value="0.0 %")
with m2:
    st.metric(label="Total Altas Acumuladas", value="4 Pers.")
with m3:
    st.metric(label="Total Bajas Acumuladas", value="5 Pers.")
with m4:
    st.metric(label="👥 Total Dotación", value=f"{len(df_nomina)} Pers.")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 5. SECCIÓN DE ANIVERSARIOS LABORALES
# ==========================================
st.header("🎉 Próximos Aniversarios Laborales")

# Extraemos los meses únicos de forma segura para el filtro
if 'Mes' in df_nomina.columns:
    meses_limpios = df_nomina['Mes'].dropna().astype(str).unique()
    meses_disponibles = sorted(list(meses_limpios))
else:
    meses_disponibles = []

# Multiselect (Si queda vacío, muestra todos de forma automática)
meses_seleccionados = st.multiselect(
    label="🔍 Filtrar por uno o más meses:",
    options=meses_disponibles,
    placeholder="Mostrando todos los meses por defecto..."
)

# Filtro dinámico
if meses_seleccionados:
    df_filtrado = df_nomina[df_nomina['Mes'].isin(meses_seleccionados)]
else:
    df_filtrado = df_nomina # Vista completa de la plataforma

st.write(f"Mostrando **{len(df_filtrado)}** colaboradores en la lista:")


# ==========================================
# 6. RENDERIZADO EN TARJETAS (Grid de 3 columnas)
# ==========================================
col1, col2, col3 = st.columns(3)

for idx, fila in df_filtrado.reset_index(drop=True).iterrows():
    # Repartimos las tarjetas equitativamente en la grilla
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
