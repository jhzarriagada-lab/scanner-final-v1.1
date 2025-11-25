import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import unicodedata

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Digital", page_icon="🚀", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #0A2A43 !important; }
    div.stButton > button { background-color: #4BB7A1; color: white; border: none; border-radius: 5px; }
    div.stButton > button:hover { background-color: #3AA690; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE LOGO EN LA APP ---
if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"): st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.write("### ⏱️ Test Rápido")
st.sidebar.info("Diagnóstico simple para entender tu negocio.")

# --- FUNCIÓN DE LIMPIEZA ---
def limpiar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.encode('latin-1', 'replace').decode('latin-1')

# --- FUNCIÓN: GUARDAR EN GOOGLE SHEETS ---
def guardar_en_sheets(datos):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Base de Datos Scanner").sheet1
        
        fila = [
            str(datetime.now()),
            datos['nombre'],
            datos['empresa'],
            datos['email'],
            datos['whatsapp'],
            datos['web'],
            datos['puntaje']
        ]
        sheet.append_row(fila)
        return True
    except Exception as e:
        return False

# --- FUNCIÓN GRÁFICO ---
def crear_grafico_comparativo(puntajes_usuario):
    categorias = list(puntajes_usuario.keys())
    valores_usuario = list(puntajes_usuario.values())
    valores_mercado = [12, 10, 8, 5, 5] 
    
    x = np.arange(len(categorias))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, valores_usuario, width, label='Tu Negocio', color='#0A2A43')
    ax.bar(x + width/2, valores_mercado, width, label='Promedio de otros', color='#CCCCCC')
    
    ax.set_ylabel('Puntaje')
    ax.set_title('Comparativa Simple', fontweight='bold', color='#333333')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.set_ylim(0, 22)
    
    plt.tight_layout()
    nombre = "temp_chart.png"
    plt.savefig(nombre, dpi=100)
    plt.close()
    return nombre

# --- FUNCIÓN PDF (LOGO ABAJO A LA DERECHA) ---
def generar_pdf(cliente, score_total, recs, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    
    # Espacio inicial
    pdf.ln(10)

    # 1. TÍTULO
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt="Informe de Estado Digital", ln=1, align='C')
    
    # 2. DATOS DEL CLIENTE
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(100, 100, 100)
    
    txt_empresa = limpiar_texto(f"Empresa: {cliente['empresa']}")
    txt_cliente = limpiar_texto(f"Preparado para: {cliente['nombre']}")
    
    pdf.cell(0, 6, txt=txt_empresa, ln=1, align='C')
    pdf.cell(0, 6, txt=txt_cliente, ln=1, align='C')
    pdf.ln(10) # Un poco más de espacio antes del gráfico

    # 3. GRÁFICO
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=30, w=150)
        pdf.ln(10)

    # 4. PUNTAJE
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt=f"Tu Calificacion Final: {score_total}/100", ln=1, align='C')
    pdf.ln(10)
    
    # 5. RECOMENDACIONES
    pdf.set_fill_color(75, 183, 161)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="CONSEJOS PERSONALIZADOS", ln=1, align='C', fill=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_
