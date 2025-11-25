import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Pro 12 Puntos", page_icon="🎯", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #0A2A43 !important; }
    div.stButton > button { background-color: #4BB7A1; color: white; border: none; border-radius: 5px; }
    div.stButton > button:hover { background-color: #3AA690; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE LOGO ---
if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)
elif os.path.exists("logo.jpg"): st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.write("### ⏱️ Auditoría Express")
st.sidebar.info("Comparativa de mercado inmediata.")

# --- FUNCIÓN: GUARDAR EN GOOGLE SHEETS ---
def guardar_en_sheets(datos):
    try:
        # Buscamos las credenciales en los secretos de Streamlit
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Esta lógica crea las credenciales desde los secretos cargados en la nube
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Abre la hoja por su nombre (Asegúrate que sea exacto)
        sheet = client.open("Base de Datos Scanner").sheet1
        
        # Fila a insertar
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
        st.warning(f"No se pudo guardar en la base de datos (Error de conexión), pero tu PDF se generará igual. Error: {e}")
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
    ax.bar(x + width/2, valores_mercado, width, label='Promedio Industria', color='#CCCCCC')
    
    ax.set_ylabel('Puntaje (Max 20)')
    ax.set_title('Tu Desempeño vs. El Mercado', fontweight='bold', color='#333333')
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.legend()
    ax.axhline(y=15, color='#4BB7A1', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_ylim(0, 22)
    
    plt.tight_layout()
    nombre = "temp_chart_benchmark.png"
    plt.savefig(nombre, dpi=100)
    plt.close()
    return nombre

# --- FUNCIÓN PDF ---
def generar_pdf(cliente, score_total, recs, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(75, 183, 161)
    pdf.rect(0, 0, 210, 15, 'F')
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt="Diagnostico de Competitividad", ln=1, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, txt=f"Empresa: {cliente['empresa']} | Fecha: {pd.Timestamp.now().strftime('%d/%m/%Y')}", ln=1, align='C')
    pdf.ln(5)
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=35, w=140)
        pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(10, 42, 67)
    pdf.cell(0, 10, txt=f"Puntaje Global: {score_total}/100", ln=1, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, txt="  PLAN DE ACCION PRIORITARIO:", ln=1, align='L', fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(50, 50, 50)
    for rec in recs:
        pdf.set_text_color(75, 183, 161)
        pdf.cell(5, 6, txt=">", align='R')
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, txt=rec.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🎯 Scanner de Mercado")
st.markdown("Descubre cómo posiciona tu marca frente al promedio de tu industria.")

with st.expander("👤 Tus Datos", expanded=True):
    col_a, col_b = st.columns(2)
    nombre = col_a.text_input("Tu Nombre")
    empresa = col_b.text_input("Nombre del Negocio")
    col_c, col_d = st.columns(2)
    email = col_c.text_input("Correo Electrónico")
    whatsapp = col_d.text_input("WhatsApp (Opcional)")
    web_input = st.text_input("Sitio Web actual")

with st.form("audit_12_points"):
    st.subheader("1. Identidad (Branding)")
    p1 = st.radio("Identidad Visual", ["Manual completo", "Solo Logo", "Nada definido"])
    p2 = st.selectbox("Claridad", ["Muy claro (3 seg)", "Confuso", "No definido"])
    st.divider()
    st.subheader("2. Infraestructura (Web/SEO)")
    p3 = st.radio("Sitio Web", ["E-commerce/Web Pro", "Básica/Linktree", "No tengo"])
    p4 = st.checkbox("¿Apareces en Google Maps?")
    st.divider()
    st.subheader("3. Contenido")
    p5 = st.select_slider("Frecuencia", options=["Casi Nunca", "1/sem", "3/sem", "Diario"])
    p6 = st.radio("Video Vertical", ["Sí, foco principal", "A veces", "Nunca"])
    p7 = st.radio("Humanización", ["Sí, mostramos equipo", "Solo productos"])
    st.divider()
    st.subheader("4. Tráfico (Ads)")
    p8 = st.radio("Inversión Ads", ["Presupuesto fijo", "Solo botón Promocionar", "Cero"])
    p9 = st.checkbox("¿Usas Píxel de Meta?")
    st.divider()
    st.subheader("5. Ventas (Conversión)")
    p10 = st.radio("Base de Datos", ["CRM Activo", "Excel", "Nada"])
    p11 = st.select_slider("Tiempo Respuesta", options=["+24h", "Mismo día", "Inmediato"])
    p12 = st.checkbox("¿Proceso de cierre definido?")
    st.markdown("---")
    submitted = st.form_submit_button("📊 Ver Comparativa de Mercado")

if submitted:
    if not nombre or not email:
        st.error("⚠️ Nombre y Email son obligatorios.")
    else:
        # CÁLCULOS
        s1 = 0; s2 = 0; s3 = 0; s4 = 0; s5 = 0
        recs = []
        # Branding
        if p1 == "Manual completo": s1 += 10
        elif p1 == "Solo Logo": s1 += 5
        if p2 == "Muy claro (3 seg)": s1 += 10
        # Infra
        if p3 == "E-commerce/Web Pro": s2 += 15
        elif p3 == "Básica/Linktree": s2 += 5
        if p4: s2 += 5
        # Contenido
        if p5 == "Diario": s3 += 8
        elif p5 == "3/sem": s3 += 5
        if p6 == "Sí, foco principal": s3 += 7
        elif p6 == "A veces": s3 += 3
        if p7 == "Sí, mostramos equipo": s3 += 5
        # Ads
        if p8 == "Presupuesto fijo": s4 += 15
        elif p8 == "Solo botón Promocionar": s4 += 5
        if p9: s4 += 5
        # Ventas
        if p10 == "CRM Activo": s5 += 10
        elif p10 == "Excel": s5 += 5
        if p11 == "Inmediato": s5 += 5
        elif p11 == "Mismo día": s5 += 3
        if p12: s5 += 5
        
        score_total = min(s1+s2+s3+s4+s5, 100)
        
        # --- INTENTO DE GUARDAR EN SHEETS ---
        datos_para_sheet = {
            'nombre': nombre, 'empresa': empresa, 'email': email,
            'whatsapp': whatsapp, 'web': web_input, 'puntaje': score_total
        }
        # Llamamos a la función. Si falla, el usuario verá un aviso pero el PDF funciona.
        guardar_en_sheets(datos_para_sheet)

        # RESULTADOS VISUALES
        dict_puntajes = {"Marca": s1, "Web": s2, "Contenido": s3, "Ads": s4, "Ventas": s5}
        
        st.divider()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Tu Nivel Digital", f"{score_total}/100")
            if score_total < 50: st.error("Debajo del promedio"); recs.append("ESTRATEGIA: Pierdes cuota frente a competidores.")
            else: st.success("Competitivo")
        with c2:
            chart_file = crear_grafico_comparativo(dict_puntajes)
            st.image(chart_file)
            
        cliente_data = {'nombre': nombre, 'empresa': empresa}
        pdf_bytes = generar_pdf(cliente_data, score_total, recs, chart_file)
        st.download_button("📥 Descargar Reporte Comparativo", data=pdf_bytes, file_name="Auditoria_Mercado.pdf", mime="application/pdf")
        if os.path.exists(chart_file): os.remove(chart_file)
