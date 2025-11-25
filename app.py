import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import unicodedata
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Scanner Digital", page_icon="🍊", layout="centered")

# --- ID DE LA CARPETA DE DRIVE (¡PEGALO AQUÍ!) ---
# Ejemplo: "123456abcdefg..." (Lo sacas de la URL de tu carpeta)
CARPETA_ID = 1__TtGjCa5ZvV2sFUr08th1keyGuNuO42

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #1E4620 !important; }
    div.stButton > button { background-color: #FF7F50; color: white; border: none; border-radius: 8px; }
    div.stButton > button:hover { background-color: #E06030; color: white; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"): st.sidebar.image("logo.png", use_container_width=True)

# --- FUNCIÓN LIMPIEZA ---
def limpiar_texto(texto):
    if not isinstance(texto, str): texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.encode('latin-1', 'replace').decode('latin-1')

# --- FUNCIÓN: SUBIR PDF A GOOGLE DRIVE ---
def subir_a_drive(pdf_bytes, nombre_archivo):
    try:
        # Autenticación (Usamos las mismas credenciales que para Sheets)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ['https://www.googleapis.com/auth/drive'])
        
        # Crear servicio de Drive
        service = build('drive', 'v3', credentials=creds)
        
        # Metadatos del archivo
        file_metadata = {
            'name': nombre_archivo,
            'parents': [CARPETA_ID] # Aquí le decimos en qué carpeta guardarlo
        }
        
        # Convertir los bytes del PDF a un formato que Drive entienda
        media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype='application/pdf')
        
        # Subir
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # Retornar el enlace para verlo
        return file.get('webViewLink')
        
    except Exception as e:
        st.error(f"Error subiendo a Drive: {e}")
        return "Error al subir PDF"

# --- FUNCIÓN: GUARDAR EN SHEETS (Ahora con Link) ---
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
            datos['puntaje'],
            datos['link_pdf'] # Nueva columna
        ]
        sheet.append_row(fila)
        return True
    except: return False

# --- GRÁFICO ---
def crear_grafico_comparativo(puntajes_usuario):
    categorias = list(puntajes_usuario.keys())
    valores_usuario = list(puntajes_usuario.values())
    valores_mercado = [12, 10, 8, 5, 5] 
    x = np.arange(len(categorias))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, valores_usuario, width, label='Tu Negocio', color='#1E4620')
    ax.bar(x + width/2, valores_mercado, width, label='Promedio', color='#E5E7EB')
    ax.set_title('Tu Desempeño vs El Mercado', fontweight='bold', color='#1E4620')
    ax.set_xticks(x); ax.set_xticklabels(categorias); ax.legend(); ax.set_ylim(0, 22)
    ax.axhline(y=15, color='#F59E0B', linestyle='--', linewidth=1.5, alpha=0.8)
    plt.tight_layout()
    nombre = "temp_chart.png"
    plt.savefig(nombre, dpi=100); plt.close()
    return nombre

# --- PDF ---
def generar_pdf_bytes(cliente, score_total, recs, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(20); pdf.set_right_margin(20)
    
    # Diseño
    pdf.set_fill_color(30, 70, 32); pdf.rect(0, 0, 210, 20, 'F'); pdf.ln(25)
    pdf.set_font("Arial", 'B', 24); pdf.set_text_color(30, 70, 32)
    pdf.cell(0, 10, txt="Informe de Crecimiento", ln=1, align='C')
    
    pdf.set_font("Arial", '', 11); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, txt=limpiar_texto(f"Empresa: {cliente['empresa']}"), ln=1, align='C')
    pdf.cell(0, 6, txt=limpiar_texto(f"Solicitado por: {cliente['nombre']}"), ln=1, align='C')
    pdf.ln(10)

    if os.path.exists(chart_path): pdf.image(chart_path, x=30, w=150); pdf.ln(10)

    pdf.set_font("Arial", 'B', 18); pdf.set_text_color(30, 70, 32)
    pdf.cell(0, 10, txt=f"Calificacion Digital: {score_total}/100", ln=1, align='C'); pdf.ln(10)
    
    pdf.set_fill_color(255, 127, 80); pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt="OPORTUNIDADES DE MEJORA", ln=1, align='C', fill=True); pdf.ln(8)
    
    pdf.set_font("Arial", size=11); pdf.set_text_color(50, 50, 50)
    for rec in recs:
        pdf.set_text_color(255, 127, 80); pdf.cell(8, 8, txt=">", align='C')
        pdf.set_text_color(0, 0, 0); pdf.multi_cell(0, 8, txt=limpiar_texto(rec)); pdf.ln(2)

    if os.path.exists("logo.png"): pdf.image("logo.png", x=160, y=255, w=30)
    
    # Retorna los bytes 'crudos'
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🍊 Scanner de Crecimiento Digital")
st.markdown("Descubre en 2 minutos dónde estás perdiendo clientes.")

with st.expander("📝 Tus datos para el reporte", expanded=True):
    col_a, col_b = st.columns(2)
    nombre = col_a.text_input("Tu Nombre")
    empresa = col_b.text_input("Nombre del Negocio")
    col_c, col_d = st.columns(2)
    email = col_c.text_input("Correo Electrónico")
    whatsapp = col_d.text_input("WhatsApp (Opcional)")
    web_input = st.text_input("Sitio Web actual (Si tienes)")

