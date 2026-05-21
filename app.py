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
        border-left: 6px solid #1E3A8A; /* Azul corporativo por defecto */
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
    .card-subtitle { font-size: 13px; color: #475569; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; }
    .card-badge { display: inline-block; background-color: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 12px; }
    
    /* Diseño estilizado para los contenedores de las métricas superiores */
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        text-align: center;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. COLORES Y TRADUCCIONES
PALETA_AZUL_GRIS = ['#1E3A8A', '#64748B', '#3B82F6', '#94A3B8', '#1D4ED8', '#CBD5E1', '#0F172A']
COLOR_BAJAS_SUAVE = '#64748B'  
MESES_ES = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

@st.cache_data(ttl=30)
def cargar_datos(gid):
    try:
        url = f"
