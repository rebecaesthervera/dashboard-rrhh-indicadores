import streamlit as pd
import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA O ESTILOS ---
st.markdown("""
    <style>
    .anniversary-card {
        background-color: #f0f4f8;
        border-left: 5px solid #ff4b4b; /* Color que resalte (ej. Rojo/Naranja Exincor) */
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 5px;
    }
    .card-subtitle {
        font-size: 14px;
        color: #64748b;
    }
    .highlight {
        color: #ff4b4b;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎉 Centro de Aniversarios Laborales")

# --- 1. CARGA DE DATOS (Ejemplo) ---
# Aquí iría tu lectura de Excel / Base de datos (ej. Nómina Exincor)
nomina = [
    {"nombre": "Daniel Abalos", "puesto": "Maquinista Impresora", "mes": "Mayo", "anios": 5},
    {"nombre": "Roman Aban", "puesto": "Supervisor de Mantenimiento", "mes": "Junio", "anios": 3},
    {"nombre": "Estela Bustamante", "puesto": "Jefe de Administración", "mes": "Mayo", "anios": 10},
]

# --- 2. FILTROS (Si no elige nada, muestra TODOS) ---
meses_disponibles = list(set([emp["mes"] for emp in nomina]))
meses_seleccionados = st.multiselect("Filtrar por Mes de Aniversario", opciones=meses_disponibles, default=[])

# Aplicar filtro si hay selección; si no, mostrar todos
if meses_seleccionados:
    empleados_filtrados = [emp for emp in nomina if emp["mes"] in meses_seleccionados]
else:
    empleados_filtrados = nomina

# --- 3. DESPLIEGUE EN TARJETAS CON COLOR ---
st.write(f"Mostrando {len(empleados_filtrados)} aniversarios:")

# Creamos columnas para que las tarjetas no ocupen todo el ancho horizontal si son muchas
col1, col2 = st.columns(2)

for i, emp in enumerate(empleados_filtrados):
    # Alternamos entre columna 1 y columna 2 para diseño Grid
    target_col = col1 if i % 2 == 0 else col2
    
    with target_col:
        st.markdown(f"""
            <div class="anniversary-card">
                <div class="card-title">🎂 {emp['nombre']}</div>
                <div class="card-subtitle">Puesto: {emp['puesto']}</div>
                <div style="margin-top: 10px; font-size: 15px;">
                    ¡Cumple <span class="highlight">{emp['anios']} años</span> en la empresa este mes de <b>{emp['mes']}</b>!
                </div>
            </div>
        """, unsafe_allow_html=True)