with st.form("audit_simple"):
    # (Preguntas resumidas por espacio, son las mismas de antes)
    st.subheader("1. Imagen y Marca")
    p1 = st.radio("¿Tienes un logotipo oficial?", ["Sí, manual completo", "Solo tengo el logo", "No, uso cualquier imagen"])
    p2 = st.selectbox("¿Se entiende rápido qué vendes?", ["Sí, en menos de 3 segundos", "Es confuso", "No estoy seguro"])
    st.divider(); st.subheader("2. Presencia Web")
    p3 = st.radio("¿Tienes página web?", ["Sí, web profesional/tienda", "Básica / Linktree", "No, solo redes"])
    p4 = st.checkbox("¿Apareces en Google Maps?")
    st.divider(); st.subheader("3. Contenido")
    p5 = st.select_slider("Frecuencia", options=["Nunca", "1/mes", "1/semana", "2-3/semana", "Diario"])
    p6 = st.radio("¿Usas video vertical?", ["Sí, es mi foco", "A veces", "Nunca"])
    p7 = st.radio("¿Humanizas la marca?", ["Sí, salimos en cámara", "Solo productos"])
    st.divider(); st.subheader("4. Publicidad")
    p8 = st.radio("¿Inviertes en publicidad?", ["Sí, presupuesto fijo", "A veces (Botón Promocionar)", "Nunca"])
    p10 = st.radio("¿Gestión de contactos?", ["CRM / Sistema", "Excel / Cuaderno", "No los guardo"])
    st.divider(); st.subheader("5. Velocidad")
    p11 = st.select_slider("Tiempo de respuesta", options=["+24 horas", "Mismo día", "Al instante"])
    st.markdown("---")
    submitted = st.form_submit_button("🚀 Ver Resultados")

if submitted:
    if not nombre or not email:
        st.error("⚠️ Nombre y Correo son obligatorios.")
    else:
        # Lógica de puntaje (La misma de antes)
        s1=0; s2=0; s3=0; s4=0; s5=0; recs = []
        if "manual" in p1: s1+=10
        elif "logo" in p1: s1+=5; recs.append("Imagen: Define tus colores oficiales para diferenciarte.")
        else: recs.append("Imagen: Necesitas una identidad visual profesional urgente.")
        if "3 segundos" in p2: s1+=10
        else: recs.append("Mensaje: Tu biografía es confusa. Aclara qué vendes.")
        if "profesional" in p3: s2+=15
        elif "Básica" in p3: s2+=5; recs.append("Web: Una web profesional aumentaría tus ventas.")
        else: recs.append("Web: Depender solo de Instagram es riesgoso. Crea tu web.")
        if p4: s2+=5
        else: recs.append("Google: Regístrate gratis en Google Maps.")
        if p5=="Diario": s3+=8
        elif "2-3" in p5: s3+=5
        else: recs.append("Frecuencia: Publica al menos 3 veces por semana.")
        if "foco" in p6: s3+=7
        elif "A veces" in p6: s3+=3
        else: recs.append("Video: El video vertical (Reels) es obligatorio hoy.")
        if "salimos" in p7: s3+=5
        else: recs.append("Humanización: Muestra al equipo, la gente conecta con gente.")
        if "fijo" in p8: s4+=20
        elif "A veces" in p8: s4+=10; recs.append("Ads: El botón 'Promocionar' no basta. Usa campañas profesionales.")
        else: recs.append("Tráfico: Sin publicidad, tu crecimiento será muy lento.")
        if "CRM" in p10: s5+=10
        elif "Excel" in p10: s5+=5; recs.append("Datos: Pasa del cuaderno a un sistema digital.")
        else: recs.append("Ventas: Estás perdiendo clientes por no guardar sus datos.")
        if "instante" in p11: s5+=10
        elif "Mismo día" in p11: s5+=5
        else: recs.append("Atención: La velocidad cierra ventas. Responde más rápido.")
        
        score = min(s1+s2+s3+s4+s5, 100)
        
        # 1. Generar Chart y Bytes del PDF
        chart = crear_grafico_comparativo({"Imagen":s1, "Web":s2, "Contenido":s3, "Ads":s4, "Ventas":s5})
        cliente_data = {'nombre':nombre, 'empresa':empresa}
        pdf_bytes = generar_pdf_bytes(cliente_data, score, recs, chart)
        
        # 2. Subir a Drive y obtener Link
        with st.spinner("Generando reporte y guardando en la nube..."):
            link_drive = subir_a_drive(pdf_bytes, f"Reporte_{empresa}_{nombre}.pdf")
        
        # 3. Guardar en Sheets con el Link
        guardar_en_sheets({
            'nombre':nombre, 'empresa':empresa, 'email':email, 
            'whatsapp':whatsapp, 'web':web_input, 'puntaje':score, 
            'link_pdf': link_drive
        })
        
        # 4. Mostrar
        st.divider()
        col1, col2 = st.columns([1,2])
        with col1:
            st.metric("Puntaje", f"{score}/100")
            if score<50: st.error("Necesita Atención")
            else: st.success("Buen Potencial")
        with col2:
            st.image(chart)
            
        st.download_button("📥 Descargar Reporte Color", data=pdf_bytes, file_name="Reporte_Growth.pdf", mime="application/pdf")
        if os.path.exists(chart): os.remove(chart)
